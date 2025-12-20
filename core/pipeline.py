from __future__ import annotations

from core.normalization import normalize
from core.scoring.scorer import compute_metrics
from core.reporting.report_builder import build_markdown_report
from pack.config import ScoringConfig, compute_score_with_config, classify_risk_with_config


def run_pipeline(test_case_dicts: list[dict], result_dicts: list[dict]) -> dict:
    """
    Run the end-to-end QA pipeline: normalize, compute metrics, score, risk, and generate report.

    Returns dict with:
    - metrics: dictionary from compute_metrics
    - score: release readiness score (0-100)
    - risk: risk level ("Low", "Medium", or "High")
    - markdown_report: complete markdown report string
    - counts: dictionary with test_cases_count, results_count, mapped_results_count
    """
    data = normalize(test_case_dicts, result_dicts)
    metrics = compute_metrics(data)
    config = ScoringConfig()
    score = compute_score_with_config(metrics, config)
    risk = classify_risk_with_config(score, config)
    markdown = build_markdown_report(metrics, score, risk)

    test_cases_count = len(data.test_cases)
    results_count = len(data.results)
    mapped_results_count = metrics["mapped_results"]

    return {
        "metrics": metrics,
        "score": score,
        "risk": risk,
        "markdown_report": markdown,
        "counts": {
            "test_cases_count": test_cases_count,
            "results_count": results_count,
            "mapped_results_count": mapped_results_count,
        },
    }


