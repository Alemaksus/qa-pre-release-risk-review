from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Insight:
    """An insight derived from metrics, score, and risk."""

    code: str  # stable identifier, e.g. "FAILED_TESTS_PRESENT"
    severity: str  # "info" | "warning" | "critical"
    title: str  # short headline
    details: str  # one short paragraph


_SEVERITY_ORDER = {"critical": 0, "warning": 1, "info": 2}


def generate_insights(metrics: dict, score: int, risk: str) -> list[Insight]:
    """
    Generate deterministic insights from metrics, score, and risk.

    Returns a list sorted by severity (critical, warning, info) and then by code.
    Always includes at least one "info" insight for score summary.
    """
    insights: list[Insight] = []

    # Critical insights
    if metrics["failed"] > 0:
        insights.append(
            Insight(
                code="FAILED_TESTS_PRESENT",
                severity="critical",
                title="Failed Tests Detected",
                details=f"{metrics['failed']} test(s) failed, which may indicate functional issues that require immediate attention before release.",
            )
        )

    if metrics["mapped_results"] == 0:
        insights.append(
            Insight(
                code="NO_MAPPED_RESULTS",
                severity="critical",
                title="No Mapped Test Results",
                details="No test results were successfully mapped to test cases, indicating a potential traceability or data quality issue that needs resolution.",
            )
        )

    if risk == "High":
        insights.append(
            Insight(
                code="HIGH_RISK_CLASSIFICATION",
                severity="critical",
                title="High Risk Classification",
                details=f"The release readiness score of {score} indicates a high risk level, suggesting significant concerns that should be addressed before proceeding with release.",
            )
        )

    # Warning insights
    if metrics["unmapped_results"] > 0:
        insights.append(
            Insight(
                code="UNMAPPED_RESULTS_PRESENT",
                severity="warning",
                title="Unmapped Test Results",
                details=f"{metrics['unmapped_results']} test result(s) could not be mapped to test cases, which may indicate traceability gaps or missing test case definitions.",
            )
        )

    if metrics["skip_rate"] > 0.2:
        skip_pct = metrics["skip_rate"] * 100
        insights.append(
            Insight(
                code="HIGH_SKIP_RATE",
                severity="warning",
                title="High Skip Rate",
                details=f"Skip rate is {skip_pct:.1f}%, indicating a significant proportion of tests were not executed. This may reduce confidence in release readiness assessment.",
            )
        )

    if risk == "Medium":
        insights.append(
            Insight(
                code="MEDIUM_RISK_CLASSIFICATION",
                severity="warning",
                title="Medium Risk Classification",
                details=f"The release readiness score of {score} indicates a medium risk level, suggesting that some review and validation may be warranted before release.",
            )
        )

    # Info insights (always include at least one)
    insights.append(
        Insight(
            code="SCORE_SUMMARY",
            severity="info",
            title="Release Readiness Summary",
            details=f"The release readiness score is {score} out of 100, indicating a {risk.lower()} risk level. Review detailed metrics and recommendations for comprehensive assessment.",
        )
    )

    # Sort by severity (critical < warning < info), then by code alphabetically
    insights.sort(key=lambda i: (_SEVERITY_ORDER[i.severity], i.code))

    return insights

