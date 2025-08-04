#!/usr/bin/env python3
"""
Find actual ledger names in Tally company
"""

import requests
import xml.etree.ElementTree as ET
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TALLY_URL = "http://localhost:9000"
COMPANY_NAME = "SKM IMPEX-CHENNAI-(24-25)"

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
    print("=== Finding Actual Ledgers ===\n")
    print(f"Using company: {COMPANY_NAME}\n")
    
    # Get ledgers from the company
    xml_request_ledgers = f"""
    <ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>List of Ledgers</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES>
            <SVCOMPANYCONNECT>{COMPANY_NAME}</SVCOMPANYCONNECT>
          </STATICVARIABLES>
          <TDL>
            <TDLMESSAGE>
              <COLLECTION NAME="List of Ledgers">
                <TYPE>Ledger</TYPE>
                <FETCH>NAME,GUID</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    
    try:
        root_ledgers = send_tally_request(xml_request_ledgers)
        ledgers = []
        
        for collection in root_ledgers.iter("COLLECTION"):
            for ledger in collection:
                ledger_name = ledger.findtext("NAME")
                if ledger_name:
                    ledgers.append(ledger_name)
        
        print(f"Found {len(ledgers)} ledgers")
        
        # Show first 20 ledgers
        print("\nFirst 20 ledgers:")
        for i, ledger in enumerate(ledgers[:20]):
            print(f"  {i+1:2d}. {ledger}")
        
        if len(ledgers) > 20:
            print(f"  ... and {len(ledgers) - 20} more ledgers")
        
        # Look for common ledger types
        common_keywords = ['cash', 'bank', 'sales', 'purchase', 'receipt', 'payment', 'income', 'expense']
        found_common = []
        
        print("\nLooking for common ledger types:")
        for keyword in common_keywords:
            matching_ledgers = [l for l in ledgers if keyword.lower() in l.lower()]
            if matching_ledgers:
                found_common.extend(matching_ledgers[:3])  # Take first 3 matches
                print(f"  {keyword.title()}: {matching_ledgers[:3]}")
        
        # Try to get voucher entries from first few ledgers
        print(f"\nTesting voucher entries for first 3 ledgers...")
        
        for i, ledger_name in enumerate(ledgers[:3]):
            print(f"\n{i+1}. Testing ledger: {ledger_name}")
            
            xml_request_vouchers = f"""
            <ENVELOPE>
              <HEADER>
                <TALLYREQUEST>Export Data</TALLYREQUEST>
              </HEADER>
              <BODY>
                <EXPORTDATA>
                  <REQUESTDESC>
                    <REPORTNAME>LedgerVouchers</REPORTNAME>
                    <STATICVARIABLES>
                      <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                      <SVCURRENTCOMPANY>{COMPANY_NAME}</SVCURRENTCOMPANY>
                      <SVLEDGERNAME>{ledger_name}</SVLEDGERNAME>
                      <SVFROMDATE Type='Date'>1-Apr-2024</SVFROMDATE>
                      <SVTODATE Type='Date'>31-Mar-2025</SVTODATE>
                    </STATICVARIABLES>
                  </REQUESTDESC>
                </EXPORTDATA>
              </BODY>
            </ENVELOPE>
            """
            
            try:
                root_vouchers = send_tally_request(xml_request_vouchers, timeout=30)
                voucher_entries = []
                
                for voucher in root_vouchers.iter("VOUCHER"):
                    voucher_number = voucher.findtext("VOUCHERNUMBER")
                    voucher_date = voucher.findtext("DATE")
                    voucher_type = voucher.findtext("VOUCHERTYPENAME")
                    
                    for entry in voucher.iter("LEDGERENTRY"):
                        voucher_entries.append({
                            "VoucherNumber": voucher_number,
                            "VoucherDate": voucher_date,
                            "VoucherType": voucher_type,
                            "LedgerName": entry.findtext("LEDGERNAME"),
                            "Amount": entry.findtext("AMOUNT"),
                            "Narration": entry.findtext("NARRATION"),
                            "PartyLedgerName": entry.findtext("PARTYLEDGERNAME")
                        })
                
                print(f"     Found {len(voucher_entries)} voucher entries")
                if len(voucher_entries) > 0:
                    print(f"     Sample entry: {voucher_entries[0]}")
                    
            except Exception as e:
                print(f"     ❌ Failed: {e}")
        
        print("\n=== Summary ===")
        print(f"Total ledgers found: {len(ledgers)}")
        print("If no voucher entries are found, it may be because:")
        print("1. The ledgers don't have transactions in the specified date range")
        print("2. The voucher entries are stored differently in this Tally version")
        print("3. The company data structure is different")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 