from fastapi import FastAPI
from fastapi.responses import JSONResponse
import requests
import xml.etree.ElementTree as ET

app = FastAPI()

TALLY_URL = "http://localhost:9000"  # Tally default URL

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
        
        headers = {'Content-Type': 'application/xml'}
        response = requests.post(TALLY_URL, data=test_xml.encode(), headers=headers)
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
        root = ET.fromstring(response.text)

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
        return JSONResponse({"error": str(e)}, status_code=500)

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

    headers = {'Content-Type': 'application/xml'}

    try:
        response = requests.post(TALLY_URL, data=xml_request.encode(), headers=headers)
        root = ET.fromstring(response.text)

        divisions = []
        for collection in root.iter("COLLECTION"):
            for div in collection:
                divisions.append({
                    "Name": div.findtext("NAME"),
                    "GUID": div.findtext("GUID"),
                    "Parent": div.findtext("PARENT"),
                    "Address": div.findtext("ADDRESS"),
                    "Phone": div.findtext("PHONE"),
                    "Email": div.findtext("EMAIL"),
                    "ContactPerson": div.findtext("CONTACTPERSON"),
                    "MobileNumber": div.findtext("MOBILENUMBER"),
                    "FaxNumber": div.findtext("FAXNUMBER"),
                    "Website": div.findtext("WEBSITE")
                })

        return JSONResponse(divisions)

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

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

    headers = {'Content-Type': 'application/xml'}

    try:
        response = requests.post(TALLY_URL, data=xml_request.encode(), headers=headers)
        root = ET.fromstring(response.text)

        ledgers = []
        for collection in root.iter("COLLECTION"):
            for ledger in collection:
                ledgers.append({
                    "Name": ledger.findtext("NAME"),
                    "GUID": ledger.findtext("GUID"),
                    "Parent": ledger.findtext("PARENT"),
                    "OpeningBalance": ledger.findtext("OPENINGBALANCE"),
                    "CurrentBalance": ledger.findtext("CURRENTBALANCE"),
                    "Address": ledger.findtext("ADDRESS"),
                    "Phone": ledger.findtext("PHONE"),
                    "Email": ledger.findtext("EMAIL"),
                    "ContactPerson": ledger.findtext("CONTACTPERSON"),
                    "MobileNumber": ledger.findtext("MOBILENUMBER"),
                    "FaxNumber": ledger.findtext("FAXNUMBER"),
                    "Website": ledger.findtext("WEBSITE"),
                    "LedgerFormalName": ledger.findtext("LEDGERFORMALNAME"),
                    "LedgerType": ledger.findtext("LEDGERTYPE")
                })

        return JSONResponse(ledgers)

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

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
                <FETCH>VOUCHERNUMBER,VOUCHERTYPENAME,DATE,NARRATION,REFERENCE,AMOUNT</FETCH>
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
        root = ET.fromstring(response.text)

        vouchers = []
        for collection in root.iter("COLLECTION"):
            for voucher in collection:
                vouchers.append({
                    "VoucherNumber": voucher.findtext("VOUCHERNUMBER"),
                    "VoucherTypeName": voucher.findtext("VOUCHERTYPENAME"),
                    "Date": voucher.findtext("DATE"),
                    "Narration": voucher.findtext("NARRATION"),
                    "Reference": voucher.findtext("REFERENCE"),
                    "Amount": voucher.findtext("AMOUNT")
                })

        return JSONResponse(vouchers)

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 