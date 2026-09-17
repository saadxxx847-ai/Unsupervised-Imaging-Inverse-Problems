import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from omegaconf import OmegaConf

from ddm4ip.trainers.deepinv_denoiser import DeepinvDenoiserTrainer


class _StubLoss:
    def __init__(self, *args, **kwargs):
        del args, kwargs


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class KernelHashCanonicalizationTests(unittest.TestCase):
    def test_uppercase_kernel_claim_matches_file_hash_and_stays_canonical(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pairs_path = root / "dev-reserve" / "pairs.jsonl"
            pairs_path.parent.mkdir()
            pairs_path.write_text("{}\n", encoding="utf-8")
            summary_path = root / "summary.json"
            summary_path.write_text("{}\n", encoding="utf-8")
            kernel_path = root / "degradation" / "kernel-gt.pt"
            kernel_path.parent.mkdir()
            kernel_path.write_bytes(b"kernel")

            kernel_hash = _sha256(kernel_path)
            cfg = OmegaConf.create(
                {
                    "exp_name": "hash-regression",
                    "paths": {"data": str(root)},
                    "dataset": {"test": {"path": str(pairs_path)}},
                    "models": {"deepinv_solver": {}},
                    "loss": {},
                    "evaluation": {
                        "quantitative": True,
                        "variant": "oracle",
                        "step2_seed": None,
                        "kernel_gt_path": str(kernel_path),
                        "kernel_gt_sha256": kernel_hash.upper(),
                        "expected_records": 1,
                        "pairs_manifest_sha256": _sha256(pairs_path).upper(),
                        "benchmark_summary_sha256": _sha256(summary_path).upper(),
                    },
                }
            )

            trainer = object.__new__(DeepinvDenoiserTrainer)
            trainer.eval_dir = str(root / "plots")
            trainer.get_physics = lambda _cfg: None

            with patch("ddm4ip.trainers.deepinv_denoiser.DeepInvLoss", _StubLoss):
                trainer.init_loss(
                    cfg,
                    {"deepinv_model": object(), "kernel_nn": object()},
                )

            self.assertEqual(trainer.metric_writer.kernel_gt_sha256, kernel_hash)


if __name__ == "__main__":
    unittest.main()
