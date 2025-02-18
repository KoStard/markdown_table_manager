#!/usr/bin/env python3

import json
import sys
from pathlib import Path
from typing import List, Set

REQUIRED_FIELDS = {
    "name",
    "brand", 
    "type",
    "year",
    "notes"
}

def validate_json_file(file_path: Path) -> tuple[bool, Set[str], Set[str]]:
    """
    Validate a JSON file against required fields.
    Returns (is_valid, missing_fields, additional_fields)
    """
    try:
        with open(file_path) as f:
            data = json.load(f)
        
        # Convert all keys to lowercase for case-insensitive comparison
        present_fields = {k.lower() for k in data.keys()}
        missing_fields = REQUIRED_FIELDS - present_fields
        
        # Find additional fields
        additional_fields = present_fields - REQUIRED_FIELDS
        
        return (len(missing_fields) == 0, missing_fields, additional_fields)
    
    except json.JSONDecodeError:
        print(f"Error: {file_path} is not valid JSON")
        return (False, REQUIRED_FIELDS, set())
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        return (False, REQUIRED_FIELDS, set())

def main():
    if len(sys.argv) < 2:
        print("Usage: validate_json_schema.py <json_file1> [json_file2 ...]")
        sys.exit(1)

    all_valid = True
    
    for file_path in sys.argv[1:]:
        path = Path(file_path)
        print(f"\nChecking {path}:")
        
        is_valid, missing_fields, additional_fields = validate_json_file(path)
        
        if is_valid:
            print("✓ All required fields present")
        else:
            all_valid = False
            print("✗ Missing required fields:")
            for field in sorted(missing_fields):
                print(f"  - {field.capitalize()}")
        
        if additional_fields:
            print("! Additional fields found:")
            for field in sorted(additional_fields):
                print(f"  - {field.capitalize()}")

    sys.exit(0 if all_valid else 1)

if __name__ == "__main__":
    main()
