import pytest

from core.pipeline import run_pipeline


def test_pipeline_counts_mapped_results():
    test_cases = [
        {"id": "TC-1", "title": "Test A"},
        {"id": "TC-2", "title": "Test B"},
    ]
    results = [
        {"id": "TC-1", "status": "passed"},
        {"id": "TC-2", "status": "failed"},
        {"id": "TC-3", "status": "passed"},  # not in test_cases
    ]

    counts = run_pipeline(test_cases, results)
    assert counts["test_cases_count"] == 2
    assert counts["results_count"] == 3
    assert counts["mapped_results_count"] == 2


def test_pipeline_counts_no_mapped_results():
    test_cases = [{"id": "TC-1", "title": "Test A"}]
    results = [
        {"id": "TC-X", "status": "passed"},
        {"id": "TC-Y", "status": "failed"},
    ]

    counts = run_pipeline(test_cases, results)
    assert counts["test_cases_count"] == 1
    assert counts["results_count"] == 2
    assert counts["mapped_results_count"] == 0


def test_pipeline_counts_all_mapped():
    test_cases = [
        {"id": "TC-1", "title": "Test A"},
        {"id": "TC-2", "title": "Test B"},
    ]
    results = [
        {"id": "TC-1", "status": "passed"},
        {"id": "TC-2", "status": "failed"},
    ]

    counts = run_pipeline(test_cases, results)
    assert counts["test_cases_count"] == 2
    assert counts["results_count"] == 2
    assert counts["mapped_results_count"] == 2


def test_pipeline_propagates_validation_errors():
    test_cases = [
        {"id": "TC-1", "title": "Test A"},
        {"id": "TC-1", "title": "Test B"},  # duplicate
    ]
    results = []

    with pytest.raises(Exception):  # ValidationError from normalize
        run_pipeline(test_cases, results)

