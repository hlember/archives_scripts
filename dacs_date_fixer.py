"""
script parses XML EAD file, reads <unitdate> tags,
and corrects dates that are not DACS compliant 
run from the command line 

"""
import argparse
from bs4 import BeautifulSoup
import re

def format_dacs_date(normal_date):
    months = {
        "01": "January", "02": "February", "03": "March", "04": "April",
        "05": "May", "06": "June", "07": "July", "08": "August",
        "09": "September", "10": "October", "11": "November", "12": "December"
    }

    def parse_date(date_str):
        parts = date_str.split('-')
        year = parts[0]
        month = months.get(f"{int(parts[1]):02d}") if len(parts) > 1 else ""
        day = str(int(parts[2])) if len(parts) > 2 else ""
        return year, month, day

    try:
        if '/' in normal_date:
            start_date, end_date = normal_date.split('/')
            start_year, start_month, start_day = parse_date(start_date)
            end_year, end_month, end_day = parse_date(end_date)

            if start_year == end_year:
                if start_month == end_month:
                    if start_day and end_day:
                        
                        return f"{start_year} {start_month} {start_day}–{end_day}"
                    else:
                       
                        return f"{start_year} {start_month}"
                else:
                
                    start_parts = " ".join(filter(None, [start_month, start_day]))
                    end_parts = " ".join(filter(None, [end_month, end_day]))
                    return f"{start_year} {start_parts}–{end_parts}".strip()
            else:
                
                start_parts = " ".join(filter(None, [start_year, start_month, start_day]))
                end_parts = " ".join(filter(None, [end_year, end_month, end_day]))
                return f"{start_parts}–{end_parts}".strip()
        else:
           
            year, month, day = parse_date(normal_date)
            return " ".join(filter(None, [year, month, day]))

    except Exception as e:
        print(f"Error: Could not process date '{normal_date}': {e}")
        return normal_date
    
def format_text_date_if_needed(text):
   
    abbreviations = {
        r"\bJan\.?\b": "January",
        r"\bFeb\.?\b": "February",
        r"\bMar\.?\b": "March",
        r"\bApr\.?\b": "April",
        r"\bJun\.?\b": "June",
        r"\bJul\.?\b": "July",
        r"\bAug\.?\b": "August",
        r"\bSep\.?\b": "September",
        r"\bOct\.?\b": "October",
        r"\bNov\.?\b": "November",
        r"\bDec\.?\b": "December"
    }

    full_months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    cleaned = text.strip()

    cleaned = re.sub(r'\s*[-–]\s*', '–', cleaned)

    cleaned = re.sub(r'\.(\d)', r'. \1', cleaned)

    for pattern, full in abbreviations.items():
        cleaned = re.sub(pattern, full, cleaned)

    for month in full_months:
        cleaned = re.sub(fr"\b{month}\.", month, cleaned)

    return cleaned

def update_unitdate_text(xml_content):
   
    soup = BeautifulSoup(xml_content, "xml")
    
    for unitdate in soup.find_all("unitdate"):
        normal = unitdate.get("normal")
        if normal:
            formatted_date = format_dacs_date(normal)
            unitdate.string = formatted_date
        else:
            original_text = unitdate.get_text()
            cleaned_text = format_text_date_if_needed(original_text)
            unitdate.string = cleaned_text

    return str(soup)

def main():
    parser = argparse.ArgumentParser(description="Update <unitdate> tags in an XML file to DACS-compliant dates.")
    parser.add_argument("input_file", help="Path to the input XML file")
    parser.add_argument("output_file", help="Path to save the updated XML file")
    
    args = parser.parse_args()

    with open(args.input_file, "r", encoding="utf-8") as file:
        xml_content = file.read()

    updated_xml = update_unitdate_text(xml_content)
    

    with open(args.output_file, "w", encoding="utf-8") as file:
        file.write(updated_xml)
    
    print(f"Updated XML file saved to {args.output_file}")


if __name__ == "__main__":
    main()