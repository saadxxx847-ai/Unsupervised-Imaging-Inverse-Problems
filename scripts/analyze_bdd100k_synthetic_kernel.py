from __future__ import annotations

import argparse
import hashlib
import json
import pickle
import re
import sys
from contextlib import contextmanager
from pathlib import Path

import torch

from ddm4ip.utils.benchmark_metrics import compute_kernel_metrics


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@contextmanager
def _repository_import_path(repository_root: Path):
    repository_root = str(Path(repository_root).resolve())
    old_path = list(sys.path)
    if repository_root not in sys.path:
        sys.path.insert(0, repository_root)
    try:
        yield
    finally:
        sys.path[:] = old_path


def analyze_snapshot(
    snapshot: Path,
    snapshot_sha256: str,
    expected_global_step: int,
    kernel_gt: Path,
    kernel_gt_sha256: str,
    output: Path,
    repository_root: Path,
) -> dict[str, object]:
    if output.exists():
        raise FileExistsError(output)
    snapshot = Path(snapshot)
    match = re.fullmatch(r"network-snapshot-(\d+)\.pkl", snapshot.name)
    if match is None or int(match.group(1)) + 1 != expected_global_step:
        raise ValueError("snapshot filename does not match expected global step")
    if _sha256(snapshot).lower() != snapshot_sha256.lower():
        raise ValueError("snapshot SHA-256 mismatch")
    if _sha256(kernel_gt).lower() != kernel_gt_sha256.lower():
        raise ValueError("true kernel SHA-256 mismatch")
    with _repository_import_path(repository_root):
        with snapshot.open("rb") as handle:
            payload = pickle.load(handle)
    if payload.get("global_step") != expected_global_step:
        raise ValueError("snapshot internal global step mismatch")
    if "kernel_nn" not in payload:
        raise ValueError("snapshot does not contain kernel_nn")
    estimated = payload["kernel_nn"].get_kernel(None, None)
    truth = torch.load(kernel_gt, map_location="cpu", weights_only=True)
    metrics = compute_kernel_metrics(estimated, truth)
    result = {
        "snapshot": str(snapshot),
        "snapshot_sha256": snapshot_sha256,
        "global_step": expected_global_step,
        "kernel_gt": str(kernel_gt),
        "kernel_gt_sha256": kernel_gt_sha256,
        "estimated_shape": list(estimated.shape),
        "truth_shape": list(truth.shape),
        "alignment_rule": "equate_kernel_shapes center-padding",
        **metrics,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--snapshot-sha256", required=True)
    parser.add_argument("--expected-global-step", type=int, required=True)
    parser.add_argument("--kernel-gt", type=Path, required=True)
    parser.add_argument("--kernel-gt-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    analyze_snapshot(
        args.snapshot,
        args.snapshot_sha256,
        args.expected_global_step,
        args.kernel_gt,
        args.kernel_gt_sha256,
        args.output,
        args.repository_root,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
