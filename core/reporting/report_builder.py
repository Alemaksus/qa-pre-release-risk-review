from __future__ import annotations


def build_markdown_report(metrics: dict, score: int, risk: str, insights: list | None = None) -> str:
    """
    Build a deterministic Markdown report for pre-release QA risk review.

    Args:
        metrics: Dictionary with keys: total_cases, total_results, mapped_results,
                 unmapped_results, passed, failed, skipped, failure_rate, skip_rate
        score: Release readiness score (0-100)
        risk: Risk level ("Low", "Medium", or "High")
        insights: Optional list of insights to include in the report

    Returns:
        Complete Markdown report as a string
    """
    lines = [
        "# Pre-Release QA Risk Review",
        "",
        "## Executive Summary",
        "",
        _build_executive_summary(score, risk),
        "",
        "## Release Readiness Score",
        "",
        f"**Score:** {score} / 100",
        f"**Risk Level:** {risk}",
        "",
        "## Key Metrics",
        "",
        f"- Total test cases: {metrics['total_cases']}",
        f"- Total test results: {metrics['total_results']}",
        f"- Mapped results: {metrics['mapped_results']}",
        f"- Unmapped results: {metrics['unmapped_results']}",
        f"- Passed: {metrics['passed']}",
        f"- Failed: {metrics['failed']}",
        f"- Skipped: {metrics['skipped']}",
        f"- Failure rate: {metrics['failure_rate'] * 100:.1f}%",
        f"- Skip rate: {metrics['skip_rate'] * 100:.1f}%",
        "",
    ]

    # Add insights section if provided
    if insights:
        lines.append("## Key Insights")
        lines.append("")
        for insight in insights:
            severity_upper = insight.severity.upper()
            lines.append(f"- **{severity_upper}** {insight.title}: {insight.details}")
        lines.append("")

    lines.append("## High-Risk Indicators")
    lines.append("")

    # Add high-risk indicators
    risk_indicators = _build_high_risk_indicators(metrics)
    lines.extend(risk_indicators)
    lines.append("")

    # Add recommendations
    lines.append("## Recommendations")
    lines.append("")
    recommendations = _build_recommendations(metrics)
    lines.extend(recommendations)

    return "\n".join(lines)


def _build_executive_summary(score: int, risk: str) -> str:
    """Build 2-4 sentence executive summary."""
    risk_lower = risk.lower()

    if risk == "Low":
        go_no_go = "The current test results suggest a favorable release outlook."
    elif risk == "Medium":
        go_no_go = "The current test results indicate moderate risk that warrants review before release."
    else:  # High
        go_no_go = "The current test results indicate elevated risk that requires attention before release."

    sentences = [
        f"This report provides an assessment of release readiness based on test execution results.",
        f"The release readiness score is {score} out of 100, indicating a {risk_lower} risk level.",
        go_no_go,
        "Review the detailed metrics and recommendations below to inform your release decision.",
    ]

    return " ".join(sentences)


def _build_high_risk_indicators(metrics: dict) -> list[str]:
    """Build conditional high-risk indicator bullets."""
    indicators = []

    if metrics["failed"] > 0:
        indicators.append(f"- {metrics['failed']} test(s) failed, indicating potential functional issues that may impact release quality.")

    if metrics["unmapped_results"] > 0:
        indicators.append(f"- {metrics['unmapped_results']} test result(s) could not be mapped to test cases, indicating traceability gaps in test coverage.")

    if metrics["skip_rate"] > 0.2:
        skip_pct = metrics["skip_rate"] * 100
        indicators.append(f"- Skip rate is {skip_pct:.1f}%, indicating a high proportion of tests were not executed, which may reduce confidence in release readiness.")

    if not indicators:
        indicators.append("- No critical risk indicators detected.")

    return indicators


def _build_recommendations(metrics: dict) -> list[str]:
    """Build 3-6 deterministic recommendation bullets."""
    recommendations = []

    if metrics["failed"] > 0:
        recommendations.append("- Address all failed tests before release. Investigate root causes and verify fixes through re-execution.")

    if metrics["unmapped_results"] > 0:
        recommendations.append("- Improve test-to-requirement mapping to ensure full traceability and coverage visibility.")

    if metrics["skip_rate"] > 0.2:
        recommendations.append("- Review and resolve reasons for skipped tests. High skip rates reduce test coverage confidence.")

    if metrics["failure_rate"] > 0.1:
        recommendations.append("- Investigate patterns in test failures to identify systemic issues that may require broader fixes.")

    # Always include at least one general recommendation
    if metrics["mapped_results"] > 0:
        recommendations.append("- Re-run test suite after addressing identified issues to validate fixes and confirm readiness.")
    else:
        recommendations.append("- Ensure test execution results are available and properly mapped to test cases for accurate assessment.")

    recommendations.append("- Monitor test execution trends over time to identify regressions and maintain release quality standards.")

    return recommendations

