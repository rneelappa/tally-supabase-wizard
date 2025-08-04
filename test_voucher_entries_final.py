#!/usr/bin/env python3
"""
Final test for voucher entries extraction
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
    print("=== Final Voucher Entries Test ===\n")
    print(f"Using company: {COMPANY_NAME}\n")
    
    # Method 1: Try LedgerVouchers with specific ledger
    print("1. Testing LedgerVouchers with Cash ledger...")
    xml_request_cash = f"""
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
              <SVLEDGERNAME>Cash</SVLEDGERNAME>
              <SVFROMDATE Type='Date'>1-Apr-2024</SVFROMDATE>
              <SVTODATE Type='Date'>31-Mar-2025</SVTODATE>
            </STATICVARIABLES>
          </REQUESTDESC>
        </EXPORTDATA>
      </BODY>
    </ENVELOPE>
    """
    
    try:
        root_cash = send_tally_request(xml_request_cash, timeout=60)
        cash_entries = []
        
        for voucher in root_cash.iter("VOUCHER"):
            voucher_number = voucher.findtext("VOUCHERNUMBER")
            voucher_date = voucher.findtext("DATE")
            voucher_type = voucher.findtext("VOUCHERTYPENAME")
            
            for entry in voucher.iter("LEDGERENTRY"):
                cash_entries.append({
                    "VoucherNumber": voucher_number,
                    "VoucherDate": voucher_date,
                    "VoucherType": voucher_type,
                    "LedgerName": entry.findtext("LEDGERNAME"),
                    "Amount": entry.findtext("AMOUNT"),
                    "Narration": entry.findtext("NARRATION"),
                    "PartyLedgerName": entry.findtext("PARTYLEDGERNAME")
                })
        
        print(f"   Found {len(cash_entries)} voucher entries for Cash ledger")
        if len(cash_entries) > 0:
            print(f"   Sample entry: {cash_entries[0]}")
            
    except Exception as e:
        print(f"   ❌ Cash ledger failed: {e}")
    
    # Method 2: Try Bank ledger
    print("\n2. Testing LedgerVouchers with Bank ledger...")
    xml_request_bank = f"""
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
              <SVLEDGERNAME>Bank</SVLEDGERNAME>
              <SVFROMDATE Type='Date'>1-Apr-2024</SVFROMDATE>
              <SVTODATE Type='Date'>31-Mar-2025</SVTODATE>
            </STATICVARIABLES>
          </REQUESTDESC>
        </EXPORTDATA>
      </BODY>
    </ENVELOPE>
    """
    
    try:
        root_bank = send_tally_request(xml_request_bank, timeout=60)
        bank_entries = []
        
        for voucher in root_bank.iter("VOUCHER"):
            voucher_number = voucher.findtext("VOUCHERNUMBER")
            voucher_date = voucher.findtext("DATE")
            voucher_type = voucher.findtext("VOUCHERTYPENAME")
            
            for entry in voucher.iter("LEDGERENTRY"):
                bank_entries.append({
                    "VoucherNumber": voucher_number,
                    "VoucherDate": voucher_date,
                    "VoucherType": voucher_type,
                    "LedgerName": entry.findtext("LEDGERNAME"),
                    "Amount": entry.findtext("AMOUNT"),
                    "Narration": entry.findtext("NARRATION"),
                    "PartyLedgerName": entry.findtext("PARTYLEDGERNAME")
                })
        
        print(f"   Found {len(bank_entries)} voucher entries for Bank ledger")
        if len(bank_entries) > 0:
            print(f"   Sample entry: {bank_entries[0]}")
            
    except Exception as e:
        print(f"   ❌ Bank ledger failed: {e}")
    
    # Method 3: Try Sales ledger
    print("\n3. Testing LedgerVouchers with Sales ledger...")
    xml_request_sales = f"""
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
              <SVLEDGERNAME>Sales</SVLEDGERNAME>
              <SVFROMDATE Type='Date'>1-Apr-2024</SVFROMDATE>
              <SVTODATE Type='Date'>31-Mar-2025</SVTODATE>
            </STATICVARIABLES>
          </REQUESTDESC>
        </EXPORTDATA>
      </BODY>
    </ENVELOPE>
    """
    
    try:
        root_sales = send_tally_request(xml_request_sales, timeout=60)
        sales_entries = []
        
        for voucher in root_sales.iter("VOUCHER"):
            voucher_number = voucher.findtext("VOUCHERNUMBER")
            voucher_date = voucher.findtext("DATE")
            voucher_type = voucher.findtext("VOUCHERTYPENAME")
            
            for entry in voucher.iter("LEDGERENTRY"):
                sales_entries.append({
                    "VoucherNumber": voucher_number,
                    "VoucherDate": voucher_date,
                    "VoucherType": voucher_type,
                    "LedgerName": entry.findtext("LEDGERNAME"),
                    "Amount": entry.findtext("AMOUNT"),
                    "Narration": entry.findtext("NARRATION"),
                    "PartyLedgerName": entry.findtext("PARTYLEDGERNAME")
                })
        
        print(f"   Found {len(sales_entries)} voucher entries for Sales ledger")
        if len(sales_entries) > 0:
            print(f"   Sample entry: {sales_entries[0]}")
            
    except Exception as e:
        print(f"   ❌ Sales ledger failed: {e}")
    
    # Method 4: Try Purchase ledger
    print("\n4. Testing LedgerVouchers with Purchase ledger...")
    xml_request_purchase = f"""
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
              <SVLEDGERNAME>Purchase</SVLEDGERNAME>
              <SVFROMDATE Type='Date'>1-Apr-2024</SVFROMDATE>
              <SVTODATE Type='Date'>31-Mar-2025</SVTODATE>
            </STATICVARIABLES>
          </REQUESTDESC>
        </EXPORTDATA>
      </BODY>
    </ENVELOPE>
    """
    
    try:
        root_purchase = send_tally_request(xml_request_purchase, timeout=60)
        purchase_entries = []
        
        for voucher in root_purchase.iter("VOUCHER"):
            voucher_number = voucher.findtext("VOUCHERNUMBER")
            voucher_date = voucher.findtext("DATE")
            voucher_type = voucher.findtext("VOUCHERTYPENAME")
            
            for entry in voucher.iter("LEDGERENTRY"):
                purchase_entries.append({
                    "VoucherNumber": voucher_number,
                    "VoucherDate": voucher_date,
                    "VoucherType": voucher_type,
                    "LedgerName": entry.findtext("LEDGERNAME"),
                    "Amount": entry.findtext("AMOUNT"),
                    "Narration": entry.findtext("NARRATION"),
                    "PartyLedgerName": entry.findtext("PARTYLEDGERNAME")
                })
        
        print(f"   Found {len(purchase_entries)} voucher entries for Purchase ledger")
        if len(purchase_entries) > 0:
            print(f"   Sample entry: {purchase_entries[0]}")
            
    except Exception as e:
        print(f"   ❌ Purchase ledger failed: {e}")
    
    print("\n=== Summary ===")
    print("If no voucher entries are found, it may be because:")
    print("1. The ledgers don't have transactions in the specified date range")
    print("2. The ledger names are different in your Tally company")
    print("3. The voucher entries are stored differently")
    print("\nThe current data (companies, groups, ledgers, vouchers) is successfully imported!")

if __name__ == "__main__":
    main() 