import pytest

from core.errors import ValidationError
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

    output = run_pipeline(test_cases, results)
    counts = output["counts"]
    assert counts["test_cases_count"] == 2
    assert counts["results_count"] == 3
    assert counts["mapped_results_count"] == 2


def test_pipeline_counts_no_mapped_results():
    test_cases = [{"id": "TC-1", "title": "Test A"}]
    results = [
        {"id": "TC-X", "status": "passed"},
        {"id": "TC-Y", "status": "failed"},
    ]

    output = run_pipeline(test_cases, results)
    counts = output["counts"]
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

    output = run_pipeline(test_cases, results)
    counts = output["counts"]
    assert counts["test_cases_count"] == 2
    assert counts["results_count"] == 2
    assert counts["mapped_results_count"] == 2


def test_pipeline_propagates_validation_errors():
    test_cases = [
        {"id": "TC-1", "title": "Test A"},
        {"id": "TC-1", "title": "Test B"},  # duplicate
    ]
    results = []

    with pytest.raises(ValidationError):
        run_pipeline(test_cases, results)



