#!/usr/bin/env python3
"""
Research script to find correct XML structures for Tally Prime data types.
"""

import requests
import xml.etree.ElementTree as ET
import time

def test_xml_structure(xml_request, description):
    """Test a specific XML structure and return results."""
    print(f"\n=== {description} ===")
    
    try:
        response = requests.post(
            "http://localhost:9000", 
            data=xml_request.encode(), 
            headers={'Content-Type': 'application/xml'},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response length: {len(response.text)}")
        
        if response.status_code == 200 and response.text.strip():
            print(f"Response preview: {response.text[:300]}...")
            
            # Try to parse XML
            try:
                root = ET.fromstring(response.text)
                
                # Look for any data in the response
                data_found = False
                for elem in root.iter():
                    if elem.text and elem.text.strip():
                        print(f"Found data element: {elem.tag} = {elem.text[:50]}...")
                        data_found = True
                        break
                
                if not data_found:
                    print("No data found in response")
                    
                return True, response.text
                
            except ET.ParseError as e:
                print(f"XML parse error: {e}")
                return False, response.text
        else:
            print("No response or empty response")
            return False, ""
            
    except Exception as e:
        print(f"Request failed: {e}")
        return False, ""

def test_divisions_structures():
    """Test different XML structures for divisions."""
    print("\n" + "="*60)
    print("TESTING DIVISIONS XML STRUCTURES")
    print("="*60)
    
    # Test 1: Basic Division
    xml1 = """
    <ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>Divisions</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES />
          <TDL>
            <TDLMESSAGE>
              <COLLECTION NAME="Divisions">
                <TYPE>Division</TYPE>
                <FETCH>NAME,GUID,PARENT</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    test_xml_structure(xml1, "Test 1: Basic Division")
    
    # Test 2: Cost Centre (as divisions)
    xml2 = """
    <ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>Cost Centres</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES />
          <TDL>
            <TDLMESSAGE>
              <COLLECTION NAME="Cost Centres">
                <TYPE>CostCentre</TYPE>
                <FETCH>NAME,GUID,PARENT</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    test_xml_structure(xml2, "Test 2: Cost Centre")
    
    # Test 3: Group (as divisions)
    xml3 = """
    <ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>Groups</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES />
          <TDL>
            <TDLMESSAGE>
              <COLLECTION NAME="Groups">
                <TYPE>Group</TYPE>
                <FETCH>NAME,GUID,PARENT</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    test_xml_structure(xml3, "Test 3: Group")
    
    # Test 4: Branch (as divisions)
    xml4 = """
    <ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>Branches</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES />
          <TDL>
            <TDLMESSAGE>
              <COLLECTION NAME="Branches">
                <TYPE>Branch</TYPE>
                <FETCH>NAME,GUID,PARENT</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    test_xml_structure(xml4, "Test 4: Branch")

def test_ledgers_structures():
    """Test different XML structures for ledgers."""
    print("\n" + "="*60)
    print("TESTING LEDGERS XML STRUCTURES")
    print("="*60)
    
    # Test 1: Basic Ledger
    xml1 = """
    <ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>Ledgers</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES />
          <TDL>
            <TDLMESSAGE>
              <COLLECTION NAME="Ledgers">
                <TYPE>Ledger</TYPE>
                <FETCH>NAME,GUID,PARENT,OPENINGBALANCE,CLOSINGBALANCE</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    test_xml_structure(xml1, "Test 1: Basic Ledger")
    
    # Test 2: Ledger with more fields
    xml2 = """
    <ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>Ledgers Detailed</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES />
          <TDL>
            <TDLMESSAGE>
              <COLLECTION NAME="Ledgers">
                <TYPE>Ledger</TYPE>
                <FETCH>NAME,GUID,PARENT,OPENINGBALANCE,CLOSINGBALANCE,ADDRESS,PHONE,MOBILE,EMAIL</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    test_xml_structure(xml2, "Test 2: Ledger Detailed")

def test_vouchers_structures():
    """Test different XML structures for vouchers."""
    print("\n" + "="*60)
    print("TESTING VOUCHERS XML STRUCTURES")
    print("="*60)
    
    # Test 1: Basic Voucher
    xml1 = """
    <ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>Vouchers</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES />
          <TDL>
            <TDLMESSAGE>
              <COLLECTION NAME="Vouchers">
                <TYPE>Voucher</TYPE>
                <FETCH>VOUCHERNUMBER,DATE,NARRATION,VOUCHERTYPENAME</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    test_xml_structure(xml1, "Test 1: Basic Voucher")
    
    # Test 2: Voucher with more fields
    xml2 = """
    <ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>Vouchers Detailed</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES />
          <TDL>
            <TDLMESSAGE>
              <COLLECTION NAME="Vouchers">
                <TYPE>Voucher</TYPE>
                <FETCH>VOUCHERNUMBER,DATE,NARRATION,VOUCHERTYPENAME,REFERENCE,AMOUNT</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    test_xml_structure(xml2, "Test 2: Voucher Detailed")
    
    # Test 3: Voucher Entry
    xml3 = """
    <ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>Voucher Entries</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES />
          <TDL>
            <TDLMESSAGE>
              <COLLECTION NAME="Voucher Entries">
                <TYPE>VoucherEntry</TYPE>
                <FETCH>LEDGERNAME,AMOUNT,NARRATION,ISDEEMEDPOSITIVE</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    test_xml_structure(xml3, "Test 3: Voucher Entry")

def test_alternative_approaches():
    """Test alternative approaches for getting data."""
    print("\n" + "="*60)
    print("TESTING ALTERNATIVE APPROACHES")
    print("="*60)
    
    # Test 1: Using Object instead of Collection
    xml1 = """
    <ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Object</TYPE>
        <ID>Company Info</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES />
          <TDL>
            <TDLMESSAGE>
              <OBJECT NAME="Company Info">
                <TYPE>Company</TYPE>
                <FETCH>NAME,GUID,EMAIL,STATE,PINCODE,PHONE,COMPANYNUMBER</FETCH>
              </OBJECT>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    test_xml_structure(xml1, "Test 1: Object Type")
    
    # Test 2: Using Report instead of Collection
    xml2 = """
    <ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Report</TYPE>
        <ID>Ledger Report</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES />
          <TDL>
            <TDLMESSAGE>
              <REPORT NAME="Ledger Report">
                <TYPE>Ledger</TYPE>
                <FETCH>NAME,GUID,PARENT,OPENINGBALANCE,CLOSINGBALANCE</FETCH>
              </REPORT>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    test_xml_structure(xml2, "Test 2: Report Type")

def test_company_specific_data():
    """Test getting data for a specific company."""
    print("\n" + "="*60)
    print("TESTING COMPANY-SPECIFIC DATA")
    print("="*60)
    
    # First get companies to find a company name
    xml_companies = """
    <ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>Companies</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES />
          <TDL>
            <TDLMESSAGE>
              <COLLECTION NAME="Companies">
                <TYPE>Company</TYPE>
                <FETCH>NAME</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    
    success, response = test_xml_structure(xml_companies, "Get Companies First")
    
    if success and response:
        try:
            root = ET.fromstring(response)
            company_name = None
            for collection in root.iter("COLLECTION"):
                for comp in collection:
                    if comp.tag == "COMPANY":
                        name_elem = comp.find("NAME")
                        if name_elem is not None and name_elem.text:
                            company_name = name_elem.text
                            break
                if company_name:
                    break
            
            if company_name:
                print(f"\nFound company: {company_name}")
                
                # Test getting ledgers for specific company
                xml_company_ledgers = f"""
                <ENVELOPE>
                  <HEADER>
                    <VERSION>1</VERSION>
                    <TALLYREQUEST>Export</TALLYREQUEST>
                    <TYPE>Collection</TYPE>
                    <ID>Company Ledgers</ID>
                  </HEADER>
                  <BODY>
                    <DESC>
                      <STATICVARIABLES>
                        <SVCURRENTCOMPANY>{company_name}</SVCURRENTCOMPANY>
                      </STATICVARIABLES>
                      <TDL>
                        <TDLMESSAGE>
                          <COLLECTION NAME="Ledgers">
                            <TYPE>Ledger</TYPE>
                            <FETCH>NAME,GUID,PARENT,OPENINGBALANCE,CLOSINGBALANCE</FETCH>
                          </COLLECTION>
                        </TDLMESSAGE>
                      </TDL>
                    </DESC>
                  </BODY>
                </ENVELOPE>
                """
                test_xml_structure(xml_company_ledgers, f"Company-specific Ledgers for {company_name}")
                
        except Exception as e:
            print(f"Error parsing company response: {e}")

def main():
    """Run all tests."""
    print("Tally Prime XML Structure Research")
    print("="*60)
    
    # Test divisions
    test_divisions_structures()
    
    # Test ledgers
    test_ledgers_structures()
    
    # Test vouchers
    test_vouchers_structures()
    
    # Test alternative approaches
    test_alternative_approaches()
    
    # Test company-specific data
    test_company_specific_data()
    
    print("\n" + "="*60)
    print("RESEARCH COMPLETE")
    print("="*60)
    print("Check the output above to see which XML structures work for each data type.")

if __name__ == "__main__":
    main() 