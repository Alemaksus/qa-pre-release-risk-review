from __future__ import annotations

from pack.insights import Insight, generate_insights


def test_generate_insights_always_includes_score_summary():
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

    insights = generate_insights(metrics, 100, "Low")

    assert len(insights) >= 1
    score_insight = next((i for i in insights if i.code == "SCORE_SUMMARY"), None)
    assert score_insight is not None
    assert score_insight.severity == "info"
    assert "100" in score_insight.details
    assert "low" in score_insight.details.lower()


def test_severity_and_sorting_is_stable():
    metrics = {
        "total_cases": 10,
        "total_results": 10,
        "mapped_results": 0,  # triggers critical
        "unmapped_results": 1,  # triggers warning
        "passed": 0,
        "failed": 1,  # triggers critical
        "skipped": 0,
        "failure_rate": 1.0,
        "skip_rate": 0.0,
    }

    insights = generate_insights(metrics, 50, "High")

    # Check ordering: critical before warning before info
    severity_order = [i.severity for i in insights]
    assert severity_order.index("critical") < severity_order.index("warning") if "warning" in severity_order else True
    assert severity_order.index("warning") < severity_order.index("info") if "warning" in severity_order else True

    # Check within same severity, sorted by code alphabetically
    critical_codes = [i.code for i in insights if i.severity == "critical"]
    if len(critical_codes) > 1:
        assert critical_codes == sorted(critical_codes)

    warning_codes = [i.code for i in insights if i.severity == "warning"]
    if len(warning_codes) > 1:
        assert warning_codes == sorted(warning_codes)


def test_failed_adds_critical():
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

    insights = generate_insights(metrics, 80, "Medium")

    failed_insight = next((i for i in insights if i.code == "FAILED_TESTS_PRESENT"), None)
    assert failed_insight is not None
    assert failed_insight.severity == "critical"
    assert "2" in failed_insight.details
    assert "failed" in failed_insight.details.lower()


def test_unmapped_adds_warning():
    metrics = {
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

    insights = generate_insights(metrics, 90, "Low")

    unmapped_insight = next((i for i in insights if i.code == "UNMAPPED_RESULTS_PRESENT"), None)
    assert unmapped_insight is not None
    assert unmapped_insight.severity == "warning"
    assert "2" in unmapped_insight.details
    assert "mapped" in unmapped_insight.details.lower()


def test_skip_rate_threshold_adds_warning():
    metrics = {
        "total_cases": 10,
        "total_results": 10,
        "mapped_results": 10,
        "unmapped_results": 0,
        "passed": 7,
        "failed": 0,
        "skipped": 3,
        "failure_rate": 0.0,
        "skip_rate": 0.3,  # > 0.2 threshold
    }

    insights = generate_insights(metrics, 70, "Medium")

    skip_insight = next((i for i in insights if i.code == "HIGH_SKIP_RATE"), None)
    assert skip_insight is not None
    assert skip_insight.severity == "warning"
    assert "30.0" in skip_insight.details or "30" in skip_insight.details

