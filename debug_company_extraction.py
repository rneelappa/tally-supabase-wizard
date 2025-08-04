#!/usr/bin/env python3
"""
Debug script to check company extraction
"""

import requests
import xml.etree.ElementTree as ET
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TALLY_URL = "http://localhost:9000"

def clean_xml_response(xml_text):
    """Clean malformed XML from Tally responses"""
    xml_text = xml_text.replace('\x00', '')
    xml_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', xml_text)
    xml_text = xml_text.replace('&', '&amp;')
    xml_text = re.sub(r'xmlns:[^=]*="[^"]*"', '', xml_text)
    xml_text = re.sub(r'[a-zA-Z]+:', '', xml_text)
    xml_text = re.sub(r'xmlns="[^"]*"', '', xml_text)
    return xml_text

def safe_parse_xml(xml_text):
    """Safely parse XML with error handling"""
    try:
        cleaned_xml = clean_xml_response(xml_text)
        return ET.fromstring(cleaned_xml)
    except ET.ParseError as e:
        logger.error(f"XML Parse Error: {e}")
        logger.error(f"XML Content (first 500 chars): {xml_text[:500]}")
        raise e

def send_tally_request(xml_request, timeout=30):
    """Send XML request to Tally"""
    headers = {'Content-Type': 'application/xml'}
    try:
        response = requests.post(TALLY_URL, data=xml_request.encode(), headers=headers, timeout=timeout)
        response.raise_for_status()
        return safe_parse_xml(response.text)
    except Exception as e:
        logger.error(f"Error sending request: {e}")
        raise

def main():
    print("=== Debug Company Extraction ===\n")
    
    # Get company name first
    print("Getting company information...")
    xml_request_companies = """
    <ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>List of Companies</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES />
          <TDL>
            <TDLMESSAGE>
              <COLLECTION NAME="List of Companies">
                <TYPE>Company</TYPE>
                <FETCH>NAME,GUID,EMAIL,STATE,PINCODE,PHONE,COMPANYNUMBER</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    
    try:
        root_companies = send_tally_request(xml_request_companies)
        companies = []
        
        print("Raw XML response structure:")
        print(f"Root tag: {root_companies.tag}")
        
        # Debug: Print all tags in the response
        all_tags = set()
        for elem in root_companies.iter():
            all_tags.add(elem.tag)
        print(f"All tags found: {sorted(all_tags)}")
        
        # Try different approaches to find companies
        print("\nTrying different extraction methods:")
        
        # Method 1: Look for COLLECTION tags
        collections = list(root_companies.iter("COLLECTION"))
        print(f"Found {len(collections)} COLLECTION tags")
        
        for i, collection in enumerate(collections):
            print(f"Collection {i+1}:")
            for child in collection:
                print(f"  - {child.tag}: {child.text}")
        
        # Method 2: Look for COMPANY tags directly
        companies_direct = list(root_companies.iter("COMPANY"))
        print(f"\nFound {len(companies_direct)} direct COMPANY tags")
        
        for i, company in enumerate(companies_direct):
            print(f"Company {i+1}:")
            for child in company:
                print(f"  - {child.tag}: {child.text}")
        
        # Method 3: Look for any tags that might contain company info
        for tag in ['NAME', 'COMPANYNAME', 'COMPANY']:
            elements = list(root_companies.iter(tag))
            if elements:
                print(f"\nFound {len(elements)} {tag} elements:")
                for i, elem in enumerate(elements[:3]):  # Show first 3
                    print(f"  {i+1}: {elem.text}")
        
        # Try to extract companies using the working method from simple_tally_api.py
        print("\nTrying extraction method from simple_tally_api.py:")
        for collection in root_companies.iter("COLLECTION"):
            for comp in collection:
                company_data = {
                    "Name": comp.findtext("NAME"),
                    "GUID": comp.findtext("GUID"),
                    "Email": comp.findtext("EMAIL"),
                    "State": comp.findtext("STATE"),
                    "Pincode": comp.findtext("PINCODE"),
                    "Phone": comp.findtext("PHONE"),
                    "CompanyNumber": comp.findtext("COMPANYNUMBER")
                }
                companies.append(company_data)
                print(f"Extracted company: {company_data}")
        
        if not companies:
            print("❌ No companies found with any method")
            return
        
        company_name = companies[0].get('Name', '')
        print(f"\nUsing company: '{company_name}'")
        
        if not company_name:
            print("❌ Company name is empty")
            return
        
        print(f"✅ Successfully extracted company: {company_name}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 