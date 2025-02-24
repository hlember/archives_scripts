"""a script that looks for 'local_mss' and 'local_mss_er in consecutive lines, and swaps the order"""

from bs4 import BeautifulSoup

def er_mss_swap(xml_file, new_file):
 
    with open(xml_file, 'r') as file:
        content = file.read()

    soup = BeautifulSoup(content, 'xml')

    # Find all <unitid> tags with the required type attributes
    unitids = soup.find_all('unitid', {'type': ['local_mss', 'local_mss_er']})

    # Iterate over the <unitid> tags and swap them if they are consecutive
    for atr in range(len(unitids) - 1):
        if (unitids[atr]['type'] == 'local_mss' and unitids[atr + 1]['type'] == 'local_mss_er'):
            # Swap the tags in the original XML content
            unitids[atr].insert_before(unitids[atr + 1])
            unitids[atr + 1].insert_after(unitids[atr])

    with open(new_file, 'w') as file:
        file.write(str(soup))

xml_file = 'mss186236.xml'  # Replace with the path to your XML file
new_file = 'mss186236_modified.xml'  # The new file where the changes will be saved
er_mss_swap(xml_file, new_file)