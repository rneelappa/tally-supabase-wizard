#!/usr/bin/env python3
"""
Corrected Tally Prime XML API integration.
Based on proper XML structures and company context requirements.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import requests
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Tally Data Extractor API",
    description="An API to fetch Companies, Divisions (Cost Centres), Ledgers, and Vouchers from Tally ERP 9 / Prime via its XML interface.",
    version="1.0.0",
)

TALLY_URL = "http://localhost:9000"

def send_tally_request(xml_request: str):
    """
    Sends an XML request to the Tally server and returns the parsed XML response.
    """
    headers = {'Content-Type': 'application/xml; charset=utf-8'}
    try:
        response = requests.post(TALLY_URL, data=xml_request.encode('utf-8'), headers=headers, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes
        return ET.fromstring(response.content)
    except requests.exceptions.RequestException as e:
        logger.error(f"Request to Tally timed out: {e}")
        raise ConnectionError(f"Failed to connect to Tally at {TALLY_URL}. Error: {e}")
    except ET.ParseError as e:
        # Tally might return an error message in the body that is not valid XML
        # We try to extract the error message from the response text.
        error_text = response.text
        raise ValueError(f"Failed to parse Tally's XML response. Tally Error: {error_text}. Details: {e}")

@app.get("/companies", tags=["1. Companies"])
def get_companies():
    """
    Fetches a list of all companies loaded in Tally.
    This request is global and does not require a company context.
    """
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
          <STATICVARIABLES/>
          <TDL>
            <TDLMESSAGE>
              <COLLECTION NAME="List of Companies" ISMODIFY="No">
                <TYPE>Company</TYPE>
                <FETCH>NAME,GUID,STARTINGFROM</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    try:
        root = send_tally_request(xml_request)
        companies = []
        for comp in root.findall(".//COMPANY"):
            companies.append({
                "Name": comp.findtext("NAME"),
                "GUID": comp.findtext("GUID"),
                "FinancialYearStart": comp.findtext("STARTINGFROM"),
            })
        return JSONResponse(content=companies)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/divisions/{company_name}", tags=["2. Company Data"])
def get_divisions(company_name: str):
    """
    Fetches Cost Centres (Divisions/Departments) for a specific company.
    This requires providing the company name for context.
    """
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
              <COLLECTION NAME="List of Cost Centres" ISMODIFY="No">
                <TYPE>CostCentre</TYPE>
                <FETCH>NAME,PARENT,CATEGORY</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    try:
        root = send_tally_request(xml_request)
        divisions = []
        for div in root.findall(".//COSTCENTRE"):
            divisions.append({
                "Name": div.findtext("NAME"),
                "Parent": div.findtext("PARENT"),
                "Category": div.findtext("CATEGORY"),
            })
        return JSONResponse(content=divisions)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/ledgers/{company_name}", tags=["2. Company Data"])
def get_ledgers(company_name: str):
    """
    Fetches all Ledgers for a specific company.
    """
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
              <COLLECTION NAME="List of Ledgers" ISMODIFY="No">
                <TYPE>Ledger</TYPE>
                <FETCH>NAME,PARENT,OPENINGBALANCE,CLOSINGBALANCE</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    try:
        root = send_tally_request(xml_request)
        ledgers = []
        for ledger in root.findall(".//LEDGER"):
            ledgers.append({
                "Name": ledger.findtext("NAME"),
                "Group": ledger.findtext("PARENT"),
                "OpeningBalance": ledger.findtext("OPENINGBALANCE"),
                "ClosingBalance": ledger.findtext("CLOSINGBALANCE"),
            })
        return JSONResponse(content=ledgers)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/groups/{company_name}", tags=["2. Company Data"])
def get_groups(company_name: str):
    """
    Fetches all Groups for a specific company.
    """
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
              <COLLECTION NAME="List of Groups" ISMODIFY="No">
                <TYPE>Group</TYPE>
                <FETCH>NAME,PARENT</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    try:
        root = send_tally_request(xml_request)
        groups = []
        for group in root.findall(".//GROUP"):
            groups.append({
                "Name": group.findtext("NAME"),
                "Parent": group.findtext("PARENT"),
            })
        return JSONResponse(content=groups)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/vouchers/{company_name}", tags=["3. Transactions"])
def get_vouchers(company_name: str, from_date: str, to_date: str):
    """
    Fetches Vouchers with their entries for a company within a date range.
    Dates must be in Tally format: YYYYMMDD (e.g., 20230401)
    """
    xml_request = f"""
    <ENVELOPE>
        <HEADER>
            <TALLYREQUEST>Export Data</TALLYREQUEST>
        </HEADER>
        <BODY>
            <EXPORTDATA>
                <REQUESTDESC>
                    <STATICVARIABLES>
                        <SVFROMDATE>{from_date}</SVFROMDATE>
                        <SVTODATE>{to_date}</SVTODATE>
                        <SVCOMPANYCONNECT>{company_name}</SVCOMPANYCONNECT>
                    </STATICVARIABLES>
                    <REPORTNAME>Day Book</REPORTNAME>
                </REQUESTDESC>
            </EXPORTDATA>
        </BODY>
    </ENVELOPE>
    """
    try:
        root = send_tally_request(xml_request)
        vouchers = []
        for voucher in root.findall(".//VOUCHER"):
            ledger_entries = []
            for entry in voucher.findall(".//ALLLEDGERENTRIES.LIST"):
                ledger_entries.append({
                    "LedgerName": entry.findtext("LEDGERNAME"),
                    "IsDeemedPositive": entry.findtext("ISDEEMEDPOSITIVE"),
                    "Amount": entry.findtext("AMOUNT"),
                })
            
            vouchers.append({
                "Date": voucher.findtext("DATE"),
                "VoucherTypeName": voucher.findtext("VOUCHERTYPENAME"),
                "VoucherNumber": voucher.findtext("VOUCHERNUMBER"),
                "PartyLedgerName": voucher.findtext("PARTYLEDGERNAME"),
                "Narration": voucher.findtext("NARRATION"),
                "LedgerEntries": ledger_entries,
            })
        return JSONResponse(content=vouchers)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/voucher-entries/{company_name}", tags=["3. Transactions"])
def get_voucher_entries(company_name: str):
    """
    Fetches Voucher Entries for a specific company.
    """
    xml_request = f"""
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
              <COLLECTION NAME="List of Voucher Entries" ISMODIFY="No">
                <TYPE>VoucherEntry</TYPE>
                <FETCH>LEDGERNAME,AMOUNT,NARRATION,ISDEEMEDPOSITIVE</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    try:
        root = send_tally_request(xml_request)
        entries = []
        for entry in root.findall(".//VOUCHERENTRY"):
            entries.append({
                "LedgerName": entry.findtext("LEDGERNAME"),
                "Amount": entry.findtext("AMOUNT"),
                "Narration": entry.findtext("NARRATION"),
                "IsDeemedPositive": entry.findtext("ISDEEMEDPOSITIVE"),
            })
        return JSONResponse(content=entries)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/", tags=["Info"])
def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Tally Data Extractor API",
        "description": "API to fetch data from Tally Prime via XML interface",
        "version": "1.0.0",
        "endpoints": {
            "GET /companies": "Get list of all companies",
            "GET /divisions/{company_name}": "Get cost centres (divisions) for a company",
            "GET /ledgers/{company_name}": "Get ledgers for a company",
            "GET /groups/{company_name}": "Get groups for a company",
            "GET /vouchers/{company_name}": "Get vouchers for a company (with date range)",
            "GET /voucher-entries/{company_name}": "Get voucher entries for a company"
        },
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    
    print("Starting Tally Prime API Server...")
    print("Make sure Tally Prime is running and accessible at http://localhost:9000")
    print("API documentation will be available at http://127.0.0.1:8000/docs")
    
    uvicorn.run(app, host="127.0.0.1", port=8000) 