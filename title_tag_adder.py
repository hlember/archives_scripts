""""script to add <title> tags to fileds in an excel file"""
"""can be revised to add different types of tags to use for ASpace processing spreadsheets"""
"""run in the command line: python3 inputfile.xlsx outputfile.xlsx column index number"""

import pandas as pd
import argparse

def wrap_with_title_tag(input_file, output_file, column_index):
    df = pd.read_excel(input_file)

    if column_index < 0 or column_index >= len(df.columns):
        raise IndexError(f"Column index {column_index} is out of range.")

    col_name = df.columns[column_index]

    df[col_name] = df[col_name].apply(
        lambda x: f"<title>{x}</title>" if pd.notna(x) and str(x).strip() != "" else x
    )
    df.to_excel(output_file, index=False)
    print(f" Updated Excel file saved as '{output_file}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wrap text in a column (by index) with <title> tags.")
    parser.add_argument("input_file", help="Path to input Excel file (.xlsx)")
    parser.add_argument("output_file", help="Path to save the output Excel file")
    parser.add_argument("column_index", type=int, help="Zero-based index of the column to wrap")

    args = parser.parse_args()
    wrap_with_title_tag(args.input_file, args.output_file, args.column_index)
