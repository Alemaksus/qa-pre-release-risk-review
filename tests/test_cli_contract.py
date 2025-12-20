from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from core.control.cli_contract import RunPlan, build_parser, main, parse_run_plan
from core.errors import ValidationError


def test_parse_run_plan_success_defaults():
    argv = ["run", "--tests", "a.csv", "--results", "b.xml"]
    plan = parse_run_plan(argv)

    assert plan.tests_path == Path("a.csv")
    assert plan.results_path == Path("b.xml")
    assert plan.outdir == Path("reports")
    assert plan.prefix == "pre_release_report"
    assert plan.format == "md"


def test_parse_run_plan_custom_values():
    argv = [
        "run",
        "--tests",
        "custom_tests.csv",
        "--results",
        "custom_results.xml",
        "--outdir",
        "custom_output",
        "--prefix",
        "custom_report",
        "--format",
        "md",
    ]
    plan = parse_run_plan(argv)

    assert plan.tests_path == Path("custom_tests.csv")
    assert plan.results_path == Path("custom_results.xml")
    assert plan.outdir == Path("custom_output")
    assert plan.prefix == "custom_report"
    assert plan.format == "md"


def test_prefix_validation_rejects_bad():
    # Prefixes that cause argparse to fail (starting with -) will raise SystemExit
    # Others will raise ValidationError
    bad_prefixes_validation = ["", " space", "../x", "x!", "_invalid", "valid-but-too-long-" + "x" * 50]
    bad_prefixes_argparse = ["-invalid"]

    for bad_prefix in bad_prefixes_validation:
        argv = ["run", "--tests", "a.csv", "--results", "b.xml", "--prefix", bad_prefix]
        with pytest.raises(ValidationError):
            parse_run_plan(argv)

    # Prefixes starting with - cause argparse to interpret as new option
    for bad_prefix in bad_prefixes_argparse:
        argv = ["run", "--tests", "a.csv", "--results", "b.xml", "--prefix", bad_prefix]
        with pytest.raises(SystemExit):
            parse_run_plan(argv)


def test_prefix_validation_accepts_good():
    good_prefixes = ["a", "A1", "test_report", "test-report", "test_report_123", "a" * 64]

    for good_prefix in good_prefixes:
        argv = ["run", "--tests", "a.csv", "--results", "b.xml", "--prefix", good_prefix]
        plan = parse_run_plan(argv)
        assert plan.prefix == good_prefix


def test_main_outputs_json_and_exit_code_0(capsys):
    argv = ["run", "--tests", "a.csv", "--results", "b.xml"]
    exit_code = main(argv)

    assert exit_code == 0
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert "tests" in output
    assert "results" in output
    assert "outdir" in output
    assert "prefix" in output
    assert "format" in output
    assert output["tests"] == "a.csv"
    assert output["results"] == "b.xml"
    assert output["outdir"] == "reports"
    assert output["prefix"] == "pre_release_report"
    assert output["format"] == "md"
    assert captured.err == ""


def test_main_validation_error_exit_code_2(capsys):
    argv = ["run", "--tests", "a.csv", "--results", "b.xml", "--prefix", "invalid!"]
    exit_code = main(argv)

    assert exit_code == 2
    captured = capsys.readouterr()
    assert "Error:" in captured.err
    assert captured.out == ""


def test_main_missing_required_args_exit_code_2(capsys):
    argv = ["run", "--tests", "a.csv"]
    exit_code = main(argv)

    assert exit_code == 2
    captured = capsys.readouterr()
    assert captured.out == ""


def test_parse_run_plan_validates_empty_paths():
    # Empty tests path
    with pytest.raises(ValidationError, match="tests path must be non-empty"):
        parse_run_plan(["run", "--tests", "", "--results", "b.xml"])

    # Empty results path
    with pytest.raises(ValidationError, match="results path must be non-empty"):
        parse_run_plan(["run", "--tests", "a.csv", "--results", ""])

    # Whitespace-only paths
    with pytest.raises(ValidationError, match="tests path must be non-empty"):
        parse_run_plan(["run", "--tests", "   ", "--results", "b.xml"])

    with pytest.raises(ValidationError, match="results path must be non-empty"):
        parse_run_plan(["run", "--tests", "a.csv", "--results", "   "])


def test_parse_run_plan_validates_empty_outdir():
    with pytest.raises(ValidationError, match="outdir must be non-empty"):
        parse_run_plan(["run", "--tests", "a.csv", "--results", "b.xml", "--outdir", ""])


def test_build_parser():
    parser = build_parser()
    assert parser is not None
    # Test that subparser exists
    args = parser.parse_args(["run", "--tests", "a.csv", "--results", "b.xml"])
    assert args.command == "run"
    assert args.tests == "a.csv"
    assert args.results == "b.xml"

