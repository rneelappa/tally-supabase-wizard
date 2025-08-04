#!/usr/bin/env python3
"""
Simple test to check if there are any vouchers in Tally
"""

import requests

def test_vouchers_simple():
    """Test vouchers with a very simple approach"""
    tally_url = "http://localhost:9000"
    company_name = "SKM IMPEX-CHENNAI-(24-25)"
    
    print("🧪 Testing Vouchers - Simple Approach")
    print("=" * 50)
    
    # Try a very simple voucher request
    xml_request = f"""
    <ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>Vouchers</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES>
            <SVCOMPANYCONNECT>{company_name}</SVCOMPANYCONNECT>
          </STATICVARIABLES>
          <TDL>
            <TDLMESSAGE>
              <COLLECTION NAME="Vouchers">
                <TYPE>Voucher</TYPE>
                <FETCH>VOUCHERNUMBER,DATE,VOUCHERTYPENAME</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    
    headers = {'Content-Type': 'application/xml'}
    
    try:
        response = requests.post(tally_url, data=xml_request.encode(), headers=headers)
        print(f"Response Status: {response.status_code}")
        print(f"Response Length: {len(response.text)}")
        print(f"Response (first 1000 chars): {response.text[:1000]}")
        
        # Check if response contains voucher data
        if "VOUCHER" in response.text:
            print("✅ Found VOUCHER in response")
        else:
            print("❌ No VOUCHER found in response")
            
        if "CMPINFO" in response.text:
            print("✅ Found CMPINFO in response (company info)")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_vouchers_simple() 