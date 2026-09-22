import tempfile
import unittest
from pathlib import Path

import dill
import torch

from ddm4ip.networks.blur_nets import DirectKernel
from ddm4ip.trainers.base import BaseTrainer


RUNTIME_TEMP = Path(r"D:\DDM4IP-runtime\temp")


class _LossFixture:
    def state_dict(self):
        return {}


class _CheckpointFixture(BaseTrainer):
    def init_datasets(self, cfg):
        raise NotImplementedError

    def init_dataloaders(self, cfg, dsets):
        raise NotImplementedError

    def init_models(self, cfg, dsets, device):
        raise NotImplementedError

    def init_loss(self, cfg, models):
        raise NotImplementedError

    def validate_batch(self, val_batch):
        raise NotImplementedError

    def make_plots(self, cfg, dsets, dloaders, models, tb_writer, global_step):
        raise NotImplementedError


class CheckpointNonLeafFilterTests(unittest.TestCase):
    def test_terminal_snapshot_handles_non_leaf_kernel_filter(self):
        root = Path(tempfile.mkdtemp(prefix="step2-nonleaf-filter-", dir=RUNTIME_TEMP))
        checkpoint_dir = root / "checkpoints"
        checkpoint_dir.mkdir()

        trainer = _CheckpointFixture()
        trainer.ckpt_dir = str(checkpoint_dir)
        trainer.run_dir = str(root)
        trainer.global_step = 2048
        model = DirectKernel(
            kernel_size=28,
            padding="replicate",
            factor=1,
            sum_to_one=True,
            learn_output_noise=False,
        )
        trainer.models = {"kernel_nn": model}
        trainer.loss_optim = _LossFixture()

        model(torch.rand(1, 3, 64, 64), noise_level=torch.tensor(0.02))
        self.assertFalse(model.degradation.filter.is_leaf)

        trainer.maybe_save_checkpoint(force=True)

        state_path = checkpoint_dir / "training-state-2048.pt"
        snapshot_path = checkpoint_dir / "network-snapshot-2048.pkl"
        self.assertTrue(state_path.is_file())
        self.assertTrue(snapshot_path.is_file())
        with snapshot_path.open("rb") as handle:
            snapshot = dill.load(handle)
        self.assertEqual(snapshot["global_step"], 2049)
        self.assertIn("kernel_nn", snapshot)


if __name__ == "__main__":
    unittest.main()
