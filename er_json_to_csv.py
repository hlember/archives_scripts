"""script to transform a JSON export from FTK to csv for import into ArchivesSpace"""
"""run program in the command line"""
"""python3 er_json_to_csv.py input.json output.csv, replace with actual file names"""

import json
import csv
import re
import argparse

def format_extent(file_size_bytes, file_count):
    if file_size_bytes is None or file_count is None:
        return None

    size = float(file_size_bytes)
    orders = {
        1.0: 'bytes',
        1000.0: 'kilobytes',
        1000000.0: 'megabytes',
        1000000000.0: 'gigabytes',
        1000000000000.0: 'terabytes'
    }
    magnitudes = sorted(orders.keys(), reverse=True)
    magnitude = 1.0  # Default to bytes

    for mag in magnitudes:
        if size >= mag:
            magnitude = mag
            break

    return {
        'number': f"{size / magnitude:.1f}",
        'extent_type': orders[magnitude],
        'container_summary': f"{file_count} computer files",
        'portion': 'whole'
    }

def flatten_json(json_obj, parent_title="", flattened_list=[]):
    for child in json_obj.get('children', []):
        title = child.get('title', '')
        combined_title = f"{parent_title} > {title}" if parent_title else title

        er_name = child.get('er_name', '')
        date_found = None

        # Regular expression to find a comma followed by the specified date formats
        date_regex = r',\s*(' + \
             r'\d{4}-\d{4}' + r'|' + \
             r'circa\s+\d{4}' + r'|' + \
             r'\d{4}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}' + r'|' + \
             r'\d{4}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)' + r'|' + \
             r'\d{4}' + \
             r')'

        match = re.search(date_regex, er_name)
        if match:
            date_found = match.group(1).strip()
            # Remove the comma and the matched date from the ER Name
            er_name = re.sub(date_regex, '', er_name).strip()

        if 'er_number' in child:
            er_number = child['er_number']
            top_container_number = None
            if er_number and er_number.startswith('ER'):
                top_container_number = er_number[2:].strip()
                er_number_prefix = 'er'
            else:
                er_number_prefix = er_number  # Keep the original if it doesn't start with 'ER'

            file_size = child.get('file_size')
            file_count = child.get('file_count')
            extent = format_extent(file_size, file_count)

            row = {
                'ER Number': er_number_prefix,
                'Top Container Number': top_container_number,
                'ER Name': er_name,
                'Extent': extent,
            }
            if date_found:
                row['Date'] = date_found
            row.update({  # Add the rest of the fields
                'Hierarchy': combined_title
            })
            flattened_list.append(row)

        flatten_json(child, combined_title, flattened_list)

    return flattened_list

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a JSON file to a CSV file.")
    parser.add_argument("input_file", help="Path to the input JSON file.")
    parser.add_argument("output_file", help="Path to the output CSV file.")
    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file

    with open(input_file, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from '{input_file}': {e}")
            exit(1)

    flattened_data = flatten_json(data)

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['ER Number', 'Top Container Number', 'ER Name', 'Date', 'Extent', 'Hierarchy']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(flattened_data)

    print(f"Data has been successfully converted and saved to '{output_file}'")