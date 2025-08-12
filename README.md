# Markdown Table Manager

A generic markdown table management tool with CLI and MCP integration, designed for Obsidian-style markdown tables.

## Features

- Register, list, and unregister markdown table files.
- Show status of registered tables, including column names and row counts.
- Run an MCP server to expose table operations (list, add, delete rows) to other tools.
- Works with any markdown file containing a standard pipe‑delimited table.
- Configuration stored in `~/.config/markdown_table_manager/config.json` (or a custom location via `MARKDOWN_TABLE_MANAGER_CONFIG_DIR`).

## Installation

```bash
uv tool install git+https://github.com/KoStard/markdown_table_manager
```

## Usage

```bash
# Register a table
markdown_table_manager register mytable /path/to/table.md
# If the specified markdown file does not exist, it will be created automatically.

# List all registered tables
markdown_table_manager list

# Unregister a table
markdown_table_manager unregister mytable

# Show detailed status (columns, row count)
markdown_table_manager status

# Start the MCP server (list/add/delete rows via MCP)
markdown_table_manager mcp-server
```

## ⚠️ Warning

**Important:** Once a markdown file is registered as a catalog table, it should not be modified directly with other tools or text editors. Doing so may cause data corruption or loss if the table format is changed. Always use the Markdown Table Manager or its MCP API to modify the contents of registered tables.

## Development

Run the test suite:

```bash
uv run pytest -v
```

The tests use a temporary configuration directory to avoid affecting your personal config.

## License

MIT
