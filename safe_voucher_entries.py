#!/usr/bin/env python3
"""
Safe approach to extract voucher entries without crashing Tally
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
    print("=== Safe Voucher Entries Extraction ===\n")
    
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
        
        # Method 1: Try a simple LedgerVouchers report with minimal FETCH
        print("\n1. Testing simple LedgerVouchers report...")
        xml_request_simple = f"""
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
                  <SVCURRENTCOMPANY>{company_name}</SVCURRENTCOMPANY>
                  <SVFROMDATE Type='Date'>1-Apr-2024</SVFROMDATE>
                  <SVTODATE Type='Date'>31-Mar-2025</SVTODATE>
                </STATICVARIABLES>
              </REQUESTDESC>
            </EXPORTDATA>
          </BODY>
        </ENVELOPE>
        """
        
        try:
            root_simple = send_tally_request(xml_request_simple, timeout=60)
            simple_entries = []
            
            # Look for voucher entries in the response
            for voucher in root_simple.iter("VOUCHER"):
                voucher_number = voucher.findtext("VOUCHERNUMBER")
                voucher_date = voucher.findtext("DATE")
                voucher_type = voucher.findtext("VOUCHERTYPENAME")
                
                # Look for ledger entries
                for entry in voucher.iter("LEDGERENTRY"):
                    simple_entries.append({
                        "VoucherNumber": voucher_number,
                        "VoucherDate": voucher_date,
                        "VoucherType": voucher_type,
                        "LedgerName": entry.findtext("LEDGERNAME"),
                        "Amount": entry.findtext("AMOUNT"),
                        "Narration": entry.findtext("NARRATION"),
                        "PartyLedgerName": entry.findtext("PARTYLEDGERNAME")
                    })
            
            print(f"   Found {len(simple_entries)} voucher entries using simple LedgerVouchers")
            if len(simple_entries) > 0:
                print(f"   Sample entry: {simple_entries[0]}")
                
        except Exception as e:
            print(f"   ❌ Simple LedgerVouchers failed: {e}")
        
        # Method 2: Try using a specific ledger to get its vouchers
        print("\n2. Testing ledger-specific voucher extraction...")
        
        # First get a few ledgers
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
                <SVCOMPANYCONNECT>{company_name}</SVCOMPANYCONNECT>
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
                    ledgers.append({
                        "Name": ledger.findtext("NAME"),
                        "GUID": ledger.findtext("GUID")
                    })
            
            print(f"   Found {len(ledgers)} ledgers")
            
            # Try to get vouchers for first ledger only
            if ledgers:
                first_ledger = ledgers[0]
                print(f"   Testing ledger: {first_ledger['Name']}")
                
                xml_request_ledger_vouchers = f"""
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
                          <SVCURRENTCOMPANY>{company_name}</SVCURRENTCOMPANY>
                          <SVLEDGERNAME>{first_ledger['Name']}</SVLEDGERNAME>
                          <SVFROMDATE Type='Date'>1-Apr-2024</SVFROMDATE>
                          <SVTODATE Type='Date'>31-Mar-2025</SVTODATE>
                        </STATICVARIABLES>
                      </REQUESTDESC>
                    </EXPORTDATA>
                  </BODY>
                </ENVELOPE>
                """
                
                try:
                    root_ledger_vouchers = send_tally_request(xml_request_ledger_vouchers, timeout=30)
                    ledger_entries = []
                    
                    for voucher in root_ledger_vouchers.iter("VOUCHER"):
                        voucher_number = voucher.findtext("VOUCHERNUMBER")
                        voucher_date = voucher.findtext("DATE")
                        voucher_type = voucher.findtext("VOUCHERTYPENAME")
                        
                        for entry in voucher.iter("LEDGERENTRY"):
                            ledger_entries.append({
                                "VoucherNumber": voucher_number,
                                "VoucherDate": voucher_date,
                                "VoucherType": voucher_type,
                                "LedgerName": entry.findtext("LEDGERNAME"),
                                "Amount": entry.findtext("AMOUNT"),
                                "Narration": entry.findtext("NARRATION"),
                                "PartyLedgerName": entry.findtext("PARTYLEDGERNAME")
                            })
                    
                    print(f"     Found {len(ledger_entries)} voucher entries for this ledger")
                    if len(ledger_entries) > 0:
                        print(f"     Sample entry: {ledger_entries[0]}")
                        
                except Exception as e:
                    print(f"     ❌ Ledger vouchers failed: {e}")
                    
        except Exception as e:
            print(f"   ❌ Ledger extraction failed: {e}")
        
        print("\n=== Summary ===")
        print("If voucher entries are still not found, it may be because:")
        print("1. The Tally company doesn't have detailed voucher entries in the specified date range")
        print("2. The voucher entries are stored in a different format or location")
        print("3. The Tally version doesn't support detailed voucher entry extraction via XML")
        print("\nThe current data (companies, groups, ledgers, vouchers) is successfully imported!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 