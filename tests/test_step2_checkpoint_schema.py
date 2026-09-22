import dill
import pickle
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from omegaconf import OmegaConf

import torch

import ddm4ip.trainers.deepinv_denoiser as deepinv_module
from ddm4ip.data.base import Datasplit
from ddm4ip.trainers.deepinv_denoiser import DeepinvDenoiserTrainer
from ddm4ip.trainers.diffinstruct_learn_op import DiffinstructOpTrainer
from scripts import bdd100k_synthetic_runner as runner


RUNTIME_TEMP = Path("D:/DDM4IP-runtime/temp")
PICKLE_PATHS = []


class _LossFixture:
    def state_dict(self):
        return {}


class _PicklePathProbe:
    def __setstate__(self, state):
        PICKLE_PATHS.append(list(sys.path))
        self.__dict__.update(state)


def _linear(fill: float) -> torch.nn.Linear:
    model = torch.nn.Linear(2, 2)
    with torch.no_grad():
        model.weight.fill_(fill)
        model.bias.fill_(fill + 1)
    return model


def _step2_trainer(root: Path) -> DiffinstructOpTrainer:
    trainer = DiffinstructOpTrainer()
    checkpoint_dir = root / "checkpoints"
    checkpoint_dir.mkdir(parents=True)
    trainer.ckpt_dir = str(checkpoint_dir)
    trainer.run_dir = str(root)
    trainer.global_step = 12
    trainer.models = {
        "aux_flow_nn": _linear(2.0),
        "prtr_flow_nn": _linear(1.0),
        "kernel_nn": _linear(3.0),
    }
    trainer.loss_optim = _LossFixture()
    return trainer


def _write_pair(root: Path, keys: tuple[str, ...]) -> tuple[Path, Path]:
    checkpoints = root / "checkpoints"
    checkpoints.mkdir(parents=True)
    pt = checkpoints / "training-state-12.pt"
    pkl = checkpoints / "network-snapshot-12.pkl"
    state = {"global_step": 12}
    snapshot = {"global_step": 13}
    for key in keys:
        state[key] = {"state_dict": {"weight": torch.ones(1)}
        }
        snapshot[key] = {"weight": torch.ones(1)}
    torch.save(state, pt)
    with pkl.open("wb") as handle:
        pickle.dump(snapshot, handle)
    return pt, pkl


class Step2CheckpointSchemaTests(unittest.TestCase):
    def test_step2_checkpoint_contains_distinct_canonical_flow_view_and_round_trips(self):
        with tempfile.TemporaryDirectory(prefix="step2-schema-", dir=RUNTIME_TEMP) as temporary:
            root = Path(temporary)
            trainer = _step2_trainer(root)
            trainer.maybe_save_checkpoint(force=True)

            state_path = root / "checkpoints" / "training-state-12.pt"
            snapshot_path = root / "checkpoints" / "network-snapshot-12.pkl"
            state = torch.load(state_path, map_location="cpu", weights_only=False)
            with snapshot_path.open("rb") as handle:
                snapshot = dill.load(handle)

            for payload in (state, snapshot):
                self.assertIn("kernel_nn", payload)
                self.assertIn("flow_nn", payload)
                self.assertIn("aux_flow_nn", payload)
                self.assertIn("prtr_flow_nn", payload)

            self.assertIsNot(snapshot["flow_nn"], snapshot["aux_flow_nn"])
            for name, value in state["aux_flow_nn"]["state_dict"].items():
                self.assertTrue(torch.equal(value, state["flow_nn"]["state_dict"][name]))
            for name, value in snapshot["aux_flow_nn"].state_dict().items():
                self.assertTrue(torch.equal(value, snapshot["flow_nn"].state_dict()[name]))

    def test_step2_postflight_requires_exact_flow_and_kernel_keys(self):
        with tempfile.TemporaryDirectory(prefix="step2-runner-schema-", dir=RUNTIME_TEMP) as temporary:
            root = Path(temporary)
            missing_flow_root = root / "missing-flow"
            _write_pair(missing_flow_root, ("kernel_nn",))
            spec = {"stage": "step2", "overrides": {"training.max_steps": 12}}
            with self.assertRaisesRegex(ValueError, "flow_nn"):
                runner.postflight_stage_artifacts(spec, missing_flow_root)

            valid_root = root / "valid"
            _write_pair(valid_root, ("kernel_nn", "flow_nn"))
            runner.postflight_stage_artifacts(spec, valid_root)
            self.assertTrue((valid_root / "artifacts.json").is_file())

    def test_step3_loader_selects_kernel_from_extended_snapshot_and_restores_sys_path(self):
        with tempfile.TemporaryDirectory(prefix="step3-loader-", dir=RUNTIME_TEMP) as temporary:
            root = Path(temporary)
            snapshot_path = root / "network-snapshot-12.pkl"
            kernel = _linear(3.0)
            payload = {
                "global_step": 13,
                "flow_nn": _linear(7.0),
                "aux_flow_nn": _linear(2.0),
                "prtr_flow_nn": _linear(1.0),
                "kernel_nn": kernel,
                "probe": _PicklePathProbe(),
            }
            payload["probe"].marker = True
            with snapshot_path.open("wb") as handle:
                pickle.dump(payload, handle)

            project_root = str(Path(deepinv_module.__file__).resolve().parents[2])
            original_sys_path = list(sys.path)
            sys.path = [entry for entry in sys.path if entry != project_root]
            PICKLE_PATHS.clear()
            try:
                trainer = DeepinvDenoiserTrainer()
                trainer.init_wiener = lambda balance: ("wiener", balance)
                dataset = SimpleNamespace(
                    clean_img_size=(3, 8, 8),
                    clean_conditioning_channels=0,
                    label_dim=0,
                    noise_level=0.02,
                )
                cfg = OmegaConf.create({
                    "models": {
                        "kernel": {"path": str(snapshot_path)},
                        "deepinv_solver": {"method": "wiener", "balance": 0.02},
                    }
                })
                models = trainer.init_models(
                    cfg, {Datasplit.TEST: dataset}, torch.device("cpu")
                )
            finally:
                sys.path = original_sys_path

            self.assertTrue(PICKLE_PATHS)
            self.assertIn(project_root, PICKLE_PATHS[-1])
            self.assertEqual(sys.path, original_sys_path)
            self.assertAlmostEqual(models["kernel_nn"].weight.flatten()[0].item(), 3.0)


if __name__ == "__main__":
    unittest.main()
