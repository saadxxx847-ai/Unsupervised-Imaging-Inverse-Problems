import tempfile
import unittest
from pathlib import Path

import torch

from ddm4ip.degradations.degradation import (
    init_perturbation,
    load_filter_from_file,
)


class FileBlurTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="file-blur-test-"))

    def test_pt_kernel_loads_without_rotation_or_renormalization(self):
        kernel = torch.arange(1, 17, dtype=torch.float32).reshape(4, 4)
        kernel /= kernel.sum()
        path = self.root / "kernel.pt"
        torch.save(kernel, path, _use_new_zipfile_serialization=False)

        loaded = load_filter_from_file(path, kernel_size=None)

        self.assertEqual(tuple(loaded.shape), (1, 1, 4, 4))
        torch.testing.assert_close(loaded[0, 0], kernel, rtol=0, atol=0)

    def test_file_blur_rejects_invalid_kernels(self):
        for kernel in (
            torch.tensor([[float("nan")]]),
            torch.tensor([[-1.0]]),
            torch.ones(2, 2),
        ):
            path = self.root / "bad.pt"
            torch.save(kernel, path, _use_new_zipfile_serialization=False)
            with self.subTest(kernel=kernel):
                with self.assertRaises(ValueError):
                    load_filter_from_file(path, kernel_size=None)

    def test_file_blur_instantiates_project_physics(self):
        kernel = torch.zeros(3, 3, dtype=torch.float32)
        kernel[1, 1] = 1.0
        path = self.root / "kernel.pt"
        torch.save(kernel, path, _use_new_zipfile_serialization=False)

        physics = init_perturbation(
            {
                "kind": "file_blur",
                "kernel_path": str(path),
                "padding": "replicate",
            },
            {"kind": "none"},
        )

        self.assertEqual(tuple(physics.filter.shape), (1, 1, 3, 3))
        image = torch.rand(1, 3, 8, 8)
        torch.testing.assert_close(physics(image), image, rtol=0, atol=0)


if __name__ == "__main__":
    unittest.main()
