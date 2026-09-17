import tempfile
import unittest
from pathlib import Path

from omegaconf import OmegaConf
from PIL import Image

from ddm4ip.data.base import Datasplit
from ddm4ip.data.patch_dataset import PatchDataset


class SyntheticDataBoundaryTests(unittest.TestCase):
    def _write_image(self, path: Path, value: int):
        path.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (32, 32), (value, value, value)).save(path / "sample.png")

    def test_step1_reads_only_noisy_and_step2_reads_only_clean(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            clean = root / "clean"
            noisy = root / "noisy"
            self._write_image(clean, 10)
            self._write_image(noisy, 20)
            step1_cfg = OmegaConf.create({
                "patch_size": 16, "x_flip": False, "full_test": False,
                "space_conditioning": False, "random_space_conditioning": False,
                "inflate_patches": 0, "cuda": False, "need_clean": False,
                "need_noisy": True, "noisy_path": str(noisy), "num_patches_per_image": 1,
            })
            step2_cfg = OmegaConf.create({
                "patch_size": 16, "x_flip": False, "full_test": False,
                "space_conditioning": False, "random_space_conditioning": False,
                "inflate_patches": 0, "cuda": False, "need_clean": True,
                "need_noisy": False, "noisy_path": str(root / "must-not-read"),
                "noise_level_override": 0.02, "num_patches_per_image": 1,
            })
            step1 = PatchDataset(
                root / "must-not-read", None, Datasplit.TRAIN, step1_cfg, shuffle_clean=False
            )
            self.assertIsNone(step1[0].clean)
            self.assertIsNotNone(step1[0].corrupt)

            step2 = PatchDataset(clean, None, Datasplit.TRAIN, step2_cfg, shuffle_clean=False)
            self.assertIsNotNone(step2[0].clean)
            self.assertIsNone(step2[0].corrupt)
            self.assertIsNone(step2[0].kernel)
            self.assertAlmostEqual(step2[0].noise_level.item(), 0.02)


if __name__ == "__main__":
    unittest.main()
