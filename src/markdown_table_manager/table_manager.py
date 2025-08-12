"""
Table manipulation utilities for the Markdown Table Manager.

All business logic related to reading, writing and mutating markdown tables
is encapsulated in the ``TableManager`` class.  The MCP server (and any
future callers) should instantiate this class and invoke its methods rather
than re-implementing the logic.
"""

from pathlib import Path
from typing import List, Dict, Any

import pandas as pd

from . import config, parser


class TableManager:
    """
    Provides high-level operations on registered markdown tables.

    The methods raise ``ValueError`` for invalid table names or missing keys,
    ``IndexError`` for out-of-range row deletions, and ``KeyError`` for unknown
    column names.
    """

    def __init__(self) -> None:
        # No state is required beyond the configuration module.
        pass

    # --------------------------------------------------------------------- #
    # Helper methods
    # --------------------------------------------------------------------- #
    def _get_path(self, table_name: str) -> Path:
        """Return the Path object for a registered table or raise."""
        tables = config.list_tables()
        if table_name not in tables:
            raise ValueError(f"Table '{table_name}' is not registered.")
        return Path(tables[table_name])

    def _load_dataframe(self, table_name: str) -> pd.DataFrame:
        """Read the markdown file and return a DataFrame."""
        path = self._get_path(table_name)
        return parser.read_markdown_file(path)

    def _save_dataframe(self, table_name: str, df: pd.DataFrame) -> None:
        """Write the DataFrame back to the markdown file."""
        path = self._get_path(table_name)
        parser.write_markdown_file(path, df)

    def _first_column_unique(self, df: pd.DataFrame) -> bool:
        """Return ``True`` if the first column contains unique values."""
        if df.empty:
            return True
        first_col = df.columns[0]
        return df[first_col].is_unique

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #
    def list_entries(self, table_name: str) -> List[Dict[str, Any]]:
        """Return all rows of the table as a list of dictionaries."""
        df = self._load_dataframe(table_name)
        return df.to_dict(orient="records")

    def add_entry(self, table_name: str, entry: Dict[str, Any]) -> None:
        """
        Append a new row to the table.

        ``entry`` may omit some columns – missing columns are filled with an
        empty string to keep the table rectangular.

        If the target markdown file does not yet contain a table (i.e. the
        file is empty or has no recognizable markdown table), a new table is
        created.  The columns are derived from the keys of ``entry`` and any
        existing columns, preserving the original order and appending new
        columns at the end.
        """
        df = self._load_dataframe(table_name)

        # If the file had no table, start with an empty DataFrame.
        if df.empty and df.columns.empty:
            # Initialise with the columns present in the entry.
            df = pd.DataFrame(columns=list(entry.keys()))

        # Add any missing columns that are present in the entry but not in df.
        for col in entry.keys():
            if col not in df.columns:
                df[col] = ""

        # Preserve column order; fill missing columns with empty strings.
        new_row = [entry.get(col, "") for col in df.columns]
        df.loc[len(df)] = new_row

        self._save_dataframe(table_name, df)

    def delete_entry(self, table_name: str, row_index: int) -> None:
        """
        Delete the row at ``row_index`` (zero-based).

        Raises ``IndexError`` if the index is out of range.
        """
        df = self._load_dataframe(table_name)

        if row_index < 0 or row_index >= len(df):
            raise IndexError("Row index out of range.")

        df = df.drop(index=row_index).reset_index(drop=True)
        self._save_dataframe(table_name, df)

    def modify_entry(
        self, table_name: str, key: str, updates: Dict[str, Any]
    ) -> None:
        """
        Modify a row identified by the value in the first column.

        ``key`` is the primary-key value (the value in the first column).
        ``updates`` maps column names to their new values.

        Raises:
            ValueError - if the table is empty, the key does not exist, or
                         duplicate keys are found (should never happen if the
                         health check passes).
            KeyError   - if ``updates`` contains an unknown column name.
        """
        df = self._load_dataframe(table_name)

        if df.empty:
            raise ValueError("Table is empty; cannot modify entries.")

        first_col = df.columns[0]

        matches = df.index[df[first_col] == key].tolist()
        if not matches:
            raise ValueError(f"No entry found with key '{key}' in the first column.")
        if len(matches) > 1:
            raise ValueError(
                f"Multiple entries found with key '{key}'. First column must be unique."
            )

        row_idx = matches[0]

        for col, val in updates.items():
            if col not in df.columns:
                raise KeyError(f"Column '{col}' does not exist in table '{table_name}'.")
            df.at[row_idx, col] = val

        self._save_dataframe(table_name, df)

    # --------------------------------------------------------------------- #
    # Health-check helper (used by the MCP server)
    # --------------------------------------------------------------------- #
    def first_column_is_unique(self, table_name: str) -> bool:
        """Public wrapper for the uniqueness health-check."""
        df = self._load_dataframe(table_name)
        return self._first_column_unique(df)
