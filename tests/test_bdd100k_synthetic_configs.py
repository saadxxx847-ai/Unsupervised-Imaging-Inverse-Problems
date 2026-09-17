import unittest

import ddm4ip.main
from hydra import compose, initialize_config_module
from hydra.core.global_hydra import GlobalHydra
from omegaconf import OmegaConf


class SyntheticConfigTests(unittest.TestCase):
    def tearDown(self):
        GlobalHydra.instance().clear()

    def compose_synthetic(self, experiment):
        GlobalHydra.instance().clear()
        with initialize_config_module(config_module="ddm4ip.configs", version_base=None):
            cfg = compose(
                config_name="main",
                overrides=[f"exp={experiment}", "paths=bdd100k_synthetic_runtime"],
            )
        OmegaConf.resolve(cfg)
        return cfg

    def test_step1_and_step2_are_isolated_data_contracts(self):
        step1 = self.compose_synthetic("step1_bdd100k_synthetic")
        self.assertEqual(step1.dataset.train.name, "patch")
        self.assertFalse(step1.dataset.train.need_clean)
        self.assertTrue(step1.dataset.train.need_noisy)
        self.assertEqual(step1.training.max_steps, 5 * 2**20)

        step2 = self.compose_synthetic("step2_bdd100k_synthetic")
        self.assertTrue(step2.dataset.train.need_clean)
        self.assertFalse(step2.dataset.train.need_noisy)
        self.assertEqual(step2.dataset.train.noise_level_override, 0.02)
        self.assertEqual(step2.training.max_val_batches, 0)
        self.assertIsNone(step2.models.pretrained_flow.path)

    def test_oracle_and_learned_share_solver_and_evaluation_contract(self):
        oracle = self.compose_synthetic("step3_bdd100k_oracle")
        learned = self.compose_synthetic("step3_bdd100k_synthetic")
        self.assertEqual(oracle.dataset.test.name, "manifest_paired")
        self.assertIsNone(oracle.models.kernel.path)
        self.assertEqual(oracle.evaluation.variant, "oracle")
        self.assertEqual(learned.evaluation.variant, "learned")
        self.assertIsNone(learned.models.kernel.path)
        self.assertEqual(
            OmegaConf.to_container(oracle.models.deepinv_solver),
            OmegaConf.to_container(learned.models.deepinv_solver),
        )
        for cfg in (oracle, learned):
            self.assertEqual(cfg.training.batch_size, 1)
            self.assertFalse(cfg.training.train)
            self.assertTrue(cfg.training.save_eval_to_file)
            self.assertTrue(cfg.training.save_pred_only)
            self.assertTrue(cfg.training.require_output_manifest)
            self.assertEqual(cfg.evaluation.expected_records, 500)
            self.assertEqual(cfg.dataset.test.noise.std, 0.02)
            self.assertIsNone(cfg.evaluation.benchmark_summary_sha256)
        self.assertEqual(
            OmegaConf.to_container(oracle.loss), OmegaConf.to_container(learned.loss)
        )

    def test_paired_role_override_resolves_dev_reserve_path(self):
        GlobalHydra.instance().clear()
        with initialize_config_module(config_module="ddm4ip.configs", version_base=None):
            cfg = compose(
                config_name="main",
                overrides=[
                    "exp=step3_bdd100k_oracle",
                    "paths=bdd100k_synthetic_runtime",
                    "dataset.test.pairs_role=dev_reserve",
                    "dataset.test.pairs_dir=dev-reserve",
                    "dataset.test.max_imgs=16",
                ],
            )
        OmegaConf.resolve(cfg)
        self.assertEqual(cfg.dataset.test.pairs_role, "dev_reserve")
        self.assertEqual(cfg.dataset.test.role, "dev_reserve")
        self.assertTrue(str(cfg.dataset.test.path).replace("\\", "/").endswith(
            "/dev-reserve/pairs.jsonl"
        ))


if __name__ == "__main__":
    unittest.main()
