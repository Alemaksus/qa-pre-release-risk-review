from __future__ import annotations

from collections.abc import Iterable, Mapping

from core.normalization.test_model import TestCase, TestResult


def run_pipeline(test_cases: Mapping[str, TestCase], test_results: Iterable[TestResult]) -> dict:
    """
    Phase 1 placeholder.

    Deterministic behavior: only validates basic types and returns counts.
    """
    if not isinstance(test_cases, Mapping):
        raise TypeError("test_cases must be a Mapping[str, TestCase]")

    for k, v in test_cases.items():
        if not isinstance(k, str):
            raise TypeError("test_cases keys must be str")
        if not isinstance(v, TestCase):
            raise TypeError("test_cases values must be TestCase")

    if not isinstance(test_results, Iterable):
        raise TypeError("test_results must be an Iterable[TestResult]")

    results_list: list[TestResult] = []
    for r in test_results:
        if not isinstance(r, TestResult):
            raise TypeError("test_results items must be TestResult")
        results_list.append(r)

    return {
        "test_cases_count": len(test_cases),
        "results_count": len(results_list),
    }


