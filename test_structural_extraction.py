#!/usr/bin/env python3
"""
Test structural and hierarchical data extraction for vouchers
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

def send_tally_request(xml_request):
    """Send XML request to Tally"""
    headers = {'Content-Type': 'application/xml'}
    try:
        response = requests.post(TALLY_URL, data=xml_request.encode(), headers=headers, timeout=30)
        response.raise_for_status()
        return safe_parse_xml(response.text)
    except Exception as e:
        logger.error(f"Error sending request: {e}")
        raise

def test_voucher_extraction_methods(company_name):
    """Test different methods for voucher extraction"""
    
    print(f"=== Testing Voucher Extraction Methods for {company_name} ===\n")
    
    # Method 1: Collection-based voucher extraction
    print("1. Testing Collection-based voucher extraction...")
    xml_request1 = f"""
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
        root1 = send_tally_request(xml_request1)
        vouchers1 = []
        for collection in root1.iter("COLLECTION"):
            for voucher in collection:
                vouchers1.append({
                    "VoucherNumber": voucher.findtext("VOUCHERNUMBER"),
                    "Date": voucher.findtext("DATE"),
                    "VoucherTypeName": voucher.findtext("VOUCHERTYPENAME"),
                    "Narration": voucher.findtext("NARRATION"),
                    "Reference": voucher.findtext("REFERENCE"),
                    "Amount": voucher.findtext("AMOUNT")
                })
        print(f"   Found {len(vouchers1)} vouchers using Collection method")
    except Exception as e:
        print(f"   ❌ Collection method failed: {e}")
        vouchers1 = []
    
    # Method 2: Report-based voucher extraction with different report names
    print("\n2. Testing Report-based voucher extraction...")
    
    report_names = ["LedgerVouchers", "Vouchers", "DayBook", "CashBook", "BankBook"]
    
    for report_name in report_names:
        print(f"   Testing report: {report_name}")
        xml_request2 = f"""
        <ENVELOPE>
          <HEADER>
            <TALLYREQUEST>Export Data</TALLYREQUEST>
          </HEADER>
          <BODY>
            <EXPORTDATA>
              <REQUESTDESC>
                <REPORTNAME>{report_name}</REPORTNAME>
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
            root2 = send_tally_request(xml_request2)
            vouchers2 = []
            
            # Look for different possible voucher tags
            for tag_name in ["VOUCHER", "VOUCHERENTRY", "LEDGERENTRY"]:
                for voucher in root2.iter(tag_name):
                    vouchers2.append({
                        "VoucherNumber": voucher.findtext("VOUCHERNUMBER") or voucher.findtext("VOUCHERNO"),
                        "Date": voucher.findtext("DATE"),
                        "VoucherTypeName": voucher.findtext("VOUCHERTYPENAME") or voucher.findtext("VOUCHERTYPE"),
                        "Narration": voucher.findtext("NARRATION"),
                        "Reference": voucher.findtext("REFERENCE"),
                        "Amount": voucher.findtext("AMOUNT")
                    })
            
            print(f"     Found {len(vouchers2)} vouchers using {report_name}")
            if len(vouchers2) > 0:
                print(f"     Sample voucher: {vouchers2[0]}")
        except Exception as e:
            print(f"     ❌ {report_name} failed: {e}")
    
    # Method 3: Hierarchical extraction through ledgers
    print("\n3. Testing Hierarchical extraction through ledgers...")
    
    # First get some ledgers
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
        
        # Try to get vouchers for first few ledgers
        for i, ledger in enumerate(ledgers[:3]):  # Test first 3 ledgers
            print(f"   Testing ledger {i+1}: {ledger['Name']}")
            
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
                      <SVLEDGERNAME>{ledger['Name']}</SVLEDGERNAME>
                      <SVFROMDATE Type='Date'>1-Apr-2023</SVFROMDATE>
                      <SVTODATE Type='Date'>31-Mar-2025</SVTODATE>
                    </STATICVARIABLES>
                  </REQUESTDESC>
                </EXPORTDATA>
              </BODY>
            </ENVELOPE>
            """
            
            try:
                root_ledger_vouchers = send_tally_request(xml_request_ledger_vouchers)
                ledger_vouchers = []
                
                for voucher in root_ledger_vouchers.iter("VOUCHER"):
                    ledger_vouchers.append({
                        "LedgerName": ledger['Name'],
                        "VoucherNumber": voucher.findtext("VOUCHERNUMBER"),
                        "Date": voucher.findtext("DATE"),
                        "VoucherTypeName": voucher.findtext("VOUCHERTYPENAME"),
                        "Narration": voucher.findtext("NARRATION"),
                        "Reference": voucher.findtext("REFERENCE"),
                        "Amount": voucher.findtext("AMOUNT")
                    })
                
                print(f"     Found {len(ledger_vouchers)} vouchers for this ledger")
                if len(ledger_vouchers) > 0:
                    print(f"     Sample: {ledger_vouchers[0]}")
                    
            except Exception as e:
                print(f"     ❌ Failed for ledger {ledger['Name']}: {e}")
                
    except Exception as e:
        print(f"   ❌ Hierarchical extraction failed: {e}")
    
    # Method 4: Try different date ranges
    print("\n4. Testing different date ranges...")
    
    date_ranges = [
        ("1-Apr-2023", "31-Mar-2025"),
        ("1-Apr-2024", "31-Mar-2025"),
        ("1-Jan-2024", "31-Dec-2024"),
        ("1-Apr-2022", "31-Mar-2023")
    ]
    
    for from_date, to_date in date_ranges:
        print(f"   Testing date range: {from_date} to {to_date}")
        
        xml_request_dates = f"""
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
                  <SVFROMDATE Type='Date'>{from_date}</SVFROMDATE>
                  <SVTODATE Type='Date'>{to_date}</SVTODATE>
                </STATICVARIABLES>
              </REQUESTDESC>
            </EXPORTDATA>
          </BODY>
        </ENVELOPE>
        """
        
        try:
            root_dates = send_tally_request(xml_request_dates)
            date_vouchers = []
            
            for voucher in root_dates.iter("VOUCHER"):
                date_vouchers.append({
                    "VoucherNumber": voucher.findtext("VOUCHERNUMBER"),
                    "Date": voucher.findtext("DATE"),
                    "VoucherTypeName": voucher.findtext("VOUCHERTYPENAME"),
                    "Narration": voucher.findtext("NARRATION"),
                    "Reference": voucher.findtext("REFERENCE"),
                    "Amount": voucher.findtext("AMOUNT")
                })
            
            print(f"     Found {len(date_vouchers)} vouchers")
            if len(date_vouchers) > 0:
                print(f"     Sample: {date_vouchers[0]}")
                
        except Exception as e:
            print(f"     ❌ Failed: {e}")

def main():
    print("=== Structural and Hierarchical Voucher Extraction Test ===\n")
    
    # First get company name
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
        
        # Test voucher extraction methods
        test_voucher_extraction_methods(company_name)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 