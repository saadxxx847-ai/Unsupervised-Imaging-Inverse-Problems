import unittest

import ddm4ip.main  # Registers the parse_nimg resolver used by the job configs.
from hydra import compose, initialize_config_module
from hydra.core.global_hydra import GlobalHydra
from hydra.errors import MissingConfigException
from omegaconf import OmegaConf


class Bdd100kConfigTests(unittest.TestCase):
    def tearDown(self):
        GlobalHydra.instance().clear()

    def compose_bdd100k(self, experiment):
        GlobalHydra.instance().clear()
        try:
            with initialize_config_module(
                config_module="ddm4ip.configs", version_base=None
            ):
                cfg = compose(
                    config_name="main",
                    overrides=[
                        f"exp={experiment}",
                        "paths=bdd100k_runtime",
                    ],
                )
            OmegaConf.resolve(cfg)
            return cfg
        except MissingConfigException as exc:
            self.fail(f"{experiment} must compose as a BDD100K job: {exc}")

    def test_step1_composes_noisy_only_patch_datasets(self):
        cfg = self.compose_bdd100k("step1_bdd100k")

        for dataset in (cfg.dataset.train, cfg.dataset.test):
            self.assertEqual(dataset.name, "patch")
            self.assertFalse(dataset.need_clean)
            self.assertTrue(dataset.need_noisy)
        self.assertEqual(
            cfg.dataset.train.train_path,
            "D:/DDM4IP-runtime/group-data-views/BDD100K_Blur_Sharp/train/noisy",
        )
        self.assertEqual(
            cfg.dataset.test.test_path,
            "D:/DDM4IP-runtime/group-data-views/BDD100K_Blur_Sharp/val/noisy",
        )
        self.assertEqual(cfg.training.max_val_batches, 0)

    def test_step2_composes_unpaired_clean_and_noisy_datasets(self):
        cfg = self.compose_bdd100k("step2_bdd100k")

        for dataset in (cfg.dataset.train, cfg.dataset.test):
            self.assertEqual(dataset.name, "simple_patch")
        self.assertEqual(
            cfg.dataset.train.train_path,
            "D:/DDM4IP-runtime/group-data-views/BDD100K_Blur_Sharp/train/clean",
        )
        self.assertEqual(
            cfg.dataset.train.noisy_path,
            "D:/DDM4IP-runtime/group-data-views/BDD100K_Blur_Sharp/train/noisy",
        )
        self.assertEqual(
            cfg.dataset.test.test_path,
            "D:/DDM4IP-runtime/group-data-views/BDD100K_Blur_Sharp/val/clean",
        )
        self.assertEqual(
            cfg.dataset.test.noisy_path,
            "D:/DDM4IP-runtime/group-data-views/BDD100K_Blur_Sharp/val/noisy",
        )
        self.assertEqual(cfg.training.max_val_batches, 0)
        self.assertIsNone(cfg.models.pretrained_flow.path)

    def test_step3_composes_no_reference_evaluation(self):
        cfg = self.compose_bdd100k("step3_bdd100k")

        self.assertEqual(cfg.dataset.test.name, "patch")
        self.assertFalse(cfg.dataset.test.need_clean)
        self.assertTrue(cfg.dataset.test.need_noisy)
        self.assertEqual(
            cfg.dataset.test.test_path,
            "D:/DDM4IP-runtime/group-data-views/BDD100K_Blur_Sharp/val/noisy",
        )
        self.assertFalse(cfg.training.train)
        self.assertTrue(cfg.training.save_eval_to_file)
        self.assertTrue(cfg.training.save_pred_only)
        self.assertIsNone(cfg.models.kernel.path)


if __name__ == "__main__":
    unittest.main()
