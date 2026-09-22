"""BDD100K runner with validation fixtures and fail-closed experiment contracts."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import pickle
import re
import socket
import subprocess
import sys
import traceback

import torch

RUNTIME = Path(r"D:\DDM4IP-runtime")
EXPERIMENTS = RUNTIME / "experiments"
REPOSITORY = Path(r"D:\Unsupervised Imaging Inverse Problems")
PYTHON = Path(r"E:\Anaconda3\envs\ddm4ip\python.exe")
TASK_PATTERN = r"DDM4IP-BDD100K-[A-Za-z0-9_-]+"
SHA256_PATTERN = r"[0-9a-f]{64}"
SAFE_OVERRIDE_PATTERN = re.compile(r"(?:training\.(?:batch_size|max_steps|report_every_steps|plot_every_steps|save_every_steps|num_workers|max_val_batches)|loss\.n_accum_steps)=\d+")


def write_new(path, text):
    with path.open("x", encoding="utf-8") as fh:
        fh.write(text)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@contextmanager
def repository_import_path():
    repository = str(REPOSITORY.resolve())
    sys.path.insert(0, repository)
    try:
        yield
    finally:
        sys.path.remove(repository)


def has_reparse_point(path):
    return any(ancestor.exists() and (ancestor.stat().st_file_attributes & 0x400) for ancestor in [path, *path.parents])


def safe_root(raw):
    root = Path(raw)
    if not root.is_absolute() or ".." in root.parts or not root.resolve().is_relative_to(EXPERIMENTS.resolve()) or root.resolve() == EXPERIMENTS.resolve():
        raise ValueError("run_root must be a new descendant of D:\\DDM4IP-runtime\\experiments")
    if has_reparse_point(root):
        raise ValueError("Reparse points are not accepted in run_root")
    return root


def safe_artifact(raw, suffix):
    path = Path(raw)
    if not path.is_absolute() or path.suffix != suffix or not path.is_file() or not path.resolve().is_relative_to(EXPERIMENTS.resolve()) or has_reparse_point(path):
        raise ValueError(f"Checkpoint must be a regular {suffix} file below D:\\DDM4IP-runtime\\experiments")
    return path


def load_spec(path):
    if socket.gethostname().upper() != "DESKTOP-KBM1345":
        raise RuntimeError("Wrong execution host")
    if Path(sys.executable).resolve() != PYTHON.resolve():
        raise RuntimeError("Wrong Python executable")
    spec = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    root = safe_root(spec["run_root"])
    if not re.fullmatch(TASK_PATTERN, spec.get("task_name", "")):
        raise ValueError("Invalid task_name")
    return spec, root


class Run:
    def __init__(self, spec, root):
        self.spec, self.root = spec, root
        self.state = dict(state="RUNNING", step="validate-spec", detail="", updated_at="",
            host=socket.gethostname(), python=str(PYTHON), repository=str(REPOSITORY),
            runtime_root=str(RUNTIME), stage_root=str(root), run_root=str(root), task_name=spec["task_name"],
            log_path=str(root / "task.log"), config_path=str(root / "resolved-config.yaml"),
            output_path=str(root / "output"), process_id=os.getpid(), child_process_id=None,
            exit_code=None, native_exit_code=None)

    @property
    def is_validation(self):
        return self.spec["mode"] == "validation"

    @property
    def is_experiment(self):
        return self.spec["mode"] in ("pilot", "full")

    def update(self, state=None, step=None, detail="", **extra):
        self.state.update(extra)
        self.state.update(detail=detail, updated_at=datetime.now(timezone.utc).isoformat(), process_id=os.getpid())
        if state:
            self.state["state"] = state
        if step:
            self.state["step"] = step
        payload = json.dumps(self.state, ensure_ascii=False)
        with (self.root / "status-history.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(payload + "\n")
        temporary = self.root / "status.json.tmp"
        temporary.write_text(payload + "\n", encoding="utf-8")
        os.replace(temporary, self.root / "status.json")
        with (self.root / "task.log").open("a", encoding="utf-8") as fh:
            fh.write(f"{self.state['updated_at']} {self.state['state']} {self.state['step']} {detail}\n")

    def validate(self):
        spec = self.spec
        allowed = {"task_name", "stage", "mode", "run_root", "hydra_overrides", "expected_artifacts", "validation_case", "delay_seconds", "predecessor", "expected_final_global_step", "expected_manifest_records", "execution_timeout_minutes"}
        unknown = set(spec) - allowed
        if unknown:
            raise ValueError("Unknown spec fields: " + ", ".join(sorted(unknown)))
        for field in ("stage", "mode", "hydra_overrides"):
            if field not in spec:
                raise ValueError("Missing required field: " + field)
        if spec["stage"] not in ("step1", "step2", "step3") or spec["mode"] not in ("validation", "pilot", "full"):
            raise ValueError("Invalid stage or mode")
        self.validate_validation() if self.is_validation else self.validate_experiment()

    def validate_validation(self):
        spec = self.spec
        if spec["stage"] != "step1":
            raise ValueError("Phase-B execution fixture must use step1; step2/3 are configuration-only checks")
        if spec["hydra_overrides"] != []:
            raise ValueError("Phase-B fixture accepts only its fixed configuration; no arbitrary overrides")
        if spec.get("validation_case") not in ("success", "native-failure", "missing-artifact"):
            raise ValueError("Invalid validation_case")
        if type(spec.get("delay_seconds", 0)) is not int or not 0 <= spec.get("delay_seconds", 0) <= 120:
            raise ValueError("delay_seconds must be an integer from 0 to 120")
        if spec.get("expected_artifacts") != ["fixture.ok"]:
            raise ValueError("Phase-B expected_artifacts must be [fixture.ok]; path escapes are forbidden")

    def validate_experiment(self):
        spec = self.spec
        if {"validation_case", "delay_seconds", "expected_artifacts"} & set(spec):
            raise ValueError("Experiment spec cannot contain validation-only fields")
        if not isinstance(spec["hydra_overrides"], list) or not spec["hydra_overrides"] or any(not isinstance(item, str) or not SAFE_OVERRIDE_PATTERN.fullmatch(item) for item in spec["hydra_overrides"]):
            raise ValueError("hydra_overrides must contain only explicit numeric training/loss budget overrides")
        if type(spec.get("execution_timeout_minutes")) is not int or not 1 <= spec["execution_timeout_minutes"] <= 4320:
            raise ValueError("execution_timeout_minutes must be an integer from 1 to 4320")
        if spec["stage"] in ("step1", "step2"):
            if type(spec.get("expected_final_global_step")) is not int or spec["expected_final_global_step"] <= 0:
                raise ValueError("Step 1/2 require a positive expected_final_global_step")
        elif type(spec.get("expected_manifest_records")) is not int or spec["expected_manifest_records"] <= 0:
            raise ValueError("Step 3 requires a positive expected_manifest_records")
        if spec["stage"] == "step1":
            if "predecessor" in spec:
                raise ValueError("Step 1 must not inject a predecessor checkpoint")
        elif "predecessor" not in spec:
            raise ValueError("Step 2/3 require an independently verified predecessor")
        else:
            self.validate_predecessor()

    def validate_predecessor(self):
        predecessor = self.spec["predecessor"]
        required = {"stage", "training_state_path", "training_state_sha256", "network_snapshot_path", "network_snapshot_sha256", "final_global_step"}
        if not isinstance(predecessor, dict) or set(predecessor) != required:
            raise ValueError("predecessor must contain only the complete paired checkpoint contract")
        expected_stage = "step1" if self.spec["stage"] == "step2" else "step2"
        if predecessor["stage"] != expected_stage:
            raise ValueError(f"{self.spec['stage']} requires a {expected_stage} predecessor")
        step = predecessor["final_global_step"]
        if type(step) is not int or step <= 0:
            raise ValueError("predecessor final_global_step must be positive")
        state = safe_artifact(predecessor["training_state_path"], ".pt")
        snapshot = safe_artifact(predecessor["network_snapshot_path"], ".pkl")
        if state.parent != snapshot.parent or state.name != f"training-state-{step}.pt" or snapshot.name != f"network-snapshot-{step}.pkl":
            raise ValueError("predecessor checkpoint pair must be sibling terminal files with the same step")
        for field, path in (("training_state_sha256", state), ("network_snapshot_sha256", snapshot)):
            claimed = predecessor[field]
            if not isinstance(claimed, str) or not re.fullmatch(SHA256_PATTERN, claimed) or sha256(path) != claimed:
                raise ValueError(f"Predecessor {field} does not match the current file")
        state_data = torch.load(state, map_location="cpu", weights_only=False)
        with repository_import_path():
            with snapshot.open("rb") as fh:
                snapshot_data = pickle.load(fh)
            from ddm4ip.utils.checkpoint_validation import require_finite_tensors
            require_finite_tensors(state_data, 'training-state')
            require_finite_tensors(snapshot_data, 'network-snapshot')
        if not isinstance(state_data, dict) or state_data.get("global_step") != step:
            raise ValueError("training-state global_step is not the claimed terminal step")
        if not isinstance(snapshot_data, dict) or snapshot_data.get("global_step") != step + 1:
            raise ValueError("network-snapshot global_step must be terminal step plus one")
        model_key = "flow_nn" if expected_stage == "step1" else "kernel_nn"
        if model_key not in state_data or model_key not in snapshot_data:
            raise ValueError(f"{expected_stage} predecessor is missing {model_key}")
        return predecessor

    def environment(self):
        env = os.environ.copy()
        for key, subpath in dict(TEMP="temp", TMP="temp", PIP_CACHE_DIR="pip-cache", TORCH_HOME="torch-home", XDG_CACHE_HOME="xdg-cache", MPLCONFIGDIR="xdg-cache/matplotlib").items():
            env[key] = str(RUNTIME / subpath)
        env["PYTHONPYCACHEPREFIX"] = str(RUNTIME / "orchestration" / "pycache")
        env.update(PYTHONUTF8="1", PYTHONIOENCODING="utf-8", HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
        return env

    def config_command(self):
        if self.is_validation:
            command = [str(PYTHON), "-m", "ddm4ip.main", "exp=step1_bdd100k", "paths=bdd100k_runtime", "exp_name=fixture-config-only", f"training.log_dir={self.root.as_posix()}/output"]
        else:
            command = [str(PYTHON), "-m", "ddm4ip.main", f"exp={self.spec['stage']}_bdd100k", "paths=bdd100k_runtime", f"exp_name={self.spec['task_name']}", f"training.log_dir={self.root.as_posix()}/output", *self.spec["hydra_overrides"]]
            if self.spec["stage"] == "step2":
                command.append("models.pretrained_flow.path=" + Path(self.spec["predecessor"]["training_state_path"]).as_posix())
            elif self.spec["stage"] == "step3":
                command.append("models.kernel.path=" + Path(self.spec["predecessor"]["network_snapshot_path"]).as_posix())
        return command

    def execution_command(self):
        if self.is_validation:
            return [str(PYTHON), str(Path(__file__).with_name("runner_fixture.py")), str(self.root), self.spec["validation_case"], str(self.spec.get("delay_seconds", 0))]
        return self.config_command()

    def prepare_metadata(self):
        env = self.environment()
        allowed_env = ("TEMP", "TMP", "PIP_CACHE_DIR", "TORCH_HOME", "XDG_CACHE_HOME", "MPLCONFIGDIR", "PYTHONPYCACHEPREFIX", "HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE")
        write_new(self.root / "environment.json", json.dumps({k: v for k, v in env.items() if k in allowed_env}, indent=2))
        if self.spec["stage"] in ("step2", "step3"):
            write_new(self.root / "predecessor.json", json.dumps(self.validate_predecessor(), indent=2))
        command = self.execution_command()
        config = self.config_command() + ["--cfg", "job", "--resolve"]
        write_new(self.root / "command.json", json.dumps(command, indent=2))
        write_new(self.root / "command.txt", subprocess.list2cmdline(command) + "\n")
        write_new(self.root / "config-command.json", json.dumps(config, indent=2))
        return env, command, config

    def command(self, args, env, config=False):
        with (self.root / "task.log").open("a", encoding="utf-8") as log:
            log.write("COMMAND " + json.dumps(args) + "\n")
            log.flush()
            if config:
                with (self.root / "resolved-config.yaml").open("x", encoding="utf-8") as cfg:
                    child = subprocess.Popen(args, cwd=REPOSITORY, env=env, stdout=cfg, stderr=log)
                    self.update(child_process_id=child.pid)
                    code = child.wait()
            else:
                child = subprocess.Popen(args, cwd=REPOSITORY, env=env, stdout=log, stderr=subprocess.STDOUT)
                self.update(child_process_id=child.pid)
                code = child.wait()
        self.state["native_exit_code"] = code
        if code:
            raise subprocess.CalledProcessError(code, args)

    def stage_output_root(self):
        return self.root / "output" / self.spec["task_name"]

    def verify_checkpoint_pair(self):
        step = self.spec["expected_final_global_step"]
        checkpoints = self.stage_output_root() / "checkpoints"
        state, snapshot = checkpoints / f"training-state-{step}.pt", checkpoints / f"network-snapshot-{step}.pkl"
        for path in (state, snapshot):
            if not path.is_file():
                raise FileNotFoundError("Required terminal checkpoint is missing: " + str(path))
        state_data = torch.load(state, map_location="cpu", weights_only=False)
        with repository_import_path():
            with snapshot.open("rb") as fh:
                snapshot_data = pickle.load(fh)
            from ddm4ip.utils.checkpoint_validation import require_finite_tensors
            require_finite_tensors(state_data, 'training-state')
            require_finite_tensors(snapshot_data, 'network-snapshot')
        model_key = "flow_nn" if self.spec["stage"] == "step1" else "kernel_nn"
        if not isinstance(state_data, dict) or state_data.get("global_step") != step or model_key not in state_data:
            raise ValueError("training-state is not a valid terminal stage artifact")
        if not isinstance(snapshot_data, dict) or snapshot_data.get("global_step") != step + 1 or model_key not in snapshot_data:
            raise ValueError("network-snapshot is not the matching terminal stage artifact")
        return {"training_state": {"path": str(state), "sha256": sha256(state), "global_step": step}, "network_snapshot": {"path": str(snapshot), "sha256": sha256(snapshot), "global_step": step + 1}}

    def verify_manifest(self):
        plots = self.stage_output_root() / "plots"
        manifest = plots / "manifest.jsonl"
        if not manifest.is_file():
            raise FileNotFoundError("Required Step 3 manifest is missing: " + str(manifest))
        records = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
        if len(records) != self.spec["expected_manifest_records"]:
            raise ValueError("Manifest record count does not match expected_manifest_records")
        required = {"schema_version", "source_root", "source_path", "sample_index", "input_size", "mode", "tile_index", "tile_coordinates", "output_path", "output_size", "kernel_path", "kernel_shape", "solver_geometry", "metrics"}
        identities, artifacts = set(), []
        for record in records:
            if not required.issubset(record):
                raise ValueError("Manifest record is missing required provenance fields")
            identity = (record["source_root"], record["source_path"], record["tile_index"])
            if identity in identities:
                raise ValueError("Manifest contains duplicate source/tile provenance")
            identities.add(identity)
            if Path(record["output_path"]).name != record["output_path"] or Path(record["kernel_path"]).name != record["kernel_path"]:
                raise ValueError("Manifest output paths must be local basenames")
            output, kernel = plots / record["output_path"], plots / record["kernel_path"]
            if not output.is_file() or not kernel.is_file():
                raise FileNotFoundError("Manifest references a missing prediction or kernel artifact")
            groups = record["solver_geometry"].get("filter_groups") if isinstance(record["solver_geometry"], dict) else None
            if not isinstance(groups, list) or not groups:
                raise ValueError("Manifest record has no solver filter-group provenance")
            for group in groups:
                for field in ("tile_range", "filter_range"):
                    value = group.get(field) if isinstance(group, dict) else None
                    if not isinstance(value, list) or len(value) != 2 or not all(type(item) is int for item in value) or value[0] >= value[1]:
                        raise ValueError("Manifest filter groups require non-empty half-open ranges")
            artifacts.append({"output_path": str(output), "output_sha256": sha256(output), "kernel_path": str(kernel), "kernel_sha256": sha256(kernel), "source": list(identity)})
        return {"manifest": {"path": str(manifest), "sha256": sha256(manifest), "records": len(records)}, "records": artifacts}

    def verify_stage_artifacts(self):
        if self.is_experiment:
            return self.verify_manifest() if self.spec["stage"] == "step3" else self.verify_checkpoint_pair()
        artifacts = {}
        for name in self.spec["expected_artifacts"]:
            path = self.root / "output" / name
            if not path.is_file():
                raise FileNotFoundError("Expected artifact missing: " + str(path))
            artifacts[name] = {"path": str(path), "sha256": sha256(path)}
        return artifacts

    def execute(self):
        self.update(step="validate-spec")
        self.validate()
        env = self.environment()
        (self.root / "output").mkdir()
        command, config = self.execution_command(), self.config_command() + ["--cfg", "job", "--resolve"]
        self.update(step="resolve-config")
        self.command(config, env, config=True)
        if (self.root / "resolved-config.yaml").stat().st_size < 100:
            raise ValueError("Resolved configuration is empty")
        self.update(step="execute")
        self.command(command, env)
        self.update(step="verify-artifacts")
        artifacts = self.verify_stage_artifacts()
        write_new(self.root / "artifacts.json", json.dumps(artifacts, indent=2))
        detail = "Validation fixture only; no trained artifact or restoration result" if self.is_validation else "Stage artifacts passed the frozen spec contract"
        self.update(state="SUCCESS", step="completed", exit_code=0, child_process_id=None, detail=detail)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "execute", "direct", "dispatch-failed"])
    parser.add_argument("spec")
    args = parser.parse_args()
    run = None
    try:
        spec, root = load_spec(args.spec)
        if args.action in ("prepare", "direct"):
            root.mkdir(parents=True, exist_ok=False)
            run = Run(spec, root)
            write_new(root / "spec.json", json.dumps(spec, indent=2))
            run.update()
            run.validate()
            run.prepare_metadata()
            if args.action == "prepare":
                run.update(step="awaiting-scheduler", detail="Reserved new run directory; no child process has been started")
                return 0
            if run.is_experiment:
                raise ValueError("pilot/full execution must be started only through start_bdd100k_task.ps1")
        else:
            if Path(args.spec).resolve() != (root / "spec.json").resolve():
                raise ValueError("Execution requires the reserved spec.json")
            if (root / "execution.claim").exists():
                raise FileExistsError("Run already claimed; existing files are untouched")
            status_path = root / 'status.json'
            if status_path.is_file() and json.loads(status_path.read_text(encoding='utf-8')).get('state') in {'SUCCESS', 'FAILED'}:
                raise ValueError('Terminal run is immutable; reserve a new authorized run')
            if args.action == "dispatch-failed":
                run = Run(spec, root)
                run.update(state="FAILED", step="dispatch", detail="Task registration/start failed; see launcher output", exit_code=1)
                return 1
            pending_run = Run(spec, root)
            pending_run.validate()
            # A losing claimant must not mark another process's run FAILED.
            write_new(root / "execution.claim", str(os.getpid()))
            run = pending_run
        if args.action == 'direct':
            write_new(root / "execution.claim", str(os.getpid()))
        run.execute()
        return 0
    except Exception as exc:
        code = exc.returncode if isinstance(exc, subprocess.CalledProcessError) else 1
        if run:
            with (run.root / "task.log").open("a", encoding="utf-8") as fh:
                traceback.print_exc(file=fh)
            run.update(state="FAILED", detail=str(exc), exit_code=code, child_process_id=None)
        traceback.print_exc()
        return code


if __name__ == "__main__":
    sys.exit(main())
