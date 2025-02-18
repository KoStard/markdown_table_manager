#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
from typing import Dict, Any
from tea_catalog_utils import add_tea_record

REQUIRED_COLUMNS = {'name', 'brand', 'type', 'year', 'notes'}

def format_column_name(name: str) -> str:
    """Format column name to Title Case."""
    return name.lower().capitalize()

def process_json_file(json_path: Path) -> Dict[str, Any]:
    """
    Process a JSON file and extract required columns case-insensitively.
    Returns formatted dictionary with proper column names.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create case-insensitive mapping of keys
    key_mapping = {k.lower(): k for k in data.keys()}
    
    # Extract and format required fields
    result = {}
    for required_col in REQUIRED_COLUMNS:
        lower_col = required_col.lower()
        if lower_col in key_mapping:
            value = data[key_mapping[lower_col]]
            result[format_column_name(required_col)] = '' if value is None else str(value)
        else:
            raise ValueError(f"Required column '{required_col}' not found in {json_path}")
    
    return result

def main():
    parser = argparse.ArgumentParser(description='Import tea records from JSON files to markdown catalog')
    parser.add_argument('json_files', nargs='+', type=Path, help='JSON files to process')
    parser.add_argument('--markdown', '-m', type=Path, required=True, 
                       help='Path to the markdown catalog file')
    
    args = parser.parse_args()
    
    # Validate JSON files exist
    for json_file in args.json_files:
        if not json_file.exists():
            raise FileNotFoundError(f"JSON file not found: {json_file}")
    
    # Process each JSON file
    for json_file in args.json_files:
        try:
            tea_record = process_json_file(json_file)
            add_tea_record(args.markdown, tea_record)
            print(f"Successfully processed: {json_file}")
        except Exception as e:
            print(f"Error processing {json_file}: {str(e)}")

if __name__ == "__main__":
    main()
