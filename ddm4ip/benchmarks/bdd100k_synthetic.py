from __future__ import annotations

import csv
import hashlib
import io
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np
import torch
from PIL import Image

from ddm4ip.degradations.degradation import instantiate_single_kernel


SOURCE_FIELDS = (
    "source_id",
    "source_relpath",
    "size_bytes",
    "sha256",
    "width",
    "height",
    "channels",
)


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    source_relpath: str
    size_bytes: int
    sha256: str
    width: int
    height: int
    channels: int


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_inventory_bytes(records: Sequence[SourceRecord]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=SOURCE_FIELDS,
        lineterminator="\n",
    )
    writer.writeheader()
    for record in sorted(records, key=lambda item: item.source_relpath):
        writer.writerow(
            {
                "source_id": record.source_id,
                "source_relpath": record.source_relpath,
                "size_bytes": record.size_bytes,
                "sha256": record.sha256,
                "width": record.width,
                "height": record.height,
                "channels": record.channels,
            }
        )
    return output.getvalue().encode("utf-8")


def source_manifest_bytes(records: Sequence[SourceRecord]) -> bytes:
    """Return the frozen UTF-8 source manifest representation."""
    return _canonical_inventory_bytes(records)


def inspect_sources(
    view_root: Path,
    expected_view_manifest_sha256: str,
    expected_source_count: int | None = None,
) -> tuple[list[SourceRecord], str]:
    view_root = Path(view_root)
    manifest_path = view_root / "manifest.csv"
    actual_view_manifest_sha256 = _sha256(manifest_path)
    if actual_view_manifest_sha256.lower() != expected_view_manifest_sha256.lower():
        raise ValueError("view manifest SHA-256 does not match the approved digest")

    records: list[SourceRecord] = []
    seen_ids: set[str] = set()
    seen_hashes: set[str] = set()
    for path in sorted(
        path
        for split in ("train", "val")
        for path in (view_root / split / "clean").rglob("*")
        if path.is_file()
    ):
        relpath = path.relative_to(view_root).as_posix()
        source_id = path.stem
        if source_id in seen_ids:
            raise ValueError(f"duplicate source_id: {source_id}")
        digest = _sha256(path)
        if digest in seen_hashes:
            raise ValueError(f"duplicate source content: {digest}")
        try:
            with Image.open(path) as image:
                image.load()
                width, height = image.size
                channels = len(image.getbands())
                mode = image.mode
        except Exception as exc:
            raise ValueError(f"cannot decode source image: {path}") from exc
        if (width, height) != (1280, 720):
            raise ValueError(f"source image must be 1280x720: {path}")
        if mode != "RGB" or channels != 3:
            raise ValueError(f"source image must be RGB: {path}")
        record = SourceRecord(
            source_id=source_id,
            source_relpath=relpath,
            size_bytes=path.stat().st_size,
            sha256=digest,
            width=width,
            height=height,
            channels=channels,
        )
        records.append(record)
        seen_ids.add(source_id)
        seen_hashes.add(digest)

    if expected_source_count is not None and len(records) != expected_source_count:
        raise ValueError(
            f"expected {expected_source_count} source images, found {len(records)}"
        )
    records.sort(key=lambda item: item.source_relpath)
    inventory_bytes = _canonical_inventory_bytes(records)
    return records, hashlib.sha256(inventory_bytes).hexdigest()


def split_sources(
    records: Sequence[SourceRecord], split_seed: int = 42
) -> dict[str, list[SourceRecord]]:
    if len(records) != 1739:
        raise ValueError(f"expected exactly 1739 source records, found {len(records)}")
    ordered = sorted(records, key=lambda item: item.source_relpath)
    indices = list(range(len(ordered)))
    random.Random(split_seed).shuffle(indices)
    ranges = (
        ("step1_observation", 0, 1000),
        ("step2_clean", 1000, 1100),
        ("test_paired", 1100, 1600),
        ("dev_reserve", 1600, 1739),
    )
    return {
        name: sorted(
            (ordered[index] for index in indices[start:end]),
            key=lambda item: item.source_id,
        )
        for name, start, end in ranges
    }


def preprocess_image(source: Path) -> torch.Tensor:
    source = Path(source)
    try:
        with Image.open(source) as image:
            image.load()
            if image.size != (1280, 720):
                raise ValueError(f"source image must be 1280x720: {source}")
            cropped = image.crop((280, 0, 1000, 720)).resize(
                (256, 256), resample=Image.Resampling.BICUBIC
            ).convert("RGB")
            array = np.asarray(cropped, dtype=np.uint8).copy()
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"cannot decode source image: {source}") from exc
    return torch.from_numpy(array).permute(2, 0, 1).contiguous().float() / 255.0


def make_noise_seed(role: str, source_id: str) -> int:
    payload = f"bdd100k-motionblur-v1\0{role}\0{source_id}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big") % (2**31)


def _tensor_sha256(tensor: torch.Tensor) -> str:
    return hashlib.sha256(tensor.detach().cpu().contiguous().numpy().tobytes()).hexdigest()


def _save_png(tensor: torch.Tensor, path: Path) -> None:
    array = (
        tensor.detach().cpu().clamp(0, 1).mul(255).round().to(torch.uint8)
        .permute(1, 2, 0).numpy()
    )
    Image.fromarray(array, mode="RGB").save(path, format="PNG")


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fixture_or_production_roles(records: Sequence[SourceRecord]):
    if len(records) == 1739:
        return split_sources(records, split_seed=42)
    ordered = sorted(records, key=lambda item: item.source_id)
    return {
        "step1_observation": ordered,
        "step2_clean": [],
        "test_paired": [],
        "dev_reserve": [],
    }


def _preflight_records(records: Sequence[SourceRecord], source_root: Path, expected_digest: str):
    actual_digest = hashlib.sha256(_canonical_inventory_bytes(records)).hexdigest()
    if actual_digest.lower() != expected_digest.lower():
        raise ValueError("source manifest SHA-256 does not match the approved digest")
    source_root = Path(source_root).resolve()
    seen_ids: set[str] = set()
    seen_hashes: set[str] = set()
    for record in records:
        source_path = (source_root / Path(record.source_relpath)).resolve()
        try:
            source_path.relative_to(source_root)
        except ValueError as exc:
            raise ValueError("source path escapes the source root") from exc
        if not source_path.is_file():
            raise FileNotFoundError(source_path)
        if record.source_id in seen_ids:
            raise ValueError(f"duplicate source_id: {record.source_id}")
        actual_hash = _file_sha256(source_path)
        if actual_hash != record.sha256:
            raise ValueError(f"source SHA-256 mismatch: {source_path}")
        if actual_hash in seen_hashes:
            raise ValueError(f"duplicate source content: {actual_hash}")
        with Image.open(source_path) as image:
            image.load()
            if image.size != (record.width, record.height):
                raise ValueError(f"source dimensions changed: {source_path}")
            if image.mode != "RGB" or len(image.getbands()) != 3:
                raise ValueError(f"source image must be RGB: {source_path}")
        if source_path.stat().st_size != record.size_bytes:
            raise ValueError(f"source byte size changed: {source_path}")
        seen_ids.add(record.source_id)
        seen_hashes.add(actual_hash)


def _write_csv(path: Path, fieldnames, rows) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_benchmark(
    records: Sequence[SourceRecord],
    expected_source_manifest_sha256: str,
    destination: Path,
    split_seed: int = 42,
    source_root: Path | None = None,
) -> dict[str, object]:
    destination = Path(destination)
    if destination.exists():
        raise FileExistsError(destination)
    if source_root is None:
        raise ValueError("source_root is required to build derived benchmark files")
    _preflight_records(records, Path(source_root), expected_source_manifest_sha256)
    roles = _fixture_or_production_roles(records)

    destination.mkdir(parents=True)
    for relative in (
        "degradation",
        "step1-observation/noisy",
        "step2-clean/clean",
        "test-paired/clean",
        "test-paired/noisy",
        "dev-reserve/clean",
        "dev-reserve/noisy",
    ):
        (destination / relative).mkdir(parents=True, exist_ok=True)

    source_manifest = _canonical_inventory_bytes(records)
    (destination / "source-manifest.csv").write_bytes(source_manifest)
    split_rows = []
    for role, role_records in roles.items():
        for record in role_records:
            split_rows.append({"role": role, **record.__dict__})
    _write_csv(destination / "split-manifest.csv", ("role",) + SOURCE_FIELDS, split_rows)

    physics = instantiate_single_kernel(
        {
            "kind": "motion_blur",
            "kernel_size": 32,
            "intensity": 0.5,
            "rnd_seed": 1,
        },
        noise_model=None,
    )
    kernel = physics.get_kernel().detach().cpu().float()
    if tuple(kernel.shape) != (1, 1, 32, 32) or not torch.isfinite(kernel).all():
        raise ValueError("generated kernel has an unexpected shape or non-finite values")
    if (kernel < 0).any() or not torch.isclose(kernel.sum(), torch.tensor(1.0), atol=1e-6, rtol=1e-6):
        raise ValueError("generated kernel must be finite, nonnegative, and normalized")
    kernel_path = destination / "degradation" / "kernel-gt.pt"
    torch.save(kernel, kernel_path, _use_new_zipfile_serialization=False)
    kernel_tensor_sha256 = _tensor_sha256(kernel)
    kernel_file_sha256 = _file_sha256(kernel_path)
    kernel_image = kernel[0, 0] / kernel.max().clamp_min(1e-12)
    Image.fromarray(kernel_image.mul(255).round().to(torch.uint8).numpy(), mode="L").save(
        destination / "degradation" / "kernel-gt.png", format="PNG"
    )
    degradation = {
        "kind": "motion_blur",
        "kernel_size": 32,
        "intensity": 0.5,
        "rnd_seed": 1,
        "noise_std": 0.02,
        "padding": "replicate",
        "kernel_tensor_sha256": kernel_tensor_sha256,
        "kernel_file_sha256": kernel_file_sha256,
    }
    (destination / "degradation" / "degradation.json").write_text(
        json.dumps(degradation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    pair_fields = (
        "schema_version", "role", "source_id", "source_relpath", "source_sha256",
        "clean_path", "clean_sha256", "noisy_path", "noisy_sha256", "noise_seed",
        "source_size", "crop_box", "output_size", "channels", "kernel_tensor_sha256",
    )
    pair_rows = {"test_paired": [], "dev_reserve": []}
    source_root = Path(source_root)
    for role, role_records in roles.items():
        for record in role_records:
            clean = preprocess_image(source_root / Path(record.source_relpath))
            noise_seed = make_noise_seed(role, record.source_id)
            noisy = physics(clean.unsqueeze(0)).squeeze(0).cpu()
            generator = torch.Generator(device="cpu").manual_seed(noise_seed)
            noisy = (noisy + torch.randn(noisy.shape, generator=generator) * 0.02).clamp(0, 1)
            if role == "step1_observation":
                _save_png(noisy, destination / "step1-observation" / "noisy" / f"{record.source_id}.png")
            elif role == "step2_clean":
                _save_png(clean, destination / "step2-clean" / "clean" / f"{record.source_id}.png")
            elif role in pair_rows:
                role_dir = "test-paired" if role == "test_paired" else "dev-reserve"
                clean_path = destination / role_dir / "clean" / f"{record.source_id}.png"
                noisy_path = destination / role_dir / "noisy" / f"{record.source_id}.png"
                _save_png(clean, clean_path)
                _save_png(noisy, noisy_path)
                pair_rows[role].append(
                    {
                        "schema_version": 1,
                        "role": role,
                        "source_id": record.source_id,
                        "source_relpath": record.source_relpath,
                        "source_sha256": record.sha256,
                        "clean_path": f"clean/{record.source_id}.png",
                        "clean_sha256": _file_sha256(clean_path),
                        "noisy_path": f"noisy/{record.source_id}.png",
                        "noisy_sha256": _file_sha256(noisy_path),
                        "noise_seed": noise_seed,
                        "source_size": record.size_bytes,
                        "crop_box": [0, 280, 720, 1000],
                        "output_size": [256, 256],
                        "channels": 3,
                        "kernel_tensor_sha256": kernel_tensor_sha256,
                    }
                )

    for role, rows in pair_rows.items():
        pair_path = destination / ("test-paired" if role == "test_paired" else "dev-reserve") / "pairs.jsonl"
        pair_path.write_text(
            "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
            encoding="utf-8",
        )

    preprocessing = {
        "crop_box": [0, 280, 720, 1000],
        "output_size": [256, 256],
        "resample": "bicubic",
        "channels": 3,
    }
    preprocessing_path = destination / "preprocessing.json"
    preprocessing_path.write_text(
        json.dumps(preprocessing, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    counts = {key: len(value) for key, value in roles.items()}
    degradation_path = destination / "degradation" / "degradation.json"
    pairs_path = destination / "test-paired" / "pairs.jsonl"
    summary = {
        "counts": counts,
        "source_manifest_sha256": hashlib.sha256(source_manifest).hexdigest(),
        "split_manifest_sha256": _file_sha256(destination / "split-manifest.csv"),
        "pairs_manifest_sha256": _file_sha256(pairs_path),
        "preprocessing_sha256": _file_sha256(preprocessing_path),
        "degradation_sha256": _file_sha256(degradation_path),
        "kernel_tensor_sha256": kernel_tensor_sha256,
        "kernel_file_sha256": kernel_file_sha256,
        "preprocessing": preprocessing,
        "degradation": degradation,
        "split_seed": split_seed,
        "implementation_difference": "fixed saved Step 1 noise rather than online resampling",
    }
    (destination / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (destination / "status.json").write_text(
        json.dumps({"status": "SUCCESS", "counts": counts}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (destination / "build.log").write_text("benchmark build completed\n", encoding="utf-8")
    return summary
