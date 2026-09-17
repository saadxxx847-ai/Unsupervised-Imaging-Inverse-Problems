import hashlib
import tempfile
import unittest
from pathlib import Path

import dill
from omegaconf import OmegaConf
import torch
from torch.utils.data import DataLoader, TensorDataset

from ddm4ip.data.base import Datasplit
from ddm4ip.trainers.base import BaseTrainer


RUNTIME_TEMP = Path(r"D:\DDM4IP-runtime\temp")


class _LossFixture:
    has_val_loss = False

    def __init__(self):
        self.completed_steps = 0

    def __call__(self, trainer, batch):
        self.completed_steps += 1
        return {}

    def is_full_step_complete(self):
        return True

    def state_dict(self):
        return {"completed_steps": self.completed_steps}

    def load_state_dict(self, state):
        self.completed_steps = state["completed_steps"]


class _TerminalCheckpointTrainer(BaseTrainer):
    def init_datasets(self, cfg):
        return {Datasplit.TRAIN: TensorDataset(torch.arange(8, dtype=torch.float32).reshape(4, 2))}

    def init_dataloaders(self, cfg, dsets):
        return {
            Datasplit.TRAIN: DataLoader(
                dsets[Datasplit.TRAIN],
                batch_size=cfg.training.batch_size,
                shuffle=False,
                num_workers=0,
            )
        }

    def init_models(self, cfg, dsets, device):
        model = torch.nn.Linear(2, 2)
        with torch.no_grad():
            model.weight.fill_(3.0)
            model.bias.fill_(5.0)
        return {"flow_nn": model}

    def init_loss(self, cfg, models):
        return _LossFixture()

    def validate_batch(self, val_batch):
        raise AssertionError("This terminal-checkpoint fixture does not validate.")

    def make_plots(self, cfg, dsets, dloaders, models, tb_writer, global_step):
        raise AssertionError("This terminal-checkpoint fixture does not plot.")


class BaseTrainerFinalCheckpointTests(unittest.TestCase):
    def make_cfg(self, root):
        return OmegaConf.create(
            {
                "exp_name": "terminal-checkpoint",
                "training": {
                    "log_dir": str(root),
                    "seed": 123,
                    "batch_size": 2,
                    "report_every_steps": 8,
                    "plot_every_steps": 8,
                    "save_every_steps": 8,
                    "max_steps": 8,
                    "save_first_step": False,
                    "num_workers": 0,
                    "max_val_batches": 0,
                },
                "loss": {"n_accum_steps": 1},
            }
        )

    def test_train_persists_terminal_checkpoint_when_no_periodic_checkpoint_is_reachable(self):
        root = Path(tempfile.mkdtemp(prefix="base-final-checkpoint-", dir=RUNTIME_TEMP))
        print(f"Retained terminal-checkpoint fixture root: {root}")
        cfg = self.make_cfg(root)

        trainer = _TerminalCheckpointTrainer()
        trainer.train(cfg)

        checkpoint_dir = root / cfg.exp_name / "checkpoints"
        state_path = checkpoint_dir / "training-state-8.pt"
        snapshot_path = checkpoint_dir / "network-snapshot-8.pkl"
        self.assertEqual(trainer.global_step, 8)
        self.assertTrue(state_path.is_file())
        self.assertTrue(snapshot_path.is_file())

        state = torch.load(state_path, weights_only=False, map_location="cpu")
        with snapshot_path.open("rb") as handle:
            snapshot = dill.load(handle)
        self.assertEqual(state["global_step"], 8)
        self.assertEqual(state["loss_optim"]["completed_steps"], 4)
        self.assertEqual(snapshot["global_step"], 9)
        self.assertEqual(snapshot["run_dir"], str(root / cfg.exp_name))
        self.assertEqual(len(hashlib.sha256(state_path.read_bytes()).hexdigest()), 64)
        self.assertEqual(len(hashlib.sha256(snapshot_path.read_bytes()).hexdigest()), 64)

        restored_cfg = OmegaConf.create(OmegaConf.to_container(cfg, resolve=True))
        restored_cfg.training.log_dir = str(root / "restore")
        restored_cfg.training.checkpoint = str(state_path)
        restored = _TerminalCheckpointTrainer()
        restored.cfg = restored_cfg
        restored.init_train_info(restored_cfg)
        restored.models = restored.init_models(restored_cfg, {}, restored.device)
        restored.loss_optim = restored.init_loss(restored_cfg, restored.models)
        self.assertEqual(restored.maybe_load_checkpoint(), 8)
        self.assertEqual(restored.loss_optim.completed_steps, 4)


if __name__ == "__main__":
    unittest.main()
