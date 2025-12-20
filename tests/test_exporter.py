import re
from pathlib import Path

import pytest

from core.reporting.exporter import save_markdown_report


def test_save_markdown_report_creates_file(tmp_path):
    markdown_content = "hello"
    output_dir = str(tmp_path)

    file_path = save_markdown_report(markdown_content, output_dir=output_dir, prefix="test_report")

    # Check file exists
    path = tmp_path / Path(file_path).name
    assert path.exists()

    # Check filename matches pattern prefix_YYYYMMDD_HHMMSS.md
    filename = path.name
    pattern = r"^test_report_\d{8}_\d{6}\.md$"
    assert re.match(pattern, filename), f"Filename '{filename}' does not match pattern '{pattern}'"

    # Check contents
    assert path.read_text(encoding="utf-8") == "hello"


def test_save_markdown_report_creates_directory(tmp_path):
    output_dir = str(tmp_path / "reports" / "subdir")
    markdown_content = "test content"

    file_path = save_markdown_report(markdown_content, output_dir=output_dir)

    assert Path(output_dir).exists()
    assert Path(file_path).exists()
    assert Path(file_path).read_text(encoding="utf-8") == "test content"


def test_save_markdown_report_returns_absolute_path(tmp_path):
    output_dir = str(tmp_path)
    markdown_content = "content"

    file_path = save_markdown_report(markdown_content, output_dir=output_dir)

    assert Path(file_path).is_absolute()
    assert Path(file_path).exists()


def test_save_markdown_report_default_prefix(tmp_path):
    output_dir = str(tmp_path)
    markdown_content = "test"

    file_path = save_markdown_report(markdown_content, output_dir=output_dir)

    filename = Path(file_path).name
    pattern = r"^pre_release_report_\d{8}_\d{6}\.md$"
    assert re.match(pattern, filename), f"Filename '{filename}' does not match default prefix pattern"

