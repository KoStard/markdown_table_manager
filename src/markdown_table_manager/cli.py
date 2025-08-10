import argparse
from pathlib import Path
from . import config, parser
from .mcp_server import run_mcp_server


def cmd_register(args):
    config.register_table(args.name, args.path)
    print(f"Registered table '{args.name}' at {args.path}")


def cmd_unregister(args):
    config.unregister_table(args.name)
    print(f"Unregistered table '{args.name}'")


def cmd_list(args):
    tables = config.list_tables()
    if not tables:
        print("No tables registered.")
    for name, path in tables.items():
        print(f"{name}: {path}")


def cmd_status(args):
    tables = config.list_tables()
    for name, path in tables.items():
        table_path = Path(path)
        print(f"Table '{name}': {table_path}")
        try:
            df = parser.read_markdown_file(table_path)
            print(f"  Columns: {list(df.columns)}  Rows: {len(df)}")
        except Exception as e:
            print(f"  ERROR: {e}")


def cmd_mcp_server(args):
    run_mcp_server()


def main():
    ap = argparse.ArgumentParser(description="Markdown Table Manager CLI")
    sub = ap.add_subparsers()

    sp = sub.add_parser("register", help="Register a markdown table")
    sp.add_argument("name", help="Name for the table")
    sp.add_argument("path", type=Path, help="Path to markdown file")
    sp.set_defaults(func=cmd_register)

    sp = sub.add_parser("unregister", help="Unregister a markdown table")
    sp.add_argument("name")
    sp.set_defaults(func=cmd_unregister)

    sp = sub.add_parser("list", help="List registered tables")
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("status", help="Show tables info")
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("mcp-server", help="Run MCP server")
    sp.set_defaults(func=cmd_mcp_server)

    args = ap.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        ap.print_help()
