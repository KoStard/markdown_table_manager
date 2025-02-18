import pandas as pd
import re

def read_markdown_table(file_path):
    """Read markdown file and extract the first table as DataFrame."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        # Return empty DataFrame with required columns
        return pd.DataFrame(columns=['Name', 'Brand', 'Type', 'Year', 'Notes'])
    
    # Find the table in the content
    table_pattern = r'\|.*\|[\r\n]\|[-\s|]*\|[\r\n](\|.*\|[\r\n])*'
    match = re.search(table_pattern, content)
    if not match:
        return pd.DataFrame(columns=['Name', 'Brand', 'Type', 'Year', 'Notes'])
    
    table_text = match.group(0)
    
    # Convert table text to DataFrame
    # Split into lines and clean up
    lines = [line.strip() for line in table_text.split('\n') if line.strip()]
    
    # Remove the separator line
    header = [col.strip() for col in lines[0].split('|')[1:-1]]
    rows = [[col.strip() for col in line.split('|')[1:-1]] for line in lines[2:]]
    
    return pd.DataFrame(rows, columns=header)

def dataframe_to_markdown(df):
    """Convert DataFrame to markdown table string."""
    # Create header
    header = '| ' + ' | '.join(df.columns) + ' |'
    
    # Create separator
    separator = '| ' + ' | '.join(['---' for _ in df.columns]) + ' |'
    
    # Create rows
    rows = []
    for _, row in df.iterrows():
        # Convert None/null to empty string
        formatted_cells = ['' if pd.isna(cell) else str(cell) for cell in row]
        rows.append('| ' + ' | '.join(formatted_cells) + ' |')
    
    return '\n'.join([header, separator] + rows)

def add_tea_record(file_path, tea_record):
    """Add a new tea record to the catalog.
    
    Args:
        file_path: Path to the markdown file
        tea_record: Dictionary with tea information matching table columns
    """
    # Find and extract the table
    table_pattern = r'\|.*\|[\r\n]\|[-\s|]*\|[\r\n](\|.*\|[\r\n])*'
    try:
        # Read current content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        match = re.search(table_pattern, content)
        if not match:
            # Create new content with empty table if no table exists
            df = pd.DataFrame(columns=['Name', 'Brand', 'Type', 'Year', 'Notes'])
            content = "# Tea Catalog\n\n" + dataframe_to_markdown(df) + "\n"
    except FileNotFoundError:
        # Create new file with empty table
        df = pd.DataFrame(columns=['Name', 'Brand', 'Type', 'Year', 'Notes'])
        content = "# Tea Catalog\n\n" + dataframe_to_markdown(df) + "\n"
    
    # Convert to DataFrame
    df = read_markdown_table(file_path)
    
    # Add new record
    df = pd.concat([df, pd.DataFrame([tea_record])], ignore_index=True)
    
    # Convert back to markdown
    new_table = dataframe_to_markdown(df)
    
    # Replace old table with new one
    new_content = re.sub(table_pattern, new_table + '\n', content)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

# Example usage
if __name__ == "__main__":
    # Example of reading
    df = read_markdown_table("tea_catalog.md")
    print("Current catalog:")
    print(df)
    
    # Example of adding a new tea
    new_tea = {
        "Name": "Earl Grey",
        "Type": "Black",
        "Origin": "Blend",
        "Price": "15.99",
        "Rating": "4.5"
    }
    
    add_tea_record("tea_catalog.md", new_tea)
    print("\nAfter adding new tea:")
    print(read_markdown_table("tea_catalog.md"))
