import pytest

from core.errors import IngestionError
from core.ingestion.csv_loader import load_test_cases_csv


def test_csv_supports_id_synonyms_test_id(tmp_path):
    p = tmp_path / "cases.csv"
    p.write_text("test_id,name\nTC-1,My Test\n", encoding="utf-8")

    rows = load_test_cases_csv(str(p))
    assert rows == [
        {
            "id": "TC-1",
            "title": "My Test",
            "description": None,
            "priority": None,
            "component": None,
        }
    ]


def test_csv_supports_id_synonyms_case_id(tmp_path):
    p = tmp_path / "cases.csv"
    p.write_text("case_id,summary\nTC-2,Another\n", encoding="utf-8")

    rows = load_test_cases_csv(str(p))
    assert rows[0]["id"] == "TC-2"
    assert rows[0]["title"] == "Another"


def test_csv_trims_whitespace(tmp_path):
    p = tmp_path / "cases.csv"
    p.write_text(
        " ID , Name , Description , Priority , Component \n  TC-3  ,  Title  ,  Desc  ,  High  ,  Payments  \n",
        encoding="utf-8",
    )

    rows = load_test_cases_csv(str(p))
    assert rows == [
        {
            "id": "TC-3",
            "title": "Title",
            "description": "Desc",
            "priority": "High",
            "component": "Payments",
        }
    ]


def test_csv_raises_if_id_column_missing(tmp_path):
    p = tmp_path / "cases.csv"
    p.write_text("name,description\nX,Y\n", encoding="utf-8")

    with pytest.raises(IngestionError) as e:
        load_test_cases_csv(str(p))
    assert "missing id column" in str(e.value).lower()


def test_csv_raises_if_row_id_empty(tmp_path):
    p = tmp_path / "cases.csv"
    p.write_text("id,name\n   ,X\n", encoding="utf-8")

    with pytest.raises(IngestionError) as e:
        load_test_cases_csv(str(p))
    msg = str(e.value).lower()
    assert "empty id" in msg
    assert "row" in msg



