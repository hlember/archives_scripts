"""looks for dates split between <unittitle> and <unitdate> and moves the whole thing to <unitdate>"""
"""then script formats the <unitdate> into DACS compliant formatting and deletes <unittitle> if it's empty"""
"""also adds 'inclusive' attribites to the <unitdate> field"""
"""run in the command line: python3 file.xml newfile.xml"""

from bs4 import BeautifulSoup
import re
from datetime import datetime

def normalize_date(year, month, day):
    """Return normal attribute in YYYY-MM-DD format."""
    month_num = datetime.strptime(month, "%B").month
    return f"{year}-{month_num:02d}-{int(day):02d}"

def process_xml(xml_content):
    soup = BeautifulSoup(xml_content, "xml")

    for component in soup.find_all(["c", "c01", "c02", "c03", "c04", "c05", "c06", "c07"]):
        unittitle = component.find("unittitle")
        unitdate = component.find("unitdate")

        if unittitle and unitdate:
            title_text = unittitle.get_text(strip=True)
            year_text = unitdate.get_text(strip=True)

            # Match month + day like "March 1" 
            match = re.match(r"([A-Za-z]+)\s+(\d{1,2})", title_text)
            if match and year_text.isdigit():
                month, day = match.groups()
                year = year_text

                # Format according to DACS
                new_text = f"{year} {month} {int(day)}"
                normal_attr = normalize_date(year, month, day)

                # Replace unitdate text and add attributes
                unitdate.string = new_text
                unitdate["type"] = "inclusive"
                unitdate["normal"] = normal_attr

                # Remove the date from unittitle text
                new_unittitle = re.sub(rf"{month}\s+{day}", "", title_text).strip()
                if new_unittitle:
                    unittitle.string = new_unittitle
                else:
                    unittitle.decompose()

    return str(soup)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Move dates from unittitle into unitdate")
    parser.add_argument("input", help="Input XML file")
    parser.add_argument("output", help="Output XML file")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        xml_content = f.read()

    updated_xml = process_xml(xml_content)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(updated_xml)