#!/usr/bin/env python3
"""
Simple approach to get voucher entries with longer timeouts
"""

import requests
import xml.etree.ElementTree as ET
import logging
import re
import time

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

def get_voucher_entries_simple():
    """Get voucher entries using a simple approach"""
    print("=== Simple Voucher Entries Extraction ===\n")
    print(f"Using company: {COMPANY_NAME}\n")
    
    # Try a simple approach - get all voucher entries at once with a broader date range
    print("1. Trying simple DayBook with broader date range...")
    xml_request_simple = f"""
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
              <SVCURRENTCOMPANY>{COMPANY_NAME}</SVCURRENTCOMPANY>
              <SVFROMDATE Type='Date'>1-Apr-2020</SVFROMDATE>
              <SVTODATE Type='Date'>31-Mar-2025</SVTODATE>
            </STATICVARIABLES>
          </REQUESTDESC>
        </EXPORTDATA>
      </BODY>
    </ENVELOPE>
    """
    
    try:
        print("   Sending request (this may take a while)...")
        root_simple = send_tally_request(xml_request_simple, timeout=120)
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
        
        print(f"   Found {len(simple_entries)} voucher entries using simple DayBook")
        if len(simple_entries) > 0:
            print(f"   Sample entry: {simple_entries[0]}")
            return simple_entries
        else:
            print("   No entries found in DayBook response")
            
    except Exception as e:
        print(f"   ❌ Simple DayBook failed: {e}")
    
    # Try alternative approach - CashBook
    print("\n2. Trying CashBook report...")
    xml_request_cashbook = f"""
    <ENVELOPE>
      <HEADER>
        <TALLYREQUEST>Export Data</TALLYREQUEST>
      </HEADER>
      <BODY>
        <EXPORTDATA>
          <REQUESTDESC>
            <REPORTNAME>CashBook</REPORTNAME>
            <STATICVARIABLES>
              <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
              <SVCURRENTCOMPANY>{COMPANY_NAME}</SVCURRENTCOMPANY>
              <SVFROMDATE Type='Date'>1-Apr-2020</SVFROMDATE>
              <SVTODATE Type='Date'>31-Mar-2025</SVTODATE>
            </STATICVARIABLES>
          </REQUESTDESC>
        </EXPORTDATA>
      </BODY>
    </ENVELOPE>
    """
    
    try:
        print("   Sending CashBook request...")
        root_cashbook = send_tally_request(xml_request_cashbook, timeout=120)
        cashbook_entries = []
        
        for voucher in root_cashbook.iter("VOUCHER"):
            voucher_number = voucher.findtext("VOUCHERNUMBER")
            voucher_date = voucher.findtext("DATE")
            voucher_type = voucher.findtext("VOUCHERTYPENAME")
            
            for entry in voucher.iter("LEDGERENTRY"):
                cashbook_entries.append({
                    "VoucherNumber": voucher_number,
                    "VoucherDate": voucher_date,
                    "VoucherType": voucher_type,
                    "LedgerName": entry.findtext("LEDGERNAME"),
                    "Amount": entry.findtext("AMOUNT"),
                    "Narration": entry.findtext("NARRATION"),
                    "PartyLedgerName": entry.findtext("PARTYLEDGERNAME")
                })
        
        print(f"   Found {len(cashbook_entries)} voucher entries using CashBook")
        if len(cashbook_entries) > 0:
            print(f"   Sample entry: {cashbook_entries[0]}")
            return cashbook_entries
        else:
            print("   No entries found in CashBook response")
            
    except Exception as e:
        print(f"   ❌ CashBook failed: {e}")
    
    # Try BankBook
    print("\n3. Trying BankBook report...")
    xml_request_bankbook = f"""
    <ENVELOPE>
      <HEADER>
        <TALLYREQUEST>Export Data</TALLYREQUEST>
      </HEADER>
      <BODY>
        <EXPORTDATA>
          <REQUESTDESC>
            <REPORTNAME>BankBook</REPORTNAME>
            <STATICVARIABLES>
              <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
              <SVCURRENTCOMPANY>{COMPANY_NAME}</SVCURRENTCOMPANY>
              <SVFROMDATE Type='Date'>1-Apr-2020</SVFROMDATE>
              <SVTODATE Type='Date'>31-Mar-2025</SVTODATE>
            </STATICVARIABLES>
          </REQUESTDESC>
        </EXPORTDATA>
      </BODY>
    </ENVELOPE>
    """
    
    try:
        print("   Sending BankBook request...")
        root_bankbook = send_tally_request(xml_request_bankbook, timeout=120)
        bankbook_entries = []
        
        for voucher in root_bankbook.iter("VOUCHER"):
            voucher_number = voucher.findtext("VOUCHERNUMBER")
            voucher_date = voucher.findtext("DATE")
            voucher_type = voucher.findtext("VOUCHERTYPENAME")
            
            for entry in voucher.iter("LEDGERENTRY"):
                bankbook_entries.append({
                    "VoucherNumber": voucher_number,
                    "VoucherDate": voucher_date,
                    "VoucherType": voucher_type,
                    "LedgerName": entry.findtext("LEDGERNAME"),
                    "Amount": entry.findtext("AMOUNT"),
                    "Narration": entry.findtext("NARRATION"),
                    "PartyLedgerName": entry.findtext("PARTYLEDGERNAME")
                })
        
        print(f"   Found {len(bankbook_entries)} voucher entries using BankBook")
        if len(bankbook_entries) > 0:
            print(f"   Sample entry: {bankbook_entries[0]}")
            return bankbook_entries
        else:
            print("   No entries found in BankBook response")
            
    except Exception as e:
        print(f"   ❌ BankBook failed: {e}")
    
    print("\n=== Summary ===")
    print("No voucher entries found with any method.")
    print("This may be because:")
    print("1. The Tally company doesn't have detailed voucher entries")
    print("2. The voucher entries are stored differently in this Tally version")
    print("3. The date range doesn't contain voucher entries")
    print("\nThe current data (companies, groups, ledgers, vouchers) is successfully imported!")
    
    return []

if __name__ == "__main__":
    get_voucher_entries_simple() 