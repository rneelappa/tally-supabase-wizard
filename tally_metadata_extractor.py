#!/usr/bin/env python3
"""
Tally Prime Metadata Extractor
Extracts metadata from Tally Prime including companies, divisions, ledgers, vouchers, and voucher entries.
"""

import socket
import xml.etree.ElementTree as ET
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TallyConnection:
    """Manages connection to Tally Prime."""
    
    def __init__(self, host: str = "localhost", port: int = 9000):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to Tally Prime."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            self.connected = True
            logger.info(f"Connected to Tally Prime at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Tally Prime: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from Tally Prime."""
        if self.socket:
            self.socket.close()
            self.connected = False
            logger.info("Disconnected from Tally Prime")
    
    def send_request(self, request: str) -> Optional[str]:
        """Send request to Tally and get response."""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            # Add request length header
            request_with_header = f"{len(request):06d}{request}"
            self.socket.send(request_with_header.encode('utf-8'))
            
            # Read response
            response = self._read_response()
            return response
        except Exception as e:
            logger.error(f"Error sending request to Tally: {e}")
            self.connected = False
            return None
    
    def _read_response(self) -> str:
        """Read response from Tally."""
        try:
            # Read response length
            length_data = self.socket.recv(6)
            if not length_data:
                return ""
            
            response_length = int(length_data.decode('utf-8'))
            
            # Read response data
            response_data = b""
            while len(response_data) < response_length:
                chunk = self.socket.recv(response_length - len(response_data))
                if not chunk:
                    break
                response_data += chunk
            
            return response_data.decode('utf-8')
        except Exception as e:
            logger.error(f"Error reading response from Tally: {e}")
            return ""


class TallyMetadataExtractor:
    """Extracts metadata from Tally Prime."""
    
    def __init__(self, host: str = "localhost", port: int = 9000):
        self.connection = TallyConnection(host, port)
        self.cache = {}
        self.cache_timestamp = {}
        self.cache_duration = 300  # 5 minutes
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid."""
        if key not in self.cache_timestamp:
            return False
        return time.time() - self.cache_timestamp[key] < self.cache_duration
    
    def _update_cache(self, key: str, data: Any):
        """Update cache with new data."""
        self.cache[key] = data
        self.cache_timestamp[key] = time.time()
    
    def get_companies(self) -> List[Dict[str, Any]]:
        """Get list of companies from Tally."""
        cache_key = "companies"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        request = """
        <ENVELOPE>
            <HEADER>
                <TALLYREQUEST>Export Data</TALLYREQUEST>
            </HEADER>
            <BODY>
                <DESC>
                    <STATICVARIABLES>
                        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    </STATICVARIABLES>
                    <TDL>
                        <TDLMESSAGE>
                            <COLLECTION NAME="Companies" ISMODIFY="No">
                                <TYPE>Company</TYPE>
                                <FETCH>Name, StartingFrom, ClosingUpto, Address, Phone, Mobile, Email, Website</FETCH>
                            </COLLECTION>
                        </TDLMESSAGE>
                    </TDL>
                </DESC>
            </BODY>
        </ENVELOPE>
        """
        
        response = self.connection.send_request(request)
        if response:
            companies = self._parse_companies_response(response)
            self._update_cache(cache_key, companies)
            return companies
        return []
    
    def get_divisions(self, company_name: str = None) -> List[Dict[str, Any]]:
        """Get list of divisions from Tally."""
        cache_key = f"divisions_{company_name or 'all'}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        request = """
        <ENVELOPE>
            <HEADER>
                <TALLYREQUEST>Export Data</TALLYREQUEST>
            </HEADER>
            <BODY>
                <DESC>
                    <STATICVARIABLES>
                        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    </STATICVARIABLES>
                    <TDL>
                        <TDLMESSAGE>
                            <COLLECTION NAME="Divisions" ISMODIFY="No">
                                <TYPE>Division</TYPE>
                                <FETCH>Name, Parent, Address, Phone, Mobile, Email</FETCH>
                            </COLLECTION>
                        </TDLMESSAGE>
                    </TDL>
                </DESC>
            </BODY>
        </ENVELOPE>
        """
        
        response = self.connection.send_request(request)
        if response:
            divisions = self._parse_divisions_response(response)
            self._update_cache(cache_key, divisions)
            return divisions
        return []
    
    def get_ledgers(self, company_name: str = None) -> List[Dict[str, Any]]:
        """Get list of ledgers from Tally."""
        cache_key = f"ledgers_{company_name or 'all'}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        request = """
        <ENVELOPE>
            <HEADER>
                <TALLYREQUEST>Export Data</TALLYREQUEST>
            </HEADER>
            <BODY>
                <DESC>
                    <STATICVARIABLES>
                        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    </STATICVARIABLES>
                    <TDL>
                        <TDLMESSAGE>
                            <COLLECTION NAME="Ledgers" ISMODIFY="No">
                                <TYPE>Ledger</TYPE>
                                <FETCH>Name, Parent, OpeningBalance, ClosingBalance, Address, Phone, Mobile, Email</FETCH>
                            </COLLECTION>
                        </TDLMESSAGE>
                    </TDL>
                </DESC>
            </BODY>
        </ENVELOPE>
        """
        
        response = self.connection.send_request(request)
        if response:
            ledgers = self._parse_ledgers_response(response)
            self._update_cache(cache_key, ledgers)
            return ledgers
        return []
    
    def get_vouchers(self, company_name: str = None, from_date: str = None, to_date: str = None) -> List[Dict[str, Any]]:
        """Get list of vouchers from Tally."""
        cache_key = f"vouchers_{company_name or 'all'}_{from_date or 'all'}_{to_date or 'all'}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        # Build date filter
        date_filter = ""
        if from_date and to_date:
            date_filter = f"""
                <SVFROMDATE>{from_date}</SVFROMDATE>
                <SVTODATE>{to_date}</SVTODATE>
            """
        
        request = f"""
        <ENVELOPE>
            <HEADER>
                <TALLYREQUEST>Export Data</TALLYREQUEST>
            </HEADER>
            <BODY>
                <DESC>
                    <STATICVARIABLES>
                        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                        {date_filter}
                    </STATICVARIABLES>
                    <TDL>
                        <TDLMESSAGE>
                            <COLLECTION NAME="Vouchers" ISMODIFY="No">
                                <TYPE>Voucher</TYPE>
                                <FETCH>VoucherNumber, Date, VoucherTypeName, Narration, PartyLedgerName, Amount</FETCH>
                            </COLLECTION>
                        </TDLMESSAGE>
                    </TDL>
                </DESC>
            </BODY>
        </ENVELOPE>
        """
        
        response = self.connection.send_request(request)
        if response:
            vouchers = self._parse_vouchers_response(response)
            self._update_cache(cache_key, vouchers)
            return vouchers
        return []
    
    def get_voucher_entries(self, voucher_number: str = None, company_name: str = None) -> List[Dict[str, Any]]:
        """Get voucher entries from Tally."""
        cache_key = f"voucher_entries_{voucher_number or 'all'}_{company_name or 'all'}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        request = """
        <ENVELOPE>
            <HEADER>
                <TALLYREQUEST>Export Data</TALLYREQUEST>
            </HEADER>
            <BODY>
                <DESC>
                    <STATICVARIABLES>
                        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    </STATICVARIABLES>
                    <TDL>
                        <TDLMESSAGE>
                            <COLLECTION NAME="VoucherEntries" ISMODIFY="No">
                                <TYPE>Voucher</TYPE>
                                <FETCH>VoucherNumber, Date, VoucherTypeName, LedgerName, Amount, IsDeemedPositive, Narration</FETCH>
                            </COLLECTION>
                        </TDLMESSAGE>
                    </TDL>
                </DESC>
            </BODY>
        </ENVELOPE>
        """
        
        response = self.connection.send_request(request)
        if response:
            entries = self._parse_voucher_entries_response(response)
            self._update_cache(cache_key, entries)
            return entries
        return []
    
    def get_all_metadata(self, company_name: str = None) -> Dict[str, Any]:
        """Get all metadata from Tally."""
        return {
            "companies": self.get_companies(),
            "divisions": self.get_divisions(company_name),
            "ledgers": self.get_ledgers(company_name),
            "vouchers": self.get_vouchers(company_name),
            "voucher_entries": self.get_voucher_entries(company_name=company_name),
            "extracted_at": datetime.now().isoformat(),
            "tally_connection": {
                "host": self.connection.host,
                "port": self.connection.port,
                "connected": self.connection.connected
            }
        }
    
    def _parse_companies_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse companies from Tally response."""
        try:
            root = ET.fromstring(response)
            companies = []
            
            for company in root.findall(".//COLLECTION[@NAME='Companies']/COMPANY"):
                company_data = {
                    "name": company.find("NAME").text if company.find("NAME") is not None else "",
                    "starting_from": company.find("STARTINGFROM").text if company.find("STARTINGFROM") is not None else "",
                    "closing_upto": company.find("CLOSINGUPTO").text if company.find("CLOSINGUPTO") is not None else "",
                    "address": company.find("ADDRESS").text if company.find("ADDRESS") is not None else "",
                    "phone": company.find("PHONE").text if company.find("PHONE") is not None else "",
                    "mobile": company.find("MOBILE").text if company.find("MOBILE") is not None else "",
                    "email": company.find("EMAIL").text if company.find("EMAIL") is not None else "",
                    "website": company.find("WEBSITE").text if company.find("WEBSITE") is not None else ""
                }
                companies.append(company_data)
            
            return companies
        except Exception as e:
            logger.error(f"Error parsing companies response: {e}")
            return []
    
    def _parse_divisions_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse divisions from Tally response."""
        try:
            root = ET.fromstring(response)
            divisions = []
            
            for division in root.findall(".//COLLECTION[@NAME='Divisions']/DIVISION"):
                division_data = {
                    "name": division.find("NAME").text if division.find("NAME") is not None else "",
                    "parent": division.find("PARENT").text if division.find("PARENT") is not None else "",
                    "address": division.find("ADDRESS").text if division.find("ADDRESS") is not None else "",
                    "phone": division.find("PHONE").text if division.find("PHONE") is not None else "",
                    "mobile": division.find("MOBILE").text if division.find("MOBILE") is not None else "",
                    "email": division.find("EMAIL").text if division.find("EMAIL") is not None else ""
                }
                divisions.append(division_data)
            
            return divisions
        except Exception as e:
            logger.error(f"Error parsing divisions response: {e}")
            return []
    
    def _parse_ledgers_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse ledgers from Tally response."""
        try:
            root = ET.fromstring(response)
            ledgers = []
            
            for ledger in root.findall(".//COLLECTION[@NAME='Ledgers']/LEDGER"):
                ledger_data = {
                    "name": ledger.find("NAME").text if ledger.find("NAME") is not None else "",
                    "parent": ledger.find("PARENT").text if ledger.find("PARENT") is not None else "",
                    "opening_balance": ledger.find("OPENINGBALANCE").text if ledger.find("OPENINGBALANCE") is not None else "0",
                    "closing_balance": ledger.find("CLOSINGBALANCE").text if ledger.find("CLOSINGBALANCE") is not None else "0",
                    "address": ledger.find("ADDRESS").text if ledger.find("ADDRESS") is not None else "",
                    "phone": ledger.find("PHONE").text if ledger.find("PHONE") is not None else "",
                    "mobile": ledger.find("MOBILE").text if ledger.find("MOBILE") is not None else "",
                    "email": ledger.find("EMAIL").text if ledger.find("EMAIL") is not None else ""
                }
                ledgers.append(ledger_data)
            
            return ledgers
        except Exception as e:
            logger.error(f"Error parsing ledgers response: {e}")
            return []
    
    def _parse_vouchers_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse vouchers from Tally response."""
        try:
            root = ET.fromstring(response)
            vouchers = []
            
            for voucher in root.findall(".//COLLECTION[@NAME='Vouchers']/VOUCHER"):
                voucher_data = {
                    "voucher_number": voucher.find("VOUCHERNUMBER").text if voucher.find("VOUCHERNUMBER") is not None else "",
                    "date": voucher.find("DATE").text if voucher.find("DATE") is not None else "",
                    "voucher_type": voucher.find("VOUCHERTYPENAME").text if voucher.find("VOUCHERTYPENAME") is not None else "",
                    "narration": voucher.find("NARRATION").text if voucher.find("NARRATION") is not None else "",
                    "party_ledger": voucher.find("PARTYLEDGERNAME").text if voucher.find("PARTYLEDGERNAME") is not None else "",
                    "amount": voucher.find("AMOUNT").text if voucher.find("AMOUNT") is not None else "0"
                }
                vouchers.append(voucher_data)
            
            return vouchers
        except Exception as e:
            logger.error(f"Error parsing vouchers response: {e}")
            return []
    
    def _parse_voucher_entries_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse voucher entries from Tally response."""
        try:
            root = ET.fromstring(response)
            entries = []
            
            for entry in root.findall(".//COLLECTION[@NAME='VoucherEntries']/VOUCHER"):
                entry_data = {
                    "voucher_number": entry.find("VOUCHERNUMBER").text if entry.find("VOUCHERNUMBER") is not None else "",
                    "date": entry.find("DATE").text if entry.find("DATE") is not None else "",
                    "voucher_type": entry.find("VOUCHERTYPENAME").text if entry.find("VOUCHERTYPENAME") is not None else "",
                    "ledger_name": entry.find("LEDGERNAME").text if entry.find("LEDGERNAME") is not None else "",
                    "amount": entry.find("AMOUNT").text if entry.find("AMOUNT") is not None else "0",
                    "is_deemed_positive": entry.find("ISDEEMEDPOSITIVE").text if entry.find("ISDEEMEDPOSITIVE") is not None else "No",
                    "narration": entry.find("NARRATION").text if entry.find("NARRATION") is not None else ""
                }
                entries.append(entry_data)
            
            return entries
        except Exception as e:
            logger.error(f"Error parsing voucher entries response: {e}")
            return []
    
    def close(self):
        """Close the connection to Tally."""
        self.connection.disconnect()


if __name__ == "__main__":
    # Test the extractor
    extractor = TallyMetadataExtractor()
    
    try:
        # Test connection
        if extractor.connection.connect():
            print("✅ Connected to Tally Prime")
            
            # Get all metadata
            metadata = extractor.get_all_metadata()
            print(f"✅ Extracted metadata: {json.dumps(metadata, indent=2)}")
        else:
            print("❌ Failed to connect to Tally Prime")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        extractor.close() 