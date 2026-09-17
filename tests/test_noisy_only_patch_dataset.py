import unittest
from unittest.mock import patch

from omegaconf import OmegaConf
import torch

from ddm4ip.data.base import Datasplit
from ddm4ip.data.patch_dataset import PatchDataset


class _NoReadImageDataset:
    def __len__(self) -> int:
        return 1

    def __getitem__(self, index: int):
        raise AssertionError("noisy-only dataset must not read the clean source")


class _OneNoisyImageDataset:
    def __len__(self) -> int:
        return 1

    def __getitem__(self, index: int):
        return torch.full((3, 16, 16), 0.5), None


class NoisyOnlyPatchDatasetTests(unittest.TestCase):
    def test_noisy_only_dataset_never_reads_clean_source(self) -> None:
        """Would fail if PatchDataset probes or returns a clean image for noisy-only evaluation."""
        config = OmegaConf.create({
            "patch_size": 16,
            "x_flip": False,
            "full_test": False,
            "space_conditioning": False,
            "random_space_conditioning": False,
            "inflate_patches": 0,
            "cuda": False,
            "need_clean": False,
            "need_noisy": True,
            "noisy_path": "noisy-source",
        })
        def guarded_dataset(path, **kwargs):
            if path == "clean-source":
                raise AssertionError("noisy-only dataset must not construct the clean source")
            return _OneNoisyImageDataset()

        with patch(
            "ddm4ip.data.patch_dataset.BaseImageFolderDataset",
            side_effect=guarded_dataset,
        ):
            dataset = PatchDataset(
                path="clean-source",
                degradation=None,
                split=Datasplit.TEST,
                dset_cfg=config,
                shuffle_clean=False,
            )

        batch = dataset[0]
        self.assertIsNone(batch.clean)
        self.assertIsNotNone(batch.corrupt)
        self.assertEqual(dataset.clean_img_size, dataset.corrupt_img_size)
        self.assertEqual(
            dataset.clean_conditioning_channels,
            dataset.corrupt_conditioning_channels,
        )


if __name__ == "__main__":
    unittest.main()
