import re
from pathlib import Path
from typing import List, Dict
import pandas as pd


TABLE_REGEX = r"\|.*\|(?:\r?\n)\|[-\s|]*\|(?:\r?\n(?:\|.*\|(?:\r?\n|$))*)"


def parse_markdown_table(md_text: str) -> pd.DataFrame:
    match = re.search(TABLE_REGEX, md_text)
    if not match:
        raise ValueError("No markdown table found")
    table_text = match.group(0)
    lines = [line.strip() for line in table_text.split("\n") if line.strip()]
    header = [c.strip() for c in lines[0].split("|")[1:-1]]
    rows = [[c.strip() for c in line.split("|")[1:-1]] for line in lines[2:]]
    return pd.DataFrame(rows, columns=header)


def markdown_table_to_str(df: pd.DataFrame) -> str:
    header = "| " + " | ".join(df.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(df.columns)) + " |"
    rows = ["| " + " | ".join(map(str, row)) + " |" for _, row in df.iterrows()]
    return "\n".join([header, separator] + rows)


def update_markdown_table(md_text: str, df: pd.DataFrame) -> str:
    return re.sub(TABLE_REGEX, markdown_table_to_str(df), md_text)


def read_markdown_file(path: Path) -> pd.DataFrame:
    """
    Read a markdown file and return its table as a DataFrame.

    If the file does not contain a markdown table, an empty DataFrame is
    returned.  This allows callers (e.g., ``TableManager``) to create a new
    table from scratch by adding entries.
    """
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    try:
        return parse_markdown_table(content)
    except ValueError:
        # No table found – start with an empty DataFrame.
        return pd.DataFrame()


def write_markdown_file(path: Path, df: pd.DataFrame):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    updated = update_markdown_table(content, df)
    with open(path, "w", encoding="utf-8") as f:
        f.write(updated)
