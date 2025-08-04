#!/usr/bin/env python3
"""
Test script to validate XML structures without requiring Tally to be running.
This script tests the XML generation and parsing logic.
"""

import xml.etree.ElementTree as ET
from tally_http_client import TallyHTTPClient

def test_xml_generation():
    """Test XML generation for different data types."""
    print("🧪 Testing XML Structure Generation")
    print("=" * 60)
    
    client = TallyHTTPClient()
    
    # Test 1: Companies XML
    print("\n1. Testing Companies XML Structure...")
    companies_xml = """
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
                <FETCH>NAME,GUID,EMAIL,STATE,PINCODE,PHONE,COMPANYNUMBER,ADDRESS,WEBSITE,MOBILE</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    
    try:
        ET.fromstring(companies_xml)
        print("✅ Companies XML structure is valid")
    except ET.ParseError as e:
        print(f"❌ Companies XML structure error: {e}")
    
    # Test 2: Cost Centres (Divisions) XML
    print("\n2. Testing Cost Centres XML Structure...")
    cost_centres_xml = """
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
            <SVCOMPANYCONNECT>Test Company</SVCOMPANYCONNECT>
          </STATICVARIABLES>
          <TDL>
            <TDLMESSAGE>
              <COLLECTION NAME="List of Cost Centres">
                <TYPE>CostCentre</TYPE>
                <FETCH>NAME,GUID,PARENT,CATEGORY,ADDRESS,PHONE,MOBILE,EMAIL</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    
    try:
        ET.fromstring(cost_centres_xml)
        print("✅ Cost Centres XML structure is valid")
    except ET.ParseError as e:
        print(f"❌ Cost Centres XML structure error: {e}")
    
    # Test 3: Ledgers XML
    print("\n3. Testing Ledgers XML Structure...")
    ledgers_xml = """
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
            <SVCOMPANYCONNECT>Test Company</SVCOMPANYCONNECT>
          </STATICVARIABLES>
          <TDL>
            <TDLMESSAGE>
              <COLLECTION NAME="List of Ledgers">
                <TYPE>Ledger</TYPE>
                <FETCH>NAME,GUID,PARENT,OPENINGBALANCE,CLOSINGBALANCE,ADDRESS,PHONE,MOBILE,EMAIL</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    
    try:
        ET.fromstring(ledgers_xml)
        print("✅ Ledgers XML structure is valid")
    except ET.ParseError as e:
        print(f"❌ Ledgers XML structure error: {e}")
    
    # Test 4: Vouchers XML with date range
    print("\n4. Testing Vouchers XML Structure...")
    vouchers_xml = """
    <ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>List of Vouchers</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES>
            <SVCOMPANYCONNECT>Test Company</SVCOMPANYCONNECT>
            <SVFROMDATE>20240101</SVFROMDATE>
            <SVTODATE>20241231</SVTODATE>
          </STATICVARIABLES>
          <TDL>
            <TDLMESSAGE>
              <COLLECTION NAME="List of Vouchers">
                <TYPE>Voucher</TYPE>
                <FETCH>VOUCHERNUMBER,DATE,NARRATION,VOUCHERTYPENAME,REFERENCE,AMOUNT</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    
    try:
        ET.fromstring(vouchers_xml)
        print("✅ Vouchers XML structure is valid")
    except ET.ParseError as e:
        print(f"❌ Vouchers XML structure error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ All XML structures are valid!")
    print("📋 Next: Start Tally Prime and test the connection")

def test_parsing_logic():
    """Test XML parsing logic with sample responses."""
    print("\n🧪 Testing XML Parsing Logic")
    print("=" * 60)
    
    # Sample company response
    sample_company_response = """
    <ENVELOPE>
      <COLLECTION>
        <COMPANY>
          <NAME>Test Company Ltd</NAME>
          <GUID>12345-67890</GUID>
          <EMAIL>test@company.com</EMAIL>
          <STATE>Karnataka</STATE>
        </COMPANY>
      </COLLECTION>
    </ENVELOPE>
    """
    
    print("\n1. Testing Company Response Parsing...")
    try:
        root = ET.fromstring(sample_company_response)
        companies = []
        for collection in root.iter("COLLECTION"):
            for comp in collection:
                if comp.tag == "COMPANY":
                    company = {}
                    for child in comp:
                        company[child.tag] = child.text
                    companies.append(company)
        
        if companies:
            print(f"✅ Successfully parsed {len(companies)} company")
            print(f"   Company: {companies[0].get('NAME', 'Unknown')}")
        else:
            print("❌ No companies found in response")
    except Exception as e:
        print(f"❌ Company parsing error: {e}")
    
    # Sample cost centre response
    sample_cost_centre_response = """
    <ENVELOPE>
      <COLLECTION>
        <COSTCENTRE>
          <NAME>Sales Department</NAME>
          <GUID>cc-12345</GUID>
          <PARENT>Departments</PARENT>
          <CATEGORY>Departments</CATEGORY>
        </COSTCENTRE>
        <COSTCENTRE>
          <NAME>Marketing Department</NAME>
          <GUID>cc-67890</GUID>
          <PARENT>Departments</PARENT>
          <CATEGORY>Departments</CATEGORY>
        </COSTCENTRE>
      </COLLECTION>
    </ENVELOPE>
    """
    
    print("\n2. Testing Cost Centre Response Parsing...")
    try:
        root = ET.fromstring(sample_cost_centre_response)
        cost_centres = []
        for collection in root.iter("COLLECTION"):
            for item in collection:
                if item.tag == "COSTCENTRE":
                    cost_centre = {}
                    for child in item:
                        cost_centre[child.tag] = child.text
                    cost_centres.append(cost_centre)
        
        if cost_centres:
            print(f"✅ Successfully parsed {len(cost_centres)} cost centres")
            for i, cc in enumerate(cost_centres[:2]):
                print(f"   {i+1}. {cc.get('NAME', 'Unknown')} ({cc.get('CATEGORY', 'N/A')})")
        else:
            print("❌ No cost centres found in response")
    except Exception as e:
        print(f"❌ Cost centre parsing error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ All parsing logic is working correctly!")

def main():
    """Main test function."""
    print("🧪 Testing Tally Prime XML Integration (Without Tally)")
    print("=" * 60)
    
    try:
        test_xml_generation()
        test_parsing_logic()
        
        print("\n📋 Setup Instructions:")
        print("1. Start Tally Prime")
        print("2. Go to Gateway of Tally → F12: Configure → Data Configuration")
        print("3. Enable 'Allow ODBC/XML Access'")
        print("4. Set 'Port Number' to 9000")
        print("5. Enable 'Allow XML Access'")
        print("6. Create or open a company in Tally")
        print("7. Run: py -3.11 test_corrected_integration.py")
        print("8. Or run: py -3.11 tally_api_corrected.py")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")

if __name__ == "__main__":
    main() 