"""Build deterministic, non-overwriting hard-link views for BDD100K data."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
from typing import Iterable


SHARP_DIRNAME = "Kept_High_Score(Sharp)"
BLURRY_DIRNAME = "Kept_Low_Score(Blurry)"
DEFAULT_SEED = "ddm4ip-bdd100k-v1"


def _jpg_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        raise FileNotFoundError(directory)
    files = sorted(path for path in directory.iterdir() if path.is_file() and path.suffix.lower() == ".jpg")
    if not files:
        raise ValueError(f"No JPG files in {directory}")
    if len({path.name for path in files}) != len(files):
        raise ValueError(f"Duplicate filenames in {directory}")
    return files


def _blur_scores(metrics_csv: Path, expected_names: set[str]) -> dict[str, float]:
    scores: dict[str, float] = {}
    with metrics_csv.open("r", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("group") != "blurry":
                continue
            name = row.get("filename")
            score = row.get("laplacian_variance")
            if not name or score is None:
                raise ValueError("Missing blurry filename or laplacian_variance in metrics CSV")
            if name in scores:
                raise ValueError(f"Duplicate blurry metric row for {name}")
            scores[name] = float(score)
    if set(scores) != expected_names:
        missing = sorted(expected_names - set(scores))
        extra = sorted(set(scores) - expected_names)
        raise ValueError(f"Metrics/source mismatch; missing={missing[:3]}, extra={extra[:3]}")
    return scores


def _middle_blurry_strata(blurry_files: list[Path], scores: dict[str, float]) -> dict[str, list[Path]]:
    ranked = sorted(blurry_files, key=lambda path: (scores[path.name], path.name))
    if len(ranked) < 4:
        raise ValueError("At least four blurry files are required to define Q2/Q3")
    q1_end = len(ranked) // 4
    q2_end = len(ranked) // 2
    q3_end = (3 * len(ranked)) // 4
    q2 = ranked[q1_end:q2_end]
    q3 = ranked[q2_end:q3_end]
    if not q2 or not q3:
        raise ValueError("Q2/Q3 selection is empty")
    return {"blurry_q2": q2, "blurry_q3": q3}


def _validation_count(size: int, fraction: float) -> int:
    if not 0 < fraction < 1:
        raise ValueError("val_fraction must be strictly between zero and one")
    if size <= 1:
        return 0
    return min(size - 1, max(1, int(size * fraction + 0.5)))


def _split(paths: Iterable[Path], stratum: str, seed: str, val_fraction: float) -> tuple[list[Path], list[Path]]:
    ordered = sorted(
        paths,
        key=lambda path: hashlib.sha256(f"{seed}\0{stratum}\0{path.name}".encode("utf-8")).hexdigest(),
    )
    val_count = _validation_count(len(ordered), val_fraction)
    val_names = {path.name for path in ordered[:val_count]}
    return (
        [path for path in ordered if path.name not in val_names],
        [path for path in ordered if path.name in val_names],
    )


def _link(paths: Iterable[Path], destination: Path) -> list[str]:
    destination.mkdir(parents=True, exist_ok=False)
    linked: list[str] = []
    for source in paths:
        target = destination / source.name
        os.link(source, target)
        linked.append(source.name)
    return linked


def build_view(
    source_root: Path,
    metrics_csv: Path,
    destination: Path,
    *,
    seed: str = DEFAULT_SEED,
    val_fraction: float = 0.10,
) -> dict:
    """Create train/val clean/noisy hard-link folders without overwriting a prior view."""
    source_root = source_root.resolve()
    metrics_csv = metrics_csv.resolve()
    destination = destination.resolve()
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing view: {destination}")

    sharp_files = _jpg_files(source_root / SHARP_DIRNAME)
    blurry_files = _jpg_files(source_root / BLURRY_DIRNAME)
    scores = _blur_scores(metrics_csv, {path.name for path in blurry_files})
    blurry_strata = _middle_blurry_strata(blurry_files, scores)

    clean_train, clean_val = _split(sharp_files, "sharp", seed, val_fraction)
    q2_train, q2_val = _split(blurry_strata["blurry_q2"], "blurry_q2", seed, val_fraction)
    q3_train, q3_val = _split(blurry_strata["blurry_q3"], "blurry_q3", seed, val_fraction)
    noisy_train = sorted(q2_train + q3_train, key=lambda path: path.name)
    noisy_val = sorted(q2_val + q3_val, key=lambda path: path.name)

    destination.mkdir(parents=True, exist_ok=False)
    linked = {
        "train": {
            "clean": _link(clean_train, destination / "train" / "clean"),
            "noisy": _link(noisy_train, destination / "train" / "noisy"),
        },
        "val": {
            "clean": _link(clean_val, destination / "val" / "clean"),
            "noisy": _link(noisy_val, destination / "val" / "noisy"),
        },
    }
    summary = {
        "source_root": str(source_root),
        "metrics_csv": str(metrics_csv),
        "destination": str(destination),
        "seed": seed,
        "val_fraction": val_fraction,
        "blur_selection": {
            "method": "rank by (laplacian_variance, filename), retain Q2 and Q3",
            "q2_count": len(blurry_strata["blurry_q2"]),
            "q3_count": len(blurry_strata["blurry_q3"]),
        },
        "counts": {split: {kind: len(names) for kind, names in groups.items()} for split, groups in linked.items()},
    }
    with (destination / "manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["split", "kind", "filename"])
        writer.writeheader()
        for split, groups in linked.items():
            for kind, names in groups.items():
                for name in names:
                    writer.writerow({"split": split, "kind": kind, "filename": name})
    with (destination / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--metrics-csv", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--seed", default=DEFAULT_SEED)
    parser.add_argument("--val-fraction", type=float, default=0.10)
    args = parser.parse_args()
    print(json.dumps(build_view(**vars(args)), indent=2))


if __name__ == "__main__":
    main()
