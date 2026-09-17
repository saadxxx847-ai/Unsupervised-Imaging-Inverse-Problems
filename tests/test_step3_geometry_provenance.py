"""Training-free Step 3 geometry/provenance regressions; no pretrained downloads."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import torch
import torchvision
from hydra import compose, initialize_config_module
from hydra.core.global_hydra import GlobalHydra
from omegaconf import OmegaConf
import ddm4ip.main
from ddm4ip.data.base import Batch, Datasplit, init_dataset
from ddm4ip.data.patch_dataset import PatchDataset
from ddm4ip.losses.deepinv_loss import DeepInvLoss
from ddm4ip.trainers.deepinv_denoiser import DeepinvDenoiserTrainer


def make_batch(image, meta=None):
    return Batch(None, None, image, None, None, None, None, meta=meta or {})


def geometry_loss(shared=True):
    # Keep real run_model/run_on_iterable (including CUDA and batching).
    # Only replace the expensive solver/kernel query; no constructor downloads.
    loss = object.__new__(DeepInvLoss)
    loss.patch_size, loss.padding, loss.patch_batch_size = 128, 32, 7
    def identity(y, x=None, conditioning=None):
        return y.clone(), torch.ones((1 if shared else len(y), 1, 3, 3), device=y.device)
    loss.run_on_data = identity
    return loss


def config(experiment):
    GlobalHydra.instance().clear()
    with initialize_config_module(config_module="ddm4ip.configs", version_base=None):
        cfg = compose(config_name="main", overrides=[f"exp={experiment}", "paths=bdd100k_runtime"])
    OmegaConf.resolve(cfg)
    return cfg


class Step3GeometryTests(unittest.TestCase):
    @unittest.skipUnless(torch.cuda.is_available(), "CUDA is required by the existing loss execution path")
    def test_small_and_nondivisible_images_keep_every_pixel(self):
        # Catches negative patch origins, shifted crop, lost edges and unfilled seams.
        for h, w in [(64, 64), (1, 9), (63, 257), (129, 173), (720, 1280), (128, 128)]:
            with self.subTest(size=(h, w)):
                image = torch.arange(3*h*w, dtype=torch.float32).reshape(1, 3, h, w) / (3*h*w)
                prediction, _ = geometry_loss().run_model(make_batch(image))
                self.assertEqual(tuple(prediction.shape), (1, 3, h, w))
                torch.testing.assert_close(prediction, image, rtol=0, atol=0)

    def test_bdd_step3_reads_original_full_view_without_changing_step1(self):
        # Catches accidental center crop (including 720-square) and shared config regression.
        cfg = config("step3_bdd100k")
        dataset = init_dataset(cfg, Datasplit.TEST, is_paired=True)
        self.assertEqual(len(dataset), 104)
        batch = dataset[0]
        self.assertIsNone(batch.clean)
        self.assertEqual(tuple(batch.corrupt.shape), (3, 720, 1280))
        source = dataset.noisy_full_data.img_files[0]
        path = source.root / source.name
        before = hashlib.sha256(path.read_bytes()).hexdigest()
        expected = torchvision.io.read_image(str(path)).float() / 255
        torch.testing.assert_close(batch.corrupt, expected)
        self.assertEqual(batch.meta["source_path"], source.name.replace("\\", "/"))
        self.assertEqual(batch.meta["mode"], "full_image")
        self.assertEqual(batch.meta["tile_coordinates"].tolist(), [0, 0, 720, 1280])
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before)
        if torch.cuda.is_available():
            collated = Batch.collate_fn([batch])
            prediction, _ = geometry_loss().run_model(collated)
            torch.testing.assert_close(prediction[0], batch.corrupt, rtol=0, atol=0)
        self.assertTrue(cfg.training.require_output_manifest)
        self.assertFalse(config("step1_bdd100k").dataset.test.get("full_image", False))
        self.assertEqual(config("step1_bdd100k").dataset.train.patch_size, 64)

    @unittest.skipUnless(torch.cuda.is_available(), "CUDA is required")
    def test_internal_tile_kernel_association_handles_shared_and_per_tile_filters(self):
        # A shared filter per solver sub-batch must not be mistaken for one per tile.
        for shared, expected_count in [(True, 2), (False, 9)]:
            with self.subTest(shared=shared):
                loss = geometry_loss(shared)
                _, filters = loss.run_model(make_batch(torch.rand(1, 3, 257, 257)))
                geometry = loss.output_geometry
                self.assertEqual(len(geometry["tiles"]), 9)
                self.assertEqual(geometry["tiles"][0], [0, 0, 128, 128])
                self.assertEqual(geometry["tiles"][-1], [129, 129, 257, 257])
                self.assertEqual(filters.shape[0], expected_count)
                groups = geometry["filter_groups"]
                self.assertEqual(groups[0]["tile_range"], [0, 7])
                self.assertEqual(groups[1]["tile_range"], [7, 9])
                self.assertEqual(groups[0]["filter_range"], [0, 1 if shared else 7])
                self.assertEqual(groups[1]["filter_range"], [1 if shared else 7, expected_count])
                self.assertEqual(groups[0]["association"], "shared" if shared else "per_tile")


class Step3ProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Retain explicit test evidence; no recursive cleanup.
        cls.root = Path(tempfile.mkdtemp(prefix="step3-geometry-"))
        cls.source = cls.root / "source"
        cls.source.mkdir()
        for index in range(2):
            torchvision.io.write_png(torch.full((3, 19, 23), 50 + index, dtype=torch.uint8),
                                     str(cls.source / f"source-{index}.png"))
        print(f"STEP3_TEST_ARTIFACTS={cls.root}")

    def dataset(self):
        return PatchDataset(str(self.source), None, Datasplit.TEST, OmegaConf.create({
            "patch_size": 64, "full_image": True, "full_test": False,
            "need_clean": False, "need_noisy": True, "inflate_patches": 0,
        }), shuffle_clean=False)

    def test_collation_device_transfer_and_slice_preserve_source_identity(self):
        # Catches filenames receiving .to(), or slicing metadata along the wrong axis.
        dataset = self.dataset()
        batch = Batch.collate_fn([dataset[0], dataset[1]]).to("cpu")[1:]
        self.assertEqual(batch.meta["source_path"], ["source-1.png"])
        self.assertEqual(batch.meta["sample_index"].tolist(), [1])
        self.assertEqual(batch.meta["input_size"].tolist(), [[19, 23]])
        self.assertEqual(batch.meta["tile_coordinates"].tolist(), [[0, 0, 19, 23]])
        self.assertEqual(tuple(batch.corrupt.shape), (1, 3, 19, 23))

    @unittest.skipUnless(torch.cuda.is_available(), "CUDA is required")
    def test_saved_manifest_covers_each_prediction_and_refuses_overwrite(self):
        # Exercises actual data -> collate -> loss geometry -> validate_batch -> disk.
        dataset = self.dataset()
        output = Path(tempfile.mkdtemp(prefix="outputs-", dir=self.root))
        loss = geometry_loss()
        class IdentityPhysics(torch.nn.Module):
            def A(self, x):
                return x
        loss.physics = IdentityPhysics()
        trainer = object.__new__(DeepinvDenoiserTrainer)
        trainer.loss_optim = loss
        trainer.save_eval_to_file = trainer.save_pred_only = True
        trainer.require_output_manifest = True
        trainer.eval_dir = str(output)
        for index in range(2):
            trainer.global_step = index
            metrics = trainer.validate_batch(Batch.collate_fn([dataset[index]]))
            self.assertEqual(set(metrics), {"val_loss/reprojection_l1", "val_loss/reprojection_l2"})
        manifest = output / "manifest.jsonl"
        self.assertTrue(manifest.is_file(), "Each saved prediction needs a manifest row")
        rows = [json.loads(line) for line in manifest.read_text().splitlines()]
        self.assertEqual(len(rows), 2)
        self.assertEqual({r["output_path"] for r in rows}, {p.name for p in output.glob("img_*.png")})
        self.assertEqual({r["kernel_path"] for r in rows}, {p.name for p in output.glob("kernel_*.pt")})
        for i, row in enumerate(rows):
            self.assertEqual(row["source_path"], f"source-{i}.png")
            self.assertEqual(row["sample_index"], i)
            self.assertEqual(row["input_size"], [19, 23])
            self.assertEqual(row["mode"], "full_image")
            self.assertEqual(row["tile_coordinates"], [0, 0, 19, 23])
            self.assertEqual(row["solver_geometry"]["tiles"], [[0, 0, 19, 23]])
            self.assertEqual(row["solver_geometry"]["filter_groups"][0]["filter_range"], [0, 1])
            self.assertEqual(tuple(torchvision.io.read_image(str(output / row["output_path"])).shape), (3, 19, 23))
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir()}
        with self.assertRaises(FileExistsError):
            trainer.validate_batch(Batch.collate_fn([dataset[1]]))
        self.assertEqual(before, {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir()})
        trainer.global_step = 2
        with self.assertRaises(FileExistsError):
            trainer.validate_batch(Batch.collate_fn([dataset[1]]))
        self.assertEqual(before, {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir()})

    def test_required_provenance_missing_fails_before_saving(self):
        # Missing source metadata must never silently produce anonymous BDD100K output.
        from tests.test_deepinv_no_reference import _OutputOnlyLoss
        output = Path(tempfile.mkdtemp(prefix="missing-", dir=self.root))
        trainer = object.__new__(DeepinvDenoiserTrainer)
        trainer.loss_optim = _OutputOnlyLoss()
        trainer.save_eval_to_file = trainer.save_pred_only = True
        trainer.require_output_manifest = True
        trainer.eval_dir, trainer.global_step = str(output), 0
        with self.assertRaisesRegex(ValueError, "provenance"):
            trainer.validate_batch(make_batch(torch.zeros(1, 3, 16, 16)))
        self.assertEqual(list(output.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
