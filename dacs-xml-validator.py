"""
script that reads DACS and an XML file and checks if it's DACS compliant
reads DACS Part I and Part II
returns list of missing and present DACS elements
"""

# pip3 install requests beautifulsoup4 lxml 
# run in the command line: python3 dacs_validator.py path/to/finding_aid.xml

import requests
from bs4 import BeautifulSoup
import re
import os
import argparse
from lxml import etree

dacs_url = 'https://saa-ts-dacs.github.io/'

class DACSValidator:
    def __init__(self):
        self.requirements = []

    def fetch_dacs_standards(self):
        """
        Scrapes the DACS website to find 'Required', 'Optimum', and 'Added Value' elements.
        Manually adds 'Abstract' as a Required element.
        """
        print(f'Reading DACS standards from {dacs_url}...')
        try:
            response = requests.get(dacs_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            found_rules = []
            # Regex to capture Required, Optimum, and Added Value
            pattern = re.compile(r"(\d+\.\d+(?:\.\d+)?)\s+(.*?)\s+\((Required|Optimum|Added Value)\)", re.IGNORECASE)
            seen_ids = set()
            
            for element in soup.find_all(['a', 'h2', 'h3', 'p', 'li']):
                text = element.get_text(" ", strip=True)
                match = pattern.search(text)
                if match:
                    rule_num = match.group(1)
                    rule_name = match.group(2)
                    status = match.group(3)
                    
                    if "added value" in status.lower():
                        status = "Added Value"
                    else:
                        status = status.capitalize()
                    
                    full_label = f"{rule_num} {rule_name}"
                    
                    if rule_num not in seen_ids:
                        found_rules.append({
                            "id": rule_num,
                            "name": rule_name,
                            "full": full_label,
                            "status": status
                        })
                        seen_ids.add(rule_num)
            
            # --- MANUAL INJECTIONS ---

            # 1.0 Level of Description
            if not any(r['id'] == "1.0" for r in found_rules):
                found_rules.insert(0, {
                    "id": "1.0", "name": "Level of Description", "full": "1.0 Level of Description", "status": "Required"
                })

            # 3.1.Abstract (DACS Commentary - Institutional Requirement)
            # We inject this manually because it is buried in commentary on the website
            if not any(r['id'] == "3.1.Abstract" for r in found_rules):
                found_rules.append({
                    "id": "3.1.Abstract", 
                    "name": "Abstract", 
                    "full": "3.1 Commentary: Abstract", 
                    "status": "Required" 
                })

            # 7.1.x Specific Notes (Manually defined as specific "Added Value" types)
            note_types = [
                ("7.1.1", "General Note"),
                ("7.1.2", "Conservation Note"),
                ("7.1.3", "Citation Note"),
                ("7.1.4", "Custodial History Note"),
                ("7.1.5", "Appraisal Note"),
                ("7.1.6", "Accruals Note"),
                ("7.1.7", "Reproduction and Use Note"),
                ("7.1.8", "Processing Information"),
            ]

            for nid, nname in note_types:
                if not any(r['id'] == nid for r in found_rules):
                    found_rules.append({
                        "id": nid, "name": nname, "full": f"{nid} {nname}", "status": "Added Value"
                    })

            # Updated sort key to handle non-numeric IDs like "3.1.Abstract"
            def sort_key(x):
                parts = x['id'].split('.')
                cleaned_parts = []
                for p in parts:
                    try:
                        cleaned_parts.append(int(p))
                    except ValueError:
                        # If part is text (e.g. "Abstract"), treat it as a high number to put it at the end of the section
                        cleaned_parts.append(999) 
                return cleaned_parts
            
            self.requirements = sorted(found_rules, key=sort_key)
            print(f'Successfully identified {len(self.requirements)} DACS elements (Required, Optimum & Added Value).')
            
        except Exception as e:
            print(f"Error reading DACS standards: {e}")
            # Fallback list if scraping fails
            self.requirements = [
                {"id": "1.0", "name": "Level of Description", "full": "1.0 Level of Description", "status": "Required"},
                {"id": "2.1", "name": "Reference Code", "full": "2.1 Reference Code", "status": "Required"},
                {"id": "2.2", "name": "Name and Location of Repository", "full": "2.2 Name and Location of Repository", "status": "Required"},
                {"id": "2.3", "name": "Title", "full": "2.3 Title", "status": "Required"},
                {"id": "2.4", "name": "Date", "full": "2.4 Date", "status": "Required"},
                {"id": "2.5", "name": "Extent", "full": "2.5 Extent", "status": "Required"},
                {"id": "2.6", "name": "Name of Creator(s)", "full": "2.6 Name of Creator(s)", "status": "Required"},
                {"id": "2.7", "name": "Administrative/Biographical History", "full": "2.7 Administrative/Biographical History", "status": "Optimum"},
                {"id": "3.1", "name": "Scope and Content", "full": "3.1 Scope and Content", "status": "Required"},
                {"id": "3.1.Abstract", "name": "Abstract", "full": "3.1 Commentary: Abstract", "status": "Required"},
                {"id": "3.2", "name": "System of Arrangement", "full": "3.2 System of Arrangement", "status": "Added Value"},
                {"id": "4.1", "name": "Conditions Governing Access", "full": "4.1 Conditions Governing Access", "status": "Required"},
                {"id": "4.5", "name": "Languages and Scripts of the Material", "full": "4.5 Languages and Scripts of the Material", "status": "Required"},
                
                {"id": "7.1.1", "name": "General Note", "full": "7.1.1 General Note", "status": "Added Value"},
                {"id": "7.1.2", "name": "Conservation Note", "full": "7.1.2 Conservation Note", "status": "Added Value"},
                {"id": "7.1.3", "name": "Citation Note", "full": "7.1.3 Citation Note", "status": "Added Value"},
                {"id": "7.1.4", "name": "Custodial History Note", "full": "7.1.4 Custodial History Note", "status": "Added Value"},
                {"id": "7.1.5", "name": "Appraisal Note", "full": "7.1.5 Appraisal Note", "status": "Added Value"},
                {"id": "7.1.6", "name": "Accruals Note", "full": "7.1.6 Accruals Note", "status": "Added Value"},
                {"id": "7.1.7", "name": "Reproduction and Use Note", "full": "7.1.7 Reproduction and Use Note", "status": "Added Value"},
                {"id": "7.1.8", "name": "Processing Information", "full": "7.1.8 Processing Information", "status": "Added Value"},

                {"id": "10.1", "name": "Authorized Form of the Name", "full": "10.1 Authorized Form of the Name", "status": "Required"},
                {"id": "13.2", "name": "Authority Record Identifier", "full": "13.2 Authority Record Identifier", "status": "Required"},
            ]

    def validate_ead_xml(self, file_path):
        
        print(f"\nAnalyzing EAD XML: {file_path}")
        try:
            tree = etree.parse(file_path)
            root = tree.getroot()
            
            # Handle Namespaces (strip them for easier processing)
            for elem in root.getiterator():
                if not hasattr(elem.tag, 'find'): continue
                elem.tag = etree.QName(elem).localname
            
            present_elements = []
            missing_elements = []
            
            # Check Chapter 1 (Level of Description attribute)
            has_level = False
            if root.get('level') or root.find(".//archdesc[@level]") is not None:
                has_level = True

            dacs_xpath_map = {
                # DACS Chapter 1: Level
                "1.0": ["//@level", "//archdesc/@level"],

                # DACS Part I: Required
                "2.1": ["//unitid", "//eadid"],
                "2.2": ["//repository"],
                "2.3": ["//unittitle", "//titleproper"],
                "2.4": ["//unitdate"],
                "2.5": ["//physdesc/extent", "//physdesc", "//extent"],
                "2.6": ["//origination", "//origination/persname", "//origination/corpname", "//origination/famname"],
                "3.1": ["//scopecontent"],
                
                # Maps the custom ID to the Abstract tag
                "3.1.Abstract": ["//abstract", "//did/abstract"], 

                "4.1": ["//accessrestrict"],
                "4.5": ["//langmaterial", "//language"],
                
                # DACS Part I: Optimum
                "2.7": ["//bioghist", "//bioghist/note"], 
                
                # DACS Part I: Added Value
                "3.2": ["//arrangement"],
                "4.2": ["//phystech"], # Physical Access
                "4.3": ["//phystech"], # Technical Access
                "4.4": ["//userestrict"], # Conditions Governing Reproduction
                "4.6": ["//otherfindaid"], # Finding Aids
                "5.1": ["//custodhist"], # Custodial History
                "5.2": ["//acqinfo"], # Immediate Source of Acquisition
                "5.3": ["//appraisal"], # Appraisal
                "5.4": ["//accruals"], # Accruals
                "6.1": ["//originalsloc"], # Existence/Location of Originals
                "6.2": ["//altformavail"], # Existence/Location of Copies
                "6.3": ["//relatedmaterial", "//separatedmaterial"], # Related Materials
                "6.4": ["//bibliography", "//publicationstmt"], # Publication Note
                
                # CHAPTER 7 NOTES (7.1.1 - 7.1.8)
                "7.1":   ["//odd", "//note"], # Generic
                "7.1.1": ["//odd", "//note"], # General Note
                "7.1.2": ["//phystech"],      # Conservation Note
                "7.1.3": ["//prefercite"],    # Citation Note
                "7.1.4": ["//custodhist"],    # Custodial History Note (often treated as note)
                "7.1.5": ["//appraisal"],     # Appraisal Note
                "7.1.6": ["//accruals"],      # Accruals Note
                "7.1.7": ["//userestrict"],   # Reproduction/Use Note
                "7.1.8": ["//processinfo"],   # Processing Information
                
                "8.1": ["//processinfo", "//maintenancehistory"], # Description Control

                # DACS Part II (Authority Records)
                "10.1": ["//origination/persname", "//origination/corpname", "//origination/famname", "//controlaccess/persname", "//controlaccess/corpname"],
                "10.2": ["//origination/persname", "//origination/corpname", "//origination/famname"],
                "11.1": ["//bioghist", "//origination//date", "//persname//date"],
                "13.2": ["//eadid", "//@authfilenumber"],
                "13.11": ["//eadheader//rightsdeclaration", "//eadheader//publicationstmt/p[contains(translate(., 'RIGHTS', 'rights'), 'rights')]", "//eadheader//notestmt/note[contains(translate(., 'RIGHTS', 'rights'), 'rights')]"]
            }

            for req in self.requirements:
                found = False
                rule_id = req['id']
                
                xpaths = dacs_xpath_map.get(rule_id)
                
                if xpaths:
                    for xpath in xpaths:
                        matches = root.xpath(xpath)
                        if matches:
                            first_match = matches[0]
                            
                            if isinstance(first_match, (str, etree._ElementUnicodeResult)):
                                if str(first_match).strip():
                                    found = True
                                    break
                            else:
                                has_text = any(str(m.text).strip() for m in matches if m.text)
                                has_children = any(len(m) > 0 for m in matches)
                                
                                if has_text or has_children:
                                    found = True
                                    break
                
                if found:
                    present_elements.append(req)
                else:
                    missing_elements.append(req)

            self._print_report(present_elements, missing_elements)
        except Exception as e:
            print(f" Error parsing XML: {e}")

    def _print_report(self, present, missing):
    
        missing_required = [m for m in missing if m['status'] == 'Required']
        missing_optimum = [m for m in missing if m['status'] == 'Optimum']
        missing_added_value = [m for m in missing if m['status'] == 'Added Value']
        
        present_required = [p for p in present if p['status'] == 'Required']
        present_optimum = [p for p in present if p['status'] == 'Optimum']
        present_added_value = [p for p in present if p['status'] == 'Added Value']
        
        print("\n" + "="*50)
        print("DACS COMPLIANCE & ANALYSIS REPORT (XML)")
        print("="*50)
        
        # Calculate DACS compliance
        total_required = len(present_required) + len(missing_required)
        score = 0
        if total_required > 0:
            score = (len(present_required) / total_required) * 100

        # 1. DACS Required Only 
        if not missing_required:
            print("DACS Compliant Status: PASSED")
            print("(All Minimum Required Elements are present)")
        else:
            print("DACS Compliant Status: FAILED")
            print(f"(Missing {len(missing_required)} Required Elements)")

        print(f"Compliance Score: {score:.1f}%")

        # 2. REQUIRED Elements
        if missing_required:
            print("\n Missing REQUIRED elements:")
            for m in missing_required:
                print(f"   [ ] {m['full']}")
        
        if present_required:
            print("\n Present REQUIRED elements:")
            for p in present_required:
                print(f"   [x] {p['full']}")

        # 3. OPTIMUM Elements
        if missing_optimum:
            print("\n Missing OPTIMUM elements (Recommended):")
            for m in missing_optimum:
                print(f"   [ ] {m['full']}")
        
        if present_optimum:
            print("\n Present OPTIMUM elements:")
            for p in present_optimum:
                print(f"   [x] {p['full']}")

        # 4. ADDED VALUE Elements (7.1.x included here)
        if present_added_value:
            print("\n ADDED VALUE elements found:")
            for p in present_added_value:
                print(f"   [x] {p['full']}")
        
        if missing_added_value:
            print("\n Other ADDED VALUE fields (Not Found):")
            for m in missing_added_value:
                print(f"   [ ] {m['full']}")
                
        # 5. Summary
        print("\n" + "-"*30)
        print(f"Summary: {len(present_required)} Required, {len(present_optimum)} Optimum, and {len(present_added_value)} Added Value elements found.")
        print("="*50 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Validate an EAD XML finding aid against DACS standards.")
    parser.add_argument("file", help="Path to the finding aid (XML file).")
    args = parser.parse_args()

    if not args.file.lower().endswith('.xml'):
        print(" This script is optimized for XML files only. Please provide a .xml file.")
        return

    validator = DACSValidator()
    validator.fetch_dacs_standards()
    validator.validate_ead_xml(args.file)

if __name__ == "__main__":
    main()