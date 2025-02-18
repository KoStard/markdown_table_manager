from tea_catalog_utils import read_markdown_table, add_tea_record

def test_tea_catalog():
    # Create a test markdown file
    test_content = """
# Tea Catalog

Welcome to our tea collection!

| Name | Type | Origin | Price | Rating |
| --- | --- | --- | --- | --- |
| Sencha | Green | Japan | 12.99 | 4.8 |
| Darjeeling | Black | India | 14.99 | 4.6 |

More text after the table.
"""
    
    with open("test_catalog.md", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    # Test reading
    df = read_markdown_table("test_catalog.md")
    print("Initial catalog:")
    print(df)
    
    # Test adding a new tea
    new_tea = {
        "Name": "Earl Grey",
        "Type": "Black",
        "Origin": "Blend",
        "Price": "15.99",
        "Rating": "4.5"
    }
    
    add_tea_record("test_catalog.md", new_tea)
    print("\nAfter adding new tea:")
    print(read_markdown_table("test_catalog.md"))
    
    # Show the final file content
    with open("test_catalog.md", "r", encoding="utf-8") as f:
        print("\nFinal file content:")
        print(f.read())

if __name__ == "__main__":
    test_tea_catalog()
