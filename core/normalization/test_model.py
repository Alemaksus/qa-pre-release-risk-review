from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TestCase:
    id: str
    title: str
    priority: str | None = None
    component: str | None = None
    description: str | None = None


@dataclass(frozen=True, slots=True)
class TestResult:
    id: str
    status: str
    duration_sec: float | None = None
    raw_name: str | None = None


@dataclass(frozen=True, slots=True)
class NormalizedData:
    test_cases: dict[str, TestCase]
    results: list[TestResult]


