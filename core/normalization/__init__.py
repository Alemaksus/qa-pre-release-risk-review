"""Normalization package (Phase 1 skeleton)."""

from .normalizer import normalize
from .models import NormalizedData, TestCaseModel, TestResultModel

__all__ = [
    "normalize",
    "NormalizedData",
    "TestCaseModel",
    "TestResultModel",
]
