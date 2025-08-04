from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import xml.etree.ElementTree as ET
import logging
from typing import List, Dict, Any, Optional
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Tally Prime REST API",
    description="REST API for accessing Tally Prime data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TALLY_URL = "http://localhost:9000"  # Tally default URL

def make_tally_request(xml_request: str) -> ET.Element:
    """Make a request to Tally Prime and return parsed XML response"""
    headers = {'Content-Type': 'application/xml'}
    
    try:
        response = requests.post(TALLY_URL, data=xml_request.encode(), headers=headers, timeout=30)
        response.raise_for_status()
        return ET.fromstring(response.text)
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to Tally Prime: {e}")
        raise HTTPException(status_code=503, detail=f"Tally Prime connection failed: {str(e)}")
    except ET.ParseError as e:
        logger.error(f"Failed to parse Tally response: {e}")
        raise HTTPException(status_code=500, detail=f"Invalid response from Tally Prime: {str(e)}")

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Tally Prime REST API",
        "version": "1.0.0",
        "endpoints": [
            "/companies",
            "/divisions", 
            "/ledgers",
            "/vouchers",
            "/voucher-entries",
            "/health"
        ]
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Simple test request to Tally
        test_xml = """
        <ENVELOPE>
          <HEADER>
            <VERSION>1</VERSION>
            <TALLYREQUEST>Export</TALLYREQUEST>
            <TYPE>Collection</TYPE>
            <ID>Test</ID>
          </HEADER>
          <BODY>
            <DESC>
              <STATICVARIABLES />
              <TDL>
                <TDLMESSAGE>
                  <COLLECTION NAME="Test">
                    <TYPE>Company</TYPE>
                    <FETCH>NAME</FETCH>
                  </COLLECTION>
                </TDLMESSAGE>
              </TDL>
            </DESC>
          </BODY>
        </ENVELOPE>
        """
        
        root = make_tally_request(test_xml)
        return {"status": "healthy", "tally_connection": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "tally_connection": "disconnected", "error": str(e)}

@app.get("/companies")
def get_companies():
    """Get all companies from Tally Prime"""
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
                <FETCH>NAME,GUID,EMAIL,STATE,PINCODE,PHONE,COMPANYNUMBER,ADDRESS,COUNTRY,CURRENCYNAME,BOOKSBEGINFROM,COMPANYNUMBER,FAXNUMBER,MOBILENUMBER,WEBSITE</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """

    try:
        root = make_tally_request(xml_request)
        companies = []
        
        for collection in root.iter("COLLECTION"):
            for comp in collection:
                company_data = {}
                for field in ["NAME", "GUID", "EMAIL", "STATE", "PINCODE", "PHONE", 
                             "COMPANYNUMBER", "ADDRESS", "COUNTRY", "CURRENCYNAME", 
                             "BOOKSBEGINFROM", "FAXNUMBER", "MOBILENUMBER", "WEBSITE"]:
                    value = comp.findtext(field)
                    if value:
                        company_data[field.lower()] = value
                
                if company_data:  # Only add if we have data
                    companies.append(company_data)

        return {"companies": companies, "count": len(companies)}

    except Exception as e:
        logger.error(f"Error fetching companies: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch companies: {str(e)}")

@app.get("/divisions")
def get_divisions():
    """Get all divisions/cost centres from Tally Prime"""
    xml_request = """
    <ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>List of Cost Centres</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES />
          <TDL>
            <TDLMESSAGE>
              <COLLECTION NAME="List of Cost Centres">
                <TYPE>CostCentre</TYPE>
                <FETCH>NAME,GUID,PARENT,ADDRESS,PHONE,EMAIL,CONTACTPERSON,MOBILENUMBER,FAXNUMBER,WEBSITE</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """

    try:
        root = make_tally_request(xml_request)
        divisions = []
        
        for collection in root.iter("COLLECTION"):
            for div in collection:
                division_data = {}
                for field in ["NAME", "GUID", "PARENT", "ADDRESS", "PHONE", "EMAIL", 
                             "CONTACTPERSON", "MOBILENUMBER", "FAXNUMBER", "WEBSITE"]:
                    value = div.findtext(field)
                    if value:
                        division_data[field.lower()] = value
                
                if division_data:
                    divisions.append(division_data)

        return {"divisions": divisions, "count": len(divisions)}

    except Exception as e:
        logger.error(f"Error fetching divisions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch divisions: {str(e)}")

@app.get("/ledgers")
def get_ledgers():
    """Get all ledgers from Tally Prime"""
    xml_request = """
    <ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>List of Ledgers</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES />
          <TDL>
            <TDLMESSAGE>
              <COLLECTION NAME="List of Ledgers">
                <TYPE>Ledger</TYPE>
                <FETCH>NAME,GUID,PARENT,OPENINGBALANCE,CURRENTBALANCE,ADDRESS,PHONE,EMAIL,CONTACTPERSON,MOBILENUMBER,FAXNUMBER,WEBSITE,LEDGERFORMALNAME,LEDGERTYPE</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """

    try:
        root = make_tally_request(xml_request)
        ledgers = []
        
        for collection in root.iter("COLLECTION"):
            for ledger in collection:
                ledger_data = {}
                for field in ["NAME", "GUID", "PARENT", "OPENINGBALANCE", "CURRENTBALANCE", 
                             "ADDRESS", "PHONE", "EMAIL", "CONTACTPERSON", "MOBILENUMBER", 
                             "FAXNUMBER", "WEBSITE", "LEDGERFORMALNAME", "LEDGERTYPE"]:
                    value = ledger.findtext(field)
                    if value:
                        ledger_data[field.lower()] = value
                
                if ledger_data:
                    ledgers.append(ledger_data)

        return {"ledgers": ledgers, "count": len(ledgers)}

    except Exception as e:
        logger.error(f"Error fetching ledgers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch ledgers: {str(e)}")

@app.get("/vouchers")
def get_vouchers():
    """Get all vouchers from Tally Prime"""
    xml_request = """
    <ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>List of Vouchers</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES />
          <TDL>
            <TDLMESSAGE>
              <COLLECTION NAME="List of Vouchers">
                <TYPE>Voucher</TYPE>
                <FETCH>VOUCHERNUMBER,VOUCHERTYPENAME,DATE,NARRATION,REFERENCE,AMOUNT,LEDGERENTRIES.LEDGERNAME,LEDGERENTRIES.ISDEEMEDPOSITIVE,LEDGERENTRIES.AMOUNT</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """

    try:
        root = make_tally_request(xml_request)
        vouchers = []
        
        for collection in root.iter("COLLECTION"):
            for voucher in collection:
                voucher_data = {}
                for field in ["VOUCHERNUMBER", "VOUCHERTYPENAME", "DATE", "NARRATION", "REFERENCE", "AMOUNT"]:
                    value = voucher.findtext(field)
                    if value:
                        voucher_data[field.lower()] = value
                
                # Handle ledger entries
                ledger_entries = []
                for entry in voucher.findall(".//LEDGERENTRIES"):
                    entry_data = {}
                    for field in ["LEDGERNAME", "ISDEEMEDPOSITIVE", "AMOUNT"]:
                        value = entry.findtext(field)
                        if value:
                            entry_data[field.lower()] = value
                    if entry_data:
                        ledger_entries.append(entry_data)
                
                if ledger_entries:
                    voucher_data["ledger_entries"] = ledger_entries
                
                if voucher_data:
                    vouchers.append(voucher_data)

        return {"vouchers": vouchers, "count": len(vouchers)}

    except Exception as e:
        logger.error(f"Error fetching vouchers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch vouchers: {str(e)}")

@app.get("/metadata")
def get_all_metadata():
    """Get all metadata from Tally Prime in one request"""
    try:
        # Get all data
        companies_response = get_companies()
        divisions_response = get_divisions()
        ledgers_response = get_ledgers()
        vouchers_response = get_vouchers()
        
        return {
            "companies": companies_response.get("companies", []),
            "divisions": divisions_response.get("divisions", []),
            "ledgers": ledgers_response.get("ledgers", []),
            "vouchers": vouchers_response.get("vouchers", []),
            "summary": {
                "companies_count": companies_response.get("count", 0),
                "divisions_count": divisions_response.get("count", 0),
                "ledgers_count": ledgers_response.get("count", 0),
                "vouchers_count": vouchers_response.get("count", 0)
            }
        }
    except Exception as e:
        logger.error(f"Error fetching all metadata: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch metadata: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 