from mcp.server.fastmcp import FastMCP
from . import config, parser
from pathlib import Path


def _generate_instructions() -> str:
    """
    Build a detailed instruction string for the MCP server.

    It includes:
    * A short description of the server's purpose.
    * A list of registered tables together with their column schemas.
    * A summary of the available tools (list, add, delete).
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
        )

    lines = [
        "Markdown Table Manager MCP Server.",
        "",
        "This server provides tools to list, add, and delete rows in registered markdown tables.",
        "",
        "Registered tables and their schemas:",
    ]

    for name, path_str in tables.items():
        path = Path(path_str)
        try:
            df = parser.read_markdown_file(path)
            cols = ", ".join(df.columns)
            lines.append(f"- {name}: columns [{cols}]")
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
            "",
            "Use these tools via MCP to manage your markdown tables programmatically.",
        ]
    )
    return "\n".join(lines)


def run_mcp_server():
    # Generate a helpful instruction string that includes registered tables and their schemas.
    mcp = FastMCP("Markdown Table Manager")

    instructions = _generate_instructions()

    @mcp.tool(title="List table entries", description=instructions)
    async def markdown_table_manager__list_entries(table_name: str):
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
    async def markdown_table_manager__add_entry(table_name: str, entry: dict):
        """
        Adds a row to the specified registered table.
        """
        tables = config.list_tables()
        if table_name not in tables:
            raise ValueError("Table not registered.")
        path = Path(tables[table_name])
        df = parser.read_markdown_file(path)
        # Ensure the entry aligns with the table's columns; missing columns get empty strings.
        df.loc[len(df)] = [entry.get(c, "") for c in df.columns]
        parser.write_markdown_file(path, df)
        return {"status": "ok"}

    @mcp.tool(title="Delete table entry")
    async def markdown_table_manager__delete_entry(table_name: str, row_index: int):
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

    mcp.run()
