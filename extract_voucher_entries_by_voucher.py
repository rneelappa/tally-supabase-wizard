#!/usr/bin/env python3
"""
Extract voucher entries by iterating through each voucher
"""

import requests
import xml.etree.ElementTree as ET
import logging
import re
from supabase_manager import SupabaseManager

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

def get_vouchers():
    """Get list of vouchers from Tally"""
    print("Getting vouchers list...")
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
              <SVCURRENTCOMPANY>{COMPANY_NAME}</SVCURRENTCOMPANY>
              <SVFROMDATE Type='Date'>1-Apr-2023</SVFROMDATE>
              <SVTODATE Type='Date'>31-Mar-2025</SVTODATE>
            </STATICVARIABLES>
          </REQUESTDESC>
        </EXPORTDATA>
      </BODY>
    </ENVELOPE>
    """
    
    try:
        root_vouchers = send_tally_request(xml_request_vouchers)
        vouchers = []
        
        for voucher in root_vouchers.iter("VOUCHER"):
            voucher_data = {
                "VoucherNumber": voucher.findtext("VOUCHERNUMBER"),
                "Date": voucher.findtext("DATE"),
                "VoucherTypeName": voucher.findtext("VOUCHERTYPENAME"),
                "Narration": voucher.findtext("NARRATION"),
                "Reference": voucher.findtext("REFERENCE"),
                "Amount": voucher.findtext("AMOUNT")
            }
            if voucher_data["VoucherNumber"]:
                vouchers.append(voucher_data)
        
        print(f"Found {len(vouchers)} vouchers")
        return vouchers
        
    except Exception as e:
        print(f"❌ Error getting vouchers: {e}")
        return []

def get_voucher_entries_for_voucher(voucher_number):
    """Get detailed voucher entries for a specific voucher"""
    print(f"  Getting entries for voucher: {voucher_number}")
    
    # Method 1: Try using Collection method for specific voucher
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
            <SVCOMPANYCONNECT>{COMPANY_NAME}</SVCOMPANYCONNECT>
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
        
        if entries:
            print(f"    Found {len(entries)} entries using Collection method")
            return entries
            
    except Exception as e:
        print(f"    ❌ Collection method failed: {e}")
    
    # Method 2: Try using Voucher report
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
              <SVCURRENTCOMPANY>{COMPANY_NAME}</SVCURRENTCOMPANY>
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
        
        if report_entries:
            print(f"    Found {len(report_entries)} entries using Voucher report")
            return report_entries
            
    except Exception as e:
        print(f"    ❌ Voucher report failed: {e}")
    
    print(f"    No entries found for voucher {voucher_number}")
    return []

def map_voucher_entry_to_supabase(entry, voucher_data):
    """Map voucher entry to Supabase schema"""
    return {
        'user_id': 'faa3bf60-717e-4dd8-8159-e9dc1fe9b8d0',  # Your user ID
        'company_name': COMPANY_NAME,
        'voucher_number': entry.get('VoucherNumber', ''),
        'voucher_date': voucher_data.get('Date', ''),
        'voucher_type': voucher_data.get('VoucherTypeName', ''),
        'ledger_name': entry.get('LedgerName', ''),
        'amount': float(entry.get('Amount', 0) or 0),
        'narration': entry.get('Narration', ''),
        'party_ledger_name': entry.get('PartyLedgerName', '')
    }

def main():
    print("=== Extract Voucher Entries by Voucher ===\n")
    print(f"Using company: {COMPANY_NAME}\n")
    
    # Initialize Supabase manager
    project_url = "https://ppfwlhfehwelinfprviw.supabase.co"
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBwZndsaGZlaHdlbGluZnBydml3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDMxNzYxOCwiZXhwIjoyMDY5ODkzNjE4fQ._qiN-8ZAqg2Lz9TD2hENgCoKjEiFDFCafkymiDPRH7A"
    
    supabase_manager = SupabaseManager(project_url, api_key)
    
    # Get list of vouchers
    vouchers = get_vouchers()
    if not vouchers:
        print("❌ No vouchers found")
        return
    
    print(f"\nProcessing {len(vouchers)} vouchers...")
    
    total_entries = 0
    successful_vouchers = 0
    
    for i, voucher in enumerate(vouchers):
        print(f"\n{i+1}/{len(vouchers)}. Processing voucher: {voucher['VoucherNumber']}")
        
        # Get voucher entries for this voucher
        entries = get_voucher_entries_for_voucher(voucher['VoucherNumber'])
        
        if entries:
            # Map entries to Supabase schema
            supabase_entries = []
            for entry in entries:
                mapped_entry = map_voucher_entry_to_supabase(entry, voucher)
                supabase_entries.append(mapped_entry)
            
            # Insert entries to Supabase
            try:
                result = supabase_manager.insert_data('tally_voucher_entries', supabase_entries)
                print(f"    ✅ Inserted {len(supabase_entries)} entries to Supabase")
                total_entries += len(supabase_entries)
                successful_vouchers += 1
            except Exception as e:
                print(f"    ❌ Failed to insert entries: {e}")
        else:
            print(f"    ⚠️  No entries found for this voucher")
    
    print(f"\n=== Summary ===")
    print(f"Total vouchers processed: {len(vouchers)}")
    print(f"Vouchers with entries: {successful_vouchers}")
    print(f"Total voucher entries inserted: {total_entries}")
    
    if total_entries > 0:
        print(f"✅ Successfully extracted and imported {total_entries} voucher entries!")
    else:
        print("❌ No voucher entries were found or imported")

if __name__ == "__main__":
    main() 