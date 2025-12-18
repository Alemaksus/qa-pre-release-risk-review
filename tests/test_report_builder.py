import pytest

from core.reporting import build_markdown_report


def test_report_contains_sections():
    """Verify all required section headers are present."""
    metrics = {
        "total_cases": 10,
        "total_results": 8,
        "mapped_results": 8,
        "unmapped_results": 0,
        "passed": 7,
        "failed": 1,
        "skipped": 0,
        "failure_rate": 0.125,
        "skip_rate": 0.0,
    }
    score = 88
    risk = "Low"

    report = build_markdown_report(metrics, score, risk)

    assert "# Pre-Release QA Risk Review" in report
    assert "## Executive Summary" in report
    assert "## Release Readiness Score" in report
    assert "## Key Metrics" in report
    assert "## High-Risk Indicators" in report
    assert "## Recommendations" in report


def test_metrics_rendering():
    """Verify numeric values from metrics appear in output."""
    metrics = {
        "total_cases": 25,
        "total_results": 20,
        "mapped_results": 18,
        "unmapped_results": 2,
        "passed": 15,
        "failed": 2,
        "skipped": 1,
        "failure_rate": 0.111,
        "skip_rate": 0.056,
    }
    score = 75
    risk = "Medium"

    report = build_markdown_report(metrics, score, risk)

    assert "25" in report  # total_cases
    assert "20" in report  # total_results
    assert "18" in report  # mapped_results
    assert "2" in report  # unmapped_results
    assert "15" in report  # passed
    assert "2" in report  # failed
    assert "1" in report  # skipped


def test_rates_formatting():
    """Verify failure_rate and skip_rate rendered as percentages with 1 decimal."""
    metrics = {
        "total_cases": 10,
        "total_results": 10,
        "mapped_results": 10,
        "unmapped_results": 0,
        "passed": 5,
        "failed": 3,
        "skipped": 2,
        "failure_rate": 0.3,
        "skip_rate": 0.2,
    }
    score = 50
    risk = "High"

    report = build_markdown_report(metrics, score, risk)

    assert "30.0%" in report  # failure_rate
    assert "20.0%" in report  # skip_rate

    # Test with more precise decimals
    metrics_precise = {
        "total_cases": 10,
        "total_results": 10,
        "mapped_results": 10,
        "unmapped_results": 0,
        "passed": 7,
        "failed": 2,
        "skipped": 1,
        "failure_rate": 0.1234,
        "skip_rate": 0.0567,
    }
    report2 = build_markdown_report(metrics_precise, 80, "Medium")
    assert "12.3%" in report2  # failure_rate rounded to 1 decimal
    assert "5.7%" in report2  # skip_rate rounded to 1 decimal


def test_high_risk_indicators_logic():
    """Verify conditional high-risk indicators logic."""
    # Test with failed > 0
    metrics_failed = {
        "total_cases": 10,
        "total_results": 10,
        "mapped_results": 10,
        "unmapped_results": 0,
        "passed": 8,
        "failed": 2,
        "skipped": 0,
        "failure_rate": 0.2,
        "skip_rate": 0.0,
    }
    report1 = build_markdown_report(metrics_failed, 80, "Medium")
    assert "failed" in report1.lower()
    assert "test(s) failed" in report1

    # Test with unmapped_results > 0
    metrics_unmapped = {
        "total_cases": 10,
        "total_results": 12,
        "mapped_results": 10,
        "unmapped_results": 2,
        "passed": 10,
        "failed": 0,
        "skipped": 0,
        "failure_rate": 0.0,
        "skip_rate": 0.0,
    }
    report2 = build_markdown_report(metrics_unmapped, 90, "Low")
    assert "unmapped" in report2.lower()
    assert "traceability gaps" in report2.lower()

    # Test with skip_rate > 0.2
    metrics_high_skip = {
        "total_cases": 10,
        "total_results": 10,
        "mapped_results": 10,
        "unmapped_results": 0,
        "passed": 7,
        "failed": 0,
        "skipped": 3,
        "failure_rate": 0.0,
        "skip_rate": 0.3,
    }
    report3 = build_markdown_report(metrics_high_skip, 70, "Medium")
    assert "skip rate" in report3.lower()
    assert "30.0%" in report3

    # Test with none of the conditions (should show "No critical risk indicators")
    metrics_clean = {
        "total_cases": 10,
        "total_results": 10,
        "mapped_results": 10,
        "unmapped_results": 0,
        "passed": 10,
        "failed": 0,
        "skipped": 0,
        "failure_rate": 0.0,
        "skip_rate": 0.0,
    }
    report4 = build_markdown_report(metrics_clean, 100, "Low")
    assert "No critical risk indicators detected" in report4


def test_recommendations_present():
    """Verify output contains at least 3 recommendation bullets."""
    metrics = {
        "total_cases": 10,
        "total_results": 10,
        "mapped_results": 10,
        "unmapped_results": 0,
        "passed": 8,
        "failed": 2,
        "skipped": 0,
        "failure_rate": 0.2,
        "skip_rate": 0.0,
    }
    score = 80
    risk = "Medium"

    report = build_markdown_report(metrics, score, risk)

    # Count recommendation bullets (lines starting with "-" after "## Recommendations")
    rec_section_start = report.find("## Recommendations")
    assert rec_section_start != -1

    rec_section = report[rec_section_start:]
    rec_bullets = [line for line in rec_section.split("\n") if line.strip().startswith("-")]
    assert len(rec_bullets) >= 3


def test_recommendations_conditional_logic():
    """Verify recommendations adapt based on metrics."""
    # Test with failed > 0
    metrics_failed = {
        "total_cases": 10,
        "total_results": 10,
        "mapped_results": 10,
        "unmapped_results": 0,
        "passed": 7,
        "failed": 3,
        "skipped": 0,
        "failure_rate": 0.3,
        "skip_rate": 0.0,
    }
    report1 = build_markdown_report(metrics_failed, 70, "Medium")
    assert "failed tests" in report1.lower() or "Address all failed" in report1

    # Test with unmapped_results > 0
    metrics_unmapped = {
        "total_cases": 10,
        "total_results": 15,
        "mapped_results": 10,
        "unmapped_results": 5,
        "passed": 10,
        "failed": 0,
        "skipped": 0,
        "failure_rate": 0.0,
        "skip_rate": 0.0,
    }
    report2 = build_markdown_report(metrics_unmapped, 90, "Low")
    assert "test-to-requirement mapping" in report2.lower() or "traceability" in report2.lower()

    # Test with skip_rate > 0.2
    metrics_high_skip = {
        "total_cases": 10,
        "total_results": 10,
        "mapped_results": 10,
        "unmapped_results": 0,
        "passed": 6,
        "failed": 0,
        "skipped": 4,
        "failure_rate": 0.0,
        "skip_rate": 0.4,
    }
    report3 = build_markdown_report(metrics_high_skip, 60, "High")
    assert "skipped tests" in report3.lower() or "skip rate" in report3.lower()


def test_executive_summary_mentions_score_and_risk():
    """Verify executive summary mentions score and risk level."""
    metrics = {
        "total_cases": 10,
        "total_results": 10,
        "mapped_results": 10,
        "unmapped_results": 0,
        "passed": 9,
        "failed": 1,
        "skipped": 0,
        "failure_rate": 0.1,
        "skip_rate": 0.0,
    }

    # Test with Low risk
    report_low = build_markdown_report(metrics, 85, "Low")
    assert "85" in report_low
    assert "low risk" in report_low.lower()

    # Test with Medium risk
    report_medium = build_markdown_report(metrics, 75, "Medium")
    assert "75" in report_medium
    assert "medium risk" in report_medium.lower()

    # Test with High risk
    report_high = build_markdown_report(metrics, 65, "High")
    assert "65" in report_high
    assert "high risk" in report_high.lower()


def test_score_display_format():
    """Verify score is displayed in the correct format."""
    metrics = {
        "total_cases": 10,
        "total_results": 10,
        "mapped_results": 10,
        "unmapped_results": 0,
        "passed": 10,
        "failed": 0,
        "skipped": 0,
        "failure_rate": 0.0,
        "skip_rate": 0.0,
    }

    report = build_markdown_report(metrics, 95, "Low")
    assert "**Score:** 95 / 100" in report
    assert "**Risk Level:** Low" in report

