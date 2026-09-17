from __future__ import annotations

import hashlib
import json
import os
import stat
from dataclasses import dataclass
from pathlib import Path

import torch
from PIL import Image
from torch.utils.data import Dataset

from ddm4ip.data.base import Batch, Datasplit, DatasetType


PAIR_FIELDS = (
    "schema_version", "role", "source_id", "source_relpath", "source_sha256",
    "clean_path", "clean_sha256", "noisy_path", "noisy_sha256", "noise_seed",
    "source_size", "crop_box", "output_size", "channels", "kernel_tensor_sha256",
)


@dataclass(frozen=True)
class PairRecord:
    values: dict


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_reparse_point(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        return bool(path.stat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except (AttributeError, OSError):
        return False


def _safe_child(root: Path, relative: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError("manifest paths must be relative and stay within the pairs root")
    root = root.resolve()
    resolved = (root / candidate).resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("manifest path escapes the pairs root") from exc
    current = root
    for part in candidate.parts:
        current = current / part
        if _is_reparse_point(current):
            raise ValueError("manifest path traverses a reparse point")
    return resolved


class ManifestPairedDataset(Dataset[Batch], DatasetType):
    def __init__(
        self,
        path,
        degradation,
        split: Datasplit,
        dset_cfg,
        shuffle_clean: bool = False,
        generator=None,
    ):
        del shuffle_clean, generator
        if split != Datasplit.TEST:
            raise ValueError("manifest_paired is an evaluation-only dataset")
        self.path = Path(path).resolve()
        self.root = self.path.parent
        self.corruption = degradation
        expected_role = dset_cfg.get("role", None)
        rows: list[dict] = []
        seen_ids: set[str] = set()
        seen_paths: set[Path] = set()
        with self.path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid JSON on line {line_number}") from exc
                if set(row) != set(PAIR_FIELDS):
                    raise ValueError(f"unexpected manifest keys on line {line_number}")
                if row["schema_version"] != 1:
                    raise ValueError("unsupported pair manifest schema")
                if row["role"] not in {"test_paired", "dev_reserve"}:
                    raise ValueError("invalid paired manifest role")
                if expected_role is not None and row["role"] != expected_role:
                    raise ValueError("manifest role does not match dataset configuration")
                source_id = row["source_id"]
                if source_id in seen_ids:
                    raise ValueError(f"duplicate source_id: {source_id}")
                clean_path = _safe_child(self.root, row["clean_path"])
                noisy_path = _safe_child(self.root, row["noisy_path"])
                if clean_path == noisy_path:
                    raise ValueError("clean and noisy paths must be distinct")
                if clean_path in seen_paths or noisy_path in seen_paths:
                    raise ValueError("manifest image path is referenced more than once")
                if clean_path.stem != source_id or noisy_path.stem != source_id:
                    raise ValueError("source_id must match clean and noisy filename stems")
                if not clean_path.is_file() or not noisy_path.is_file():
                    raise FileNotFoundError("manifest image is missing")
                if _sha256(clean_path) != row["clean_sha256"]:
                    raise ValueError("clean image SHA-256 mismatch")
                if _sha256(noisy_path) != row["noisy_sha256"]:
                    raise ValueError("noisy image SHA-256 mismatch")
                for image_path in (clean_path, noisy_path):
                    with Image.open(image_path) as image:
                        image.load()
                        if image.mode != "RGB" or image.size != (256, 256):
                            raise ValueError("paired images must be 256x256 RGB")
                if list(row["output_size"]) != [256, 256] or row["channels"] != 3:
                    raise ValueError("manifest output geometry is not 256x256 RGB")
                rows.append(row)
                seen_ids.add(source_id)
                seen_paths.update((clean_path, noisy_path))
        if not rows:
            raise ValueError("pair manifest is empty")
        max_imgs = dset_cfg.get("max_imgs", None)
        self.rows = tuple(rows[: int(max_imgs)] if max_imgs is not None else rows)
        self.clean_img_size = (3, 256, 256)
        self.corrupt_img_size = (3, 256, 256)
        self.clean_conditioning_channels = 0
        self.corrupt_conditioning_channels = 0
        self.label_dim = 0

    def _read(self, relative: str) -> torch.Tensor:
        path = _safe_child(self.root, relative)
        with Image.open(path) as image:
            image.load()
            data = torch.frombuffer(bytearray(image.convert("RGB").tobytes()), dtype=torch.uint8)
            data = data.reshape(256, 256, 3).permute(2, 0, 1).contiguous()
        return data.float() / 255.0

    @property
    def noise_level(self) -> torch.Tensor:
        if self.corruption is None:
            return torch.tensor(0.0)
        noise_model = getattr(self.corruption, "noise_model", None)
        sigma = getattr(noise_model, "sigma", 0.0)
        if isinstance(sigma, torch.Tensor):
            return sigma.detach().cpu().float()
        return torch.tensor(float(sigma))

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index) -> Batch:
        row = self.rows[index]
        clean = self._read(row["clean_path"])
        noisy = self._read(row["noisy_path"])
        return Batch(
            clean=clean,
            clean_label=None,
            corrupt=noisy,
            corrupt_label=None,
            noise_level=self.noise_level,
            clean_conditioning=None,
            corrupt_conditioning=None,
            kernel=None,
            meta={
                "source_id": row["source_id"],
                "source_relpath": row["source_relpath"],
                "source_sha256": row["source_sha256"],
                "clean_path": row["clean_path"],
                "noisy_path": row["noisy_path"],
                "clean_sha256": row["clean_sha256"],
                "noisy_sha256": row["noisy_sha256"],
                "noise_seed": torch.tensor(row["noise_seed"], dtype=torch.int64),
                "input_size": torch.tensor([256, 256], dtype=torch.int64),
                "output_size": torch.tensor(row["output_size"], dtype=torch.int64),
                "mode": "paired",
            },
        )
