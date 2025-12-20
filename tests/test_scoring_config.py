from __future__ import annotations

import pytest

from core.scoring.scorer import compute_release_readiness_score, classify_risk
from pack.config import ScoringConfig, compute_score_with_config, classify_risk_with_config


def test_default_config_matches_core_behavior():
    metrics = {
        "total_cases": 10,
        "total_results": 8,
        "mapped_results": 7,
        "unmapped_results": 1,
        "passed": 5,
        "failed": 1,
        "skipped": 1,
        "failure_rate": 0.14285714285714285,
        "skip_rate": 0.14285714285714285,
    }

    default_config = ScoringConfig()

    core_score = compute_release_readiness_score(metrics)
    config_score = compute_score_with_config(metrics, default_config)
    assert core_score == config_score

    core_risk = classify_risk(core_score)
    config_risk = classify_risk_with_config(config_score, default_config)
    assert core_risk == config_risk


def test_custom_config_changes_score():
    metrics = {"failed": 2, "skipped": 0, "unmapped_results": 0}

    default_config = ScoringConfig()
    default_score = compute_score_with_config(metrics, default_config)

    custom_config = ScoringConfig(failed_penalty_per_test=5)
    custom_score = compute_score_with_config(metrics, custom_config)

    assert custom_score > default_score
    assert custom_score == 90
    assert default_score == 80


def test_custom_config_changes_risk_bucket():
    score = 75

    default_config = ScoringConfig()
    default_risk = classify_risk_with_config(score, default_config)
    assert default_risk == "Medium"

    custom_config = ScoringConfig(medium_risk_threshold=80)
    custom_risk = classify_risk_with_config(score, custom_config)
    assert custom_risk == "High"


def test_config_is_immutable():
    from dataclasses import FrozenInstanceError

    config = ScoringConfig()

    with pytest.raises(FrozenInstanceError):
        config.max_failed_penalty = 100

