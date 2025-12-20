from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from core.errors import ValidationError

_PREFIX_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$")


@dataclass(frozen=True, slots=True)
class RunPlan:
    """CLI contract for running QA review."""

    tests_path: Path
    results_path: Path
    outdir: Path
    prefix: str
    format: str  # for now fixed to "md" but present for future compatibility


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with 'run' subcommand."""
    parser = argparse.ArgumentParser(description="QA review command-line interface")
    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=True)

    run_parser = subparsers.add_parser("run", help="Run QA review analysis")
    run_parser.add_argument(
        "--tests",
        required=True,
        help="Path to test cases file (CSV)",
    )
    run_parser.add_argument(
        "--results",
        required=True,
        help="Path to test results file (JUnit XML)",
    )
    run_parser.add_argument(
        "--outdir",
        default="reports",
        help="Output directory for reports (default: reports)",
    )
    run_parser.add_argument(
        "--prefix",
        default="pre_release_report",
        help="Filename prefix for output report (default: pre_release_report)",
    )
    run_parser.add_argument(
        "--format",
        choices=["md"],
        default="md",
        help="Output format (default: md)",
    )

    return parser


def parse_run_plan(argv: list[str]) -> RunPlan:
    """
    Parse command-line arguments and validate to produce a RunPlan.

    Raises ValidationError if validation fails.
    Raises SystemExit if argparse parsing fails (e.g., invalid argument format).
    """
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        # Re-raise SystemExit from argparse (e.g., for malformed arguments like --prefix -invalid)
        raise

    # Validate tests_path
    tests_str = args.tests
    if not tests_str or not tests_str.strip():
        raise ValidationError("tests path must be non-empty")
    tests_path = Path(tests_str)

    # Validate results_path
    results_str = args.results
    if not results_str or not results_str.strip():
        raise ValidationError("results path must be non-empty")
    results_path = Path(results_str)

    # Validate outdir
    outdir_str = args.outdir
    if not outdir_str or not outdir_str.strip():
        raise ValidationError("outdir must be non-empty")
    outdir = Path(outdir_str)

    # Validate prefix
    prefix = args.prefix
    if not _PREFIX_PATTERN.match(prefix):
        raise ValidationError(
            f"prefix '{prefix}' is invalid: must start with alphanumeric and contain only [a-zA-Z0-9_-], max 64 chars"
        )

    format_str = args.format

    return RunPlan(
        tests_path=tests_path,
        results_path=results_path,
        outdir=outdir,
        prefix=prefix,
        format=format_str,
    )


def main(argv: list[str] | None = None) -> int:
    """
    CLI entry point for QA review.

    On success: prints JSON to stdout and returns 0.
    On validation error: prints error message to stderr and returns 2.
    On parsing error: returns 2 (argparse prints usage).
    """
    if argv is None:
        argv = sys.argv[1:]

    try:
        run_plan = parse_run_plan(argv)
        output = {
            "tests": str(run_plan.tests_path),
            "results": str(run_plan.results_path),
            "outdir": str(run_plan.outdir),
            "prefix": run_plan.prefix,
            "format": run_plan.format,
        }
        print(json.dumps(output))
        return 0
    except ValidationError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except SystemExit as e:
        # argparse raises SystemExit on parse errors
        return 2

