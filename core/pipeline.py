from __future__ import annotations

from core.normalization import normalize


def run_pipeline(test_case_dicts: list[dict], result_dicts: list[dict]) -> dict:
    """
    Run the QA pipeline: normalize input data and compute basic counts.

    Returns dict with:
    - test_cases_count: number of unique test cases
    - results_count: number of test results
    - mapped_results_count: number of results with ids present in test_cases
    """
    data = normalize(test_case_dicts, result_dicts)

    test_cases_count = len(data.test_cases)
    results_count = len(data.results)

    mapped_results_count = sum(1 for r in data.results if r.id in data.test_cases)

    return {
        "test_cases_count": test_cases_count,
        "results_count": results_count,
        "mapped_results_count": mapped_results_count,
    }


