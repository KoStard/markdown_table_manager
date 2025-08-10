import os
import json
from pathlib import Path

import pytest

from markdown_table_manager import config, parser, table_manager


@pytest.fixture
def temp_config_dir(tmp_path, monkeypatch):
    """
    Create a temporary configuration directory and point the environment variable
    to it so that the library uses this location during the test.
    """
    config_dir = tmp_path / "config"
    monkeypatch.setenv("MARKDOWN_TABLE_MANAGER_CONFIG_DIR", str(config_dir))
    # Ensure a clean config file exists.
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "config.json").write_text(json.dumps({"tables": {}}))
    return config_dir


@pytest.fixture
def sample_table(tmp_path, temp_config_dir):
    """
    Create a temporary markdown file containing a simple table and register it.
    Returns the table name and the Path object.
    """
    table_name = "people"
    md_path = tmp_path / "people.md"
    md_content = """\
| id | name |
| --- | --- |
| 1 | Alice |
| 2 | Bob |
"""
    md_path.write_text(md_content)

    # Register the table using the library's config helper.
    config.register_table(table_name, md_path)

    return table_name, md_path


def test_list_entries(sample_table):
    table_name, _ = sample_table
    mgr = table_manager.TableManager()
    entries = mgr.list_entries(table_name)
    assert isinstance(entries, list)
    assert entries == [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
    ]


def test_add_entry(sample_table):
    table_name, _ = sample_table
    mgr = table_manager.TableManager()
    mgr.add_entry(table_name, {"id": "3", "name": "Charlie"})
    entries = mgr.list_entries(table_name)
    assert entries[-1] == {"id": "3", "name": "Charlie"}

    # Adding with missing column should fill with empty string.
    mgr.add_entry(table_name, {"id": "4"})
    entries = mgr.list_entries(table_name)
    assert entries[-1] == {"id": "4", "name": ""}


def test_delete_entry(sample_table):
    table_name, _ = sample_table
    mgr = table_manager.TableManager()
    # Delete the first row (index 0)
    mgr.delete_entry(table_name, 0)
    entries = mgr.list_entries(table_name)
    assert entries == [
        {"id": "2", "name": "Bob"},
    ]

    # Deleting out of range should raise IndexError
    with pytest.raises(IndexError):
        mgr.delete_entry(table_name, 10)


def test_modify_entry(sample_table):
    table_name, _ = sample_table
    mgr = table_manager.TableManager()
    # Change Bob's name to Bobby using the primary key (first column)
    mgr.modify_entry(table_name, "2", {"name": "Bobby"})
    entries = mgr.list_entries(table_name)
    assert entries[1] == {"id": "2", "name": "Bobby"}

    # Attempt to modify a non‑existent key
    with pytest.raises(ValueError):
        mgr.modify_entry(table_name, "999", {"name": "Nobody"})

    # Attempt to modify using an unknown column
    with pytest.raises(KeyError):
        mgr.modify_entry(table_name, "2", {"age": "30"})


def test_uniqueness_health_check(sample_table):
    table_name, _ = sample_table
    mgr = table_manager.TableManager()
    # Initially the first column is unique.
    assert mgr.first_column_is_unique(table_name) is True

    # Manually create a duplicate key in the markdown file.
    duplicate_md = """\
| id | name |
| --- | --- |
| 1 | Alice |
| 1 | Duplicate |
"""
    path = config.list_tables()[table_name]
    Path(path).write_text(duplicate_md)

    # The health‑check should now report False.
    assert mgr.first_column_is_unique(table_name) is False

    # The modify operation should raise because duplicates exist.
    with pytest.raises(ValueError):
        mgr.modify_entry(table_name, "1", {"name": "ShouldFail"})
