import hashlib
import json
import os
import pickle
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import torch
from PIL import Image


from scripts import bdd100k_synthetic_runner as runner
from ddm4ip.utils.benchmark_metrics import BenchmarkMetricWriter


HOST = "DESKTOP-KBM1345"
PYTHON = r"E:\Anaconda3\envs\ddm4ip\python.exe"
PICKLE_PATHS = []


class _PicklePathProbe:
    def __setstate__(self, state):
        PICKLE_PATHS.append(list(sys.path))
        self.__dict__.update(state)


class SyntheticRunnerTests(unittest.TestCase):
    def base_spec(self, stage="step1", mode="pilot", variant=None, seed=None):
        run_root = Path(r"D:\DDM4IP-runtime\experiments\bdd100k-synthetic-runner-test")
        return {
            "schema_version": 1,
            "task_name": "DDM4IP-BDD100K-SYNTH-Test-v1",
            "stage": stage,
            "mode": mode,
            "variant": variant,
            "seed": seed,
            "host": HOST,
            "python": PYTHON,
            "benchmark_root": r"D:\DDM4IP-runtime\synthetic-benchmarks\bdd100k-motionblur-v1",
            "run_root": str(run_root),
            "benchmark_summary": "summary.json",
            "pairs_manifest": "pairs.jsonl",
            "kernel_gt": "kernel-gt.pt",
            "expected_manifest_records": 2,
            "benchmark_hashes": {
                "summary": "a" * 64,
                "pairs": "b" * 64,
                "kernel": "c" * 64,
            },
            "runner_sha256": "d" * 64,
        }

    def _temporary_oracle_spec(self, root: Path, *, expected=1):
        benchmark = root / "benchmark"
        (benchmark / "dev-reserve").mkdir(parents=True)
        pairs = benchmark / "dev-reserve" / "pairs.jsonl"
        pairs.write_text(json.dumps({"source_id": "fixture-0"}) + "\n", encoding="utf-8")
        summary = benchmark / "summary.json"
        summary.write_text(json.dumps({"status": "SUCCESS", "counts": {"dev_reserve": expected}}), encoding="utf-8")
        kernel = benchmark / "kernel-gt.pt"
        kernel.write_bytes(b"true-kernel")
        run_root = root / "experiments" / "oracle-run"
        return {
            **self.base_spec(stage="oracle", mode="full", variant="oracle"),
            "benchmark_root": str(benchmark),
            "run_root": str(run_root),
            "pairs_manifest": "dev-reserve/pairs.jsonl",
            "expected_manifest_records": expected,
            "benchmark_hashes": {
                "summary": hashlib.sha256(summary.read_bytes()).hexdigest(),
                "pairs": hashlib.sha256(pairs.read_bytes()).hexdigest(),
                "kernel": hashlib.sha256(kernel.read_bytes()).hexdigest(),
            },
        }

    def _patch_temporary_roots(self, root: Path, benchmark: Path):
        return mock.patch.multiple(
            runner,
            EXPERIMENTS_ROOT=root / "experiments",
            BENCHMARK_ROOT=benchmark,
        )

    def test_rejects_unknown_fields_host_python_and_unsafe_paths(self):
        spec = self.base_spec()
        with self.assertRaises(ValueError):
            runner.validate_spec({**spec, "unexpected": True}, current_host=HOST, current_python=PYTHON)
        with self.assertRaises(ValueError):
            runner.validate_spec(spec, current_host="OTHER-HOST", current_python=PYTHON)
        with self.assertRaises(ValueError):
            runner.validate_spec(spec, current_host=HOST, current_python=r"C:\Python\python.exe")
        with self.assertRaises(ValueError):
            runner.validate_spec({**spec, "run_root": r"D:\DDM4IP-runtime\experiments\..\bad"}, current_host=HOST, current_python=PYTHON)
        with self.assertRaises(ValueError):
            runner.validate_spec({**spec, "run_root": r"C:\outside\run"}, current_host=HOST, current_python=PYTHON)

    def test_rejects_existing_run_or_benchmark_root(self):
        spec = self.base_spec()
        with tempfile.TemporaryDirectory() as temp:
            run_root = Path(temp) / "run"
            run_root.mkdir()
            with self.assertRaises(ValueError):
                runner.reserve_spec({**spec, "run_root": str(run_root)}, current_host=HOST, current_python=PYTHON)
            benchmark_root = Path(temp) / "benchmark"
            benchmark_root.mkdir()
            with self.assertRaises(ValueError):
                runner.reserve_spec({**spec, "stage": "build", "benchmark_root": str(benchmark_root)}, current_host=HOST, current_python=PYTHON)

    def test_rejects_predecessor_and_seed_contract_violations(self):
        with self.assertRaises(ValueError):
            runner.validate_spec(self.base_spec(stage="step2"), current_host=HOST, current_python=PYTHON)
        with self.assertRaises(ValueError):
            runner.validate_spec(self.base_spec(stage="step3", variant="learned", seed=0), current_host=HOST, current_python=PYTHON)
        with self.assertRaises(ValueError):
            runner.validate_spec(self.base_spec(stage="step2", seed=5), current_host=HOST, current_python=PYTHON)
        with self.assertRaises(ValueError):
            runner.validate_spec(self.base_spec(stage="step3", variant="oracle", seed=0), current_host=HOST, current_python=PYTHON)

    def _checkpoint_pair(self, root: Path, *, step=12, model_key="flow_nn", probe=False):
        checkpoints = root / "checkpoints"
        checkpoints.mkdir(parents=True, exist_ok=True)
        pt = checkpoints / f"training-state-{step}.pt"
        pkl = checkpoints / f"network-snapshot-{step}.pkl"
        torch.save({"global_step": step, model_key: {"weight": 1}}, pt)
        payload = {"global_step": step + 1, model_key: {"weight": 1}}
        if probe:
            probe_object = _PicklePathProbe()
            probe_object.marker = True
            payload["probe"] = probe_object
        with pkl.open("wb") as handle:
            pickle.dump(payload, handle)
        return pt, pkl

    def _predecessor(self, root: Path, *, stage="step1", step=12, seed=None, model_key="flow_nn"):
        pt, pkl = self._checkpoint_pair(root, step=step, model_key=model_key, probe=True)
        return {
            "stage": stage,
            "run_root": str(root),
            "expected_step": step,
            "training_state": f"checkpoints/training-state-{step}.pt",
            "training_state_sha256": hashlib.sha256(pt.read_bytes()).hexdigest(),
            "network_snapshot": f"checkpoints/network-snapshot-{step}.pkl",
            "network_snapshot_sha256": hashlib.sha256(pkl.read_bytes()).hexdigest(),
            "seed": seed,
        }

    def test_checkpoint_pair_uses_same_model_key_and_restores_sys_path_after_pickle(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pt, pkl = self._checkpoint_pair(root, model_key="flow_nn", probe=True)
            original_sys_path = list(sys.path)
            fake_project_root = root / "repo-root"
            sys.path = [entry for entry in sys.path if entry != str(fake_project_root)]
            PICKLE_PATHS.clear()
            try:
                with mock.patch.object(runner, "PROJECT_ROOT", fake_project_root):
                    runner.verify_checkpoint_pair(pt, pkl, expected_step=12, model_key="flow_nn")
            finally:
                sys.path = original_sys_path
            self.assertTrue(PICKLE_PATHS)
            self.assertIn(str(fake_project_root), PICKLE_PATHS[-1])
            self.assertEqual(sys.path, original_sys_path)

            kernel_pt, kernel_pkl = self._checkpoint_pair(root / "kernel", model_key="kernel_nn")
            runner.verify_checkpoint_pair(kernel_pt, kernel_pkl, expected_step=12, model_key="kernel_nn")
            with self.assertRaises(ValueError):
                runner.verify_checkpoint_pair(kernel_pt, kernel_pkl, expected_step=12, model_key="flow_nn")

    def test_resolve_predecessor_checks_schema_hash_step_stage_seed_and_model_key(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            experiments = root / "experiments"
            predecessor_root = experiments / "step1-full"
            predecessor = self._predecessor(predecessor_root, stage="step1", seed=None, model_key="flow_nn")
            spec = {
                **self.base_spec(stage="step2", mode="full", seed=2),
                "run_root": str(experiments / "step2-full-seed2"),
                "predecessor": predecessor,
            }
            with mock.patch.object(runner, "EXPERIMENTS_ROOT", experiments):
                resolved = runner.resolve_and_verify_predecessor(spec)
                overrides = runner.build_hydra_overrides(spec, **resolved)
            self.assertEqual(resolved["flow_checkpoint"], str(predecessor_root / predecessor["training_state"]))
            self.assertIsNone(resolved["kernel_snapshot"])
            self.assertIn("models.pretrained_flow.path=" + str(predecessor_root / predecessor["training_state"]).replace("\\", "/"), overrides)

            bad_stage = {**predecessor, "stage": "step2"}
            with mock.patch.object(runner, "EXPERIMENTS_ROOT", experiments):
                with self.assertRaises(ValueError):
                    runner.resolve_and_verify_predecessor({**spec, "predecessor": bad_stage})
                with self.assertRaises(ValueError):
                    runner.resolve_and_verify_predecessor({**spec, "predecessor": {**predecessor, "seed": 1}})
                with self.assertRaises(ValueError):
                    runner.resolve_and_verify_predecessor({**spec, "predecessor": {**predecessor, "training_state_sha256": "0" * 64}})

    def test_learned_step3_requires_same_seed_kernel_predecessor(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            experiments = root / "experiments"
            predecessor_root = experiments / "step2-full-seed3"
            predecessor = self._predecessor(predecessor_root, stage="step2", seed=3, model_key="kernel_nn")
            spec = {
                **self.base_spec(stage="step3", mode="full", variant="learned", seed=3),
                "run_root": str(experiments / "step3-full-seed3"),
                "predecessor": predecessor,
            }
            with mock.patch.object(runner, "EXPERIMENTS_ROOT", experiments):
                resolved = runner.resolve_and_verify_predecessor(spec)
                overrides = runner.build_hydra_overrides(spec, **resolved)
            self.assertIsNone(resolved["flow_checkpoint"])
            self.assertEqual(resolved["kernel_snapshot"], str(predecessor_root / predecessor["network_snapshot"]))
            self.assertIn("models.kernel.path=" + str(predecessor_root / predecessor["network_snapshot"]).replace("\\", "/"), overrides)
            with mock.patch.object(runner, "EXPERIMENTS_ROOT", experiments):
                with self.assertRaises(ValueError):
                    runner.resolve_and_verify_predecessor({**spec, "predecessor": {**predecessor, "seed": 2}})

    def test_execute_passes_verified_predecessor_paths_to_stage_command(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            experiments = root / "experiments"
            predecessor_root = experiments / "step1-full"
            predecessor = self._predecessor(predecessor_root, stage="step1", seed=None, model_key="flow_nn")
            spec = {
                **self.base_spec(stage="step2", mode="full", seed=1),
                "run_root": str(experiments / "step2-full-seed1"),
                "predecessor": predecessor,
            }
            with mock.patch.object(runner, "EXPERIMENTS_ROOT", experiments):
                runner.reserve_spec(spec, current_host=HOST, current_python=PYTHON)
                with mock.patch.object(runner, "preflight_benchmark_artifacts"), \
                     mock.patch.object(runner, "stage_command", return_value=[PYTHON, "-c", "pass"]) as stage_command, \
                     mock.patch.object(runner.subprocess, "run", return_value=mock.Mock(returncode=0)), \
                     mock.patch.object(runner, "postflight_stage_artifacts"):
                    code = runner.main([
                        "execute", "--spec", str(Path(spec["run_root"]) / "spec.json"),
                        "--current-host", HOST, "--current-python", PYTHON,
                    ])
            self.assertEqual(code, 0)
            _, kwargs = stage_command.call_args
            self.assertEqual(kwargs["flow_checkpoint"], str(predecessor_root / predecessor["training_state"]))
            self.assertIsNone(kwargs["kernel_snapshot"])

    def test_command_selection_and_injections_are_exact(self):
        expected = {
            ("step1", None): "exp=step1_bdd100k_synthetic",
            ("step2", None): "exp=step2_bdd100k_synthetic",
            ("oracle", "oracle"): "exp=step3_bdd100k_oracle",
            ("step3", "oracle"): "exp=step3_bdd100k_oracle",
            ("step3", "learned"): "exp=step3_bdd100k_synthetic",
        }
        for key, value in expected.items():
            self.assertEqual(runner.command_for(*key), value)
        step2 = runner.build_hydra_overrides({**self.base_spec(stage="step2", seed=2), "predecessor": {"step": 1}},
                                             flow_checkpoint=r"D:\flow.pt")
        self.assertIn("models.pretrained_flow.path=D:/flow.pt", step2)
        learned = runner.build_hydra_overrides({**self.base_spec(stage="step3", variant="learned", seed=2), "predecessor": {"step": 2, "network_snapshot_sha256": "f" * 64}},
                                               kernel_snapshot=r"D:\kernel.pkl")
        self.assertIn("models.kernel.path=D:/kernel.pkl", learned)
        self.assertIn("evaluation.step2_seed=2", learned)
        oracle = runner.build_hydra_overrides(self.base_spec(stage="step3", variant="oracle"))
        self.assertFalse(any("models.kernel.path=" in item for item in oracle))

    def test_oracle_pilot_is_fixed_to_dev_reserve_and_16_records(self):
        spec = {
            **self.base_spec(stage="oracle", mode="pilot", variant="oracle"),
            "pairs_manifest": "dev-reserve/pairs.jsonl",
            "expected_manifest_records": 16,
            "overrides": {"dataset.test.max_imgs": 16},
        }
        runner.validate_spec(spec, current_host=HOST, current_python=PYTHON)
        overrides = runner.build_hydra_overrides(spec)
        self.assertIn("dataset.test.pairs_role=dev_reserve", overrides)
        self.assertIn("dataset.test.max_imgs=16", overrides)
        self.assertIn("evaluation.expected_records=16", overrides)
        self.assertIn("evaluation.kernel_gt_path=D:/DDM4IP-runtime/synthetic-benchmarks/bdd100k-motionblur-v1/kernel-gt.pt", overrides)
        self.assertIn("evaluation.kernel_gt_sha256=" + "c" * 64, overrides)
        self.assertIn("evaluation.pairs_manifest_sha256=" + "b" * 64, overrides)
        self.assertIn("evaluation.benchmark_summary_sha256=" + "a" * 64, overrides)

        for invalid in (
            {**spec, "variant": None},
            {**spec, "variant": "learned"},
            {**spec, "seed": 0},
            {**spec, "predecessor": {"stage": "step1"}},
        ):
            with self.assertRaises(ValueError):
                runner.validate_spec(invalid, current_host=HOST, current_python=PYTHON)

        invalid = {
            **self.base_spec(stage="oracle", mode="pilot", variant="oracle"),
            "expected_manifest_records": 2,
            "overrides": {"dataset.test.max_imgs": 2},
        }
        with self.assertRaises(ValueError):
            runner.validate_spec(invalid, current_host=HOST, current_python=PYTHON)

    def test_oracle_pilot_maps_logical_role_to_frozen_pairs_directory(self):
        spec = {
            **self.base_spec(stage="oracle", mode="pilot", variant="oracle"),
            "pairs_manifest": "dev-reserve/pairs.jsonl",
            "expected_manifest_records": 16,
            "overrides": {"dataset.test.max_imgs": 16},
        }
        overrides = runner.build_hydra_overrides(spec)
        self.assertIn("dataset.test.pairs_role=dev_reserve", overrides)
        self.assertIn("dataset.test.pairs_dir=dev-reserve", overrides)
        with self.assertRaises(ValueError):
            runner.validate_spec(
                {**spec, "pairs_manifest": "test-paired/pairs.jsonl"},
                current_host=HOST,
                current_python=PYTHON,
            )

    def test_inventory_and_build_use_the_benchmark_builder_not_hydra(self):
        inventory = {**self.base_spec(stage="inventory"),
                     "view_root": r"D:\DDM4IP-runtime\group-data-views\BDD100K_Blur_Sharp",
                     "view_manifest_sha256": "e" * 64}
        inventory_command = runner.stage_command(inventory)
        self.assertEqual(inventory_command[2], "inspect")
        self.assertIn("--expected-source-count", inventory_command)
        self.assertIn("1739", inventory_command)
        build = {**self.base_spec(stage="build"),
                 "view_root": r"D:\DDM4IP-runtime\group-data-views\BDD100K_Blur_Sharp",
                 "source_manifest_sha256": "f" * 64,
                 "source_manifest": r"D:\DDM4IP-runtime\experiments\inventory\source-manifest.csv"}
        build_command = runner.stage_command(build)
        self.assertEqual(build_command[2], "build")
        self.assertIn("--expected-source-manifest-sha256", build_command)
        self.assertIn(build["source_manifest"], build_command)

    def test_child_process_environment_includes_project_root(self):
        env = runner.child_process_environment()
        self.assertEqual(env["PYTHONPATH"].split(os.pathsep)[0], str(runner.PROJECT_ROOT))

    def test_stage_command_binds_reserved_run_root_to_hydra_and_training_output(self):
        spec = self.base_spec()
        command = runner.stage_command(spec)
        self.assertIn(f"training.log_dir={Path(spec['run_root']).parent.as_posix()}", command)
        self.assertIn(f"exp_name={Path(spec['run_root']).name}", command)
        self.assertIn(f"hydra.run.dir={Path(spec['run_root']).as_posix()}", command)

    def test_execute_preflight_rejects_changed_benchmark_before_child(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            spec = self._temporary_oracle_spec(root)
            benchmark = Path(spec["benchmark_root"])
            with self._patch_temporary_roots(root, benchmark):
                runner.reserve_spec(spec, current_host=HOST, current_python=PYTHON)
                (benchmark / "summary.json").write_text("changed", encoding="utf-8")
                with mock.patch.object(runner.subprocess, "run", side_effect=AssertionError("child must not start")) as child:
                    code = runner.main([
                        "execute", "--spec", str(Path(spec["run_root"]) / "spec.json"),
                        "--current-host", HOST, "--current-python", PYTHON,
                    ])
                self.assertEqual(code, 1)
                child.assert_not_called()
                status = json.loads((Path(spec["run_root"]) / "status.json").read_text(encoding="utf-8"))
                self.assertEqual(status["status"], "FAILED")

    def test_real_execute_fixture_uses_subprocess_and_binds_log_and_postflight(self):
        fixture = Path(r"D:\Unsupervised Imaging Inverse Problems\tests\fixtures\synthetic_execute_child.py")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            spec = self._temporary_oracle_spec(root)
            benchmark = Path(spec["benchmark_root"])
            with self._patch_temporary_roots(root, benchmark):
                runner.reserve_spec(spec, current_host=HOST, current_python=PYTHON)
                with mock.patch.object(
                    runner, "stage_command",
                    side_effect=lambda current, **_: [PYTHON, str(fixture), str(current["run_root"])],
                ):
                    code = runner.main([
                        "execute", "--spec", str(Path(spec["run_root"]) / "spec.json"),
                        "--current-host", HOST, "--current-python", PYTHON,
                    ])
                self.assertEqual(code, 0)
                run_root = Path(spec["run_root"])
                status = json.loads((run_root / "status.json").read_text(encoding="utf-8"))
                self.assertEqual(status["status"], "SUCCESS")
                log = (run_root / "task.log").read_text(encoding="utf-8")
                self.assertIn("FIXTURE_CHILD_STDOUT", log)
                self.assertIn("FIXTURE_CHILD_STDERR", log)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            spec = self._temporary_oracle_spec(root)
            benchmark = Path(spec["benchmark_root"])
            with self._patch_temporary_roots(root, benchmark):
                runner.reserve_spec(spec, current_host=HOST, current_python=PYTHON)
                with mock.patch.object(
                    runner, "stage_command",
                    side_effect=lambda current, **_: [PYTHON, str(fixture), str(current["run_root"]), "corrupt"],
                ):
                    code = runner.main([
                        "execute", "--spec", str(Path(spec["run_root"]) / "spec.json"),
                        "--current-host", HOST, "--current-python", PYTHON,
                    ])
                self.assertEqual(code, 1)
                status = json.loads((Path(spec["run_root"]) / "status.json").read_text(encoding="utf-8"))
                self.assertEqual(status["status"], "FAILED")

    def test_execute_accepts_reserved_spec_file_path(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec_path = root / "spec.json"
            spec = {**self.base_spec(), "run_root": str(root),
                    "runner_sha256": runner.current_runner_sha256()}
            spec_path.write_text(json.dumps(spec), encoding="utf-8")
            loaded = runner.execute_reserved(
                spec_path, current_runner_sha256=runner.current_runner_sha256()
            )
            self.assertEqual(loaded["run_root"], str(root))
            self.assertTrue((root / "execution.claim").is_file())

    def test_inventory_artifacts_freeze_source_manifest_for_build_handoff(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = root / "source-manifest.csv"
            manifest.write_text(
                "source_id,source_relpath,size_bytes,sha256,width,height,channels\n"
                "a,train/clean/a.png,1," + "a" * 64 + ",1280,720,3\n"
                "b,val/clean/b.png,2," + "b" * 64 + ",1280,720,3\n",
                encoding="utf-8",
            )
            artifacts = runner.write_inventory_artifacts(root, expected_source_count=2)
            self.assertEqual(artifacts["source_manifest"]["path"], str(manifest))
            self.assertEqual(
                artifacts["source_manifest"]["sha256"],
                hashlib.sha256(manifest.read_bytes()).hexdigest(),
            )
            self.assertEqual(artifacts["source_manifest"]["records"], 2)
            self.assertEqual(artifacts["source_manifest"]["source_roots"],
                             {"train": 1, "val": 1})

    def test_build_artifacts_freeze_benchmark_and_input_provenance_without_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            benchmark = root / "benchmark"
            run_root = root / "build-audit"
            source_manifest = root / "inventory" / "source-manifest.csv"
            source_manifest.parent.mkdir()
            source_manifest.write_text(
                "source_id,source_relpath,size_bytes,sha256,width,height,channels\n"
                "a,train/clean/a.png,1," + "a" * 64 + ",1280,720,3\n",
                encoding="utf-8",
            )
            (benchmark / "degradation").mkdir(parents=True)
            (benchmark / "test-paired").mkdir()
            (benchmark / "source-manifest.csv").write_bytes(source_manifest.read_bytes())
            (benchmark / "split-manifest.csv").write_text(
                "role,source_id\nstep1_observation,a\n", encoding="utf-8"
            )
            (benchmark / "test-paired" / "pairs.jsonl").write_text(
                json.dumps({"source_id": "a"}) + "\n", encoding="utf-8"
            )
            (benchmark / "preprocessing.json").write_text(
                json.dumps({"output_size": [256, 256]}) + "\n", encoding="utf-8"
            )
            (benchmark / "degradation" / "degradation.json").write_text(
                json.dumps({"kind": "motion_blur"}) + "\n", encoding="utf-8"
            )
            kernel = torch.ones(1, 1, 1, 1)
            torch.save(kernel, benchmark / "degradation" / "kernel-gt.pt")
            (benchmark / "summary.json").write_text(
                json.dumps({
                    "counts": {"step1_observation": 1},
                    "source_manifest_sha256": hashlib.sha256(
                        (benchmark / "source-manifest.csv").read_bytes()
                    ).hexdigest(),
                    "kernel_tensor_sha256": "k" * 64,
                    "kernel_file_sha256": "f" * 64,
                }), encoding="utf-8"
            )
            (benchmark / "status.json").write_text(
                json.dumps({"status": "SUCCESS"}), encoding="utf-8"
            )
            before = {
                path.relative_to(benchmark): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in benchmark.rglob("*") if path.is_file()
            }
            spec = {
                "benchmark_root": str(benchmark),
                "source_manifest": str(source_manifest),
                "source_manifest_sha256": hashlib.sha256(
                    source_manifest.read_bytes()
                ).hexdigest(),
                "benchmark_summary": "summary.json",
                "pairs_manifest": "test-paired/pairs.jsonl",
                "kernel_gt": "degradation/kernel-gt.pt",
                "expected_manifest_records": 1,
            }
            artifacts = runner.write_build_artifacts(run_root, spec)
            self.assertEqual(
                artifacts["source_manifest"]["sha256"],
                spec["source_manifest_sha256"],
            )
            self.assertEqual(
                artifacts["benchmark"]["files"]["split-manifest.csv"],
                hashlib.sha256((benchmark / "split-manifest.csv").read_bytes()).hexdigest(),
            )
            self.assertEqual(
                artifacts["benchmark"]["files"]["test-paired/pairs.jsonl"],
                hashlib.sha256((benchmark / "test-paired" / "pairs.jsonl").read_bytes()).hexdigest(),
            )
            self.assertEqual(
                before,
                {
                    path.relative_to(benchmark): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in benchmark.rglob("*") if path.is_file()
                },
            )
            self.assertTrue((run_root / "artifacts.json").is_file())

    def test_start_wrapper_executes_reserved_spec_file(self):
        wrapper = Path(r"D:\DDM4IP-runtime\orchestration\start_bdd100k_synthetic_task.ps1")
        text = wrapper.read_text(encoding="utf-8")
        self.assertIn("$reservedSpec", text)
        self.assertIn('-SpecPath `"$reservedSpec`"', text)
        self.assertNotIn('-SpecPath `"$SpecPath`""', text)

    def test_wrappers_have_one_manual_start_no_time_trigger_and_offline_torch_home(self):
        launcher = Path(r"D:\DDM4IP-runtime\orchestration\start_bdd100k_synthetic_task.ps1")
        stage_wrapper = Path(r"D:\DDM4IP-runtime\orchestration\run_bdd100k_synthetic_stage.ps1")
        launcher_text = launcher.read_text(encoding="utf-8")
        stage_text = stage_wrapper.read_text(encoding="utf-8")
        self.assertNotIn("New-ScheduledTaskTrigger", launcher_text)
        self.assertEqual(launcher_text.count("Start-ScheduledTask"), 1)
        self.assertIn("Register-ScheduledTask", launcher_text)
        self.assertIn('-SpecPath `"$reservedSpec`"', launcher_text)
        self.assertIn("$env:TORCH_HOME = 'D:\\DDM4IP-runtime\\torch-home'", stage_text)
        self.assertIn("$env:HF_HUB_OFFLINE = '1'", stage_text)
        self.assertIn("$env:TRANSFORMERS_OFFLINE = '1'", stage_text)
        self.assertIn("$LASTEXITCODE", stage_text)

    def test_powerShell_wrappers_have_zero_parser_errors(self):
        for script_path in (
            Path(r"D:\DDM4IP-runtime\orchestration\start_bdd100k_synthetic_task.ps1"),
            Path(r"D:\DDM4IP-runtime\orchestration\run_bdd100k_synthetic_stage.ps1"),
        ):
            command = (
                "$errors=@(); $tokens=$null; "
                "[System.Management.Automation.Language.Parser]::ParseFile('"
                + str(script_path).replace("'", "''")
                + "',[ref]$tokens,[ref]$errors) | Out-Null; "
                "Write-Output ('parse_errors=' + $errors.Count); "
                "if ($errors.Count -ne 0) { exit 1 }"
            )
            result = subprocess.run(
                ["powershell.exe", "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", command],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("parse_errors=0", result.stdout)

    def test_runtime_spec_schema_freezes_predecessor_and_benchmark_hash_contract(self):
        schema_path = Path(r"D:\DDM4IP-runtime\orchestration\synthetic-step-spec.schema.json")
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        predecessor = schema["properties"]["predecessor"]
        self.assertFalse(predecessor["additionalProperties"])
        self.assertEqual(set(predecessor["required"]), {
            "stage", "run_root", "expected_step", "training_state", "training_state_sha256",
            "network_snapshot", "network_snapshot_sha256", "seed",
        })
        self.assertEqual(set(schema["properties"]["benchmark_hashes"]["required"]), {
            "summary", "pairs", "kernel",
        })

    def test_execute_requires_reserved_spec_and_matching_runner_sha(self):
        with tempfile.TemporaryDirectory() as temp:
            run_root = Path(temp) / "run"
            with self.assertRaises(FileNotFoundError):
                runner.execute_reserved(run_root, current_runner_sha256="e" * 64)
            run_root.mkdir()
            (run_root / "spec.json").write_text(json.dumps(self.base_spec()), encoding="utf-8")
            with self.assertRaises(ValueError):
                runner.execute_reserved(run_root, current_runner_sha256="e" * 64)
        reserved = {**self.base_spec(), "reserved_at": "2026-09-06T00:00:00+00:00"}
        self.assertIn("exp=step1_bdd100k_synthetic", runner.build_hydra_overrides(reserved))

    def test_checkpoint_pair_and_evaluation_artifact_verification(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            pt = root / "training-state-12.pt"
            pkl = root / "network-snapshot-12.pkl"
            import torch

            torch.save({"global_step": 12, "flow_nn": {"weight": 1}}, pt)
            with pkl.open("wb") as handle:
                pickle.dump({"global_step": 13, "flow_nn": {"weight": 1}}, handle)
            runner.verify_checkpoint_pair(pt, pkl, expected_step=12, model_key="flow_nn")

            plots = root / "plots"
            kernel_gt = root / "kernel-gt.pt"
            kernel_gt.write_bytes(b"true-kernel")
            writer = BenchmarkMetricWriter(
                plots, "fixture", "oracle", None, "e" * 64, kernel_gt, 1,
                pairs_manifest_sha256="a" * 64,
                benchmark_summary_sha256="b" * 64,
            )
            prediction = plots / "prediction-a.png"
            kernel = plots / "kernel-a.pt"
            Image.new("RGB", (8, 8), color=(128, 128, 128)).save(prediction, format="PNG")
            kernel.write_bytes(b"fixture-kernel")
            row_text = writer.prepare_record(
                {
                    "source_id": "a", "source_relpath": "source/a.png", "source_sha256": "1" * 64,
                    "clean_path": "clean/a.png", "noisy_path": "noisy/a.png",
                    "clean_sha256": "2" * 64, "noisy_sha256": "3" * 64,
                },
                torch.full((1, 3, 8, 8), 0.5), torch.ones((1, 1, 3, 3)),
                prediction.name, kernel.name, {"filter_groups": []},
                {"psnr": 10.0, "ssim": 0.1, "lpips": 0.9},
                {"psnr": 11.0, "ssim": 0.2, "lpips": 0.8},
                prediction_sha256=hashlib.sha256(prediction.read_bytes()).hexdigest(),
                kernel_sha256=hashlib.sha256(kernel.read_bytes()).hexdigest(),
            )
            writer.append(row_text)
            row = json.loads(row_text)
            (plots / "manifest.jsonl").write_text(
                json.dumps({"schema_version": 2, **row}) + "\n", encoding="utf-8"
            )
            writer.finalize_if_complete()
            runner.verify_evaluation_artifacts(
                root, expected_manifest_records=1,
                expected_hashes={"pairs_manifest_sha256": "a" * 64,
                                 "benchmark_summary_sha256": "b" * 64,
                                 "kernel_gt_sha256": hashlib.sha256(kernel_gt.read_bytes()).hexdigest()},
                oracle=True,
            )

    def test_step2_defaults_to_single_process_dataloader(self):
        spec = {
            **self.base_spec(stage="step2", mode="pilot", seed=0),
            "predecessor": {"stage": "step1"},
        }
        overrides = runner.build_hydra_overrides(
            spec, flow_checkpoint=r"D:\flow.pt"
        )
        worker_overrides = [
            item for item in overrides if item.startswith("training.num_workers=")
        ]
        self.assertEqual(worker_overrides, ["training.num_workers=0"])

    def test_step2_rejects_nonzero_dataloader_workers(self):
        spec = {
            **self.base_spec(stage="step2", mode="pilot", seed=0),
            "predecessor": {"stage": "step1"},
            "overrides": {"training.num_workers": 4},
        }
        with self.assertRaisesRegex(ValueError, "training.num_workers=0"):
            runner.build_hydra_overrides(spec, flow_checkpoint=r"D:\flow.pt")


if __name__ == "__main__":
    unittest.main()
