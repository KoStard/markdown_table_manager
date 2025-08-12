from mcp.server.fastmcp import FastMCP
from . import config, parser
from .table_manager import TableManager
from pathlib import Path


def _first_column_unique(df) -> bool:
    """
    Check whether the first column of the DataFrame contains unique values.
    Returns True if all entries are unique, False otherwise.
    """
    if df.empty:
        return True
    first_col = df.columns[0]
    return df[first_col].is_unique


def _generate_instructions() -> str:
    """
    Build a detailed instruction string for the MCP server.

    It includes:
    * A short description of the server's purpose.
    * A list of registered tables together with their column schemas.
    * A summary of the available tools (list, add, delete, modify).
    * Health check notes, e.g., uniqueness of the first column.
    """
    tables = config.list_tables()
    if not tables:
        return (
            "Markdown Table Manager MCP Server.\n\n"
            "No tables are currently registered.\n\n"
            "Available tools:\n"
            "- list_entries(table_name): list all rows of a registered table.\n"
            "- add_entry(table_name, entry): add a row to a registered table.\n"
            "- delete_entry(table_name, row_index): delete a row from a registered table.\n"
            "- modify_entry(table_name, key, updates): modify a row identified by the first column.\n"
        )

    lines = [
        "Markdown Table Manager MCP Server.",
        "",
        "This server provides tools to list, add, delete, and modify rows in registered markdown tables.",
        "",
        "Registered tables and their schemas:",
    ]

    for name, path_str in tables.items():
        path = Path(path_str)
        try:
            df = parser.read_markdown_file(path)
            cols = ", ".join(df.columns)
            uniq_note = ""
            if not _first_column_unique(df):
                uniq_note = " (first column NOT unique!)"
            lines.append(f"- {name}: columns [{cols}]{uniq_note}")
        except Exception as e:
            # If the table cannot be read, still list it but note the error.
            lines.append(f"- {name}: could not read table ({e})")

    lines.extend(
        [
            "",
            "Available tools:",
            "- list_entries(table_name): returns all rows as a list of records.",
            "- add_entry(table_name, entry): adds a row; `entry` is a dict mapping column names to values.",
            "- delete_entry(table_name, row_index): deletes the row at the given zero‑based index.",
            "- modify_entry(table_name, key, updates): modifies a row identified by the first column value; "
            "`updates` is a dict of column/value pairs.",
            "- register_table(name, path): registers a markdown table file. The file must already exist and be a markdown file.",
            "",
            "Use these tools via MCP to manage your markdown tables programmatically.",
        ]
    )
    return "\n".join(lines)


def run_mcp_server():
    # Generate a helpful instruction string that includes registered tables and their schemas.
    mcp = FastMCP("Markdown Table Manager")
    manager = TableManager()

    instructions = _generate_instructions()

    @mcp.tool(title="List table entries", description=instructions)
    async def markdown_table_manager__list_entries(table_name: str):
        """
        Lists all rows from the specified registered table.
        """
        return manager.list_entries(table_name)

    @mcp.tool(title="Add table entry")
    async def markdown_table_manager__add_entry(table_name: str, entry: dict):
        """
        Adds a row to the specified registered table.
        """
        manager.add_entry(table_name, entry)
        return {"status": "ok"}

    @mcp.tool(title="Delete table entry")
    async def markdown_table_manager__delete_entry(table_name: str, row_index: int):
        """
        Deletes a row by index from the specified registered table.
        """
        manager.delete_entry(table_name, row_index)
        return {"status": "ok"}

    @mcp.tool(title="Modify table entry")
    async def markdown_table_manager__modify_entry(table_name: str, key: str, updates: dict):
        """
        Modifies a row in the specified registered table, identified by the value
        in the first column (the primary key). `updates` is a dict mapping column
        names to their new values.
        """
        manager.modify_entry(table_name, key, updates)
        return {"status": "ok"}

    @mcp.tool(title="Register table")
    async def markdown_table_manager__register_table(name: str, path: str):
        """
        Registers a markdown table file. The file must already exist and be a markdown file.
        """
        manager.register_table(name, Path(path))
        return {"status": "ok"}

    mcp.run()
