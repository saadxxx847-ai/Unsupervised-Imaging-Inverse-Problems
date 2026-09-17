import unittest
from types import SimpleNamespace

import torch
from deepinv.physics import Blur

from ddm4ip.losses.deepinv_loss import DeepInvLoss


@unittest.skipUnless(torch.cuda.is_available(), "CUDA is required for this regression")
class PhysicsDeviceMismatchTests(unittest.TestCase):
    def test_reprojection_uses_cuda_physics_buffer_for_cpu_outputs(self):
        kernel = torch.ones((1, 1, 3, 3), dtype=torch.float32) / 9.0
        physics = Blur(filter=kernel, padding="replicate", noise_model=None).to("cuda")
        self.assertEqual(list(physics.parameters()), [])
        self.assertEqual(physics.filter.device.type, "cuda")

        reconstructed = torch.rand((1, 3, 8, 8), dtype=torch.float32)
        observation = torch.rand((1, 3, 8, 8), dtype=torch.float32)
        metrics = DeepInvLoss.reprojection_metrics(
            SimpleNamespace(physics=physics), reconstructed, observation
        )

        self.assertEqual(metrics["reprojection_l1"].device, physics.filter.device)
        self.assertEqual(metrics["reprojection_l2"].device, physics.filter.device)
        self.assertTrue(torch.isfinite(metrics["reprojection_l1"]))
        self.assertTrue(torch.isfinite(metrics["reprojection_l2"]))


if __name__ == "__main__":
    unittest.main()
