from __future__ import annotations

import re
from pathlib import Path
from xml.etree import ElementTree as ET

from core.errors import IngestionError

_TC_ID_RE = re.compile(r"\bTC-\d+\b")


def load_junit_results(path: str) -> list[dict]:
    """
    Load JUnit XML results into a list of dictionaries.

    Output keys are exactly:
      { "id": str, "status": str, "duration_sec": float|None, "raw_name": str|None }
    """
    xml_path = Path(path)
    try:
        tree = ET.parse(xml_path)
    except FileNotFoundError as e:
        raise IngestionError(f"JUnit '{path}': file not found") from e
    except OSError as e:
        raise IngestionError(f"JUnit '{path}': unable to read file ({e})") from e
    except ET.ParseError as e:
        raise IngestionError(f"JUnit '{path}': invalid XML ({e})") from e

    root = tree.getroot()

    out: list[dict] = []
    for tc in _iter_testcases(root):
        raw_name = (tc.attrib.get("name") or "").strip()

        duration_sec: float | None = None
        time_attr = tc.attrib.get("time")
        if time_attr is not None and time_attr.strip() != "":
            try:
                duration_sec = float(time_attr)
            except ValueError as e:
                raise IngestionError(
                    f"JUnit '{path}': invalid testcase time value '{time_attr}' for name '{raw_name}'"
                ) from e

        status = _status_from_testcase(tc)

        m = _TC_ID_RE.search(raw_name)
        result_id = m.group(0) if m else raw_name
        result_id = result_id.strip()
        if result_id == "":
            raise IngestionError(f"JUnit '{path}': empty testcase id (name missing or blank)")

        out.append(
            {
                "id": result_id,
                "status": status,
                "duration_sec": duration_sec,
                "raw_name": raw_name if raw_name != "" else None,
            }
        )

    return out


def _iter_testcases(root: ET.Element):
    # Supports <testsuite> root, <testsuites> root, or nested structures.
    for el in root.iter():
        if _local_name(el.tag) == "testcase":
            yield el


def _status_from_testcase(tc: ET.Element) -> str:
    has_failure_or_error = False
    has_skipped = False
    for child in list(tc):
        t = _local_name(child.tag)
        if t in {"failure", "error"}:
            has_failure_or_error = True
        elif t == "skipped":
            has_skipped = True

    if has_failure_or_error:
        return "failed"
    if has_skipped:
        return "skipped"
    return "passed"


def _local_name(tag: str) -> str:
    # Handles tags with namespaces: "{ns}testcase" -> "testcase"
    return tag.rsplit("}", 1)[-1]


