from __future__ import annotations

import argparse
import csv
from pathlib import Path

from ddm4ip.benchmarks.bdd100k_synthetic import (
    SOURCE_FIELDS,
    SourceRecord,
    build_benchmark,
    inspect_sources,
    source_manifest_bytes,
)


def _records_from_manifest(path: Path) -> list[SourceRecord]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return [
            SourceRecord(
                source_id=row["source_id"],
                source_relpath=row["source_relpath"],
                size_bytes=int(row["size_bytes"]),
                sha256=row["sha256"],
                width=int(row["width"]),
                height=int(row["height"]),
                channels=int(row["channels"]),
            )
            for row in csv.DictReader(handle)
        ]


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect")
    inspect_parser.add_argument("--view-root", type=Path, required=True)
    inspect_parser.add_argument("--expected-view-manifest-sha256", required=True)
    inspect_parser.add_argument("--expected-source-count", type=int, required=True)
    inspect_parser.add_argument("--output-manifest", type=Path, required=True)

    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("--view-root", type=Path, required=True)
    build_parser.add_argument("--source-manifest", type=Path, required=True)
    build_parser.add_argument("--expected-source-manifest-sha256", required=True)
    build_parser.add_argument("--destination", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "inspect":
        if args.output_manifest.exists():
            raise FileExistsError(args.output_manifest)
        records, _ = inspect_sources(
            args.view_root,
            args.expected_view_manifest_sha256,
            expected_source_count=args.expected_source_count,
        )
        args.output_manifest.parent.mkdir(parents=True, exist_ok=True)
        args.output_manifest.write_bytes(source_manifest_bytes(records))
        return 0

    records = _records_from_manifest(args.source_manifest)
    source_digest = __import__("hashlib").sha256(source_manifest_bytes(records)).hexdigest()
    if source_digest.lower() != args.expected_source_manifest_sha256.lower():
        raise ValueError("source manifest digest mismatch")
    build_benchmark(
        records,
        args.expected_source_manifest_sha256,
        args.destination,
        source_root=args.view_root,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
