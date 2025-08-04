#!/usr/bin/env python3
"""
Test getting detailed voucher entries by accessing individual vouchers
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
    print("=== Testing Individual Voucher Details ===\n")
    
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
        
        # First get some vouchers to get their voucher numbers
        print("\nGetting voucher list...")
        xml_request_vouchers = f"""
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
        
        root_vouchers = send_tally_request(xml_request_vouchers)
        voucher_numbers = []
        
        for voucher in root_vouchers.iter("VOUCHER"):
            voucher_number = voucher.findtext("VOUCHERNUMBER")
            if voucher_number:
                voucher_numbers.append(voucher_number)
        
        print(f"Found {len(voucher_numbers)} vouchers")
        if len(voucher_numbers) > 0:
            print(f"Sample voucher numbers: {voucher_numbers[:3]}")
        
        # Test getting detailed voucher entries for first few vouchers
        print("\nTesting individual voucher details...")
        
        for i, voucher_number in enumerate(voucher_numbers[:3]):  # Test first 3 vouchers
            print(f"\nTesting voucher {i+1}: {voucher_number}")
            
            # Method 1: Try to get voucher details using Collection
            xml_request_voucher_detail = f"""
            <ENVELOPE>
              <HEADER>
                <VERSION>1</VERSION>
                <TALLYREQUEST>Export</TALLYREQUEST>
                <TYPE>Collection</TYPE>
                <ID>Voucher Details</ID>
              </HEADER>
              <BODY>
                <DESC>
                  <STATICVARIABLES>
                    <SVCOMPANYCONNECT>{company_name}</SVCOMPANYCONNECT>
                    <SVVOUCHERNUMBER>{voucher_number}</SVVOUCHERNUMBER>
                  </STATICVARIABLES>
                  <TDL>
                    <TDLMESSAGE>
                      <COLLECTION NAME="Voucher Details">
                        <TYPE>Voucher</TYPE>
                        <FETCH>VOUCHERNUMBER,DATE,VOUCHERTYPENAME,NARRATION,REFERENCE,AMOUNT,ALLEDGERENTRIES</FETCH>
                      </COLLECTION>
                    </TDLMESSAGE>
                  </TDL>
                </DESC>
              </BODY>
            </ENVELOPE>
            """
            
            try:
                root_detail = send_tally_request(xml_request_voucher_detail, timeout=15)
                entries = []
                
                for collection in root_detail.iter("COLLECTION"):
                    for voucher in collection:
                        # Look for ALLEDGERENTRIES
                        for all_entries in voucher.iter("ALLEDGERENTRIES"):
                            for entry in all_entries.iter("LEDGERENTRY"):
                                entries.append({
                                    "VoucherNumber": voucher_number,
                                    "LedgerName": entry.findtext("LEDGERNAME"),
                                    "Amount": entry.findtext("AMOUNT"),
                                    "Narration": entry.findtext("NARRATION"),
                                    "PartyLedgerName": entry.findtext("PARTYLEDGERNAME")
                                })
                
                print(f"   Found {len(entries)} entries using Collection method")
                if len(entries) > 0:
                    print(f"   Sample entry: {entries[0]}")
                    
            except Exception as e:
                print(f"   ❌ Collection method failed: {e}")
            
            # Method 2: Try using a specific voucher report
            xml_request_voucher_report = f"""
            <ENVELOPE>
              <HEADER>
                <TALLYREQUEST>Export Data</TALLYREQUEST>
              </HEADER>
              <BODY>
                <EXPORTDATA>
                  <REQUESTDESC>
                    <REPORTNAME>Voucher</REPORTNAME>
                    <STATICVARIABLES>
                      <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                      <SVCURRENTCOMPANY>{company_name}</SVCURRENTCOMPANY>
                      <SVVOUCHERNUMBER>{voucher_number}</SVVOUCHERNUMBER>
                    </STATICVARIABLES>
                  </REQUESTDESC>
                </EXPORTDATA>
              </BODY>
            </ENVELOPE>
            """
            
            try:
                root_report = send_tally_request(xml_request_voucher_report, timeout=15)
                report_entries = []
                
                for voucher in root_report.iter("VOUCHER"):
                    for entry in voucher.iter("LEDGERENTRY"):
                        report_entries.append({
                            "VoucherNumber": voucher_number,
                            "LedgerName": entry.findtext("LEDGERNAME"),
                            "Amount": entry.findtext("AMOUNT"),
                            "Narration": entry.findtext("NARRATION"),
                            "PartyLedgerName": entry.findtext("PARTYLEDGERNAME")
                        })
                
                print(f"   Found {len(report_entries)} entries using Voucher report")
                if len(report_entries) > 0:
                    print(f"   Sample entry: {report_entries[0]}")
                    
            except Exception as e:
                print(f"   ❌ Voucher report failed: {e}")
        
        print("\n=== Test Complete ===")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 