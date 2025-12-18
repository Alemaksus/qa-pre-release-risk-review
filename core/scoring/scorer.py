from __future__ import annotations

from core.normalization.models import NormalizedData


def compute_metrics(data: NormalizedData) -> dict:
    """
    Compute metrics from normalized test data.

    Only counts passed/failed/skipped for mapped results (results where
    result.id exists in data.test_cases).
    """
    total_cases = len(data.test_cases)
    total_results = len(data.results)

    # Identify mapped and unmapped results
    mapped_results = [r for r in data.results if r.id in data.test_cases]
    unmapped_results = total_results - len(mapped_results)

    # Count statuses only for mapped results
    passed = sum(1 for r in mapped_results if r.status == "passed")
    failed = sum(1 for r in mapped_results if r.status == "failed")
    skipped = sum(1 for r in mapped_results if r.status == "skipped")

    # Calculate rates (avoid division by zero)
    mapped_count = len(mapped_results)
    failure_rate = failed / mapped_count if mapped_count > 0 else 0.0
    skip_rate = skipped / mapped_count if mapped_count > 0 else 0.0

    return {
        "total_cases": total_cases,
        "total_results": total_results,
        "mapped_results": mapped_count,
        "unmapped_results": unmapped_results,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "failure_rate": failure_rate,
        "skip_rate": skip_rate,
    }


def compute_release_readiness_score(metrics: dict) -> int:
    """
    Compute release readiness score (0-100).

    MVP formula:
    - start = 100
    - failed_penalty = min(60, metrics["failed"] * 10)
    - skipped_penalty = min(20, metrics["skipped"] * 2)
    - unmapped_penalty = min(20, metrics["unmapped_results"] * 2)
    - score = max(0, 100 - failed_penalty - skipped_penalty - unmapped_penalty)
    """
    start = 100
    failed_penalty = min(60, metrics["failed"] * 10)
    skipped_penalty = min(20, metrics["skipped"] * 2)
    unmapped_penalty = min(20, metrics["unmapped_results"] * 2)
    score = max(0, start - failed_penalty - skipped_penalty - unmapped_penalty)
    return int(score)


def classify_risk(score: int) -> str:
    """
    Classify risk level based on readiness score.

    - score >= 85 -> "Low"
    - 70 <= score <= 84 -> "Medium"
    - score < 70 -> "High"
    """
    if score >= 85:
        return "Low"
    elif score >= 70:
        return "Medium"
    else:
        return "High"

