from __future__ import annotations

from datetime import datetime
from pathlib import Path


def save_markdown_report(markdown: str, output_dir: str = "reports", prefix: str = "pre_release_report") -> str:
    """
    Save markdown report to a timestamped file.

    Args:
        markdown: Markdown content to save
        output_dir: Directory to save the report (created if missing)
        prefix: Filename prefix (default: "pre_release_report")

    Returns:
        Absolute path to the saved file as a string
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.md"
    file_path = output_path / filename

    file_path.write_text(markdown, encoding="utf-8")

    return str(file_path.resolve())

