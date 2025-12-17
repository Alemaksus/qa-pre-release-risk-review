import pytest

from core.errors import ValidationError
from core.normalization import normalize
from core.normalization.models import NormalizedData, TestCaseModel, TestResultModel


def test_normalize_creates_test_cases():
    test_cases = [{"id": "TC-1", "title": "Test A"}]
    results = []

    data = normalize(test_cases, results)
    assert isinstance(data, NormalizedData)
    assert len(data.test_cases) == 1
    assert isinstance(data.test_cases["TC-1"], TestCaseModel)
    assert data.test_cases["TC-1"].id == "TC-1"
    assert data.test_cases["TC-1"].title == "Test A"
    assert data.test_cases["TC-1"].description is None


def test_normalize_raises_on_duplicate_test_case_id():
    test_cases = [
        {"id": "TC-1", "title": "Test A"},
        {"id": "TC-1", "title": "Test B"},
    ]
    results = []

    with pytest.raises(ValidationError) as e:
        normalize(test_cases, results)
    assert "Duplicate test case id: TC-1" in str(e.value)


def test_normalize_handles_empty_optional_fields():
    test_cases = [{"id": "TC-1", "title": ""}]
    results = [{"id": "R1", "status": "passed"}]

    data = normalize(test_cases, results)
    assert data.test_cases["TC-1"].title == ""
    assert data.test_cases["TC-1"].description is None
    assert data.test_cases["TC-1"].priority is None
    assert data.test_cases["TC-1"].component is None
    assert data.results[0].duration_sec is None
    assert data.results[0].raw_name is None


def test_normalize_raises_on_invalid_status():
    test_cases = []
    results = [{"id": "R1", "status": "unknown"}]

    with pytest.raises(ValidationError) as e:
        normalize(test_cases, results)
    assert "Invalid status" in str(e.value)
    assert "unknown" in str(e.value)


def test_normalize_parses_duration_sec_to_float():
    test_cases = []
    results = [
        {"id": "R1", "status": "passed", "duration_sec": "1.5"},
        {"id": "R2", "status": "failed", "duration_sec": 2.7},
    ]

    data = normalize(test_cases, results)
    assert data.results[0].duration_sec == 1.5
    assert data.results[1].duration_sec == 2.7


def test_normalize_raises_on_invalid_duration_sec():
    test_cases = []
    results = [{"id": "R1", "status": "passed", "duration_sec": "not-a-float"}]

    with pytest.raises(ValidationError) as e:
        normalize(test_cases, results)
    assert "Invalid duration_sec" in str(e.value)


def test_normalize_strips_whitespace_from_ids():
    test_cases = [{"id": "  TC-1  ", "title": "Test"}]
    results = [{"id": "  R1  ", "status": "passed"}]

    data = normalize(test_cases, results)
    assert "TC-1" in data.test_cases
    assert data.results[0].id == "R1"


def test_normalize_raises_on_empty_id():
    test_cases = [{"id": "   ", "title": "Test"}]
    results = []

    with pytest.raises(ValidationError) as e:
        normalize(test_cases, results)
    assert "empty or whitespace-only" in str(e.value)

