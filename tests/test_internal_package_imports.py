import unittest

import torch

from ddm4ip.data.base import Batch, Datasplit, init_dataloader
from ddm4ip.degradations.degradation import init_perturbation
from ddm4ip.networks.unets import UNet


class _TinyBatchDataset(torch.utils.data.Dataset):
    def __len__(self):
        return 2

    def __getitem__(self, index):
        image = torch.full((3, 16, 16), float(index))
        return Batch(
            clean=image,
            clean_label=None,
            corrupt=image.clone(),
            corrupt_label=None,
            noise_level=torch.tensor(0.0),
            clean_conditioning=None,
            corrupt_conditioning=None,
        )


class InternalPackageImportTests(unittest.TestCase):
    def test_motion_blur_constructs_and_applies_from_package_entry(self):
        try:
            degradation = init_perturbation(
                {
                    "kind": "motion_blur",
                    "kernel_size": 32,
                    "intensity": 0.5,
                    "rnd_seed": 1,
                },
                {"kind": "none"},
            )
        except ModuleNotFoundError as exc:
            self.fail(f"Internal package import failed: {exc}")

        image = torch.zeros((1, 3, 64, 64))
        result = degradation(image)
        self.assertEqual(result.shape, image.shape)
        self.assertTrue(torch.isfinite(result).all())
        self.assertEqual(degradation.__class__.__module__, "ddm4ip.degradations.blur")

    def test_dataloader_constructs_and_yields_a_real_batch(self):
        try:
            loader = init_dataloader(
                dset=_TinyBatchDataset(),
                split=Datasplit.TEST,
                batch_size=1,
                num_workers=0,
                seed=0,
                start_idx=0,
                is_infinite=False,
            )
        except ModuleNotFoundError as exc:
            self.fail(f"Internal package import failed: {exc}")

        batch = next(iter(loader))
        self.assertEqual(batch.batch_size, 1)
        self.assertEqual(tuple(batch.clean.shape), (1, 3, 16, 16))

    def test_unet_constructs_and_runs_registered_load_state_hook(self):
        model = UNet(
            img_resolution=16,
            img_channels=3,
            label_dim=0,
            model_channels=8,
            channel_mult=[1, 2],
            num_blocks=1,
            attn_resolutions=[],
            dropout=0.0,
            channels_per_head=4,
        )

        result = model.load_state_dict(model.state_dict())
        self.assertEqual(result.missing_keys, [])
        self.assertEqual(result.unexpected_keys, [])


if __name__ == "__main__":
    unittest.main()
