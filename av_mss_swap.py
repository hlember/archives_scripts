"""a script that looks for 'local_mss' and 'local_mss_av' in consecutive lines, and swaps the order
swapping the order fixes the aeon issue of every component being requestable twice"""

from bs4 import BeautifulSoup

def mss_av_swap(xml_file, new_file):
 
    with open(xml_file, 'r') as file:
        content = file.read()

    soup = BeautifulSoup(content, 'xml')

    unitids = soup.find_all('unitid', {'type': ['local_mss', 'local_mss_av']})

    for atr in range(len(unitids) - 1):
        if (unitids[atr]['type'] == 'local_mss' and unitids[atr + 1]['type'] == 'local_mss_av'):
          
            unitids[atr].insert_before(unitids[atr + 1])
            unitids[atr + 1].insert_after(unitids[atr])

    with open(new_file, 'w') as file:
        file.write(str(soup))


xml_file = 'mss1248.xml' 
new_file = 'mss1248_modified.xml' 

mss_av_swap(xml_file, new_file)