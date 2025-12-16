from __future__ import annotations

import csv
from pathlib import Path

from core.errors import IngestionError


def load_test_cases_csv(path: str) -> list[dict]:
    """
    Load test cases from a CSV file into a normalized list of dictionaries.

    Output keys are exactly:
      { "id": str, "title": str, "description": str|None, "priority": str|None, "component": str|None }
    """
    csv_path = Path(path)
    try:
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            header_map = {_canon(h): h for h in headers if h is not None}

            id_col = _pick_col(header_map, {"id", "test_id", "case_id"})
            if id_col is None:
                raise IngestionError(
                    f"CSV '{path}': missing id column (expected one of: id, test_id, case_id)"
                )

            title_col = _pick_col(header_map, {"title", "name", "summary"})
            desc_col = _pick_col(header_map, {"description", "steps"})
            prio_col = _pick_col(header_map, {"priority", "severity"})
            comp_col = _pick_col(header_map, {"component", "area", "module"})

            out: list[dict] = []
            # csv.DictReader line numbers start at 2 for first data row (header is line 1)
            for row_idx, row in enumerate(reader, start=2):
                tc_id = _get_cell(row, id_col)
                if tc_id == "":
                    raise IngestionError(f"CSV '{path}': empty id at row {row_idx}")

                title = _get_cell(row, title_col) if title_col else ""
                description = _none_if_blank(_get_cell(row, desc_col)) if desc_col else None
                priority = _none_if_blank(_get_cell(row, prio_col)) if prio_col else None
                component = _none_if_blank(_get_cell(row, comp_col)) if comp_col else None

                out.append(
                    {
                        "id": tc_id,
                        "title": title,
                        "description": description,
                        "priority": priority,
                        "component": component,
                    }
                )

            return out
    except IngestionError:
        raise
    except FileNotFoundError as e:
        raise IngestionError(f"CSV '{path}': file not found") from e
    except OSError as e:
        raise IngestionError(f"CSV '{path}': unable to read file ({e})") from e
    except csv.Error as e:
        raise IngestionError(f"CSV '{path}': invalid CSV ({e})") from e


def _canon(header: str) -> str:
    return header.strip().lower()


def _pick_col(header_map: dict[str, str], candidates: set[str]) -> str | None:
    for c in candidates:
        if c in header_map:
            return header_map[c]
    return None


def _get_cell(row: dict, col_name: str | None) -> str:
    if not col_name:
        return ""
    v = row.get(col_name)
    if v is None:
        return ""
    return str(v).strip()


def _none_if_blank(v: str) -> str | None:
    return v if v != "" else None
