"""script that pareses XML file for <unittitle> and capitializes the first letter of each word"""
"""Similar to the =PROPER() function in excel/google sheets"""

from bs4 import BeautifulSoup

def proper_title(tag):

    for element in tag.contents:
        if isinstance(element, str):
            tag.string = element.title()

def process_xml(input_file, output_file):

    with open(input_file, 'r') as file:
        soup = BeautifulSoup(file, 'xml')

    for unittitle in soup.find_all('unittitle'):
        proper_title(unittitle)

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(str(soup))

input_filename = 'input.xml'
output_filename = 'output.xml'

process_xml(input_filename, output_filename)