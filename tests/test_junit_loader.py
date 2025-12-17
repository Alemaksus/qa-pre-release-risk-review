import pytest

from core.errors import IngestionError
from core.ingestion.junit_loader import load_junit_results


def test_junit_parses_passed_failed_skipped(tmp_path):
    p = tmp_path / "junit.xml"
    p.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<testsuite name="suite">
  <testcase name="TC-1 ok" time="0.5" />
  <testcase name="TC-2 broken" time="1.2">
    <failure message="nope"/>
  </testcase>
  <testcase name="TC-3 skipped">
    <skipped/>
  </testcase>
</testsuite>
""",
        encoding="utf-8",
    )

    rows = load_junit_results(str(p))
    assert [r["status"] for r in rows] == ["passed", "failed", "skipped"]
    assert rows[0]["duration_sec"] == 0.5
    assert rows[1]["duration_sec"] == 1.2
    assert rows[2]["duration_sec"] is None


def test_junit_extracts_tc_id_from_name(tmp_path):
    p = tmp_path / "junit.xml"
    p.write_text(
        """<testsuite>
  <testcase name="login flow TC-123 should work"/>
</testsuite>
""",
        encoding="utf-8",
    )

    rows = load_junit_results(str(p))
    assert rows[0]["id"] == "TC-123"


def test_junit_falls_back_to_raw_name_when_no_tc_pattern(tmp_path):
    p = tmp_path / "junit.xml"
    p.write_text(
        """<testsuite>
  <testcase name="login works"/>
</testsuite>
""",
        encoding="utf-8",
    )

    rows = load_junit_results(str(p))
    assert rows[0]["id"] == "login works"
    assert rows[0]["raw_name"] == "login works"


def test_junit_raises_if_testcase_name_missing_or_empty(tmp_path):
    p = tmp_path / "junit.xml"
    p.write_text(
        """<testsuite>
  <testcase />
</testsuite>
""",
        encoding="utf-8",
    )

    with pytest.raises(IngestionError):
        load_junit_results(str(p))



