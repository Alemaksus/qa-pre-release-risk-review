from __future__ import annotations

from core.errors import ValidationError
from core.normalization.models import NormalizedData, TestCaseModel, TestResultModel

_VALID_STATUSES = {"passed", "failed", "skipped"}


def normalize(test_case_dicts: list[dict], result_dicts: list[dict]) -> NormalizedData:
    """
    Normalize test case and result dictionaries into typed dataclasses.

    Raises ValidationError for:
    - Duplicate test case ids
    - Invalid status values
    - Invalid duration_sec values
    - Empty/missing required fields
    """
    test_cases: dict[str, TestCaseModel] = {}
    for d in test_case_dicts:
        tc_id = _get_str_field(d, "id", required=True).strip()
        if tc_id == "":
            raise ValidationError("Test case id is empty or whitespace-only")
        if tc_id in test_cases:
            raise ValidationError(f"Duplicate test case id: {tc_id}")

        title = _get_str_field(d, "title", required=False) or ""
        description = _none_if_blank(_get_str_field(d, "description", required=False))
        priority = _none_if_blank(_get_str_field(d, "priority", required=False))
        component = _none_if_blank(_get_str_field(d, "component", required=False))

        test_cases[tc_id] = TestCaseModel(
            id=tc_id,
            title=title,
            description=description,
            priority=priority,
            component=component,
        )

    results: list[TestResultModel] = []
    for d in result_dicts:
        result_id = _get_str_field(d, "id", required=True).strip()
        if result_id == "":
            raise ValidationError("Test result id is empty or whitespace-only")

        status = _get_str_field(d, "status", required=True).strip()
        if status not in _VALID_STATUSES:
            raise ValidationError(f"Invalid status '{status}' (expected one of: {sorted(_VALID_STATUSES)})")

        duration_sec: float | None = None
        if "duration_sec" in d and d["duration_sec"] is not None:
            try:
                duration_sec = float(d["duration_sec"])
            except (ValueError, TypeError) as e:
                raise ValidationError(f"Invalid duration_sec value: {d['duration_sec']}") from e

        raw_name = _none_if_blank(_get_str_field(d, "raw_name", required=False))

        results.append(
            TestResultModel(
                id=result_id,
                status=status,
                duration_sec=duration_sec,
                raw_name=raw_name,
            )
        )

    return NormalizedData(test_cases=test_cases, results=results)


def _get_str_field(d: dict, key: str, required: bool) -> str:
    v = d.get(key)
    if v is None:
        if required:
            raise ValidationError(f"Missing required field: {key}")
        return ""
    return str(v).strip()


def _none_if_blank(v: str) -> str | None:
    return v if v != "" else None

