"""Deterministic no-training child used by the runner's real subprocess test."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import torch
from PIL import Image

from ddm4ip.utils.benchmark_metrics import BenchmarkMetricWriter


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    run_root = Path(sys.argv[1])
    mode = sys.argv[2] if len(sys.argv) > 2 else "ok"
    spec = json.loads((run_root / "spec.json").read_text(encoding="utf-8"))
    plots = run_root / "plots"
    plots.mkdir(parents=True, exist_ok=True)
    kernel_gt = Path(spec["benchmark_root"]) / spec["kernel_gt"]
    writer = BenchmarkMetricWriter(
        plots,
        experiment_id=str(spec["task_name"]),
        variant=str(spec["variant"]),
        step2_seed=spec.get("seed"),
        solver_config_sha256="e" * 64,
        kernel_gt_path=kernel_gt,
        expected_count=int(spec["expected_manifest_records"]),
        pairs_manifest_sha256=str(spec["benchmark_hashes"]["pairs"]),
        benchmark_summary_sha256=str(spec["benchmark_hashes"]["summary"]),
    )
    metadata_template = {
        "source_relpath": "synthetic/fixture.png",
        "source_sha256": "1" * 64,
        "clean_path": "clean/fixture.png",
        "noisy_path": "noisy/fixture.png",
        "clean_sha256": "2" * 64,
        "noisy_sha256": "3" * 64,
    }
    rows: list[dict[str, object]] = []
    for index in range(int(spec["expected_manifest_records"])):
        source_id = f"fixture-{index}"
        prediction_path = plots / f"prediction-{source_id}.png"
        kernel_path = plots / f"kernel-{source_id}.pt"
        Image.new("RGB", (8, 8), color=(128, 128, 128)).save(prediction_path, format="PNG")
        kernel_path.write_bytes(b"fixture-kernel")
        row = json.loads(writer.prepare_record(
            {"source_id": source_id, **metadata_template},
            torch.full((1, 3, 8, 8), 0.5),
            torch.ones((1, 1, 3, 3)),
            prediction_path.name,
            kernel_path.name,
            {"filter_groups": [{"tile_range": [0, 1], "filter_range": [0, 1], "association": "shared"}]},
            {"psnr": 10.0, "ssim": 0.1, "lpips": 0.9},
            {"psnr": 11.0, "ssim": 0.2, "lpips": 0.8},
            prediction_sha256=_sha256(prediction_path),
            kernel_sha256=_sha256(kernel_path),
        ))
        writer.append(json.dumps(row, sort_keys=True))
        rows.append({"schema_version": 2, **row})

    (plots / "manifest.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    writer.finalize_if_complete()
    if mode == "corrupt":
        (plots / "prediction-fixture-0.png").write_bytes(b"corrupted-after-summary")
    print("FIXTURE_CHILD_STDOUT", flush=True)
    print("FIXTURE_CHILD_STDERR", file=sys.stderr, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
