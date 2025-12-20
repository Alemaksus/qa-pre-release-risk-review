from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScoringConfig:
    """Configuration for scoring and risk classification calculations."""

    max_failed_penalty: int = 60
    failed_penalty_per_test: int = 10

    max_skipped_penalty: int = 20
    skipped_penalty_per_test: int = 2

    max_unmapped_penalty: int = 20
    unmapped_penalty_per_result: int = 2

    low_risk_threshold: int = 85
    medium_risk_threshold: int = 70


def compute_score_with_config(metrics: dict, config: ScoringConfig) -> int:
    """
    Compute release readiness score (0-100) using configuration.

    Formula:
    - start = 100
    - failed_penalty = min(max_failed_penalty, metrics["failed"] * failed_penalty_per_test)
    - skipped_penalty = min(max_skipped_penalty, metrics["skipped"] * skipped_penalty_per_test)
    - unmapped_penalty = min(max_unmapped_penalty, metrics["unmapped_results"] * unmapped_penalty_per_result)
    - score = max(0, 100 - failed_penalty - skipped_penalty - unmapped_penalty)
    """
    start = 100
    failed_penalty = min(config.max_failed_penalty, metrics["failed"] * config.failed_penalty_per_test)
    skipped_penalty = min(config.max_skipped_penalty, metrics["skipped"] * config.skipped_penalty_per_test)
    unmapped_penalty = min(
        config.max_unmapped_penalty, metrics["unmapped_results"] * config.unmapped_penalty_per_result
    )
    score = max(0, start - failed_penalty - skipped_penalty - unmapped_penalty)
    return int(score)


def classify_risk_with_config(score: int, config: ScoringConfig) -> str:
    """
    Classify risk level based on readiness score using configuration.

    - score >= low_risk_threshold -> "Low"
    - medium_risk_threshold <= score < low_risk_threshold -> "Medium"
    - score < medium_risk_threshold -> "High"
    """
    if score >= config.low_risk_threshold:
        return "Low"
    elif score >= config.medium_risk_threshold:
        return "Medium"
    else:
        return "High"

