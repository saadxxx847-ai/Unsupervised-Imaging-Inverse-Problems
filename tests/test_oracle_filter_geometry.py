import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("TORCH_HOME", r"D:\\DDM4IP-runtime\\torch-home")
os.environ.setdefault("XDG_CACHE_HOME", r"D:\\DDM4IP-runtime\\xdg-cache")

import torch

from ddm4ip.data.base import Datasplit
from ddm4ip.degradations.blur import get_motion_blur_kernel
from ddm4ip.degradations.degradation import init_noise, instantiate_single_kernel
from ddm4ip.losses.deepinv_loss import DeepInvLoss
from ddm4ip.trainers.deepinv_denoiser import DeepinvDenoiserTrainer


@unittest.skipUnless(torch.cuda.is_available(), "CUDA is required for the Oracle physics regression")
class OracleFilterGeometryTests(unittest.TestCase):
    def test_file_blur_oracle_filter_does_not_shrink_across_samples(self):
        with tempfile.TemporaryDirectory() as temporary:
            kernel_path = Path(temporary) / "kernel-gt.pt"
            kernel = get_motion_blur_kernel(32, 0.5, 1).cpu()
            torch.save(kernel, kernel_path, _use_new_zipfile_serialization=False)
            kernel_nn = instantiate_single_kernel(
                {
                    "kind": "file_blur",
                    "kernel_path": str(kernel_path),
                    "kernel_size": None,
                    "padding": "replicate",
                },
                init_noise({"kind": "gaussian", "std": 0.02}),
            ).to("cuda")

            trainer = object.__new__(DeepinvDenoiserTrainer)
            trainer.models = {"kernel_nn": kernel_nn}
            trainer.physics = None
            trainer.device = torch.device("cuda")
            trainer.dsets = {
                Datasplit.TEST: SimpleNamespace(noise_level=torch.tensor(0.02))
            }
            physics = trainer.get_physics({})

            loss = object.__new__(DeepInvLoss)
            loss.kernel_nn = kernel_nn
            loss.physics = physics
            loss.crop_filters = 1
            loss.deepinv_model = lambda y, physics, **kwargs: y
            observation = torch.rand((1, 3, 256, 256), device="cuda")

            for _ in range(15):
                _, filters = loss.run_on_data(observation, x=None, conditioning=None)
                self.assertEqual(tuple(filters.shape), (1, 1, 30, 30))

            prior = trainer.init_deep_prior("drunet", torch.device("cuda"))
            loss.deepinv_model = trainer.init_dpir(prior, 0.02)
            _, filters = loss.run_on_data(observation, x=None, conditioning=None)

            self.assertEqual(tuple(filters.shape), (1, 1, 30, 30))
            self.assertTrue(torch.isfinite(filters).all())
            self.assertTrue((filters >= 0).all())
            self.assertAlmostEqual(float(filters.sum().item()), 1.0, places=5)
            self.assertEqual(tuple(kernel_nn.filter.shape), (1, 1, 32, 32))
            self.assertIsNot(kernel_nn, physics)


if __name__ == "__main__":
    unittest.main()
