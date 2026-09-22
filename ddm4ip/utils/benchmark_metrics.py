from __future__ import annotations

import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any, Mapping

import torch

from ddm4ip.utils.metrics import calc_ncc, calc_psnr, calc_ssim
from ddm4ip.utils.torch_utils import equate_kernel_shapes


IMAGE_METRICS = ("psnr", "ssim", "lpips")
SUMMARY_METRICS = tuple(
    f"{prefix}_{metric}"
    for prefix in ("input", "restored")
    for metric in IMAGE_METRICS
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{label} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{label} must be a SHA-256 hex string") from exc
    return value.lower()


def _scalar(value):
    if isinstance(value, torch.Tensor):
        if value.numel() != 1:
            raise ValueError("metadata or metric value must be scalar")
        return value.detach().cpu().item()
    if isinstance(value, (list, tuple)) and len(value) == 1:
        return _scalar(value[0])
    return value


def _finite_mapping(value: Mapping[str, float]) -> dict[str, float]:
    output = {}
    for key, raw in value.items():
        number = float(_scalar(raw))
        if not math.isfinite(number):
            raise ValueError(f"metric {key} is not finite")
        output[str(key)] = number
    return output


def _finite_payload(value: Any) -> None:
    if isinstance(value, dict):
        for child in value.values():
            _finite_payload(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _finite_payload(child)
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        if not math.isfinite(float(value)):
            raise ValueError("payload contains a non-finite number")


def compute_image_metrics(reference: torch.Tensor, estimate: torch.Tensor, lpips_model) -> dict[str, float]:
    if reference.ndim == 4 or estimate.ndim == 4:
        if reference.ndim != 4 or estimate.ndim != 4 or reference.shape[0] != 1 or estimate.shape[0] != 1:
            raise ValueError("compute_image_metrics accepts one image, not a batch")
        reference = reference[0]
        estimate = estimate[0]
    if reference.ndim != 3 or estimate.ndim != 3 or reference.shape != estimate.shape:
        raise ValueError("reference and estimate must have equal CHW image shapes")
    if not torch.isfinite(reference).all() or not torch.isfinite(estimate).all():
        raise ValueError('image metrics require finite pixels before clamping')
    reference = reference.detach().cpu().float().clamp(0, 1)
    estimate = estimate.detach().cpu().float().clamp(0, 1)
    try:
        lpips_device = next(lpips_model.parameters()).device
    except (AttributeError, StopIteration):
        lpips_device = reference.device
    lpips_value = lpips_model(
        reference.to(lpips_device).unsqueeze(0), estimate.to(lpips_device).unsqueeze(0)
    )
    result = _finite_mapping({
        "psnr": calc_psnr(reference, estimate),
        "ssim": calc_ssim(reference, estimate),
        "lpips": lpips_value,
    })
    if result["psnr"] < 0:
        raise ValueError("PSNR must be finite and nonnegative for normalized images")
    return result


def compute_kernel_metrics(estimated: torch.Tensor, truth: torch.Tensor) -> dict[str, float]:
    estimated, truth = equate_kernel_shapes(estimated, truth)
    estimated = estimated.detach().cpu().float()
    truth = truth.detach().cpu().float()
    mse = torch.mean((estimated - truth) ** 2)
    kernel_psnr = float((10 * torch.log10(1.0 / (mse + 1e-8))).item())
    kernel_ncc = float(_scalar(calc_ncc(estimated, truth)))
    if not math.isfinite(kernel_psnr) or not math.isfinite(kernel_ncc):
        raise ValueError("kernel metrics must be finite")
    return {"kernel_psnr": kernel_psnr, "kernel_ncc": kernel_ncc}


def canonical_json_sha256(value: Mapping[str, object]) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _source_set_sha256(source_ids: set[str]) -> str:
    return hashlib.sha256("\n".join(sorted(source_ids)).encode("utf-8")).hexdigest()


class BenchmarkMetricWriter:
    def __init__(
        self,
        output_dir: Path,
        experiment_id: str,
        variant: str,
        step2_seed: int | None,
        solver_config_sha256: str,
        kernel_gt_path: Path,
        expected_count: int,
        *,
        pairs_manifest_sha256: str,
        benchmark_summary_sha256: str,
        predecessor_network_snapshot_sha256: str | None = None,
    ):
        self.output_dir = Path(output_dir)
        if self.output_dir.exists() and any(self.output_dir.iterdir()):
            raise FileExistsError(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_path = self.output_dir / "metrics.jsonl"
        self.manifest_path = self.output_dir / "manifest.jsonl"
        self.summary_path = self.output_dir / "summary.json"
        self.experiment_id = experiment_id
        self.variant = variant
        self.step2_seed = step2_seed
        if variant == "oracle" and step2_seed is not None:
            raise ValueError("oracle records cannot carry a Step 2 seed")
        if variant == "learned" and step2_seed not in {0, 1, 2, 3, 4}:
            raise ValueError("learned records require a Step 2 seed in 0..4")
        if variant not in {"oracle", "learned"}:
            raise ValueError("variant must be oracle or learned")
        if variant == "oracle":
            if predecessor_network_snapshot_sha256 is not None:
                raise ValueError("oracle records cannot carry a predecessor snapshot hash")
            self.predecessor_network_snapshot_sha256 = None
        else:
            self.predecessor_network_snapshot_sha256 = _safe_sha(
                predecessor_network_snapshot_sha256,
                "predecessor_network_snapshot_sha256",
            )
        self.solver_config_sha256 = _safe_sha(solver_config_sha256, "solver_config_sha256")
        self.kernel_gt_path = Path(kernel_gt_path)
        if not self.kernel_gt_path.is_file():
            raise ValueError(f"true kernel file is missing: {self.kernel_gt_path}")
        self.kernel_gt_sha256 = _sha256(self.kernel_gt_path)
        self.pairs_manifest_sha256 = _safe_sha(pairs_manifest_sha256, "pairs_manifest_sha256")
        self.benchmark_summary_sha256 = _safe_sha(benchmark_summary_sha256, "benchmark_summary_sha256")
        self.expected_count = int(expected_count)
        if self.expected_count <= 0:
            raise ValueError("expected_count must be positive")
        self.rows: list[dict[str, Any]] = []
        self.source_ids: set[str] = set()

    def prepare_record(
        self,
        batch_meta: Mapping[str, object],
        prediction: torch.Tensor,
        filters: torch.Tensor,
        prediction_name: str,
        kernel_name: str,
        solver_geometry: Mapping[str, object],
        input_metrics: Mapping[str, float],
        restored_metrics: Mapping[str, float],
        *,
        prediction_sha256: str | None = None,
        kernel_sha256: str | None = None,
    ) -> str:
        source_id = _scalar(batch_meta.get("source_id"))
        if not isinstance(source_id, str) or not source_id:
            raise ValueError("batch metadata must include one source_id")
        if Path(source_id).name != source_id or source_id in self.source_ids:
            raise ValueError("source_id must be a unique safe basename")
        prediction_name = Path(prediction_name).name
        kernel_name = Path(kernel_name).name
        if prediction_name != str(prediction_name) or kernel_name != str(kernel_name):
            raise ValueError("prediction and kernel names must be basenames")
        pred = prediction[0] if prediction.ndim == 4 and prediction.shape[0] == 1 else prediction
        if pred.ndim != 3:
            raise ValueError("prediction must contain exactly one CHW image")

        required_metadata = (
            "source_relpath", "source_sha256", "clean_path", "noisy_path",
            "clean_sha256", "noisy_sha256",
        )
        metadata = {key: _scalar(batch_meta.get(key)) for key in required_metadata}
        if any(not isinstance(metadata[key], str) or not metadata[key] for key in required_metadata):
            raise ValueError("complete source and paired-image metadata is required")
        for key in ("source_sha256", "clean_sha256", "noisy_sha256"):
            _safe_sha(metadata[key], key)
        prediction_sha256 = _safe_sha(
            prediction_sha256 or _scalar(batch_meta.get("prediction_sha256")),
            "prediction_sha256",
        )
        kernel_sha256 = _safe_sha(
            kernel_sha256 or _scalar(batch_meta.get("kernel_sha256")),
            "kernel_sha256",
        )
        input_metrics = _finite_mapping(input_metrics)
        restored_metrics = _finite_mapping(restored_metrics)
        if set(input_metrics) != set(IMAGE_METRICS) or set(restored_metrics) != set(IMAGE_METRICS):
            raise ValueError("input and restored metrics must contain psnr, ssim, and lpips")
        row = {
            "experiment_id": self.experiment_id,
            "variant": self.variant,
            "step2_seed": self.step2_seed,
            "source_id": source_id,
            **metadata,
            "prediction_path": prediction_name,
            "prediction_sha256": prediction_sha256,
            "kernel_path": kernel_name,
            "kernel_sha256": kernel_sha256,
            "prediction_shape": list(pred.shape),
            "filter_shape": list(filters.shape),
            "solver_geometry": dict(solver_geometry),
            "solver_config_sha256": self.solver_config_sha256,
            "kernel_gt_sha256": self.kernel_gt_sha256,
            "pairs_manifest_sha256": self.pairs_manifest_sha256,
            "benchmark_summary_sha256": self.benchmark_summary_sha256,
            "predecessor_network_snapshot_sha256": self.predecessor_network_snapshot_sha256,
            "input_metrics": input_metrics,
            "restored_metrics": restored_metrics,
        }
        _finite_payload(row)
        return json.dumps(row, ensure_ascii=False, sort_keys=True, allow_nan=False)

    def append(self, serialized_row: str) -> None:
        if len(self.rows) >= self.expected_count:
            raise ValueError("cannot append more than expected metric rows")
        row = json.loads(serialized_row)
        source_id = row.get("source_id")
        if source_id in self.source_ids:
            raise ValueError(f"duplicate source_id: {source_id}")
        if row.get("variant") != self.variant or row.get("step2_seed") != self.step2_seed:
            raise ValueError("record variant or Step 2 seed does not match writer")
        for key, expected in {
            "solver_config_sha256": self.solver_config_sha256,
            "kernel_gt_sha256": self.kernel_gt_sha256,
            "pairs_manifest_sha256": self.pairs_manifest_sha256,
            "benchmark_summary_sha256": self.benchmark_summary_sha256,
            "predecessor_network_snapshot_sha256": self.predecessor_network_snapshot_sha256,
        }.items():
            if row.get(key) != expected:
                raise ValueError(f"record {key} mismatch")
        _safe_sha(row.get("prediction_sha256"), "prediction_sha256")
        _safe_sha(row.get("kernel_sha256"), "kernel_sha256")
        _finite_payload(row)
        self.rows.append(row)
        self.source_ids.add(source_id)
        with self.metrics_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n")

    def _statistics(self) -> tuple[dict[str, dict[str, float]], dict[str, float]]:
        ordered = sorted(self.rows, key=lambda row: row["source_id"])
        statistics_payload: dict[str, dict[str, float]] = {}
        means: dict[str, float] = {}
        for name in SUMMARY_METRICS:
            prefix, metric = name.split("_", 1)
            values = [float(row[f"{prefix}_metrics"][metric]) for row in ordered]
            stats = {
                "mean": statistics.fmean(values),
                "std": statistics.pstdev(values),
                "median": statistics.median(values),
                "min": min(values),
                "max": max(values),
            }
            statistics_payload[name] = stats
            means[name] = stats["mean"]
        return statistics_payload, means

    def finalize_if_complete(self) -> dict[str, object] | None:
        if len(self.rows) < self.expected_count:
            return None
        if len(self.rows) > self.expected_count:
            raise ValueError("more metric rows than expected")
        if self.summary_path.exists():
            raise FileExistsError(self.summary_path)
        if not self.manifest_path.is_file():
            raise ValueError("manifest.jsonl must exist before summary finalization")
        manifest_rows = [
            json.loads(line)
            for line in self.manifest_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if len(manifest_rows) != self.expected_count:
            raise ValueError("manifest record count does not match expected count")
        if {row.get("source_id") for row in manifest_rows} != self.source_ids:
            raise ValueError("manifest source set does not match metric source set")
        stats, means = self._statistics()
        summary = {
            "experiment_id": self.experiment_id,
            "variant": self.variant,
            "step2_seed": self.step2_seed,
            "records": len(self.rows),
            "failures": 0,
            "source_set_sha256": _source_set_sha256(self.source_ids),
            "pairs_manifest_sha256": self.pairs_manifest_sha256,
            "benchmark_summary_sha256": self.benchmark_summary_sha256,
            "kernel_gt_sha256": self.kernel_gt_sha256,
            "solver_config_sha256": self.solver_config_sha256,
            "predecessor_network_snapshot_sha256": self.predecessor_network_snapshot_sha256,
            "statistics": stats,
            "mean": means,
            "manifest_jsonl_sha256": _sha256(self.manifest_path),
            "metrics_jsonl_sha256": _sha256(self.metrics_path),
        }
        with self.summary_path.open("x", encoding="utf-8") as handle:
            json.dump(summary, handle, ensure_ascii=False, sort_keys=True, allow_nan=False, indent=2)
            handle.write("\n")
        return summary

    def write_summary(self) -> dict[str, object] | None:
        return self.finalize_if_complete()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not Path(path).is_file():
        raise ValueError(f"missing JSONL artifact: {path}")
    rows = [
        json.loads(line)
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    _finite_payload(rows)
    return rows


def _close_enough(left: float, right: float) -> bool:
    return math.isclose(float(left), float(right), rel_tol=1e-9, abs_tol=1e-9)


def verify_summary_against_jsonl(summary_path: Path) -> dict[str, Any]:
    summary_path = Path(summary_path)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    _finite_payload(summary)
    required_summary = {
        "records", "failures", "source_set_sha256", "pairs_manifest_sha256",
        "benchmark_summary_sha256", "kernel_gt_sha256", "solver_config_sha256",
        "predecessor_network_snapshot_sha256",
        "statistics", "mean", "manifest_jsonl_sha256", "metrics_jsonl_sha256",
    }
    if not required_summary.issubset(summary):
        raise ValueError("summary is missing the unified provenance/statistics schema")
    output_dir = summary_path.parent
    manifest_path = output_dir / "manifest.jsonl"
    metrics_path = output_dir / "metrics.jsonl"
    manifest = _read_jsonl(manifest_path)
    metrics = _read_jsonl(metrics_path)
    expected_records = int(summary["records"])
    if expected_records != len(manifest) or expected_records != len(metrics):
        raise ValueError("summary and JSONL record counts differ")
    if _sha256(manifest_path) != summary["manifest_jsonl_sha256"]:
        raise ValueError("manifest JSONL SHA-256 mismatch")
    if _sha256(metrics_path) != summary["metrics_jsonl_sha256"]:
        raise ValueError("metrics JSONL SHA-256 mismatch")
    manifest_by_id = {row.get("source_id"): row for row in manifest}
    metrics_by_id = {row.get("source_id"): row for row in metrics}
    if len(manifest_by_id) != expected_records or set(manifest_by_id) != set(metrics_by_id):
        raise ValueError("manifest and metrics source sets differ")
    for source_id, row in manifest_by_id.items():
        if not isinstance(source_id, str) or Path(source_id).name != source_id:
            raise ValueError("manifest source IDs must be unique safe basenames")
        for key in ("prediction_path", "kernel_path"):
            relative = Path(str(row.get(key, "")))
            if relative.is_absolute() or ".." in relative.parts or relative.name != str(relative):
                raise ValueError(f"{key} must be a local basename")
            artifact = output_dir / relative
            if not artifact.is_file() or _sha256(artifact) != str(row.get(key.replace("_path", "_sha256"), "")).lower():
                raise ValueError(f"{key} artifact or SHA-256 is invalid")
        metric_row = metrics_by_id[source_id]
        manifest_payload = dict(row)
        manifest_payload.pop('schema_version', None)
        metric_payload = dict(metric_row)
        metric_payload.pop('schema_version', None)
        if manifest_payload != metric_payload:
            raise ValueError('manifest and metrics rows differ')
        for key in (
            'experiment_id', 'variant', 'step2_seed',
            'predecessor_network_snapshot_sha256',
        ):
            if row.get(key) != summary.get(key):
                raise ValueError(f'row {key} disagrees with summary')
        for key in (
            "prediction_path", "prediction_sha256", "kernel_path", "kernel_sha256",
            "solver_config_sha256", "kernel_gt_sha256", "pairs_manifest_sha256",
            "benchmark_summary_sha256",
            "predecessor_network_snapshot_sha256",
        ):
            if row.get(key) != metric_row.get(key):
                raise ValueError(f"manifest and metrics disagree on {key}")
        for key in ("solver_config_sha256", "kernel_gt_sha256", "pairs_manifest_sha256", "benchmark_summary_sha256"):
            if row.get(key) != summary[key]:
                raise ValueError(f"row {key} disagrees with summary")
    source_set_sha = _source_set_sha256(set(manifest_by_id))
    if source_set_sha != summary["source_set_sha256"]:
        raise ValueError("source_set_sha256 mismatch")
    predecessor_hash = summary.get("predecessor_network_snapshot_sha256")
    if summary.get("variant") == "oracle":
        if predecessor_hash is not None:
            raise ValueError("oracle summary cannot carry a predecessor snapshot hash")
    elif summary.get("variant") == "learned":
        _safe_sha(predecessor_hash, "predecessor_network_snapshot_sha256")
    recomputed: dict[str, dict[str, float]] = {}
    means: dict[str, float] = {}
    for name in SUMMARY_METRICS:
        prefix, metric = name.split("_", 1)
        values = [float(metrics_by_id[source_id][f"{prefix}_metrics"][metric]) for source_id in sorted(metrics_by_id)]
        stats = {
            "mean": statistics.fmean(values),
            "std": statistics.pstdev(values),
            "median": statistics.median(values),
            "min": min(values),
            "max": max(values),
        }
        recomputed[name] = stats
        means[name] = stats["mean"]
    for name in SUMMARY_METRICS:
        for field in ("mean", "std", "median", "min", "max"):
            if not _close_enough(summary["statistics"][name][field], recomputed[name][field]):
                raise ValueError(f"summary statistic mismatch for {name}.{field}")
        if not _close_enough(summary["mean"][name], means[name]):
            raise ValueError(f"summary mean mismatch for {name}")
    return summary


def aggregate_summaries(
    oracle_path: Path,
    learned_paths: list[Path],
    output: Path,
    *,
    kernel_paths: list[Path] | None = None,
) -> dict[str, object]:
    if Path(output).exists():
        raise FileExistsError(output)
    if len(learned_paths) != 5:
        raise ValueError("exactly five learned summaries are required")
    if kernel_paths is None or len(kernel_paths) != 5:
        raise ValueError("exactly five kernel analysis results are required")
    oracle = verify_summary_against_jsonl(Path(oracle_path))
    learned = [verify_summary_against_jsonl(Path(path)) for path in learned_paths]
    if oracle.get("variant") != "oracle" or oracle.get("step2_seed") is not None:
        raise ValueError("oracle summary is invalid")
    seeds = [item.get("step2_seed") for item in learned]
    if set(seeds) != {0, 1, 2, 3, 4} or len(seeds) != len(set(seeds)):
        raise ValueError("learned summaries must contain seeds 0..4 exactly once")
    for item in learned:
        for key in (
            "records", "source_set_sha256", "solver_config_sha256", "kernel_gt_sha256",
            "pairs_manifest_sha256", "benchmark_summary_sha256",
        ):
            if item.get(key) != oracle.get(key):
                raise ValueError(f"summary {key} mismatch")
        if item.get("variant") != "learned":
            raise ValueError("learned summary has wrong variant")

    learned_by_seed = {item["step2_seed"]: item for item in learned}

    kernel_results = []
    for index, path in enumerate(kernel_paths):
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        _finite_payload(payload)
        for key in ("kernel_psnr", "kernel_ncc", "snapshot_sha256"):
            if key not in payload:
                raise ValueError(f"kernel analysis is missing {key}")
        if type(payload.get("step2_seed")) is not int or payload["step2_seed"] != index:
            raise ValueError("kernel analysis seed order does not match learned summaries")
        if payload.get("kernel_gt_sha256") != oracle["kernel_gt_sha256"]:
            raise ValueError("kernel analysis true-kernel hash mismatch")
        snapshot_sha256 = _safe_sha(payload.get("snapshot_sha256"), "snapshot_sha256")
        if snapshot_sha256 != learned_by_seed[index]["predecessor_network_snapshot_sha256"]:
            raise ValueError("kernel analysis snapshot does not match learned evaluation predecessor")
        kernel_results.append({
            "step2_seed": index,
            "snapshot_sha256": snapshot_sha256,
            "kernel_psnr": float(payload["kernel_psnr"]),
            "kernel_ncc": float(payload["kernel_ncc"]),
        })

    learned = sorted(learned, key=lambda item: item["step2_seed"])
    across_seed = {}
    for name in SUMMARY_METRICS:
        values = [float(item["mean"][name]) for item in learned]
        across_seed[name] = {
            "mean": statistics.fmean(values),
            "std": statistics.pstdev(values),
        }
    kernel_metrics = {
        "count": len(kernel_results),
        "per_seed": kernel_results,
        "mean": {
            "kernel_psnr": statistics.fmean([item["kernel_psnr"] for item in kernel_results]),
            "kernel_ncc": statistics.fmean([item["kernel_ncc"] for item in kernel_results]),
        },
        "std": {
            "kernel_psnr": statistics.pstdev([item["kernel_psnr"] for item in kernel_results]),
            "kernel_ncc": statistics.pstdev([item["kernel_ncc"] for item in kernel_results]),
        },
    }
    result = {
        "oracle": oracle,
        "learned": learned,
        "learned_seed_count": len(learned),
        "learned_across_seed": across_seed,
        "kernel_metrics": kernel_metrics,
        "source_set_sha256": oracle["source_set_sha256"],
        "pairs_manifest_sha256": oracle["pairs_manifest_sha256"],
        "benchmark_summary_sha256": oracle["benchmark_summary_sha256"],
        "solver_config_sha256": oracle["solver_config_sha256"],
        "kernel_gt_sha256": oracle["kernel_gt_sha256"],
    }
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with Path(output).open("x", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, sort_keys=True, allow_nan=False, indent=2)
        handle.write("\n")
    return result
