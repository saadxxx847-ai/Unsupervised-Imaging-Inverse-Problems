from __future__ import annotations

import argparse
from pathlib import Path

from ddm4ip.utils.benchmark_metrics import aggregate_summaries


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--oracle-summary", type=Path, required=True)
    parser.add_argument("--learned-summary", type=Path, action="append", required=True)
    parser.add_argument("--kernel-result", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if len(args.learned_summary) != 5:
        raise ValueError("pass exactly five --learned-summary arguments")
    if len(args.kernel_result) != 5:
        raise ValueError("pass exactly five --kernel-result arguments")
    aggregate_summaries(
        args.oracle_summary,
        args.learned_summary,
        args.output,
        kernel_paths=args.kernel_result,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
