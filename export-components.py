"""
script that extracts container lists for EAD XML files
extracts all components, regardless of if there is a container attached
also indicates the level of description:

    - collection, series, subseries, file, item
    - <c01>, <c02>, etc 

attributes can be revised for specific project, hardcoded for:

    -tag_name
    -level
    - local_mss_id
    - local_mss_av
    - local_call
    - box_type
    - box_indicator
    - folder_type
    - folder_indicator 
    - title
    - date
    - scopecontent
    - physdesc
    - did_note
    
run in command line: python3 input_file.xml output_file.csv

"""

import csv
import os
import argparse
from bs4 import BeautifulSoup

def extract_ead_data_to_csv(xml_file, csv_file):
    if not os.path.exists(xml_file):
        print(f"Error: Input XML file not found at '{xml_file}'")
        return

    data_to_export = []

    try:
        with open(xml_file, 'r', encoding='utf-8') as f:
            xml_content = f.read()

        soup = BeautifulSoup(xml_content, 'lxml-xml')
        all_dids = soup.find_all('did')

        for did in all_dids:
            parent_element = did.parent
            
            # 1. Capture the XML Tag Name (e.g., c01, c02, c03, etc)
            tag_name = parent_element.name if parent_element else ''
            
            # 2. Capture the 'level' attribute (e.g., series, file)
            level = parent_element.get('level', '') if parent_element else ''

            # 3. UnitID Logic (local_mss, local_mss_av, and local_call)
            mss_tag = did.find('unitid', type='local_mss')
            mss_id = mss_tag.get_text(strip=True) if mss_tag else ''

            av_tag = did.find('unitid', type='local_mss_av')
            av_id = av_tag.get_text(strip=True) if av_tag else ''
            
            call_tag = did.find('unitid', type='local_call')
            call_id = call_tag.get_text(strip=True) if call_tag else ''

            # 4. Basic Metadata
            title_tag = did.find('unittitle')
            title_content = title_tag.get_text(" ", strip=True) if title_tag else ''

            date_tag = did.find('unitdate')
            date_content = date_tag.get_text(" ", strip=True) if date_tag else ''
            
            physdesc_tag = did.find('physdesc')
            physdesc_content = physdesc_tag.get_text(" ", strip=True) if physdesc_tag else ''

            # 5. Containers (Excel-Safe Formula Method)
            box_tag = did.find('container', type='box')
            if box_tag:
                box_type = box_tag.get('type', 'box')
                raw_box = (box_tag.get_text() or '').strip()
                box_indicator = f'="{raw_box}"' if raw_box else ''
            else:
                box_type = ''
                box_indicator = ''

            folder_tag = did.find('container', type='folder')
            if folder_tag:
                folder_type = folder_tag.get('type', 'folder')
                raw_folder = (folder_tag.get_text() or '').strip()
                folder_indicator = f'="{raw_folder}"' if raw_folder else ''
            else:
                folder_type = ''
                folder_indicator = ''

            # 6. Scopecontent & Notes
            note_tag = did.find('note', type='did')
            note_content = note_tag.get_text(" ", strip=True) if note_tag else ''

            scope_content = ''
            if parent_element:
                scope_tag = parent_element.find('scopecontent')
                if scope_tag:
                    scope_content = scope_tag.get_text(" ", strip=True)

            # Build Row
            data_to_export.append([
                tag_name, 
                level, 
                mss_id, 
                av_id, 
                call_id, 
                box_type, 
                box_indicator, 
                folder_type, 
                folder_indicator, 
                title_content, 
                date_content, 
                scope_content, 
                physdesc_content, 
                note_content
            ])

    except Exception as e:
        print(f"An unexpected error occurred during XML processing: {e}")
        return

    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'tag_name', 'level', 'local_mss', 'local_mss_av', 'local_call', 
                'box_type', 'box_indicator', 'folder_type', 'folder_indicator', 
                'title', 'date', 'scopecontent', 'physdesc', 'did_note'
            ])
            writer.writerows(data_to_export)
        
        print(f"\nSuccessfully extracted {len(data_to_export)} entries.")
        print(f"Data saved to '{csv_file}'")

    except Exception as e:
        print(f"Error writing to CSV file: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Extracts EAD components to CSV with Tag Levels and Excel-safe formatting."
    )
    parser.add_argument('xml_file', help="Path to the input XML file.")
    parser.add_argument('csv_file', nargs='?', default='extracted_ead_data.csv', 
                        help="Path for the output CSV file.")
    args = parser.parse_args()
    extract_ead_data_to_csv(args.xml_file, args.csv_file)

if __name__ == '__main__':
    main()