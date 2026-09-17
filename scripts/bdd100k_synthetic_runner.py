"""Fail-closed orchestration for the isolated synthetic BDD100K benchmark.

This module owns reservation and artifact validation only.  The real execution
entry point is intentionally separate from the existing real-data runner.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import pickle
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXPECTED_HOST = "DESKTOP-KBM1345"
FIXED_PYTHON = Path(r"E:\Anaconda3\envs\ddm4ip\python.exe")
PROJECT_ROOT = Path(r"D:\Unsupervised Imaging Inverse Problems")
RUNTIME_ROOT = Path(r"D:\DDM4IP-runtime")
EXPERIMENTS_ROOT = RUNTIME_ROOT / "experiments"
BENCHMARK_ROOT = RUNTIME_ROOT / "synthetic-benchmarks" / "bdd100k-motionblur-v1"
RUNNER_PATH = PROJECT_ROOT / "scripts" / "bdd100k_synthetic_runner.py"

STAGES = {"inventory", "build", "oracle", "step1", "step2", "step3"}
MODES = {"audit", "pilot", "full"}
TOP_LEVEL_FIELDS = {
    "schema_version", "task_name", "stage", "mode", "variant", "seed", "host", "python",
    "benchmark_root", "run_root", "benchmark_summary", "pairs_manifest", "kernel_gt",
    "source_manifest",
    "expected_manifest_records", "benchmark_hashes", "runner_sha256", "predecessor",
    "overrides", "source_manifest_sha256", "view_manifest_sha256", "view_root",
    "reserved_at",
}
ALLOWED_OVERRIDE_FIELDS = {
    "training.seed", "training.batch_size", "training.max_steps", "training.report_every_steps",
    "training.plot_every_steps", "training.save_every_steps", "training.num_workers",
    "training.max_val_batches", "loss.n_accum_steps", "dataset.test.max_imgs",
    "evaluation.expected_records",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def current_runner_sha256() -> str:
    return _sha256(RUNNER_PATH)


def _as_path(value: str | os.PathLike[str]) -> Path:
    return Path(value)


def _resolved(path: Path) -> Path:
    return Path(os.path.abspath(os.path.normpath(str(path))))


def _is_under(path: Path, root: Path) -> bool:
    try:
        _resolved(path).relative_to(_resolved(root))
        return True
    except ValueError:
        return False


def _is_reparse(path: Path) -> bool:
    if not path.exists() and not path.is_symlink():
        return False
    try:
        attrs = path.stat().st_file_attributes
    except AttributeError:
        return path.is_symlink()
    return bool(attrs & 0x400) or path.is_symlink()


def _require_regular(path: Path, label: str) -> None:
    if not path.is_file() or _is_reparse(path):
        raise ValueError(f"{label} must be a regular non-reparse file: {path}")


def _spec_path_and_run_root(spec_or_run_root: Path) -> tuple[Path, Path]:
    """Accept either an external/reserved spec file or its run directory."""
    path = Path(spec_or_run_root)
    if path.is_file():
        return path, path.parent
    return path / "spec.json", path


def _safe_hash(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{label} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{label} must be a SHA-256 hex string") from exc
    return value.lower()


def validate_spec(spec: dict[str, Any], *, current_host: str, current_python: str | os.PathLike[str]) -> None:
    """Validate immutable execution policy before any output directory is made."""
    unknown = set(spec) - TOP_LEVEL_FIELDS
    if unknown:
        raise ValueError(f"unknown spec fields: {sorted(unknown)}")
    if spec.get("schema_version") != 1:
        raise ValueError("unsupported spec schema")
    if current_host != EXPECTED_HOST or spec.get("host") != EXPECTED_HOST:
        raise ValueError("host is not the fixed project host")
    if str(current_python).lower() != str(FIXED_PYTHON).lower() or str(spec.get("python", "")).lower() != str(FIXED_PYTHON).lower():
        raise ValueError("python executable is not the fixed project environment")
    stage = spec.get("stage")
    mode = spec.get("mode")
    variant = spec.get("variant")
    if stage not in STAGES or mode not in MODES:
        raise ValueError("invalid stage or mode")
    if stage == "oracle":
        if variant != "oracle":
            raise ValueError("oracle stage requires the oracle variant")
        if spec.get("seed") is not None or spec.get("predecessor"):
            raise ValueError("oracle stage cannot have a seed or predecessor")
    elif stage == "step3" and variant not in {"oracle", "learned"}:
        raise ValueError("Step 3 requires oracle or learned variant")
    elif stage in {"step1", "step2", "inventory", "build"} and variant is not None:
        raise ValueError("variant is only valid for oracle or Step 3")
    if stage in {"step2", "step3"} and variant != "oracle":
        seed = spec.get("seed")
        if seed not in range(5):
            raise ValueError("learned/Step 2 seed must be in 0..4")
    if stage == "step3" and variant == "oracle" and spec.get("seed") is not None:
        raise ValueError("oracle evaluation cannot have a seed")
    if stage in {"step2"} and not spec.get("predecessor"):
        raise ValueError("Step 2 requires a verified Step 1 predecessor")
    if stage == "step3" and variant == "learned" and not spec.get("predecessor"):
        raise ValueError("learned Step 3 requires a same-seed Step 2 predecessor")
    if stage == "step3" and variant == "oracle" and spec.get("predecessor"):
        raise ValueError("oracle Step 3 cannot have a Step 2 predecessor")
    if stage == "build":
        source_manifest = spec.get("source_manifest")
        source_path = Path(str(source_manifest)) if source_manifest else Path()
        if not source_manifest or not source_path.is_absolute() or not _is_under(source_path, EXPERIMENTS_ROOT):
            raise ValueError("build requires an absolute source_manifest under the experiments root")
        if mode == "audit":
            predecessor = spec.get("predecessor") or {}
            predecessor_root = Path(str(predecessor.get("run_root", "")))
            if not predecessor_root.is_absolute() or not _is_under(predecessor_root, EXPERIMENTS_ROOT):
                raise ValueError("build audit requires a predecessor run root under the experiments root")

    benchmark_root = _as_path(spec.get("benchmark_root", ""))
    run_root = _as_path(spec.get("run_root", ""))
    if _resolved(benchmark_root) != _resolved(BENCHMARK_ROOT):
        raise ValueError("benchmark_root is not the fixed synthetic benchmark root")
    if not _is_under(run_root, EXPERIMENTS_ROOT) or _resolved(run_root) == _resolved(EXPERIMENTS_ROOT):
        raise ValueError("run_root must be a new descendant of the fixed experiments root")
    if ".." in Path(str(run_root)).parts:
        raise ValueError("path traversal is not allowed")
    if _is_reparse(run_root) or _is_reparse(benchmark_root):
        raise ValueError("reparse points are not allowed")
    for key in ("benchmark_summary", "pairs_manifest", "kernel_gt"):
        value = spec.get(key)
        if value is not None and (Path(str(value)).is_absolute() or ".." in Path(str(value)).parts):
            raise ValueError(f"{key} must be a safe relative artifact name")
    hashes = spec.get("benchmark_hashes") or {}
    for key in ("summary", "pairs", "kernel"):
        _safe_hash(hashes.get(key), f"benchmark_hashes.{key}")
    if spec.get("expected_manifest_records") is not None and int(spec["expected_manifest_records"]) <= 0:
        raise ValueError("expected_manifest_records must be positive")
    overrides = spec.get("overrides") or {}
    if not isinstance(overrides, dict) or any(key not in ALLOWED_OVERRIDE_FIELDS for key in overrides):
        raise ValueError("Hydra override is not allowlisted")
    if stage == "oracle" and mode == "pilot":
        if int(spec.get("expected_manifest_records", -1)) != 16:
            raise ValueError("Oracle pilot requires exactly 16 expected manifest records")
        if int(overrides.get("dataset.test.max_imgs", -1)) != 16:
            raise ValueError("Oracle pilot requires dataset.test.max_imgs=16")
        if str(spec.get("pairs_manifest", "")).replace("\\", "/") != "dev-reserve/pairs.jsonl":
            raise ValueError("Oracle pilot requires the frozen dev-reserve pairs manifest")


def reserve_spec(spec: dict[str, Any], *, current_host: str, current_python: str | os.PathLike[str]) -> Path:
    """Reserve a new run root and write its immutable specification."""
    validate_spec(spec, current_host=current_host, current_python=current_python)
    run_root = _as_path(spec["run_root"])
    if run_root.exists():
        raise ValueError(f"run_root already exists: {run_root}")
    if (spec["stage"] == "build" and spec.get("mode") != "audit"
            and _as_path(spec["benchmark_root"]).exists()):
        raise ValueError("build refuses an existing benchmark root")
    run_root.parent.mkdir(parents=True, exist_ok=True)
    run_root.mkdir()
    reserved = dict(spec)
    reserved["runner_sha256"] = current_runner_sha256()
    reserved["reserved_at"] = _now()
    (run_root / "spec.json").write_text(json.dumps(reserved, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (run_root / "environment.json").write_text(json.dumps({
        "host": current_host, "python": str(current_python), "runner_sha256": reserved["runner_sha256"],
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (run_root / "status-history.jsonl").write_text(json.dumps({"status": "RESERVED", "updated_at": _now()}) + "\n", encoding="utf-8")
    (run_root / "status.json").write_text(json.dumps({"status": "RESERVED", "updated_at": _now()}) + "\n", encoding="utf-8")
    (run_root / "task.log").write_text("reserved; execution has not started\n", encoding="utf-8")
    return run_root


def write_inventory_artifacts(run_root: Path, *, expected_source_count: int = 1739) -> dict[str, Any]:
    """Freeze the inventory handoff consumed by the later build stage."""
    run_root = Path(run_root)
    manifest_path = run_root / "source-manifest.csv"
    _require_regular(manifest_path, "inventory source manifest")
    with manifest_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        expected_fields = {
            "source_id", "source_relpath", "size_bytes", "sha256",
            "width", "height", "channels",
        }
        if set(reader.fieldnames or ()) != expected_fields:
            raise ValueError("inventory source manifest has an unexpected header")
        rows = list(reader)
    if len(rows) != expected_source_count:
        raise ValueError(f"expected {expected_source_count} inventory rows, found {len(rows)}")
    source_ids = [row["source_id"] for row in rows]
    source_hashes = [row["sha256"].lower() for row in rows]
    if len(set(source_ids)) != len(source_ids) or len(set(source_hashes)) != len(source_hashes):
        raise ValueError("inventory source IDs and content hashes must be unique")
    source_roots: dict[str, int] = {}
    for row in rows:
        parts = Path(row["source_relpath"]).parts
        if len(parts) < 2 or parts[0] not in {"train", "val"}:
            raise ValueError("inventory source path must start with train or val")
        source_roots[parts[0]] = source_roots.get(parts[0], 0) + 1
        if (int(row["width"]), int(row["height"]), int(row["channels"])) != (1280, 720, 3):
            raise ValueError("inventory sources must all be 1280x720 RGB")
    return {
        "stage": "inventory",
        "source_manifest": {
            "path": str(manifest_path),
            "sha256": _sha256(manifest_path),
            "records": len(rows),
            "unique_source_ids": len(set(source_ids)),
            "unique_source_sha256": len(set(source_hashes)),
            "source_roots": dict(sorted(source_roots.items())),
        },
    }


def _safe_benchmark_file(benchmark_root: Path, relative: str, label: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{label} must be a safe relative benchmark path")
    resolved = benchmark_root / path
    _require_regular(resolved, label)
    return resolved


def write_build_artifacts(run_root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    """Freeze build inputs and outputs without modifying the benchmark root."""
    run_root = Path(run_root)
    run_root.mkdir(parents=True, exist_ok=True)
    artifacts_path = run_root / "artifacts.json"
    if artifacts_path.exists():
        raise FileExistsError(f"build artifacts already exist: {artifacts_path}")

    benchmark_root = Path(spec["benchmark_root"])
    if not benchmark_root.is_dir() or _is_reparse(benchmark_root):
        raise ValueError(f"benchmark root is not a regular directory: {benchmark_root}")
    source_manifest = Path(spec["source_manifest"])
    _require_regular(source_manifest, "build source manifest")
    source_manifest_sha256 = _sha256(source_manifest)
    expected_source_manifest_sha256 = _safe_hash(
        spec.get("source_manifest_sha256"), "source_manifest_sha256"
    )
    if source_manifest_sha256 != expected_source_manifest_sha256:
        raise ValueError("build source manifest hash mismatch")

    benchmark_source_manifest = _safe_benchmark_file(
        benchmark_root, "source-manifest.csv", "benchmark source manifest"
    )
    if _sha256(benchmark_source_manifest) != source_manifest_sha256:
        raise ValueError("benchmark source manifest differs from inventory handoff")
    with source_manifest.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        expected_fields = {
            "source_id", "source_relpath", "size_bytes", "sha256",
            "width", "height", "channels",
        }
        if set(reader.fieldnames or ()) != expected_fields:
            raise ValueError("build source manifest has an unexpected header")
        rows = list(reader)
    source_ids = [row["source_id"] for row in rows]
    source_hashes = [row["sha256"].lower() for row in rows]
    if len(set(source_ids)) != len(source_ids) or len(set(source_hashes)) != len(source_hashes):
        raise ValueError("build source manifest IDs and hashes must be unique")
    source_roots: dict[str, int] = {}
    for row in rows:
        parts = Path(row["source_relpath"]).parts
        if len(parts) < 2 or parts[0] not in {"train", "val"}:
            raise ValueError("build source manifest path must start with train or val")
        if (int(row["width"]), int(row["height"]), int(row["channels"])) != (1280, 720, 3):
            raise ValueError("build source manifest must contain 1280x720 RGB sources")
        source_roots[parts[0]] = source_roots.get(parts[0], 0) + 1

    summary_rel = spec.get("benchmark_summary") or "summary.json"
    pairs_rel = spec.get("pairs_manifest") or "test-paired/pairs.jsonl"
    kernel_rel = spec.get("kernel_gt") or "degradation/kernel-gt.pt"
    summary_path = _safe_benchmark_file(benchmark_root, summary_rel, "benchmark summary")
    pairs_path = _safe_benchmark_file(benchmark_root, pairs_rel, "benchmark pairs manifest")
    kernel_path = _safe_benchmark_file(benchmark_root, kernel_rel, "benchmark kernel")
    split_path = _safe_benchmark_file(benchmark_root, "split-manifest.csv", "benchmark split manifest")
    preprocessing_path = _safe_benchmark_file(
        benchmark_root, "preprocessing.json", "benchmark preprocessing"
    )
    degradation_path = _safe_benchmark_file(
        benchmark_root, "degradation/degradation.json", "benchmark degradation"
    )
    status_path = _safe_benchmark_file(benchmark_root, "status.json", "benchmark status")
    status = _load_json(status_path)
    if status.get("status") != "SUCCESS":
        raise ValueError("benchmark status is not SUCCESS")
    summary = _load_json(summary_path)
    if summary.get("source_manifest_sha256", "").lower() != source_manifest_sha256:
        raise ValueError("benchmark summary source manifest hash mismatch")
    counts = summary.get("counts")
    if not isinstance(counts, dict) or sum(int(value) for value in counts.values()) != len(rows):
        raise ValueError("benchmark summary counts do not match the source manifest")

    files = {
        "source-manifest.csv": _sha256(benchmark_source_manifest),
        "split-manifest.csv": _sha256(split_path),
        str(pairs_rel).replace("\\", "/"): _sha256(pairs_path),
        "preprocessing.json": _sha256(preprocessing_path),
        "degradation/degradation.json": _sha256(degradation_path),
        str(kernel_rel).replace("\\", "/"): _sha256(kernel_path),
        str(summary_rel).replace("\\", "/"): _sha256(summary_path),
        "status.json": _sha256(status_path),
    }
    claimed_hashes = spec.get("benchmark_hashes") or {}
    for claim_key, relative_key in (
        ("summary", str(summary_rel).replace("\\", "/")),
        ("pairs", str(pairs_rel).replace("\\", "/")),
        ("kernel", str(kernel_rel).replace("\\", "/")),
    ):
        claimed = claimed_hashes.get(claim_key)
        if isinstance(claimed, str) and set(claimed.lower()) != {"0"}:
            if claimed.lower() != files[relative_key]:
                raise ValueError(f"benchmark hash mismatch: {claim_key}")

    artifacts = {
        "stage": "build",
        "mode": spec.get("mode"),
        "source_build_run_root": str(
            (spec.get("predecessor") or {}).get("run_root", run_root)
        ),
        "source_manifest": {
            "path": str(source_manifest),
            "sha256": source_manifest_sha256,
            "records": len(rows),
            "unique_source_ids": len(set(source_ids)),
            "unique_source_sha256": len(set(source_hashes)),
            "source_roots": dict(sorted(source_roots.items())),
        },
        "benchmark": {
            "root": str(benchmark_root),
            "status": status,
            "summary": {
                "path": str(summary_path),
                "sha256": files[str(summary_rel).replace("\\", "/")],
                "counts": counts,
            },
            "files": files,
            "hashes": {
                "source_manifest_sha256": files["source-manifest.csv"],
                "split_manifest_sha256": files["split-manifest.csv"],
                "pairs_manifest_sha256": files[str(pairs_rel).replace("\\", "/")],
                "preprocessing_sha256": files["preprocessing.json"],
                "degradation_sha256": files["degradation/degradation.json"],
                "kernel_file_sha256": files[str(kernel_rel).replace("\\", "/")],
            },
        },
    }
    artifacts_path.write_text(
        json.dumps(artifacts, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return artifacts


def record_execution_status(run_root: Path, spec: dict[str, Any], status: str, **extra: Any) -> None:
    if status not in {"RUNNING", "SUCCESS", "FAILED"}:
        raise ValueError(f"invalid execution status: {status}")
    run_root = Path(run_root)
    payload = {
        "status": status,
        "updated_at": _now(),
        "host": spec.get("host"),
        "python": spec.get("python"),
        "repository": str(PROJECT_ROOT),
        "run_root": str(run_root),
        "log_path": str(run_root / "task.log"),
        **extra,
    }
    with (run_root / "status-history.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")
    (run_root / "status.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def append_task_log(run_root: Path, message: str) -> None:
    with (Path(run_root) / "task.log").open("a", encoding="utf-8") as handle:
        handle.write(message.rstrip("\n") + "\n")


def execute_reserved(spec_or_run_root: Path, *, current_runner_sha256: str) -> dict[str, Any]:
    """Load a reservation and refuse stale or absent runner state."""
    spec_path, run_root = _spec_path_and_run_root(spec_or_run_root)
    if not spec_path.is_file():
        raise FileNotFoundError(f"reserved spec is missing: {spec_path}")
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if _resolved(Path(spec.get("run_root", ""))) != _resolved(run_root):
        raise ValueError("reserved spec run_root does not match its directory")
    if spec.get("runner_sha256") != current_runner_sha256:
        raise ValueError("runner SHA-256 differs from the reserved spec")
    claim = run_root / "execution.claim"
    if claim.exists():
        raise FileExistsError(f"execution claim already exists: {claim}")
    claim.write_text(json.dumps({"claimed_at": _now(), "runner_sha256": current_runner_sha256}) + "\n", encoding="utf-8")
    return spec


def command_for(stage: str, variant: str | None = None) -> str:
    mapping = {
        ("step1", None): "exp=step1_bdd100k_synthetic",
        ("step2", None): "exp=step2_bdd100k_synthetic",
        ("oracle", "oracle"): "exp=step3_bdd100k_oracle",
        ("step3", "oracle"): "exp=step3_bdd100k_oracle",
        ("step3", "learned"): "exp=step3_bdd100k_synthetic",
    }
    try:
        return mapping[(stage, variant)]
    except KeyError as exc:
        raise ValueError(f"no command mapping for {stage}/{variant}") from exc


def _slash(path: str | os.PathLike[str]) -> str:
    return str(path).replace("\\", "/")


def child_process_environment() -> dict[str, str]:
    """Give Python child stages an import path rooted at the repository."""
    env = os.environ.copy()
    project_root = str(PROJECT_ROOT)
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = project_root if not existing else os.pathsep.join((project_root, existing))
    return env


def build_hydra_overrides(
    spec: dict[str, Any], *, flow_checkpoint: str | None = None, kernel_snapshot: str | None = None
) -> list[str]:
    """Build only the fixed/allowlisted Hydra overrides for a reserved spec."""
    validate_spec(spec, current_host=EXPECTED_HOST, current_python=FIXED_PYTHON)
    overrides = [command_for(spec["stage"], spec.get("variant")), "paths=bdd100k_synthetic_runtime"]
    for key, value in sorted((spec.get("overrides") or {}).items()):
        if key not in ALLOWED_OVERRIDE_FIELDS:
            raise ValueError(f"Hydra override is not allowlisted: {key}")
        overrides.append(f"{key}={value}")
    if spec["stage"] == "oracle" and spec.get("mode") == "pilot":
        overrides.extend([
            "dataset.test.pairs_role=dev_reserve",
            "dataset.test.pairs_dir=dev-reserve",
        ])
    if spec["stage"] == "step2":
        if not flow_checkpoint:
            raise ValueError("Step 2 requires the verified flow checkpoint")
        overrides.append(f"models.pretrained_flow.path={_slash(flow_checkpoint)}")
    if spec["stage"] == "step3" and spec.get("variant") == "learned":
        if not kernel_snapshot:
            raise ValueError("learned Step 3 requires the verified same-seed kernel snapshot")
        overrides.append(f"models.kernel.path={_slash(kernel_snapshot)}")
    if spec["stage"] in {"oracle", "step3"}:
        overrides.extend([
            f"evaluation.expected_records={int(spec['expected_manifest_records'])}",
            f"evaluation.kernel_gt_path={_slash(Path(spec['benchmark_root']) / spec['kernel_gt'])}",
            f"evaluation.kernel_gt_sha256={spec['benchmark_hashes']['kernel']}",
            f"evaluation.pairs_manifest_sha256={spec['benchmark_hashes']['pairs']}",
            f"evaluation.benchmark_summary_sha256={spec['benchmark_hashes']['summary']}",
        ])
        if spec["stage"] == "step3" and spec.get("variant") == "learned":
            overrides.append(f"evaluation.step2_seed={int(spec['seed'])}")
    return overrides


def stage_command(
    spec: dict[str, Any], *, flow_checkpoint: str | None = None, kernel_snapshot: str | None = None
) -> list[str]:
    """Return the immutable child command for any supported stage."""
    validate_spec(spec, current_host=EXPECTED_HOST, current_python=FIXED_PYTHON)
    run_root = Path(spec["run_root"])
    if spec["stage"] == "inventory":
        view_root = spec.get("view_root")
        if not view_root or not spec.get("view_manifest_sha256"):
            raise ValueError("inventory requires view_root and view_manifest_sha256")
        return [
            str(FIXED_PYTHON), str(PROJECT_ROOT / "scripts" / "build_bdd100k_synthetic_benchmark.py"),
            "inspect", "--view-root", str(view_root),
            "--expected-view-manifest-sha256", str(spec["view_manifest_sha256"]),
            "--expected-source-count", "1739",
            "--output-manifest", str(run_root / "source-manifest.csv"),
        ]
    if spec["stage"] == "build":
        if spec.get("mode") == "audit":
            return ["provenance-audit", str(BENCHMARK_ROOT)]
        view_root = spec.get("view_root")
        source_manifest = spec.get("source_manifest")
        if not view_root or not spec.get("source_manifest_sha256") or not source_manifest:
            raise ValueError("build requires view_root, source_manifest, and source_manifest_sha256")
        return [
            str(FIXED_PYTHON), str(PROJECT_ROOT / "scripts" / "build_bdd100k_synthetic_benchmark.py"),
            "build", "--view-root", str(view_root),
            "--source-manifest", str(source_manifest),
            "--expected-source-manifest-sha256", str(spec["source_manifest_sha256"]),
            "--destination", str(BENCHMARK_ROOT),
        ]
    hydra_overrides = build_hydra_overrides(
        spec, flow_checkpoint=flow_checkpoint, kernel_snapshot=kernel_snapshot
    )
    run_root = Path(spec["run_root"])
    hydra_overrides.extend([
        f"training.log_dir={_slash(run_root.parent)}",
        f"exp_name={run_root.name}",
        f"hydra.run.dir={_slash(run_root)}",
    ])
    return [str(FIXED_PYTHON), "-m", "ddm4ip.main", *hydra_overrides]


def _recursive_find(payload: Any, key: str) -> Any:
    if isinstance(payload, dict):
        if key in payload:
            return payload[key]
        for value in payload.values():
            found = _recursive_find(value, key)
            if found is not None:
                return found
    elif isinstance(payload, (list, tuple)):
        for value in payload:
            found = _recursive_find(value, key)
            if found is not None:
                return found
    return None


def _load_pickle_with_project_path(path: Path) -> Any:
    """Load a legacy snapshot with a temporary repository import path."""
    original_sys_path = list(sys.path)
    project_root = str(PROJECT_ROOT)
    try:
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        with Path(path).open("rb") as handle:
            return pickle.load(handle)
    finally:
        sys.path[:] = original_sys_path


def verify_checkpoint_pair(pt_path: Path, pkl_path: Path, *, expected_step: int, model_key: str) -> None:
    pt_path = Path(pt_path)
    pkl_path = Path(pkl_path)
    if pt_path.name != f"training-state-{expected_step}.pt" or pkl_path.name != f"network-snapshot-{expected_step}.pkl":
        raise ValueError("checkpoint filenames do not match the expected terminal step")
    _require_regular(pt_path, "training-state")
    _require_regular(pkl_path, "network snapshot")
    import torch

    if model_key not in {"flow_nn", "kernel_nn"}:
        raise ValueError("unsupported checkpoint model key")
    pt = torch.load(pt_path, map_location="cpu", weights_only=False)
    pkl = _load_pickle_with_project_path(pkl_path)
    pt_global_step = _recursive_find(pt, "global_step")
    pkl_global_step = _recursive_find(pkl, "global_step")
    if pt_global_step is None or int(pt_global_step) != expected_step:
        raise ValueError("training-state internal step mismatch")
    if pkl_global_step is None or int(pkl_global_step) != expected_step + 1:
        raise ValueError("network snapshot internal step mismatch")
    if _recursive_find(pt, model_key) is None:
        raise ValueError(f"training-state is missing {model_key}")
    if _recursive_find(pkl, model_key) is None:
        raise ValueError(f"network snapshot is missing {model_key}")


def _safe_relative_checkpoint(value: Any, label: str) -> Path:
    path = Path(str(value))
    if not str(value) or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{label} must be a safe relative path")
    return path


def resolve_and_verify_predecessor(spec: dict[str, Any]) -> dict[str, str | None]:
    """Resolve the only predecessor allowed by the current stage contract."""
    stage = spec.get("stage")
    if stage == "step2":
        expected_stage, expected_model = "step1", "flow_nn"
        expected_seed = None
    elif stage == "step3" and spec.get("variant") == "learned":
        expected_stage, expected_model = "step2", "kernel_nn"
        expected_seed = spec.get("seed")
    else:
        return {"flow_checkpoint": None, "kernel_snapshot": None}

    predecessor = spec.get("predecessor")
    required = {
        "stage", "run_root", "expected_step", "training_state", "training_state_sha256",
        "network_snapshot", "network_snapshot_sha256", "seed",
    }
    if not isinstance(predecessor, dict) or set(predecessor) != required:
        raise ValueError("predecessor does not match the frozen schema")
    if predecessor["stage"] != expected_stage or predecessor["seed"] != expected_seed:
        raise ValueError("predecessor stage or seed does not match the requested stage")
    predecessor_root = Path(str(predecessor["run_root"]))
    if not predecessor_root.is_absolute() or not _is_under(predecessor_root, EXPERIMENTS_ROOT):
        raise ValueError("predecessor run_root must be under the experiments root")
    if _resolved(predecessor_root) == _resolved(EXPERIMENTS_ROOT) or not predecessor_root.is_dir():
        raise ValueError("predecessor run_root must be an existing directory")
    try:
        expected_step = int(predecessor["expected_step"])
    except (TypeError, ValueError) as exc:
        raise ValueError("predecessor expected_step must be an integer") from exc
    if expected_step <= 0:
        raise ValueError("predecessor expected_step must be positive")
    training_state = _safe_relative_checkpoint(predecessor["training_state"], "training_state")
    network_snapshot = _safe_relative_checkpoint(predecessor["network_snapshot"], "network_snapshot")
    pt_path = predecessor_root / training_state
    pkl_path = predecessor_root / network_snapshot
    if pt_path.name != f"training-state-{expected_step}.pt" or pkl_path.name != f"network-snapshot-{expected_step}.pkl":
        raise ValueError("predecessor checkpoint filenames do not match expected_step")
    _require_regular(pt_path, "predecessor training-state")
    _require_regular(pkl_path, "predecessor network snapshot")
    if _sha256(pt_path) != _safe_hash(predecessor["training_state_sha256"], "training_state_sha256"):
        raise ValueError("predecessor training-state SHA-256 mismatch")
    if _sha256(pkl_path) != _safe_hash(predecessor["network_snapshot_sha256"], "network_snapshot_sha256"):
        raise ValueError("predecessor network snapshot SHA-256 mismatch")
    verify_checkpoint_pair(pt_path, pkl_path, expected_step=expected_step, model_key=expected_model)
    if expected_model == "flow_nn":
        return {"flow_checkpoint": str(pt_path), "kernel_snapshot": None}
    return {"flow_checkpoint": None, "kernel_snapshot": str(pkl_path)}


def _finite_numbers(payload: Any) -> None:
    if isinstance(payload, dict):
        for value in payload.values():
            _finite_numbers(value)
    elif isinstance(payload, (list, tuple)):
        for value in payload:
            _finite_numbers(value)
    elif isinstance(payload, (int, float)) and not isinstance(payload, bool):
        if not math.isfinite(float(payload)):
            raise ValueError("non-finite metric")


def _source_set_sha256(source_ids: set[str]) -> str:
    return hashlib.sha256("\n".join(sorted(source_ids)).encode("utf-8")).hexdigest()


def preflight_benchmark_artifacts(spec: dict[str, Any]) -> dict[str, str]:
    """Verify immutable benchmark inputs immediately before a child starts."""
    validate_spec(spec, current_host=EXPECTED_HOST, current_python=FIXED_PYTHON)
    benchmark_root = Path(spec["benchmark_root"])
    paths = {
        "benchmark_summary_sha256": _safe_benchmark_file(
            benchmark_root, str(spec["benchmark_summary"]), "benchmark summary"
        ),
        "pairs_manifest_sha256": _safe_benchmark_file(
            benchmark_root, str(spec["pairs_manifest"]), "benchmark pairs manifest"
        ),
        "kernel_gt_sha256": _safe_benchmark_file(
            benchmark_root, str(spec["kernel_gt"]), "benchmark kernel"
        ),
    }
    claimed = {
        "benchmark_summary_sha256": _safe_hash(spec["benchmark_hashes"]["summary"], "benchmark_hashes.summary"),
        "pairs_manifest_sha256": _safe_hash(spec["benchmark_hashes"]["pairs"], "benchmark_hashes.pairs"),
        "kernel_gt_sha256": _safe_hash(spec["benchmark_hashes"]["kernel"], "benchmark_hashes.kernel"),
    }
    actual: dict[str, str] = {}
    for key, path in paths.items():
        actual[key] = _sha256(path)
        if actual[key] != claimed[key]:
            raise ValueError(f"benchmark preflight hash mismatch: {key}")
    return actual


def verify_evaluation_artifacts(
    run_root: Path, *, expected_manifest_records: int, expected_hashes: dict[str, str], oracle: bool = False
) -> None:
    run_root = Path(run_root)
    output_dir = run_root / "plots"
    manifest_path = output_dir / "manifest.jsonl"
    metrics_path = output_dir / "metrics.jsonl"
    summary_path = output_dir / "summary.json"
    for path in (manifest_path, metrics_path, summary_path):
        _require_regular(path, path.name)
    manifest = [json.loads(line) for line in manifest_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    metrics = [json.loads(line) for line in metrics_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(manifest) != expected_manifest_records or len(metrics) != expected_manifest_records:
        raise ValueError("evaluation record count mismatch")
    source_ids = [row.get("source_id") for row in manifest]
    if any(not isinstance(source_id, str) for source_id in source_ids) or len(set(source_ids)) != len(source_ids):
        raise ValueError("source IDs must be unique")
    metric_by_source = {row.get("source_id"): row for row in metrics}
    if len(metric_by_source) != expected_manifest_records or set(metric_by_source) != set(source_ids):
        raise ValueError("manifest and metrics source sets differ")
    required_row_fields = {
        "prediction_path", "prediction_sha256", "kernel_path", "kernel_sha256",
        "kernel_gt_sha256", "pairs_manifest_sha256", "benchmark_summary_sha256",
        "solver_config_sha256", "input_metrics", "restored_metrics",
    }
    _finite_numbers(metrics)
    for row in manifest:
        if not required_row_fields.issubset(row):
            raise ValueError("evaluation row is missing the unified schema")
        for key, expected in expected_hashes.items():
            if str(row.get(key, "")).lower() != str(expected).lower():
                raise ValueError(f"evaluation hash mismatch: {key}")
        metric_row = metric_by_source[row["source_id"]]
        comparable_manifest_row = dict(row)
        comparable_manifest_row.pop("schema_version", None)
        if metric_row != comparable_manifest_row:
            raise ValueError("manifest and metrics rows differ")
        prediction_name = Path(str(row["prediction_path"]))
        kernel_name = Path(str(row["kernel_path"]))
        if prediction_name.name != str(prediction_name) or kernel_name.name != str(kernel_name):
            raise ValueError("evaluation artifact paths must be local basenames")
        prediction = output_dir / prediction_name
        kernel = output_dir / kernel_name
        _require_regular(prediction, "prediction")
        _require_regular(kernel, "kernel")
        if row["prediction_sha256"].lower() != _sha256(prediction):
            raise ValueError("prediction hash mismatch")
        if row["kernel_sha256"].lower() != _sha256(kernel):
            raise ValueError("kernel hash mismatch")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    _finite_numbers(summary)
    required_summary_fields = {
        "records", "failures", "source_set_sha256", "pairs_manifest_sha256",
        "benchmark_summary_sha256", "kernel_gt_sha256", "solver_config_sha256",
        "statistics", "mean", "manifest_jsonl_sha256", "metrics_jsonl_sha256",
    }
    if not required_summary_fields.issubset(summary):
        raise ValueError("summary is missing the unified schema")
    if int(summary["records"]) != expected_manifest_records or int(summary["failures"]) != 0:
        raise ValueError("summary record count mismatch")
    for key, expected in expected_hashes.items():
        if str(summary[key]).lower() != str(expected).lower():
            raise ValueError(f"summary hash mismatch: {key}")
    if summary["source_set_sha256"] != _source_set_sha256(set(source_ids)):
        raise ValueError("summary source set hash mismatch")
    if summary["solver_config_sha256"] != manifest[0]["solver_config_sha256"]:
        raise ValueError("solver config hash mismatch")
    if _sha256(manifest_path) != summary["manifest_jsonl_sha256"]:
        raise ValueError("manifest JSONL hash mismatch")
    if _sha256(metrics_path) != summary["metrics_jsonl_sha256"]:
        raise ValueError("metrics JSONL hash mismatch")
    for metric_name in (
        "input_psnr", "input_ssim", "input_lpips",
        "restored_psnr", "restored_ssim", "restored_lpips",
    ):
        prefix, name = metric_name.split("_", 1)
        values = [float(row[f"{prefix}_metrics"][name]) for row in metrics]
        expected_mean = math.fsum(values) / len(values)
        if not math.isclose(float(summary["mean"][metric_name]), expected_mean, rel_tol=1e-9, abs_tol=1e-9):
            raise ValueError(f"summary mean mismatch: {metric_name}")
    if oracle:
        means = summary["mean"]
        if not (means["restored_psnr"] > means["input_psnr"]
                and means["restored_ssim"] > means["input_ssim"]
                and means["restored_lpips"] < means["input_lpips"]):
            raise ValueError("oracle improvement direction failed")


def postflight_stage_artifacts(spec: dict[str, Any], run_root: Path) -> None:
    if spec["stage"] not in {"oracle", "step3"}:
        return
    verify_evaluation_artifacts(
        run_root,
        expected_manifest_records=int(spec["expected_manifest_records"]),
        expected_hashes={
            "pairs_manifest_sha256": spec["benchmark_hashes"]["pairs"],
            "benchmark_summary_sha256": spec["benchmark_hashes"]["summary"],
            "kernel_gt_sha256": spec["benchmark_hashes"]["kernel"],
        },
        oracle=spec["stage"] == "oracle" or spec.get("variant") == "oracle",
    )


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "execute", "dispatch-failed"))
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--current-host", default=os.environ.get("COMPUTERNAME", ""))
    parser.add_argument("--current-python", default=str(FIXED_PYTHON))
    args = parser.parse_args(argv)
    if args.action == "prepare":
        reserve_spec(_load_json(args.spec), current_host=args.current_host, current_python=args.current_python)
        return 0
    if args.action == "dispatch-failed":
        _, run_root = _spec_path_and_run_root(args.spec)
        (run_root / "status.json").write_text(json.dumps({"status": "FAILED", "updated_at": _now()}) + "\n", encoding="utf-8")
        return 0
    spec = execute_reserved(args.spec, current_runner_sha256=current_runner_sha256())
    _, run_root = _spec_path_and_run_root(args.spec)
    record_execution_status(
        run_root, spec, "RUNNING", stage=spec["stage"], mode=spec["mode"]
    )
    append_task_log(run_root, "execution started; preflight pending")
    try:
        if spec["stage"] in {"oracle", "step1", "step2", "step3"}:
            preflight_benchmark_artifacts(spec)
        predecessor = {}
        if spec["stage"] == "step2" or (
            spec["stage"] == "step3" and spec.get("variant") == "learned"
        ):
            predecessor = resolve_and_verify_predecessor(spec)
        command = stage_command(spec, **predecessor)
        (run_root / "command.json").write_text(
            json.dumps(command, indent=2) + "\n", encoding="utf-8"
        )
        append_task_log(run_root, f"child command: {json.dumps(command)}")
        if spec["stage"] == "build" and spec.get("mode") == "audit":
            write_build_artifacts(run_root, spec)
            returncode = 0
        else:
            with (run_root / "task.log").open("a", encoding="utf-8") as log_handle:
                result = subprocess.run(
                    command,
                    cwd=PROJECT_ROOT,
                    env=child_process_environment(),
                    stdout=log_handle,
                    stderr=subprocess.STDOUT,
                    text=True,
                    check=False,
                )
            returncode = result.returncode
            if returncode == 0 and spec["stage"] == "inventory":
                artifacts = write_inventory_artifacts(run_root)
                (run_root / "artifacts.json").write_text(
                    json.dumps(artifacts, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
            if returncode == 0 and spec["stage"] == "build":
                write_build_artifacts(run_root, spec)
            if returncode == 0:
                postflight_stage_artifacts(spec, run_root)
    except Exception as exc:
        append_task_log(run_root, f"execution failed: {type(exc).__name__}: {exc}")
        record_execution_status(
            run_root,
            spec,
            "FAILED",
            exit_code=1,
            error=f"{type(exc).__name__}: {exc}",
        )
        return 1
    status = "SUCCESS" if returncode == 0 else "FAILED"
    append_task_log(run_root, f"execution finished: status={status} exit_code={returncode}")
    record_execution_status(run_root, spec, status, exit_code=returncode)
    return returncode


if __name__ == "__main__":
    raise SystemExit(main())
