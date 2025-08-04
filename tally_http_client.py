#!/usr/bin/env python3
"""
Tally HTTP Client - Updated with working code from simple API
"""

import requests
import xml.etree.ElementTree as ET
import logging
import re

logger = logging.getLogger(__name__)

class TallyHTTPClient:
    def __init__(self, host='localhost', port=9000):
        self.base_url = f"http://{host}:{port}"
        
    def clean_xml_response(self, xml_text):
        """Clean malformed XML from Tally responses"""
        # Remove null characters
        xml_text = xml_text.replace('\x00', '')
        
        # Remove invalid XML characters
        xml_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', xml_text)
        
        # Fix common Tally XML issues
        xml_text = xml_text.replace('&', '&amp;')
        
        # Remove namespace prefixes that might cause issues
        xml_text = re.sub(r'xmlns:[^=]*="[^"]*"', '', xml_text)
        xml_text = re.sub(r'[a-zA-Z]+:', '', xml_text)
        
        # Remove any standalone namespace declarations
        xml_text = re.sub(r'xmlns="[^"]*"', '', xml_text)
        
        return xml_text

    def safe_parse_xml(self, xml_text):
        """Safely parse XML with error handling"""
        try:
            # Clean the XML first
            cleaned_xml = self.clean_xml_response(xml_text)
            return ET.fromstring(cleaned_xml)
        except ET.ParseError as e:
            logger.error(f"XML Parse Error: {e}")
            logger.error(f"XML Content (first 500 chars): {xml_text[:500]}")
            raise e

    def send_request(self, xml_request):
        """Send XML request to Tally and return parsed response"""
        headers = {'Content-Type': 'application/xml'}
        
        try:
            response = requests.post(self.base_url, data=xml_request.encode(), headers=headers, timeout=30)
            response.raise_for_status()
            return self.safe_parse_xml(response.text)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending HTTP request to Tally: {e}")
            raise

    def test_connection(self):
        """Test connection to Tally"""
        try:
            # Use the same working structure as simple_tally_api.py
            xml_request = """
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
            
            root = self.send_request(xml_request)
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def get_companies(self):
        """Get list of companies"""
        xml_request = """
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
            root = self.send_request(xml_request)
            companies = []
            
            for collection in root.iter("COLLECTION"):
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
            
            return companies
        except Exception as e:
            logger.error(f"Error getting companies: {e}")
            return []

    def get_divisions(self, company_name):
        """Get divisions for a specific company"""
        xml_request = f"""
        <ENVELOPE>
          <HEADER>
            <VERSION>1</VERSION>
            <TALLYREQUEST>Export</TALLYREQUEST>
            <TYPE>Collection</TYPE>
            <ID>List of Cost Centres</ID>
          </HEADER>
          <BODY>
            <DESC>
              <STATICVARIABLES>
                <SVCOMPANYCONNECT>{company_name}</SVCOMPANYCONNECT>
              </STATICVARIABLES>
              <TDL>
                <TDLMESSAGE>
                  <COLLECTION NAME="List of Cost Centres">
                    <TYPE>CostCentre</TYPE>
                    <FETCH>NAME,GUID,PARENT,CATEGORY</FETCH>
                  </COLLECTION>
                </TDLMESSAGE>
              </TDL>
            </DESC>
          </BODY>
        </ENVELOPE>
        """
        
        try:
            root = self.send_request(xml_request)
            divisions = []
            
            for collection in root.iter("COLLECTION"):
                for div in collection:
                    divisions.append({
                        "Name": div.findtext("NAME"),
                        "GUID": div.findtext("GUID"),
                        "Parent": div.findtext("PARENT"),
                        "Category": div.findtext("CATEGORY")
                    })
            
            return divisions
        except Exception as e:
            logger.error(f"Error getting divisions: {e}")
            return []

    def get_ledgers(self, company_name):
        """Get ledgers for a specific company"""
        xml_request = f"""
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
                    <FETCH>NAME,GUID,PARENT,OPENINGBALANCE,CLOSINGBALANCE</FETCH>
                  </COLLECTION>
                </TDLMESSAGE>
              </TDL>
            </DESC>
          </BODY>
        </ENVELOPE>
        """
        
        try:
            root = self.send_request(xml_request)
            ledgers = []
            
            for collection in root.iter("COLLECTION"):
                for ledger in collection:
                    ledgers.append({
                        "Name": ledger.findtext("NAME"),
                        "GUID": ledger.findtext("GUID"),
                        "Parent": ledger.findtext("PARENT"),
                        "OpeningBalance": ledger.findtext("OPENINGBALANCE"),
                        "ClosingBalance": ledger.findtext("CLOSINGBALANCE")
                    })
            
            return ledgers
        except Exception as e:
            logger.error(f"Error getting ledgers: {e}")
            return []

    def get_groups(self, company_name):
        """Get groups for a specific company"""
        xml_request = f"""
        <ENVELOPE>
          <HEADER>
            <VERSION>1</VERSION>
            <TALLYREQUEST>Export</TALLYREQUEST>
            <TYPE>Collection</TYPE>
            <ID>List of Groups</ID>
          </HEADER>
          <BODY>
            <DESC>
              <STATICVARIABLES>
                <SVCOMPANYCONNECT>{company_name}</SVCOMPANYCONNECT>
              </STATICVARIABLES>
              <TDL>
                <TDLMESSAGE>
                  <COLLECTION NAME="List of Groups">
                    <TYPE>Group</TYPE>
                    <FETCH>NAME,GUID,PARENT</FETCH>
                  </COLLECTION>
                </TDLMESSAGE>
              </TDL>
            </DESC>
          </BODY>
        </ENVELOPE>
        """
        
        try:
            root = self.send_request(xml_request)
            groups = []
            
            for collection in root.iter("COLLECTION"):
                for group in collection:
                    groups.append({
                        "Name": group.findtext("NAME"),
                        "GUID": group.findtext("GUID"),
                        "Parent": group.findtext("PARENT")
                    })
            
            return groups
        except Exception as e:
            logger.error(f"Error getting groups: {e}")
            return []

    def get_vouchers(self, company_name):
        """Get vouchers for a specific company using the working DayBook method"""
        xml_request = f"""
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
            root = self.send_request(xml_request)
            vouchers = []
            
            for voucher in root.iter("VOUCHER"):
                vouchers.append({
                    "VoucherNumber": voucher.findtext("VOUCHERNUMBER"),
                    "Date": voucher.findtext("DATE"),
                    "VoucherTypeName": voucher.findtext("VOUCHERTYPENAME"),
                    "Narration": voucher.findtext("NARRATION"),
                    "Reference": voucher.findtext("REFERENCE"),
                    "Amount": voucher.findtext("AMOUNT")
                })
            
            return vouchers
        except Exception as e:
            logger.error(f"Error getting vouchers: {e}")
            return []

    def get_voucher_entries(self, company_name):
        """Get voucher entries for a specific company using DayBook report"""
        xml_request = f"""
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
            root = self.send_request(xml_request)
            voucher_entries = []
            
            # Look for voucher entries in the DayBook response
            for voucher in root.iter("VOUCHER"):
                voucher_number = voucher.findtext("VOUCHERNUMBER")
                voucher_date = voucher.findtext("DATE")
                voucher_type = voucher.findtext("VOUCHERTYPENAME")
                
                # Look for ledger entries within each voucher
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
            
            return voucher_entries
        except Exception as e:
            logger.error(f"Error getting voucher entries: {e}")
            return []