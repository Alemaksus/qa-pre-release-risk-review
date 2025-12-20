import pytest

from core.pipeline import run_pipeline


def test_pipeline_end_to_end_basic():
    test_cases = [
        {"id": "TC-1", "title": "A"},
        {"id": "TC-2", "title": "B"},
    ]
    results = [
        {"id": "TC-1", "status": "passed", "duration_sec": 1.0, "raw_name": "test_a"},
        {"id": "TC-2", "status": "failed", "duration_sec": 2.0, "raw_name": "test_b"},
        {"id": "OTHER", "status": "passed", "duration_sec": 1.0, "raw_name": "OTHER"},  # unmapped
    ]

    output = run_pipeline(test_cases, results)

    # Check all required keys exist
    assert "metrics" in output
    assert "score" in output
    assert "risk" in output
    assert "markdown_report" in output
    assert "counts" in output
    assert "insights" in output

    # Check counts structure
    counts = output["counts"]
    assert counts["test_cases_count"] == 2
    assert counts["results_count"] == 3
    assert counts["mapped_results_count"] == 2

    # Check metrics structure
    metrics = output["metrics"]
    assert metrics["total_cases"] == 2
    assert metrics["total_results"] == 3
    assert metrics["mapped_results"] == 2
    assert metrics["unmapped_results"] == 1
    assert metrics["passed"] == 1
    assert metrics["failed"] == 1
    assert metrics["skipped"] == 0

    # Check score is int in range 0-100
    assert isinstance(output["score"], int)
    assert 0 <= output["score"] <= 100

    # Check risk is valid
    assert output["risk"] in {"Low", "Medium", "High"}

    # Check markdown report structure
    markdown = output["markdown_report"]
    assert isinstance(markdown, str)
    assert "# Pre-Release QA Risk Review" in markdown
    assert "Score" in markdown or "Release Readiness Score" in markdown
    assert "## Key Insights" in markdown

    # Check insights structure
    insights = output["insights"]
    assert isinstance(insights, list)
    assert len(insights) > 0
    for insight in insights:
        assert "code" in insight
        assert "severity" in insight
        assert "title" in insight
        assert "details" in insight
        assert insight["severity"] in {"info", "warning", "critical"}


def test_pipeline_end_to_end_no_failures():
    test_cases = [
        {"id": "TC-1", "title": "Test A"},
        {"id": "TC-2", "title": "Test B"},
    ]
    results = [
        {"id": "TC-1", "status": "passed", "duration_sec": 1.0, "raw_name": "test_a"},
        {"id": "TC-2", "status": "passed", "duration_sec": 1.5, "raw_name": "test_b"},
    ]

    output = run_pipeline(test_cases, results)

    assert output["metrics"]["failed"] == 0
    assert output["metrics"]["passed"] == 2
    assert output["score"] >= 70  # Should be high with no failures
    assert output["risk"] in {"Low", "Medium"}


def test_pipeline_end_to_end_with_failures():
    test_cases = [
        {"id": "TC-1", "title": "Test A"},
        {"id": "TC-2", "title": "Test B"},
        {"id": "TC-3", "title": "Test C"},
    ]
    results = [
        {"id": "TC-1", "status": "failed", "duration_sec": 1.0, "raw_name": "test_a"},
        {"id": "TC-2", "status": "failed", "duration_sec": 1.5, "raw_name": "test_b"},
        {"id": "TC-3", "status": "passed", "duration_sec": 1.0, "raw_name": "test_c"},
    ]

    output = run_pipeline(test_cases, results)

    assert output["metrics"]["failed"] == 2
    assert output["metrics"]["passed"] == 1
    assert output["score"] < 100  # Should be penalized for failures
    assert "failed" in output["markdown_report"].lower() or "failure" in output["markdown_report"].lower()


def test_pipeline_end_to_end_with_unmapped():
    test_cases = [
        {"id": "TC-1", "title": "Test A"},
    ]
    results = [
        {"id": "TC-1", "status": "passed", "duration_sec": 1.0, "raw_name": "test_a"},
        {"id": "UNMAPPED-1", "status": "passed", "duration_sec": 1.0, "raw_name": "unmapped"},
        {"id": "UNMAPPED-2", "status": "failed", "duration_sec": 1.0, "raw_name": "unmapped2"},
    ]

    output = run_pipeline(test_cases, results)

    assert output["counts"]["mapped_results_count"] == 1
    assert output["metrics"]["unmapped_results"] == 2
    assert output["metrics"]["mapped_results"] == 1


def test_pipeline_end_to_end_empty_inputs():
    test_cases = []
    results = []

    output = run_pipeline(test_cases, results)

    assert output["counts"]["test_cases_count"] == 0
    assert output["counts"]["results_count"] == 0
    assert output["counts"]["mapped_results_count"] == 0
    assert output["metrics"]["total_cases"] == 0
    assert output["metrics"]["total_results"] == 0
    assert isinstance(output["score"], int)
    assert output["risk"] in {"Low", "Medium", "High"}


def test_pipeline_end_to_end_with_skipped():
    test_cases = [
        {"id": "TC-1", "title": "Test A"},
        {"id": "TC-2", "title": "Test B"},
    ]
    results = [
        {"id": "TC-1", "status": "passed", "duration_sec": 1.0, "raw_name": "test_a"},
        {"id": "TC-2", "status": "skipped", "duration_sec": 0.0, "raw_name": "test_b"},
    ]

    output = run_pipeline(test_cases, results)

    assert output["metrics"]["skipped"] == 1
    assert output["metrics"]["skip_rate"] > 0
    assert output["score"] < 100  # Should be penalized for skips

