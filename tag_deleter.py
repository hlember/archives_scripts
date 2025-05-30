"""script that deletes XML tags and its content
   run in the command line
   eg: python3 tag_delter.py input.xml output.xml controlaccess [use any tag]
"""
import argparse
from bs4 import BeautifulSoup

def remove_tags(input_file, output_file, tag_name):
    
    with open(input_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'xml')

    for tag in soup.find_all(tag_name):
        tag.decompose()  

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(str(soup))

def main():
    parser = argparse.ArgumentParser(
        description='Remove specified tags (including content) from an XML file.'
    )
    parser.add_argument('input', help='Path to the input XML file')
    parser.add_argument('output', help='Path to save the output XML file')
    parser.add_argument('tag', help='Name of the XML tag to remove')

    args = parser.parse_args()
    remove_tags(args.input, args.output, args.tag)

if __name__ == '__main__':
    main()