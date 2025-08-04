#!/usr/bin/env python3
"""
Detailed test script to get company details first and use as context for other data types.
With comprehensive logging for research purposes.
"""

import requests
import xml.etree.ElementTree as ET
import logging
import time
from datetime import datetime

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tally_detailed_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

TALLY_URL = "http://localhost:9000"

def log_request_details(xml_request: str, response=None, error=None):
    """Log detailed request and response information."""
    logger.info("=" * 80)
    logger.info("REQUEST DETAILS")
    logger.info("=" * 80)
    logger.info(f"URL: {TALLY_URL}")
    logger.info(f"Timestamp: {datetime.now()}")
    logger.info(f"Request Length: {len(xml_request)} characters")
    logger.info("Request XML:")
    logger.info(xml_request)
    
    if response:
        logger.info("RESPONSE DETAILS")
        logger.info("=" * 80)
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response Headers: {dict(response.headers)}")
        logger.info(f"Response Length: {len(response.content)} characters")
        logger.info(f"Response Time: {response.elapsed.total_seconds():.2f} seconds")
        logger.info("Response Content (first 1000 chars):")
        logger.info(response.text[:1000])
        if len(response.text) > 1000:
            logger.info("... (truncated)")
    elif error:
        logger.info("ERROR DETAILS")
        logger.info("=" * 80)
        logger.error(f"Error Type: {type(error).__name__}")
        logger.error(f"Error Message: {str(error)}")
    
    logger.info("=" * 80)

def get_company_details():
    """Get the first company details with detailed logging."""
    logger.info("🔍 Getting Company Details...")
    logger.info("=" * 50)
    
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
        logger.info("Sending companies request...")
        headers = {'Content-Type': 'application/xml; charset=utf-8'}
        start_time = time.time()
        
        response = requests.post(TALLY_URL, data=xml_request.encode('utf-8'), headers=headers, timeout=30)
        end_time = time.time()
        
        logger.info(f"Request completed in {end_time - start_time:.2f} seconds")
        log_request_details(xml_request, response)
        
        response.raise_for_status()
        
        logger.info("Parsing XML response...")
        root = ET.fromstring(response.content)
        companies = []
        
        logger.info("Searching for COMPANY tags...")
        company_elements = root.findall(".//COMPANY")
        logger.info(f"Found {len(company_elements)} COMPANY elements")
        
        for i, comp in enumerate(company_elements):
            logger.info(f"Processing company {i+1}:")
            company = {
                "Name": comp.findtext("NAME"),
                "GUID": comp.findtext("GUID"),
                "FinancialYearStart": comp.findtext("STARTINGFROM"),
            }
            companies.append(company)
            logger.info(f"  Company Name: {company['Name']}")
            logger.info(f"  GUID: {company['GUID']}")
            logger.info(f"  Financial Year Start: {company['FinancialYearStart']}")
            
            # Log all child elements for debugging
            logger.info("  All child elements:")
            for child in comp:
                logger.info(f"    {child.tag}: {child.text}")
        
        logger.info(f"✅ Successfully processed {len(companies)} companies")
        return companies[0] if companies else None
        
    except Exception as e:
        logger.error(f"❌ Error getting company details: {e}")
        log_request_details(xml_request, error=e)
        return None

def test_with_company_context(company_name):
    """Test other data types using company context with detailed logging."""
    logger.info(f"\n🔍 Testing with Company Context: {company_name}")
    logger.info("=" * 50)
    
    # Test 1: Divisions (Cost Centres)
    logger.info("\n1. Testing Divisions (Cost Centres)...")
    divisions_xml = f"""
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
        logger.info("Sending divisions request...")
        headers = {'Content-Type': 'application/xml; charset=utf-8'}
        start_time = time.time()
        
        response = requests.post(TALLY_URL, data=divisions_xml.encode('utf-8'), headers=headers, timeout=30)
        end_time = time.time()
        
        logger.info(f"Request completed in {end_time - start_time:.2f} seconds")
        log_request_details(divisions_xml, response)
        
        response.raise_for_status()
        
        logger.info("Parsing XML response...")
        root = ET.fromstring(response.content)
        divisions = []
        
        logger.info("Searching for COSTCENTRE tags...")
        costcentre_elements = root.findall(".//COSTCENTRE")
        logger.info(f"Found {len(costcentre_elements)} COSTCENTRE elements")
        
        for i, div in enumerate(costcentre_elements):
            logger.info(f"Processing cost centre {i+1}:")
            division = {
                "Name": div.findtext("NAME"),
                "Parent": div.findtext("PARENT"),
                "Category": div.findtext("CATEGORY"),
            }
            divisions.append(division)
            logger.info(f"  Name: {division['Name']}")
            logger.info(f"  Parent: {division['Parent']}")
            logger.info(f"  Category: {division['Category']}")
            
            # Log all child elements for debugging
            logger.info("  All child elements:")
            for child in div:
                logger.info(f"    {child.tag}: {child.text}")
        
        logger.info(f"✅ Found {len(divisions)} divisions/cost centres")
        
    except Exception as e:
        logger.error(f"❌ Error getting divisions: {e}")
        log_request_details(divisions_xml, error=e)
    
    # Test 2: Ledgers
    logger.info("\n2. Testing Ledgers...")
    ledgers_xml = f"""
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
        logger.info("Sending ledgers request...")
        headers = {'Content-Type': 'application/xml; charset=utf-8'}
        start_time = time.time()
        
        response = requests.post(TALLY_URL, data=ledgers_xml.encode('utf-8'), headers=headers, timeout=30)
        end_time = time.time()
        
        logger.info(f"Request completed in {end_time - start_time:.2f} seconds")
        log_request_details(ledgers_xml, response)
        
        response.raise_for_status()
        
        logger.info("Parsing XML response...")
        root = ET.fromstring(response.content)
        ledgers = []
        
        logger.info("Searching for LEDGER tags...")
        ledger_elements = root.findall(".//LEDGER")
        logger.info(f"Found {len(ledger_elements)} LEDGER elements")
        
        for i, ledger in enumerate(ledger_elements[:5]):  # Log first 5 only to avoid spam
            logger.info(f"Processing ledger {i+1}:")
            ledger_data = {
                "Name": ledger.findtext("NAME"),
                "Group": ledger.findtext("PARENT"),
                "OpeningBalance": ledger.findtext("OPENINGBALANCE"),
                "ClosingBalance": ledger.findtext("CLOSINGBALANCE"),
            }
            ledgers.append(ledger_data)
            logger.info(f"  Name: {ledger_data['Name']}")
            logger.info(f"  Group: {ledger_data['Group']}")
            logger.info(f"  Opening Balance: {ledger_data['OpeningBalance']}")
            logger.info(f"  Closing Balance: {ledger_data['ClosingBalance']}")
            
            # Log all child elements for debugging
            logger.info("  All child elements:")
            for child in ledger:
                logger.info(f"    {child.tag}: {child.text}")
        
        logger.info(f"✅ Found {len(ledgers)} ledgers (showing first 5)")
        
    except Exception as e:
        logger.error(f"❌ Error getting ledgers: {e}")
        log_request_details(ledgers_xml, error=e)
    
    # Test 3: Groups
    logger.info("\n3. Testing Groups...")
    groups_xml = f"""
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
        logger.info("Sending groups request...")
        headers = {'Content-Type': 'application/xml; charset=utf-8'}
        start_time = time.time()
        
        response = requests.post(TALLY_URL, data=groups_xml.encode('utf-8'), headers=headers, timeout=30)
        end_time = time.time()
        
        logger.info(f"Request completed in {end_time - start_time:.2f} seconds")
        log_request_details(groups_xml, response)
        
        response.raise_for_status()
        
        logger.info("Parsing XML response...")
        root = ET.fromstring(response.content)
        groups = []
        
        logger.info("Searching for GROUP tags...")
        group_elements = root.findall(".//GROUP")
        logger.info(f"Found {len(group_elements)} GROUP elements")
        
        for i, group in enumerate(group_elements[:5]):  # Log first 5 only
            logger.info(f"Processing group {i+1}:")
            group_data = {
                "Name": group.findtext("NAME"),
                "Parent": group.findtext("PARENT"),
            }
            groups.append(group_data)
            logger.info(f"  Name: {group_data['Name']}")
            logger.info(f"  Parent: {group_data['Parent']}")
            
            # Log all child elements for debugging
            logger.info("  All child elements:")
            for child in group:
                logger.info(f"    {child.tag}: {child.text}")
        
        logger.info(f"✅ Found {len(groups)} groups (showing first 5)")
        
    except Exception as e:
        logger.error(f"❌ Error getting groups: {e}")
        log_request_details(groups_xml, error=e)

def main():
    """Main test function with detailed logging."""
    logger.info("🧪 Testing Tally Data with Company Context - DETAILED LOGGING")
    logger.info("=" * 80)
    logger.info(f"Test started at: {datetime.now()}")
    logger.info(f"Tally URL: {TALLY_URL}")
    
    # Step 1: Get company details
    company = get_company_details()
    
    if not company:
        logger.error("❌ No company found. Please ensure Tally Prime is running with a company open.")
        return
    
    # Step 2: Test other data types with company context
    test_with_company_context(company['Name'])
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ Test completed!")
    logger.info(f"Test ended at: {datetime.now()}")
    logger.info("Check 'tally_detailed_test.log' for complete details")

if __name__ == "__main__":
    main() 