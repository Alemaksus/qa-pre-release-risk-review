import pytest

from core.normalization.models import NormalizedData, TestCaseModel, TestResultModel
from core.scoring import classify_risk, compute_metrics, compute_release_readiness_score


def test_metrics_counts_only_mapped():
    """Verify unmapped results don't affect passed/failed/skipped counts."""
    test_cases = {
        "TC-1": TestCaseModel(id="TC-1", title="Test 1"),
        "TC-2": TestCaseModel(id="TC-2", title="Test 2"),
    }
    results = [
        TestResultModel(id="TC-1", status="passed"),
        TestResultModel(id="TC-2", status="failed"),
        TestResultModel(id="UNMAPPED-1", status="passed"),  # unmapped
        TestResultModel(id="UNMAPPED-2", status="failed"),  # unmapped
    ]

    data = NormalizedData(test_cases=test_cases, results=results)
    metrics = compute_metrics(data)

    assert metrics["total_cases"] == 2
    assert metrics["total_results"] == 4
    assert metrics["mapped_results"] == 2
    assert metrics["unmapped_results"] == 2
    assert metrics["passed"] == 1  # only TC-1
    assert metrics["failed"] == 1  # only TC-2
    assert metrics["skipped"] == 0


def test_failure_rate_and_skip_rate():
    """Verify correct calculation of failure and skip rates."""
    test_cases = {
        "TC-1": TestCaseModel(id="TC-1", title="Test 1"),
        "TC-2": TestCaseModel(id="TC-2", title="Test 2"),
        "TC-3": TestCaseModel(id="TC-3", title="Test 3"),
        "TC-4": TestCaseModel(id="TC-4", title="Test 4"),
    }
    results = [
        TestResultModel(id="TC-1", status="passed"),
        TestResultModel(id="TC-2", status="failed"),
        TestResultModel(id="TC-3", status="failed"),
        TestResultModel(id="TC-4", status="skipped"),
    ]

    data = NormalizedData(test_cases=test_cases, results=results)
    metrics = compute_metrics(data)

    assert metrics["mapped_results"] == 4
    assert metrics["failed"] == 2
    assert metrics["skipped"] == 1
    assert metrics["failure_rate"] == pytest.approx(0.5)  # 2/4
    assert metrics["skip_rate"] == pytest.approx(0.25)  # 1/4


def test_failure_rate_with_zero_mapped():
    """Verify rates are 0.0 when there are no mapped results."""
    test_cases = {
        "TC-1": TestCaseModel(id="TC-1", title="Test 1"),
    }
    results = [
        TestResultModel(id="UNMAPPED-1", status="failed"),
    ]

    data = NormalizedData(test_cases=test_cases, results=results)
    metrics = compute_metrics(data)

    assert metrics["mapped_results"] == 0
    assert metrics["failure_rate"] == 0.0
    assert metrics["skip_rate"] == 0.0


def test_score_bounds():
    """Verify score is always between 0 and 100."""
    # Test with many failures
    metrics_high_failures = {
        "failed": 100,
        "skipped": 0,
        "unmapped_results": 0,
    }
    score1 = compute_release_readiness_score(metrics_high_failures)
    assert 0 <= score1 <= 100

    # Test with many skipped
    metrics_high_skipped = {
        "failed": 0,
        "skipped": 100,
        "unmapped_results": 0,
    }
    score2 = compute_release_readiness_score(metrics_high_skipped)
    assert 0 <= score2 <= 100

    # Test with many unmapped
    metrics_high_unmapped = {
        "failed": 0,
        "skipped": 0,
        "unmapped_results": 100,
    }
    score3 = compute_release_readiness_score(metrics_high_unmapped)
    assert 0 <= score3 <= 100

    # Test with all penalties maxed
    metrics_all_maxed = {
        "failed": 100,
        "skipped": 100,
        "unmapped_results": 100,
    }
    score4 = compute_release_readiness_score(metrics_all_maxed)
    assert 0 <= score4 <= 100
    assert score4 == 0  # Should be 0 with all max penalties


def test_score_monotonicity():
    """Verify that more failures never increase the score."""
    metrics_low_failures = {
        "failed": 1,
        "skipped": 0,
        "unmapped_results": 0,
    }
    score_low = compute_release_readiness_score(metrics_low_failures)

    metrics_high_failures = {
        "failed": 10,
        "skipped": 0,
        "unmapped_results": 0,
    }
    score_high = compute_release_readiness_score(metrics_high_failures)

    assert score_high <= score_low


def test_risk_buckets():
    """Verify risk classification buckets."""
    assert classify_risk(85) == "Low"
    assert classify_risk(100) == "Low"
    assert classify_risk(84) == "Medium"
    assert classify_risk(70) == "Medium"
    assert classify_risk(69) == "High"
    assert classify_risk(0) == "High"


def test_score_integration():
    """Integration test: metrics -> score -> risk."""
    test_cases = {
        "TC-1": TestCaseModel(id="TC-1", title="Test 1"),
        "TC-2": TestCaseModel(id="TC-2", title="Test 2"),
        "TC-3": TestCaseModel(id="TC-3", title="Test 3"),
    }
    results = [
        TestResultModel(id="TC-1", status="passed"),
        TestResultModel(id="TC-2", status="failed"),
        TestResultModel(id="TC-3", status="skipped"),
    ]

    data = NormalizedData(test_cases=test_cases, results=results)
    metrics = compute_metrics(data)
    score = compute_release_readiness_score(metrics)
    risk = classify_risk(score)

    assert metrics["mapped_results"] == 3
    assert metrics["failed"] == 1
    assert metrics["skipped"] == 1
    assert isinstance(score, int)
    assert 0 <= score <= 100
    assert risk in ("Low", "Medium", "High")

