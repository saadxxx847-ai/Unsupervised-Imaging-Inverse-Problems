import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import torch

from ddm4ip.data.base import Batch
from ddm4ip.trainers.deepinv_denoiser import DeepinvDenoiserTrainer
from ddm4ip.utils.benchmark_metrics import BenchmarkMetricWriter, compute_image_metrics
from ddm4ip.utils.torch_utils import read_img_pt


class _MeanAbsoluteLPIPS:
    def __call__(self, reference, estimate):
        return (reference - estimate).abs().mean()


class _QuantitativeLoss:
    output_geometry = {"filter_groups": [{"tile_range": [0, 1], "filter_range": [0, 1], "association": "shared"}]}

    def val_loss_with_output(self, trainer, batch):
        del trainer
        return {
            "val_loss/reprojection_l1": torch.tensor(0.1),
            "val_loss/reprojection_l2": torch.tensor(0.01),
        }, torch.full_like(batch.clean, 0.4), torch.ones((1, 1, 3, 3))

    def compute_img_metrics(self, prediction, clean):
        return compute_image_metrics(prediction, clean, _MeanAbsoluteLPIPS())


def _paired_batch(source_id="source-1") -> Batch:
    clean = torch.full((1, 3, 8, 8), 0.5)
    noisy = torch.full((1, 3, 8, 8), 0.6)
    return Batch(
        clean=clean,
        clean_label=None,
        corrupt=noisy,
        corrupt_label=None,
        noise_level=torch.tensor(0.02),
        clean_conditioning=None,
        corrupt_conditioning=None,
        meta={
            "source_id": [source_id],
            "source_relpath": [f"train/clean/{source_id}.jpg"],
            "source_sha256": ["c" * 64],
            "clean_path": [f"clean/{source_id}.png"],
            "noisy_path": [f"noisy/{source_id}.png"],
            "clean_sha256": ["a" * 64],
            "noisy_sha256": ["b" * 64],
        },
    )


class SyntheticTrainerTests(unittest.TestCase):
    def _trainer(self, root: Path, variant="oracle", seed=None, expected_count=1):
        kernel_gt = root / "kernel-gt.pt"
        kernel_gt.write_bytes(b"true-kernel")
        trainer = object.__new__(DeepinvDenoiserTrainer)
        trainer.loss_optim = _QuantitativeLoss()
        trainer.save_eval_to_file = True
        trainer.save_pred_only = False
        trainer.eval_dir = str(root / "plots")
        trainer.global_step = 0
        trainer.quantitative = True
        trainer.metric_writer = BenchmarkMetricWriter(
            root / "plots",
            experiment_id="exp",
            variant=variant,
            step2_seed=seed,
            solver_config_sha256="e" * 64,
            kernel_gt_path=kernel_gt,
            expected_count=expected_count,
            pairs_manifest_sha256="a" * 64,
            benchmark_summary_sha256="b" * 64,
        )
        trainer.expected_pairs_manifest_sha256 = "a" * 64
        trainer.benchmark_summary_sha256 = "b" * 64
        return trainer

    def test_quantitative_validation_writes_manifest_metrics_and_kernel(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            trainer = self._trainer(root)
            metrics = trainer.validate_batch(_paired_batch())
            plots = root / "plots"

            self.assertIn("val_loss/reprojection_l1", metrics)
            self.assertTrue((plots / "prediction-source-1.png").is_file())
            self.assertTrue((plots / "kernel-source-1.pt").is_file())
            manifest = json.loads((plots / "manifest.jsonl").read_text().splitlines()[0])
            metric_row = json.loads((plots / "metrics.jsonl").read_text().splitlines()[0])
            self.assertEqual(manifest["source_id"], "source-1")
            self.assertEqual(metric_row["source_id"], "source-1")
            self.assertEqual(metric_row["step2_seed"], None)
            self.assertEqual(metric_row["solver_config_sha256"], "e" * 64)
            self.assertIn("prediction_sha256", manifest)
            self.assertIn("kernel_sha256", manifest)
            self.assertEqual(metric_row["pairs_manifest_sha256"], "a" * 64)
            expected = compute_image_metrics(
                read_img_pt(plots / "prediction-source-1.png"),
                _paired_batch().clean[0],
                _MeanAbsoluteLPIPS(),
            )
            self.assertAlmostEqual(metric_row["restored_metrics"]["psnr"], expected["psnr"], places=6)
            self.assertTrue((plots / "summary.json").is_file())

    def test_sixteen_image_writer_finalizes_only_on_the_sixteenth_image(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            trainer = self._trainer(root, expected_count=16)
            for index in range(15):
                trainer.validate_batch(_paired_batch(f"source-{index}"))
                self.assertFalse((root / "plots" / "summary.json").exists())
            trainer.validate_batch(_paired_batch("source-15"))
            self.assertTrue((root / "plots" / "summary.json").exists())

    def test_learned_seed_is_recorded_and_second_write_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            trainer = self._trainer(root, variant="learned", seed=3)
            trainer.validate_batch(_paired_batch())
            with self.assertRaises(FileExistsError):
                trainer.validate_batch(_paired_batch())


if __name__ == "__main__":
    unittest.main()
