import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import torch
from omegaconf import OmegaConf
from PIL import Image

from ddm4ip.data.base import Batch, Datasplit, init_dataset


PAIR_FIELDS = (
    "schema_version", "role", "source_id", "source_relpath", "source_sha256",
    "clean_path", "clean_sha256", "noisy_path", "noisy_sha256", "noise_seed",
    "source_size", "crop_box", "output_size", "channels", "kernel_tensor_sha256",
)


class ManifestPairedDatasetTests(unittest.TestCase):
    def _write_image(self, path: Path, value: int) -> str:
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (256, 256), (value, value, value)).save(path, format="PNG")
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def _make_pair(self, root: Path, source_id="source-1", role="test_paired"):
        clean = root / "clean" / f"{source_id}.png"
        noisy = root / "noisy" / f"{source_id}.png"
        clean_sha = self._write_image(clean, 10)
        noisy_sha = self._write_image(noisy, 20)
        row = {
            "schema_version": 1,
            "role": role,
            "source_id": source_id,
            "source_relpath": f"train/clean/{source_id}.jpg",
            "source_sha256": "0" * 64,
            "clean_path": f"clean/{source_id}.png",
            "clean_sha256": clean_sha,
            "noisy_path": f"noisy/{source_id}.png",
            "noisy_sha256": noisy_sha,
            "noise_seed": 101,
            "source_size": 123,
            "crop_box": [0, 280, 720, 1000],
            "output_size": [256, 256],
            "channels": 3,
            "kernel_tensor_sha256": "1" * 64,
        }
        return row

    def _dataset(self, root: Path, row: dict):
        pairs = root / "pairs.jsonl"
        pairs.write_text(json.dumps(row) + "\n", encoding="utf-8")
        cfg = OmegaConf.create({
            "dataset": {
                "test": {
                    "name": "manifest_paired",
                    "path": str(pairs),
                    "degradation": {"kind": "none"},
                    "noise": {"kind": "none"},
                }
            }
        })
        return init_dataset(cfg, Datasplit.TEST, is_paired=True)

    def test_manifest_rows_return_explicit_pair_and_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            row = self._make_pair(root)
            dataset = self._dataset(root, row)
            batch = Batch.collate_fn([dataset[0]])
            moved = batch.to("cpu")[0]

            self.assertEqual(moved.meta["source_id"], "source-1")
            self.assertEqual(moved.meta["source_sha256"], row["source_sha256"])
            self.assertEqual(moved.meta["clean_sha256"], row["clean_sha256"])
            self.assertEqual(moved.meta["noisy_sha256"], row["noisy_sha256"])
            self.assertEqual(moved.meta["noise_seed"].item(), 101)
            self.assertEqual(tuple(moved.clean.shape), (3, 256, 256))
            self.assertEqual(tuple(moved.corrupt.shape), (3, 256, 256))
            self.assertIsNone(moved.kernel)

    def test_manifest_rejects_invalid_rows_before_sample_access(self):
        cases = ("missing", "absolute", "duplicate", "wrong-hash", "wrong-role", "extra-key", "wrong-size", "same-path", "wrong-stem")
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                row = self._make_pair(root)
                if case == "missing":
                    row["noisy_path"] = "noisy/missing.png"
                elif case == "absolute":
                    row["clean_path"] = str((root / "clean" / "source-1.png").resolve())
                elif case == "duplicate":
                    row["source_id"] = "other"
                    row["clean_path"] = "clean/source-1.png"
                elif case == "wrong-hash":
                    row["clean_sha256"] = "0" * 64
                elif case == "wrong-role":
                    row["role"] = "step1_observation"
                elif case == "extra-key":
                    row["unexpected"] = True
                elif case == "wrong-size":
                    (root / "clean" / "source-1.png").unlink()
                    self._write_image(root / "clean" / "source-1.png", 10)
                    row["output_size"] = [128, 128]
                elif case == "same-path":
                    row["noisy_path"] = row["clean_path"]
                elif case == "wrong-stem":
                    row["clean_path"] = "clean/other.png"
                with self.assertRaises((ValueError, FileNotFoundError, OSError)):
                    self._dataset(root, row)


if __name__ == "__main__":
    unittest.main()
