from mcp.server.fastmcp import FastMCP
from . import config, parser
from pathlib import Path

mcp = FastMCP("Markdown Table Manager")


@mcp.tool(title="List table entries")
async def list_entries(table_name: str):
    """
    Lists all rows from the specified registered table.
    """
    tables = config.list_tables()
    if table_name not in tables:
        raise ValueError("Table not registered.")
    path = Path(tables[table_name])
    df = parser.read_markdown_file(path)
    return df.to_dict(orient="records")


@mcp.tool(title="Add table entry")
async def add_entry(table_name: str, entry: dict):
    """
    Adds a row to the specified registered table.
    """
    tables = config.list_tables()
    if table_name not in tables:
        raise ValueError("Table not registered.")
    path = Path(tables[table_name])
    df = parser.read_markdown_file(path)
    df.loc[len(df)] = [entry.get(c, "") for c in df.columns]
    parser.write_markdown_file(path, df)
    return {"status": "ok"}


@mcp.tool(title="Delete table entry")
async def delete_entry(table_name: str, row_index: int):
    """
    Deletes a row by index from the specified registered table.
    """
    tables = config.list_tables()
    if table_name not in tables:
        raise ValueError("Table not registered.")
    path = Path(tables[table_name])
    df = parser.read_markdown_file(path)
    if row_index < 0 or row_index >= len(df):
        raise IndexError("Row index out of range.")
    df = df.drop(index=row_index).reset_index(drop=True)
    parser.write_markdown_file(path, df)
    return {"status": "ok"}


def run_mcp_server():
    mcp.run()
