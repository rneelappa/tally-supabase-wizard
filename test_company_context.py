#!/usr/bin/env python3
"""
Test script to get company details first and use as context for other data types.
"""

import requests
import xml.etree.ElementTree as ET
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TALLY_URL = "http://localhost:9000"

def get_company_details():
    """Get the first company details."""
    print("🔍 Getting Company Details...")
    print("=" * 50)
    
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
        headers = {'Content-Type': 'application/xml; charset=utf-8'}
        response = requests.post(TALLY_URL, data=xml_request.encode('utf-8'), headers=headers, timeout=30)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        companies = []
        
        for comp in root.findall(".//COMPANY"):
            company = {
                "Name": comp.findtext("NAME"),
                "GUID": comp.findtext("GUID"),
                "FinancialYearStart": comp.findtext("STARTINGFROM"),
            }
            companies.append(company)
            print(f"✅ Found Company: {company['Name']}")
            print(f"   GUID: {company['GUID']}")
            print(f"   Financial Year Start: {company['FinancialYearStart']}")
        
        return companies[0] if companies else None
        
    except Exception as e:
        print(f"❌ Error getting company details: {e}")
        return None

def test_with_company_context(company_name):
    """Test other data types using company context."""
    print(f"\n🔍 Testing with Company Context: {company_name}")
    print("=" * 50)
    
    # Test 1: Divisions (Cost Centres)
    print("\n1. Testing Divisions (Cost Centres)...")
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
        headers = {'Content-Type': 'application/xml; charset=utf-8'}
        response = requests.post(TALLY_URL, data=divisions_xml.encode('utf-8'), headers=headers, timeout=30)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        divisions = []
        
        for div in root.findall(".//COSTCENTRE"):
            division = {
                "Name": div.findtext("NAME"),
                "Parent": div.findtext("PARENT"),
                "Category": div.findtext("CATEGORY"),
            }
            divisions.append(division)
        
        print(f"✅ Found {len(divisions)} divisions/cost centres")
        for div in divisions[:3]:  # Show first 3
            print(f"   - {div['Name']} (Parent: {div['Parent']})")
        
    except Exception as e:
        print(f"❌ Error getting divisions: {e}")
    
    # Test 2: Ledgers
    print("\n2. Testing Ledgers...")
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
        headers = {'Content-Type': 'application/xml; charset=utf-8'}
        response = requests.post(TALLY_URL, data=ledgers_xml.encode('utf-8'), headers=headers, timeout=30)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        ledgers = []
        
        for ledger in root.findall(".//LEDGER"):
            ledger_data = {
                "Name": ledger.findtext("NAME"),
                "Group": ledger.findtext("PARENT"),
                "OpeningBalance": ledger.findtext("OPENINGBALANCE"),
                "ClosingBalance": ledger.findtext("CLOSINGBALANCE"),
            }
            ledgers.append(ledger_data)
        
        print(f"✅ Found {len(ledgers)} ledgers")
        for ledger in ledgers[:3]:  # Show first 3
            print(f"   - {ledger['Name']} (Group: {ledger['Group']})")
        
    except Exception as e:
        print(f"❌ Error getting ledgers: {e}")
    
    # Test 3: Groups
    print("\n3. Testing Groups...")
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
        headers = {'Content-Type': 'application/xml; charset=utf-8'}
        response = requests.post(TALLY_URL, data=groups_xml.encode('utf-8'), headers=headers, timeout=30)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        groups = []
        
        for group in root.findall(".//GROUP"):
            group_data = {
                "Name": group.findtext("NAME"),
                "Parent": group.findtext("PARENT"),
            }
            groups.append(group_data)
        
        print(f"✅ Found {len(groups)} groups")
        for group in groups[:3]:  # Show first 3
            print(f"   - {group['Name']} (Parent: {group['Parent']})")
        
    except Exception as e:
        print(f"❌ Error getting groups: {e}")

def main():
    """Main test function."""
    print("🧪 Testing Tally Data with Company Context")
    print("=" * 60)
    
    # Step 1: Get company details
    company = get_company_details()
    
    if not company:
        print("❌ No company found. Please ensure Tally Prime is running with a company open.")
        return
    
    # Step 2: Test other data types with company context
    test_with_company_context(company['Name'])
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")

if __name__ == "__main__":
    main() 