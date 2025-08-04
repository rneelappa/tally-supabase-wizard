#!/usr/bin/env python3
"""
Test vouchers endpoint only to debug XML issues
"""

import requests
import json

def test_vouchers_only():
    """Test just the vouchers endpoint"""
    base_url = "http://127.0.0.1:8000"
    company_name = "SKM IMPEX-CHENNAI-(24-25)"
    
    print("🧪 Testing Vouchers Endpoint Only")
    print("=" * 50)
    
    print(f"Testing vouchers for company: {company_name}")
    try:
        response = requests.get(f"{base_url}/vouchers/{company_name}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            vouchers = response.json()
            print(f"✅ Found {len(vouchers)} vouchers")
            for voucher in vouchers[:3]:  # Show first 3
                print(f"   - Voucher #{voucher.get('VoucherNumber', 'N/A')} ({voucher.get('VoucherTypeName', 'N/A')}) - {voucher.get('Amount', 'N/A')}")
        else:
            print(f"❌ Vouchers failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
            # Try to get the raw response from Tally directly
            print("\n🔍 Trying direct Tally request...")
            tally_url = "http://localhost:9000"
            xml_request = f"""
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
                    <SVCOMPANYCONNECT>{company_name}</SVCOMPANYCONNECT>
                  </STATICVARIABLES>
                  <TDL>
                    <TDLMESSAGE>
                      <COLLECTION NAME="List of Vouchers">
                        <TYPE>Voucher</TYPE>
                        <FETCH>VOUCHERNUMBER,DATE,VOUCHERTYPENAME,NARRATION,REFERENCE,AMOUNT</FETCH>
                      </COLLECTION>
                    </TDLMESSAGE>
                  </TDL>
                </DESC>
              </BODY>
            </ENVELOPE>
            """
            
            headers = {'Content-Type': 'application/xml'}
            try:
                tally_response = requests.post(tally_url, data=xml_request.encode(), headers=headers)
                print(f"Tally Response Status: {tally_response.status_code}")
                print(f"Tally Response Length: {len(tally_response.text)}")
                print(f"Tally Response (first 500 chars): {tally_response.text[:500]}")
            except Exception as e:
                print(f"Direct Tally request failed: {e}")
                
    except Exception as e:
        print(f"❌ Error getting vouchers: {e}")

if __name__ == "__main__":
    test_vouchers_only() 