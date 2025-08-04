#!/usr/bin/env python3
"""
Test voucher extraction only with different approaches
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

def send_tally_request(xml_request, timeout=60):
    """Send XML request to Tally with longer timeout"""
    headers = {'Content-Type': 'application/xml'}
    try:
        response = requests.post(TALLY_URL, data=xml_request.encode(), headers=headers, timeout=timeout)
        response.raise_for_status()
        return safe_parse_xml(response.text)
    except Exception as e:
        logger.error(f"Error sending request: {e}")
        raise

def main():
    print("=== Testing Voucher Extraction Only ===\n")
    
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
        
        for collection in root_companies.iter("COLLECTION"):
            for comp in collection:
                companies.append({
                    "Name": comp.findtext("NAME"),
                    "GUID": comp.findtext("GUID"),
                    "Email": comp.findtext("EMAIL"),
                    "State": comp.findtext("STATE"),
                    "Pincode": comp.findtext("PINCODE"),
                    "Phone": comp.findtext("PHONE"),
                    "CompanyNumber": comp.findtext("COMPANYNUMBER")
                })
        
        if not companies:
            print("❌ No companies found")
            return
        
        company_name = companies[0].get('Name', '')
        print(f"Using company: {company_name}")
        
        if not company_name:
            print("❌ Company name is empty")
            return
        
        # Test 1: DayBook report (this worked in our previous test)
        print("\n1. Testing DayBook report (worked before)...")
        xml_request_daybook = f"""
        <ENVELOPE>
          <HEADER>
            <TALLYREQUEST>Export Data</TALLYREQUEST>
          </HEADER>
          <BODY>
            <EXPORTDATA>
              <REQUESTDESC>
                <REPORTNAME>DayBook</REPORTNAME>
                <STATICVARIABLES>
                  <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                  <SVCURRENTCOMPANY>{company_name}</SVCURRENTCOMPANY>
                  <SVFROMDATE Type='Date'>1-Apr-2023</SVFROMDATE>
                  <SVTODATE Type='Date'>31-Mar-2025</SVTODATE>
                </STATICVARIABLES>
              </REQUESTDESC>
            </EXPORTDATA>
          </BODY>
        </ENVELOPE>
        """
        
        try:
            root_daybook = send_tally_request(xml_request_daybook, timeout=120)
            daybook_vouchers = []
            
            for voucher in root_daybook.iter("VOUCHER"):
                daybook_vouchers.append({
                    "VoucherNumber": voucher.findtext("VOUCHERNUMBER"),
                    "Date": voucher.findtext("DATE"),
                    "VoucherTypeName": voucher.findtext("VOUCHERTYPENAME"),
                    "Narration": voucher.findtext("NARRATION"),
                    "Reference": voucher.findtext("REFERENCE"),
                    "Amount": voucher.findtext("AMOUNT")
                })
            
            print(f"   Found {len(daybook_vouchers)} vouchers using DayBook")
            if len(daybook_vouchers) > 0:
                print(f"   Sample voucher: {daybook_vouchers[0]}")
                
                # Extract voucher entries from DayBook
                voucher_entries = []
                for voucher in root_daybook.iter("VOUCHER"):
                    voucher_number = voucher.findtext("VOUCHERNUMBER")
                    voucher_date = voucher.findtext("DATE")
                    voucher_type = voucher.findtext("VOUCHERTYPENAME")
                    
                    for ledger_entry in voucher.iter("LEDGERENTRY"):
                        voucher_entries.append({
                            "VoucherNumber": voucher_number,
                            "VoucherDate": voucher_date,
                            "VoucherType": voucher_type,
                            "LedgerName": ledger_entry.findtext("LEDGERNAME"),
                            "Amount": ledger_entry.findtext("AMOUNT"),
                            "Narration": ledger_entry.findtext("NARRATION"),
                            "PartyLedgerName": ledger_entry.findtext("PARTYLEDGERNAME")
                        })
                
                print(f"   Found {len(voucher_entries)} voucher entries")
                if len(voucher_entries) > 0:
                    print(f"   Sample entry: {voucher_entries[0]}")
                    
        except Exception as e:
            print(f"   ❌ DayBook failed: {e}")
        
        # Test 2: Try Collection method with shorter timeout
        print("\n2. Testing Collection method with shorter timeout...")
        xml_request_collection = f"""
        <ENVELOPE>
          <HEADER>
            <VERSION>1</VERSION>
            <TALLYREQUEST>Export</TALLYREQUEST>
            <TYPE>Collection</TYPE>
            <ID>List of Vouchers</ID>
          </HEADER>
          <BODY>
            <DESC>
              <STATICVARIABLES>
                <SVCOMPANYCONNECT>{company_name}</SVCOMPANYCONNECT>
              </STATICVARIABLES>
              <TDL>
                <TDLMESSAGE>
                  <COLLECTION NAME="List of Vouchers">
                    <TYPE>Voucher</TYPE>
                    <FETCH>VOUCHERNUMBER,DATE,VOUCHERTYPENAME,NARRATION,REFERENCE,AMOUNT</FETCH>
                  </COLLECTION>
                </TDLMESSAGE>
              </TDL>
            </DESC>
          </BODY>
        </ENVELOPE>
        """
        
        try:
            root_collection = send_tally_request(xml_request_collection, timeout=45)
            collection_vouchers = []
            
            for collection in root_collection.iter("COLLECTION"):
                for voucher in collection:
                    collection_vouchers.append({
                        "VoucherNumber": voucher.findtext("VOUCHERNUMBER"),
                        "Date": voucher.findtext("DATE"),
                        "VoucherTypeName": voucher.findtext("VOUCHERTYPENAME"),
                        "Narration": voucher.findtext("NARRATION"),
                        "Reference": voucher.findtext("REFERENCE"),
                        "Amount": voucher.findtext("AMOUNT")
                    })
            
            print(f"   Found {len(collection_vouchers)} vouchers using Collection method")
            if len(collection_vouchers) > 0:
                print(f"   Sample voucher: {collection_vouchers[0]}")
                
        except Exception as e:
            print(f"   ❌ Collection method failed: {e}")
        
        print("\n=== Test Complete ===")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 