"""Ingestion package (Phase 1 skeleton)."""

from .csv_loader import load_test_cases_csv
from .junit_loader import load_junit_results

__all__ = [
    "load_test_cases_csv",
    "load_junit_results",
]

