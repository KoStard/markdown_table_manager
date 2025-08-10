import tempfile
import os
from pathlib import Path
import pandas as pd
from markdown_table_manager import parser, config
import pytest


@pytest.fixture(autouse=True)
def temp_config_dir(tmp_path, monkeypatch):
    # Redirect config dir to temporary path for all tests
    monkeypatch.setenv("MARKDOWN_TABLE_MANAGER_CONFIG_DIR", str(tmp_path))
    yield


def make_md(content: str) -> Path:
    path = Path(tempfile.gettempdir()) / "test_table.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def test_parse_and_write_roundtrip():
    sample = """# Heading

| Col1 | Col2 |
| --- | --- |
| A | B |"""
    path = make_md(sample)
    df = parser.read_markdown_file(path)
    assert list(df.columns) == ["Col1", "Col2"]
    assert df.iloc[0, 0] == "A"
    parser.write_markdown_file(path, df)
    reread = parser.read_markdown_file(path)
    pd.testing.assert_frame_equal(df, reread)


def test_register_and_list(tmp_path):
    # Register a table and check it appears in the list
    test_path = tmp_path / "table.md"
    test_path.write_text("| A | B |\n| --- | --- |\n| 1 | 2 |", encoding="utf-8")
    config.register_table("mytable", test_path)
    tables = config.list_tables()
    assert "mytable" in tables
    assert Path(tables["mytable"]) == test_path
