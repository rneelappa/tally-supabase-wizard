#!/usr/bin/env python3
"""
Test different approaches for extracting voucher entries with detailed ledger information
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
    print("=== Testing Voucher Entries Extraction ===\n")
    
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
        
        # Test 1: Try LedgerVouchers report with more detailed FETCH
        print("\n1. Testing LedgerVouchers report with detailed FETCH...")
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
                  <SVFROMDATE Type='Date'>1-Apr-2023</SVFROMDATE>
                  <SVTODATE Type='Date'>31-Mar-2025</SVTODATE>
                </STATICVARIABLES>
              </REQUESTDESC>
            </EXPORTDATA>
          </BODY>
        </ENVELOPE>
        """
        
        try:
            root_ledger_vouchers = send_tally_request(xml_request_ledger_vouchers, timeout=120)
            ledger_voucher_entries = []
            
            # Look for different possible structures
            for voucher in root_ledger_vouchers.iter("VOUCHER"):
                voucher_number = voucher.findtext("VOUCHERNUMBER")
                voucher_date = voucher.findtext("DATE")
                voucher_type = voucher.findtext("VOUCHERTYPENAME")
                
                # Look for ALLEDGERENTRIES or LEDGERENTRIES
                for ledger_entry in voucher.iter("ALLEDGERENTRIES"):
                    for entry in ledger_entry.iter("LEDGERENTRY"):
                        ledger_voucher_entries.append({
                            "VoucherNumber": voucher_number,
                            "VoucherDate": voucher_date,
                            "VoucherType": voucher_type,
                            "LedgerName": entry.findtext("LEDGERNAME"),
                            "Amount": entry.findtext("AMOUNT"),
                            "Narration": entry.findtext("NARRATION"),
                            "PartyLedgerName": entry.findtext("PARTYLEDGERNAME")
                        })
                
                # Also look for direct LEDGERENTRY
                for entry in voucher.iter("LEDGERENTRY"):
                    ledger_voucher_entries.append({
                        "VoucherNumber": voucher_number,
                        "VoucherDate": voucher_date,
                        "VoucherType": voucher_type,
                        "LedgerName": entry.findtext("LEDGERNAME"),
                        "Amount": entry.findtext("AMOUNT"),
                        "Narration": entry.findtext("NARRATION"),
                        "PartyLedgerName": entry.findtext("PARTYLEDGERNAME")
                    })
            
            print(f"   Found {len(ledger_voucher_entries)} voucher entries using LedgerVouchers")
            if len(ledger_voucher_entries) > 0:
                print(f"   Sample entry: {ledger_voucher_entries[0]}")
                
        except Exception as e:
            print(f"   ❌ LedgerVouchers failed: {e}")
        
        # Test 2: Try Collection method for voucher entries
        print("\n2. Testing Collection method for voucher entries...")
        xml_request_collection_entries = f"""
        <ENVELOPE>
          <HEADER>
            <VERSION>1</VERSION>
            <TALLYREQUEST>Export</TALLYREQUEST>
            <TYPE>Collection</TYPE>
            <ID>List of Voucher Entries</ID>
          </HEADER>
          <BODY>
            <DESC>
              <STATICVARIABLES>
                <SVCOMPANYCONNECT>{company_name}</SVCOMPANYCONNECT>
              </STATICVARIABLES>
              <TDL>
                <TDLMESSAGE>
                  <COLLECTION NAME="List of Voucher Entries">
                    <TYPE>VoucherEntry</TYPE>
                    <FETCH>VOUCHERNUMBER,DATE,VOUCHERTYPENAME,LEDGERNAME,AMOUNT,NARRATION,PARTYLEDGERNAME</FETCH>
                  </COLLECTION>
                </TDLMESSAGE>
              </TDL>
            </DESC>
          </BODY>
        </ENVELOPE>
        """
        
        try:
            root_collection_entries = send_tally_request(xml_request_collection_entries, timeout=45)
            collection_entries = []
            
            for collection in root_collection_entries.iter("COLLECTION"):
                for entry in collection:
                    collection_entries.append({
                        "VoucherNumber": entry.findtext("VOUCHERNUMBER"),
                        "VoucherDate": entry.findtext("DATE"),
                        "VoucherType": entry.findtext("VOUCHERTYPENAME"),
                        "LedgerName": entry.findtext("LEDGERNAME"),
                        "Amount": entry.findtext("AMOUNT"),
                        "Narration": entry.findtext("NARRATION"),
                        "PartyLedgerName": entry.findtext("PARTYLEDGERNAME")
                    })
            
            print(f"   Found {len(collection_entries)} voucher entries using Collection method")
            if len(collection_entries) > 0:
                print(f"   Sample entry: {collection_entries[0]}")
                
        except Exception as e:
            print(f"   ❌ Collection method failed: {e}")
        
        # Test 3: Try getting voucher entries through individual vouchers
        print("\n3. Testing individual voucher extraction...")
        
        # First get some vouchers
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
        
        try:
            root_vouchers = send_tally_request(xml_request_vouchers, timeout=120)
            individual_entries = []
            
            for voucher in root_vouchers.iter("VOUCHER"):
                voucher_number = voucher.findtext("VOUCHERNUMBER")
                voucher_date = voucher.findtext("DATE")
                voucher_type = voucher.findtext("VOUCHERTYPENAME")
                
                print(f"   Processing voucher: {voucher_number}")
                
                # Look for different possible entry structures
                for entry in voucher.iter("LEDGERENTRY"):
                    individual_entries.append({
                        "VoucherNumber": voucher_number,
                        "VoucherDate": voucher_date,
                        "VoucherType": voucher_type,
                        "LedgerName": entry.findtext("LEDGERNAME"),
                        "Amount": entry.findtext("AMOUNT"),
                        "Narration": entry.findtext("NARRATION"),
                        "PartyLedgerName": entry.findtext("PARTYLEDGERNAME")
                    })
                
                # Also look for ALLEDGERENTRIES
                for all_entries in voucher.iter("ALLEDGERENTRIES"):
                    for entry in all_entries.iter("LEDGERENTRY"):
                        individual_entries.append({
                            "VoucherNumber": voucher_number,
                            "VoucherDate": voucher_date,
                            "VoucherType": voucher_type,
                            "LedgerName": entry.findtext("LEDGERNAME"),
                            "Amount": entry.findtext("AMOUNT"),
                            "Narration": entry.findtext("NARRATION"),
                            "PartyLedgerName": entry.findtext("PARTYLEDGERNAME")
                        })
            
            print(f"   Found {len(individual_entries)} voucher entries from individual vouchers")
            if len(individual_entries) > 0:
                print(f"   Sample entry: {individual_entries[0]}")
                
        except Exception as e:
            print(f"   ❌ Individual voucher extraction failed: {e}")
        
        # Test 4: Try different report names for voucher entries
        print("\n4. Testing different report names...")
        
        report_names = ["VoucherEntries", "LedgerEntries", "AllLedgerEntries", "VoucherDetails"]
        
        for report_name in report_names:
            print(f"   Testing report: {report_name}")
            xml_request_report = f"""
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
                root_report = send_tally_request(xml_request_report, timeout=30)
                report_entries = []
                
                for voucher in root_report.iter("VOUCHER"):
                    voucher_number = voucher.findtext("VOUCHERNUMBER")
                    voucher_date = voucher.findtext("DATE")
                    voucher_type = voucher.findtext("VOUCHERTYPENAME")
                    
                    for entry in voucher.iter("LEDGERENTRY"):
                        report_entries.append({
                            "VoucherNumber": voucher_number,
                            "VoucherDate": voucher_date,
                            "VoucherType": voucher_type,
                            "LedgerName": entry.findtext("LEDGERNAME"),
                            "Amount": entry.findtext("AMOUNT"),
                            "Narration": entry.findtext("NARRATION"),
                            "PartyLedgerName": entry.findtext("PARTYLEDGERNAME")
                        })
                
                print(f"     Found {len(report_entries)} entries using {report_name}")
                if len(report_entries) > 0:
                    print(f"     Sample: {report_entries[0]}")
                    
            except Exception as e:
                print(f"     ❌ {report_name} failed: {e}")
        
        print("\n=== Test Complete ===")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 