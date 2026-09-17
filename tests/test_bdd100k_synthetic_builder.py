import csv
import hashlib
import tempfile
import unittest
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from ddm4ip.degradations.degradation import instantiate_single_kernel
from ddm4ip.benchmarks.bdd100k_synthetic import (
    SourceRecord,
    build_benchmark,
    inspect_sources,
    make_noise_seed,
    preprocess_image,
    split_sources,
)


class SyntheticBuilderInventoryTests(unittest.TestCase):
    def _write_image(self, path: Path, size=(1280, 720), mode="RGB", color=(10, 20, 30)):
        path.parent.mkdir(parents=True, exist_ok=True)
        if mode == "BROKEN":
            path.write_bytes(b"not an image")
        else:
            Image.new(mode, size, color=color).save(path, format="PNG")

    def _write_manifest(self, root: Path):
        rows = []
        for split in ("train", "val"):
            for path in sorted((root / split / "clean").glob("*.png")):
                rows.append({"split": split, "role": "clean", "filename": path.name})
        manifest = root / "manifest.csv"
        with manifest.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["split", "role", "filename"])
            writer.writeheader()
            writer.writerows(rows)
        return hashlib.sha256(manifest.read_bytes()).hexdigest()

    def test_inspect_sources_returns_sorted_valid_records_and_digest(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_image(root / "val" / "clean" / "b.png", color=(1, 2, 3))
            self._write_image(root / "train" / "clean" / "a.png", color=(4, 5, 6))
            view_digest = self._write_manifest(root)

            records, digest = inspect_sources(
                root, view_digest, expected_source_count=2
            )

            self.assertEqual([r.source_id for r in records], ["a", "b"])
            self.assertEqual(
                {(r.width, r.height, r.channels) for r in records}, {(1280, 720, 3)}
            )
            self.assertRegex(digest, r"^[0-9a-f]{64}$")

    def test_inspect_sources_rejects_inventory_integrity_errors(self):
        cases = ("wrong-manifest", "duplicate-id", "duplicate-content", "wrong-size", "decode", "non-rgb", "wrong-count")
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self._write_image(root / "train" / "clean" / "a.png")
                if case == "duplicate-id":
                    self._write_image(root / "val" / "clean" / "a.png", color=(1, 1, 1))
                elif case == "duplicate-content":
                    source = root / "train" / "clean" / "a.png"
                    (root / "val" / "clean").mkdir(parents=True)
                    (root / "val" / "clean" / "b.png").write_bytes(source.read_bytes())
                elif case == "wrong-size":
                    self._write_image(root / "val" / "clean" / "b.png", size=(1279, 720))
                elif case == "decode":
                    self._write_image(root / "val" / "clean" / "b.png", mode="BROKEN")
                elif case == "non-rgb":
                    self._write_image(
                        root / "val" / "clean" / "b.png", mode="L", color=10
                    )
                else:
                    self._write_image(root / "val" / "clean" / "b.png")
                view_digest = self._write_manifest(root)
                expected_digest = "0" * 64 if case == "wrong-manifest" else view_digest
                expected_count = 3 if case == "wrong-count" else 2
                with self.assertRaises((ValueError, FileNotFoundError, OSError)):
                    inspect_sources(
                        root,
                        expected_digest,
                        expected_source_count=expected_count,
                    )

    def test_split_sources_is_deterministic_and_exact(self):
        records = [
            SourceRecord(
                f"id-{i:04d}",
                f"train/clean/id-{i:04d}.jpg",
                1,
                hashlib.sha256(str(i).encode()).hexdigest(),
                1280,
                720,
                3,
            )
            for i in range(1739)
        ]
        roles = split_sources(records, split_seed=42)

        self.assertEqual(
            {key: len(value) for key, value in roles.items()},
            {
                "step1_observation": 1000,
                "step2_clean": 100,
                "test_paired": 500,
                "dev_reserve": 139,
            },
        )
        self.assertEqual(
            set().union(*(set(r.source_id for r in value) for value in roles.values())),
            {r.source_id for r in records},
        )
        self.assertEqual(split_sources(records, 42), roles)
        self.assertNotEqual(split_sources(records, 43), roles)

    def test_preprocess_uses_fixed_center_crop_and_bicubic_resize(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "coded.png"
            array = np.zeros((720, 1280, 3), dtype=np.uint8)
            array[:, :, 0] = np.arange(1280, dtype=np.uint8)[None, :]
            array[:, :, 1] = np.arange(720, dtype=np.uint8)[:, None]
            Image.fromarray(array, mode="RGB").save(path)

            actual = preprocess_image(path)
            expected_image = Image.open(path).crop((280, 0, 1000, 720)).resize(
                (256, 256), resample=Image.Resampling.BICUBIC
            ).convert("RGB")
            expected = torch.from_numpy(np.asarray(expected_image).copy()).permute(2, 0, 1).float() / 255

            self.assertEqual(tuple(actual.shape), (3, 256, 256))
            torch.testing.assert_close(actual, expected, rtol=0, atol=0)

            wrong_size = Path(temporary) / "wrong.png"
            Image.new("RGB", (640, 360)).save(wrong_size)
            with self.assertRaises(ValueError):
                preprocess_image(wrong_size)

    def test_kernel_and_noise_seed_are_stable(self):
        config = {
            "kind": "motion_blur",
            "kernel_size": 32,
            "intensity": 0.5,
            "rnd_seed": 1,
        }
        first = instantiate_single_kernel(config, noise_model=None).get_kernel()
        second = instantiate_single_kernel(config, noise_model=None).get_kernel()
        self.assertEqual(tuple(first.shape), (1, 1, 32, 32))
        self.assertTrue(torch.isfinite(first).all())
        self.assertTrue((first >= 0).all())
        self.assertAlmostEqual(float(first.sum()), 1.0, places=6)
        self.assertGreater(int((first > 0).sum()), 1)
        self.assertEqual(hashlib.sha256(first.numpy().tobytes()).digest(), hashlib.sha256(second.numpy().tobytes()).digest())
        self.assertEqual(make_noise_seed("test_paired", "source-1"), make_noise_seed("test_paired", "source-1"))
        self.assertNotEqual(make_noise_seed("test_paired", "source-1"), make_noise_seed("test_paired", "source-2"))

    def test_build_preflights_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "view"
            for index, (split, name) in enumerate((("train", "a"), ("train", "b"), ("val", "c"), ("val", "d"))):
                self._write_image(root / split / "clean" / f"{name}.png", color=(index + 1, 2, 3))
            view_digest = self._write_manifest(root)
            records, source_digest = inspect_sources(root, view_digest, expected_source_count=4)
            destination = Path(temporary) / "benchmark"

            result = build_benchmark(
                records,
                source_digest,
                destination,
                source_root=root,
            )
            self.assertEqual(result["counts"]["test_paired"], 0)
            expected_provenance = {
                "split_manifest_sha256": destination / "split-manifest.csv",
                "pairs_manifest_sha256": destination / "test-paired" / "pairs.jsonl",
                "preprocessing_sha256": destination / "preprocessing.json",
                "degradation_sha256": destination / "degradation" / "degradation.json",
            }
            for field, path in expected_provenance.items():
                self.assertEqual(result[field], hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertTrue((destination / "degradation" / "kernel-gt.pt").exists())
            noisy_files = sorted((destination / "step1-observation" / "noisy").glob("*.png"))
            self.assertGreater(len(noisy_files), 0)
            first_hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in noisy_files}

            with self.assertRaises(FileExistsError):
                build_benchmark(records, source_digest, destination, source_root=root)
            self.assertEqual(
                first_hashes,
                {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in noisy_files},
            )

            absent = Path(temporary) / "must-not-exist"
            with self.assertRaises(ValueError):
                build_benchmark(records, "0" * 64, absent, source_root=root)
            self.assertFalse(absent.exists())


if __name__ == "__main__":
    unittest.main()
