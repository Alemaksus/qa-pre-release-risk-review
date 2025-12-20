#!/usr/bin/env python3
"""
Demo script to generate a pre-release QA risk review report.

Usage:
    python demo/generate_report.py --tests <csv_path> --results <junit_xml_path> [--outdir reports]
"""

import argparse
import sys
from pathlib import Path

from core.ingestion.csv_loader import load_test_cases_csv
from core.ingestion.junit_loader import load_junit_results
from core.pipeline import run_pipeline
from core.reporting.exporter import save_markdown_report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate pre-release QA risk review report from test cases and results"
    )
    parser.add_argument(
        "--tests",
        required=True,
        help="Path to CSV file with test cases",
    )
    parser.add_argument(
        "--results",
        required=True,
        help="Path to JUnit XML file with test results",
    )
    parser.add_argument(
        "--outdir",
        default="reports",
        help="Output directory for the report (default: reports)",
    )

    args = parser.parse_args()

    try:
        test_cases = load_test_cases_csv(args.tests)
        results = load_junit_results(args.results)

        output = run_pipeline(test_cases, results)

        report_path = save_markdown_report(
            output["markdown_report"],
            output_dir=args.outdir,
            prefix="pre_release_report",
        )

        print(f"Report saved: {report_path}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

