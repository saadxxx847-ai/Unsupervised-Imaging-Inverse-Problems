import hashlib
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import torch

from ddm4ip.utils.benchmark_metrics import (
    BenchmarkMetricWriter,
    aggregate_summaries,
    compute_image_metrics,
    compute_kernel_metrics,
)
from scripts.aggregate_bdd100k_synthetic_results import main as aggregate_cli_main


class _MeanAbsoluteLPIPS:
    def __call__(self, reference, estimate):
        return (reference - estimate).abs().mean()


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class BenchmarkMetricsTests(unittest.TestCase):
    def test_image_metrics_are_scalar_and_have_expected_direction(self):
        reference = torch.full((3, 16, 16), 0.5)
        identical = compute_image_metrics(reference, reference, _MeanAbsoluteLPIPS())
        perturbed = compute_image_metrics(reference, reference + 0.1, _MeanAbsoluteLPIPS())

        self.assertGreater(identical["psnr"], 150)
        self.assertEqual(identical["ssim"], 1.0)
        self.assertEqual(identical["lpips"], 0.0)
        self.assertLess(perturbed["psnr"], identical["psnr"])
        self.assertLess(perturbed["ssim"], identical["ssim"])
        self.assertGreater(perturbed["lpips"], identical["lpips"])
        with self.assertRaises(ValueError):
            compute_image_metrics(reference.repeat(2, 1, 1, 1), reference.repeat(2, 1, 1, 1), _MeanAbsoluteLPIPS())

    def test_kernel_metrics_use_existing_center_padding_alignment(self):
        truth = torch.zeros(1, 1, 32, 32)
        truth[:, :, 12:20, 13:19] = 1.0
        truth /= truth.sum()
        estimate = truth[:, :, 2:-2, 2:-2].clone()

        aligned = compute_kernel_metrics(estimate, truth)
        shifted = compute_kernel_metrics(torch.roll(estimate, shifts=1, dims=-1), truth)

        self.assertTrue(math.isfinite(aligned["kernel_psnr"]))
        self.assertGreater(aligned["kernel_ncc"], 0.99)
        self.assertLess(shifted["kernel_ncc"], aligned["kernel_ncc"])

    def _make_writer(self, root: Path, variant: str, seed: int | None, expected: int):
        kernel_gt = root / "kernel-gt.pt"
        kernel_gt.write_bytes(b"kernel-gt")
        return BenchmarkMetricWriter(
            root / (variant if seed is None else f"{variant}-{seed}"),
            experiment_id="exp",
            variant=variant,
            step2_seed=seed,
            solver_config_sha256="e" * 64,
            kernel_gt_path=kernel_gt,
            expected_count=expected,
            pairs_manifest_sha256="a" * 64,
            benchmark_summary_sha256="b" * 64,
        )

    def _append_row(self, writer, output_dir: Path, source_id: str, value: float):
        prediction = output_dir / f"prediction-{source_id}.png"
        kernel = output_dir / f"kernel-{source_id}.pt"
        prediction.write_bytes(f"png-{source_id}".encode())
        kernel.write_bytes(f"kernel-{source_id}".encode())
        source_sha = _digest(source_id)
        row = writer.prepare_record(
            {
                "source_id": source_id,
                "source_relpath": f"train/clean/{source_id}.jpg",
                "source_sha256": source_sha,
                "clean_sha256": source_sha,
                "noisy_sha256": source_sha,
                "clean_path": f"clean/{source_id}.png",
                "noisy_path": f"noisy/{source_id}.png",
                "prediction_sha256": hashlib.sha256(prediction.read_bytes()).hexdigest(),
                "kernel_sha256": hashlib.sha256(kernel.read_bytes()).hexdigest(),
            },
            torch.zeros(3, 4, 4),
            torch.ones(1, 1, 3, 3),
            prediction.name,
            kernel.name,
            {"tiles": [[0, 0, 4, 4]]},
            input_metrics={"psnr": value, "ssim": 0.5, "lpips": 0.8},
            restored_metrics={"psnr": value + 1, "ssim": 0.6, "lpips": 0.7},
        )
        writer.append(row)
        return row

    def test_writer_finalizes_only_on_the_sixteenth_record_and_uses_one_schema(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            writer = self._make_writer(root, "oracle", None, expected=16)
            rows = []
            for index in range(15):
                rows.append(self._append_row(writer, writer.output_dir, f"source-{index}", 10.0 + index))
                (writer.output_dir / "manifest.jsonl").write_text("\n".join(rows) + "\n", encoding="utf-8")
                self.assertIsNone(writer.finalize_if_complete())
                self.assertFalse(writer.summary_path.exists())

            rows.append(self._append_row(writer, writer.output_dir, "source-15", 25.0))
            (writer.output_dir / "manifest.jsonl").write_text("\n".join(rows) + "\n", encoding="utf-8")
            summary = writer.finalize_if_complete()
            self.assertEqual(summary["records"], 16)
            self.assertEqual(summary["failures"], 0)
            self.assertEqual(summary["pairs_manifest_sha256"], "a" * 64)
            self.assertEqual(summary["benchmark_summary_sha256"], "b" * 64)
            self.assertEqual(set(summary["statistics"]), {
                "input_psnr", "input_ssim", "input_lpips",
                "restored_psnr", "restored_ssim", "restored_lpips",
            })
            self.assertEqual(summary["mean"]["restored_psnr"], 18.5)
            with self.assertRaises(ValueError):
                self._append_row(writer, writer.output_dir, "source-16", 30.0)

    def test_writer_requires_prediction_kernel_and_provenance_hashes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            writer = self._make_writer(root, "oracle", None, expected=1)
            with self.assertRaises(ValueError):
                writer.prepare_record(
                    {"source_id": "a", "source_sha256": "a" * 64},
                    torch.zeros(3, 4, 4), torch.ones(1, 1, 3, 3),
                    "prediction-a.png", "kernel-a.pt", {},
                    {"psnr": 10.0}, {"psnr": 11.0},
                )

    def _write_summary(self, root: Path, variant: str, seed: int | None):
        writer = self._make_writer(root, variant, seed, expected=3)
        rows = [
            self._append_row(writer, writer.output_dir, source_id, value)
            for source_id, value in (("a", 10.0), ("b", 11.0), ("c", 12.0))
        ]
        (writer.output_dir / "manifest.jsonl").write_text("\n".join(rows) + "\n", encoding="utf-8")
        return writer.finalize_if_complete()

    def test_aggregator_rechecks_jsonl_and_requires_five_kernel_results(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_summary(root, "oracle", None)
            for seed in range(5):
                self._write_summary(root, "learned", seed)
            summary_paths = [root / "oracle" / "summary.json"] + [
                root / f"learned-{seed}" / "summary.json" for seed in range(5)
            ]
            kernel_paths = []
            for seed in range(5):
                path = root / f"kernel-{seed}.json"
                path.write_text(json.dumps({
                    "step2_seed": seed,
                    "kernel_psnr": 20.0 + seed,
                    "kernel_ncc": 0.8 + seed * 0.01,
                    "kernel_gt_sha256": hashlib.sha256(b"kernel-gt").hexdigest(),
                }), encoding="utf-8")
                kernel_paths.append(path)
            output = root / "final-summary.json"
            result = aggregate_summaries(
                summary_paths[0], summary_paths[1:], output, kernel_paths=kernel_paths
            )
            self.assertEqual(result["learned_seed_count"], 5)
            self.assertEqual(result["learned_across_seed"]["restored_psnr"]["mean"], 12.0)
            self.assertEqual(result["kernel_metrics"]["count"], 5)
            self.assertTrue(output.exists())
            with self.assertRaises(ValueError):
                aggregate_summaries(summary_paths[0], summary_paths[1:], root / "missing-kernel.json")

    def test_aggregator_cli_validates_jsonl_five_seeds_and_kernel_psnr_ncc(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_summary(root, "oracle", None)
            for seed in range(5):
                self._write_summary(root, "learned", seed)
            oracle = root / "oracle" / "summary.json"
            learned = [root / f"learned-{seed}" / "summary.json" for seed in range(5)]
            kernels = []
            kernel_hash = hashlib.sha256(b"kernel-gt").hexdigest()
            for seed in range(5):
                path = root / f"kernel-result-{seed}.json"
                path.write_text(json.dumps({
                    "step2_seed": seed,
                    "kernel_psnr": 20.0 + seed,
                    "kernel_ncc": 0.8 + seed * 0.01,
                    "kernel_gt_sha256": kernel_hash,
                }), encoding="utf-8")
                kernels.append(path)
            output = root / "cli-final-summary.json"
            argv = [
                "aggregate_bdd100k_synthetic_results.py",
                "--oracle-summary", str(oracle),
                *sum((["--learned-summary", str(path)] for path in learned), []),
                *sum((["--kernel-result", str(path)] for path in kernels), []),
                "--output", str(output),
            ]
            with mock.patch.object(sys, "argv", argv):
                self.assertEqual(aggregate_cli_main(), 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["learned_seed_count"], 5)
            self.assertEqual(payload["learned_across_seed"]["restored_psnr"]["mean"], 12.0)
            self.assertEqual(payload["learned_across_seed"]["restored_psnr"]["std"], 0.0)
            self.assertEqual(payload["kernel_metrics"]["count"], 5)
            self.assertEqual(payload["kernel_metrics"]["mean"]["kernel_psnr"], 22.0)
            self.assertAlmostEqual(payload["kernel_metrics"]["mean"]["kernel_ncc"], 0.82)


if __name__ == "__main__":
    unittest.main()
