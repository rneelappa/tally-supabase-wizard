#!/usr/bin/env python3
"""
Simple Tally API - Based on working code
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import requests
import xml.etree.ElementTree as ET
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

TALLY_URL = "http://localhost:9000"  # Tally default URL

def clean_xml_response(xml_text):
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

def safe_parse_xml(xml_text):
    """Safely parse XML with error handling"""
    try:
        # Clean the XML first
        cleaned_xml = clean_xml_response(xml_text)
        return ET.fromstring(cleaned_xml)
    except ET.ParseError as e:
        logger.error(f"XML Parse Error: {e}")
        logger.error(f"XML Content (first 500 chars): {xml_text[:500]}")
        raise e

@app.get("/companies")
def get_companies():
    """Get list of companies - This works!"""
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

    headers = {'Content-Type': 'application/xml'}

    try:
        response = requests.post(TALLY_URL, data=xml_request.encode(), headers=headers)
        root = safe_parse_xml(response.text)

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

        return JSONResponse(companies)

    except Exception as e:
        logger.error(f"Error getting companies: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/divisions/{company_name}")
def get_divisions(company_name: str):
    """Get divisions for a specific company using the working pattern"""
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

    headers = {'Content-Type': 'application/xml'}

    try:
        response = requests.post(TALLY_URL, data=xml_request.encode(), headers=headers)
        root = safe_parse_xml(response.text)

        divisions = []
        for collection in root.iter("COLLECTION"):
            for div in collection:
                divisions.append({
                    "Name": div.findtext("NAME"),
                    "GUID": div.findtext("GUID"),
                    "Parent": div.findtext("PARENT"),
                    "Category": div.findtext("CATEGORY")
                })

        return JSONResponse(divisions)

    except Exception as e:
        logger.error(f"Error getting divisions: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/ledgers/{company_name}")
def get_ledgers(company_name: str):
    """Get ledgers for a specific company using the working pattern"""
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

    headers = {'Content-Type': 'application/xml'}

    try:
        response = requests.post(TALLY_URL, data=xml_request.encode(), headers=headers)
        root = safe_parse_xml(response.text)

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

        return JSONResponse(ledgers)

    except Exception as e:
        logger.error(f"Error getting ledgers: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/groups/{company_name}")
def get_groups(company_name: str):
    """Get groups for a specific company using the working pattern"""
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

    headers = {'Content-Type': 'application/xml'}

    try:
        response = requests.post(TALLY_URL, data=xml_request.encode(), headers=headers)
        root = safe_parse_xml(response.text)

        groups = []
        for collection in root.iter("COLLECTION"):
            for group in collection:
                groups.append({
                    "Name": group.findtext("NAME"),
                    "GUID": group.findtext("GUID"),
                    "Parent": group.findtext("PARENT")
                })

        return JSONResponse(groups)

    except Exception as e:
        logger.error(f"Error getting groups: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/vouchers/{company_name}")
def get_vouchers(company_name: str):
    """Get vouchers for a specific company using the correct XML structure"""
    xml_request = f"""
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

    headers = {'Content-Type': 'application/xml'}

    try:
        response = requests.post(TALLY_URL, data=xml_request.encode(), headers=headers)
        root = safe_parse_xml(response.text)

        vouchers = []
        # Look for voucher data in the response
        for voucher in root.iter("VOUCHER"):
            vouchers.append({
                "VoucherNumber": voucher.findtext("VOUCHERNUMBER"),
                "Date": voucher.findtext("DATE"),
                "VoucherTypeName": voucher.findtext("VOUCHERTYPENAME"),
                "Narration": voucher.findtext("NARRATION"),
                "Reference": voucher.findtext("REFERENCE"),
                "Amount": voucher.findtext("AMOUNT")
            })

        return JSONResponse(vouchers)

    except Exception as e:
        logger.error(f"Error getting vouchers: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/voucher-entries/{company_name}")
def get_voucher_entries(company_name: str):
    """Get voucher entries for a specific company - Note: Voucher entries are embedded in voucher data"""
    return JSONResponse({
        "message": "Voucher entries are embedded within voucher data. Use the /vouchers endpoint to get complete voucher information including all ledger entries.",
        "company": company_name,
        "note": "For detailed ledger entries, use the /vouchers endpoint which includes AllLedgerEntries data"
    })

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Simple Tally API - Based on Working Code",
        "endpoints": {
            "GET /companies": "Get list of all companies",
            "GET /divisions/{company_name}": "Get divisions for a company",
            "GET /ledgers/{company_name}": "Get ledgers for a company",
            "GET /groups/{company_name}": "Get groups for a company",
            "GET /vouchers/{company_name}": "Get vouchers for a company",
            "GET /voucher-entries/{company_name}": "Get voucher entries for a company"
        },
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    
    print("Starting Simple Tally API Server...")
    print("Based on your working code!")
    print("API documentation will be available at http://127.0.0.1:8000/docs")
    
    uvicorn.run(app, host="127.0.0.1", port=8000) 