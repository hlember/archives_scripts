"""script that extracts container lists for EAD XML files"""
""" attributes can be revised for specific project"""
"""run in command line: python3 input_file.xml output_file.csv"""

import csv
import os
import argparse
from bs4 import BeautifulSoup

TARGET_TAG = 'container'
TARGET_ATTRIBUTE = 'type'
TARGET_VALUE = 'folder'

def extract_folder_containers_to_csv(xml_file, csv_file):
    if not os.path.exists(xml_file):
        print(f"Error: Input XML file not found at '{xml_file}'")
        return

    data_to_export = []

    try:
        with open(xml_file, 'r', encoding='utf-8') as f:
            xml_content = f.read()

        soup = BeautifulSoup(xml_content, 'lxml-xml')
        
        results = soup.find_all(TARGET_TAG, {TARGET_ATTRIBUTE: TARGET_VALUE})

        for element in results:
            container_type = element.get(TARGET_ATTRIBUTE)
            container_text = (element.string or '').strip()
            parent_element = element.parent

         
            title_tag = parent_element.find('unittitle')
            title_content = (title_tag.string or '').strip() if title_tag else ''

            date_tag = parent_element.find('unitdate')
            date_content = (date_tag.string or '').strip() if date_tag else ''

            
            physdesc_tag = parent_element.find('physdesc')
            physdesc_content = (physdesc_tag.string or '').strip() if physdesc_tag else ''
            
            data_to_export.append([container_type, container_text, title_content, date_content, physdesc_content])

    except Exception as e:
        print(f"An unexpected error occurred during XML processing: {e}")
        return

    # Write data to CSV
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
         
            writer.writerow(['container_type', 'container_indicator', 'title', 'date', 'PhysDesc'])
            
            writer.writerows(data_to_export)
        
        print(f"\nSuccessfully extracted {len(data_to_export)} entries.")
        print(f"Data saved to '{csv_file}' using Beautiful Soup.")

    except Exception as e:
        print(f"Error writing to CSV file: {e}")

def main():
    """Defines command-line arguments and initiates the extraction process."""
    parser = argparse.ArgumentParser(
        description="Extracts data from specific XML container tags into a CSV file."
    )
    
    parser.add_argument(
        'xml_file', 
        help="Path to the input XML file."
    )
    
    parser.add_argument(
        'csv_file', 
        nargs='?',
        default='extracted_folder_data.csv', 
        help="Path for the output CSV file (default: extracted_folder_data.csv)."
    )
    
    args = parser.parse_args()
    
    extract_folder_containers_to_csv(args.xml_file, args.csv_file)

if __name__ == '__main__':
    main()
