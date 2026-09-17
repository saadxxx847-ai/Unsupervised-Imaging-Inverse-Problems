import tempfile
import unittest
from pathlib import Path

import torch

from ddm4ip.data.base import Batch
from ddm4ip.losses.deepinv_loss import DeepInvLoss
from ddm4ip.trainers.deepinv_denoiser import DeepinvDenoiserTrainer


def _noisy_batch(size: int = 16) -> Batch:
    return Batch(
        clean=None,
        clean_label=None,
        corrupt=torch.zeros((1, 3, size, size)),
        corrupt_label=None,
        noise_level=None,
        clean_conditioning=None,
        corrupt_conditioning=None,
    )


class _OutputOnlyLoss:
    def val_loss_with_output(self, trainer, batch: Batch):
        assert batch.corrupt is not None
        return {"val_loss/reprojection_l1": torch.tensor(0.0)}, batch.corrupt + 0.25, torch.ones((1, 1, 3, 3))


class _IdentityPhysics(torch.nn.Module):
    def A(self, x: torch.Tensor) -> torch.Tensor:
        return x


class DeepInvNoReferenceTests(unittest.TestCase):
    def test_noisy_only_validation_saves_prediction_and_kernel(self) -> None:
        """Would fail if evaluation still asserts that a noisy-only batch has a clean target."""
        with tempfile.TemporaryDirectory() as temporary:
            trainer = object.__new__(DeepinvDenoiserTrainer)
            trainer.loss_optim = _OutputOnlyLoss()
            trainer.save_eval_to_file = True
            trainer.save_pred_only = True
            trainer.eval_dir = temporary
            trainer.global_step = 0

            metrics = trainer.validate_batch(_noisy_batch())

            self.assertIn("val_loss/reprojection_l1", metrics)
            self.assertTrue((Path(temporary) / "img_00000.png").is_file())
            self.assertTrue((Path(temporary) / "kernel_00000.pt").is_file())

    def test_no_reference_validation_reports_reprojection_residuals(self) -> None:
        """Would fail if validation omits observed-image residuals whenever clean is unavailable."""
        loss = object.__new__(DeepInvLoss)
        loss.physics = _IdentityPhysics()
        loss.run_model = lambda batch: (
            torch.ones((1, 3, 4, 4)),
            torch.ones((1, 1, 3, 3)),
        )

        metrics, _, _ = loss.val_loss_with_output(None, _noisy_batch(size=4))

        self.assertEqual(metrics["val_loss/reprojection_l1"].item(), 1.0)
        self.assertEqual(metrics["val_loss/reprojection_l2"].item(), 1.0)
        self.assertNotIn("val_loss/psnr", metrics)
        self.assertNotIn("val_loss/ssim", metrics)
        self.assertNotIn("val_loss/lpips", metrics)


if __name__ == "__main__":
    unittest.main()
