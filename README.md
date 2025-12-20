# Pre-Release QA Risk Review

A deterministic tool that analyzes test cases and test execution results to produce a clear release-readiness assessment report.

## What This Tool Does

- Provides an objective release readiness score (0-100) based on test execution outcomes
- Classifies release risk as Low, Medium, or High using transparent criteria
- Identifies critical issues that require attention before production release
- Generates structured insights highlighting failed tests, coverage gaps, and traceability issues
- Produces timestamped Markdown reports suitable for audit trails and stakeholder review
- Supports decision-making with actionable recommendations based on test metrics

## When This Is Useful

Use this tool when:
- You have test cases defined and test execution results available
- You need an independent assessment before making a production release decision
- Test results exist in multiple places but lack a consolidated risk view
- Stakeholders require clear, quantitative evidence of release readiness
- You want traceable documentation of pre-release QA assessment

This tool does not execute tests. It analyzes existing test artifacts to produce structured reports.

## Inputs

The tool requires two input files:

**Test Cases (CSV)**
- Standard CSV format with columns: test ID, title, description (optional), priority (optional), component (optional)
- Test ID field can be labeled as `id`, `test_id`, or `case_id`
- Title field can be labeled as `title`, `name`, or `summary`
- No special formatting or integration required

**Test Results (JUnit XML)**
- Standard JUnit XML format compatible with pytest, Allure, and other test runners
- Must include test case names that map to test case IDs
- Contains execution status: passed, failed, or skipped
- Duration information is optional

Both inputs are provided as local files. No API integrations or database connections are required.

## Outputs

The tool generates a timestamped Markdown report containing:

**Release Readiness Score**
- Numerical score from 0 to 100
- Derived from failed tests, skipped tests, and unmapped results
- Formula is documented and deterministic

**Risk Classification**
- Low: Score 85-100
- Medium: Score 70-84
- High: Score below 70

**Key Metrics**
- Total test cases and test results
- Passed, failed, and skipped counts
- Mapped vs. unmapped results (traceability)
- Failure rate and skip rate percentages

**Structured Insights**
- Critical issues requiring immediate attention
- Warning-level concerns that warrant review
- Informational summary of release readiness status

**High-Risk Indicators**
- Failed tests with potential functional impact
- Unmapped results indicating traceability gaps
- High skip rates reducing test coverage confidence

**Recommendations**
- Specific actions to address identified risks
- Validation steps before release
- Long-term quality improvement suggestions

Reports are saved with timestamped filenames (e.g., `pre_release_report_20241215_143022.md`) for traceability.

## Example Output

```markdown
## Release Readiness Score

**Score:** 65 / 100
**Risk Level:** High

## Key Insights

- **CRITICAL** Failed Tests Detected: 2 test(s) failed, which may indicate functional issues that require immediate attention before release.
- **CRITICAL** High Risk Classification: The release readiness score of 65 indicates a high risk level, suggesting significant concerns that should be addressed before proceeding with release.
- **WARNING** Unmapped Test Results: 1 test result(s) could not be mapped to test cases, which may indicate traceability gaps or missing test case definitions.
- **INFO** Release Readiness Summary: The release readiness score is 65 out of 100, indicating a high risk level. Review detailed metrics and recommendations for comprehensive assessment.
```

## Who This Is For

- QA Leads and Test Managers preparing release sign-off
- Product Managers evaluating release risk
- Engineering Managers needing objective quality indicators
- Founders of early-stage products without a dedicated QA team

## How to Use

The tool is executed via command-line interface. It can be run manually or as part of a CI pipeline that produces test artifacts.

```bash
python -m demo.generate_report --tests tests.csv --results results.xml --outdir reports
```

**Parameters:**
- `--tests`: Path to test cases CSV file (required)
- `--results`: Path to test results JUnit XML file (required)
- `--outdir`: Output directory for reports (default: `reports`)

**Example:**
```bash
python -m demo.generate_report --tests test_suite.csv --results junit_results.xml --outdir release_reports
```

The tool validates inputs and provides clear error messages for invalid data or missing required fields.

## Design Principles

- **Deterministic behavior**: Same inputs always produce the same outputs
- **Transparent scoring**: Scoring formula is explicit and documented
- **Clear validation**: Invalid inputs result in descriptive error messages
- **Reproducible results**: Reports can be regenerated and verified
- **No hidden logic**: All calculations and classifications are traceable

The tool is designed for reliability in both manual review workflows and automated CI/CD pipelines.

## Scope and Limitations

This tool explicitly does not:

- Execute tests or modify test data
- Integrate with test management platforms or CI/CD systems
- Make release decisions (provides assessment, not directives)
- Provide real-time dashboards or web interfaces
- Accept inputs from databases or APIs (file-based only)

The tool focuses solely on analyzing provided test artifacts and producing structured assessment reports. It does not replace human judgment in release decision-making.

## What This Is Not

This is not:
- A test automation framework
- A CI/CD plugin
- A real-time monitoring system
- A replacement for release ownership

The tool provides post-execution analysis of test results. It does not execute tests, monitor systems, or automate deployment processes.

## Intended Usage Context

This tool is designed for:

- **Independent QA review** before production releases
- **Audit-style analysis** of test execution quality
- **Stakeholder communication** with quantitative risk assessment
- **Documentation** of pre-release QA evaluation
- **Repeatable assessment** across multiple release cycles

It serves as a decision support tool that provides structured analysis of test outcomes, enabling informed release decisions based on objective metrics.
