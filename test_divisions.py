#!/usr/bin/env python3
"""
Test script to specifically test divisions endpoint.
"""

import requests
import xml.etree.ElementTree as ET

def test_divisions():
    """Test different approaches for getting divisions."""
    
    # Test 1: Original approach (CostCentre)
    print("=== Test 1: CostCentre Approach ===")
    xml_request1 = """
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
                <FETCH>*</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    
    try:
        response1 = requests.post("http://localhost:9000", data=xml_request1.encode(), headers={'Content-Type': 'application/xml'})
        print(f"Status: {response1.status_code}")
        print(f"Response length: {len(response1.text)}")
        print(f"Response preview: {response1.text[:200]}...")
        
        # Try to parse
        root1 = ET.fromstring(response1.text)
        cost_centres = []
        for collection in root1.iter("COLLECTION"):
            for item in collection.findall("COSTCENTRE"):
                entry = {}
                for child in item:
                    entry[child.tag] = child.text
                cost_centres.append(entry)
        
        print(f"Found {len(cost_centres)} cost centres")
        if cost_centres:
            print(f"Sample: {cost_centres[0]}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n=== Test 2: Division Approach ===")
    xml_request2 = """
    <ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>List of Divisions</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES />
          <TDL>
            <TDLMESSAGE>
              <COLLECTION NAME="List of Divisions">
                <TYPE>Division</TYPE>
                <FETCH>NAME,GUID,PARENT</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    
    try:
        response2 = requests.post("http://localhost:9000", data=xml_request2.encode(), headers={'Content-Type': 'application/xml'})
        print(f"Status: {response2.status_code}")
        print(f"Response length: {len(response2.text)}")
        print(f"Response preview: {response2.text[:200]}...")
        
        # Try to parse
        root2 = ET.fromstring(response2.text)
        divisions = []
        for collection in root2.iter("COLLECTION"):
            for item in collection.findall("DIVISION"):
                entry = {}
                for child in item:
                    entry[child.tag] = child.text
                divisions.append(entry)
        
        print(f"Found {len(divisions)} divisions")
        if divisions:
            print(f"Sample: {divisions[0]}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n=== Test 3: Group Approach ===")
    xml_request3 = """
    <ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>List of Groups</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES />
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
        response3 = requests.post("http://localhost:9000", data=xml_request3.encode(), headers={'Content-Type': 'application/xml'})
        print(f"Status: {response3.status_code}")
        print(f"Response length: {len(response3.text)}")
        print(f"Response preview: {response3.text[:200]}...")
        
        # Try to parse
        root3 = ET.fromstring(response3.text)
        groups = []
        for collection in root3.iter("COLLECTION"):
            for item in collection.findall("GROUP"):
                entry = {}
                for child in item:
                    entry[child.tag] = child.text
                groups.append(entry)
        
        print(f"Found {len(groups)} groups")
        if groups:
            print(f"Sample: {groups[0]}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_divisions() 