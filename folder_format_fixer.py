"""reads XML file and looks for extra spaces between dashes in folder ranges, and delete the spaces"""
"""run in the command line: python3 old.xml new.xml"""

from bs4 import BeautifulSoup
import re

def fix_folder_ranges(xml_content):
    soup = BeautifulSoup(xml_content, 'xml')

    # Find all container elements with type="folder"
    for container in soup.find_all('container', {'type': 'folder'}):
        if container.string:
            original_text = container.string
            # Replace patterns like "1 - 2" with "1-2"
            fixed_text = re.sub(r"(\d+)\s*-\s*(\d+)", r"\1-\2", original_text)
            container.string.replace_with(fixed_text)

    return str(soup)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Fix folder number ranges in XML')
    parser.add_argument('input', help='Input XML file')
    parser.add_argument('output', help='Output XML file')
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        xml_content = f.read()

    updated_xml = fix_folder_ranges(xml_content)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(updated_xml)