#!/usr/bin/env python3
"""
Simple test script to get company name and test other endpoints
"""

import requests
import json

def test_simple_api():
    """Test the simple API endpoints"""
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing Simple Tally API")
    print("=" * 50)
    
    # Step 1: Get companies (this works!)
    print("\n1. Getting companies...")
    try:
        response = requests.get(f"{base_url}/companies")
        if response.status_code == 200:
            companies = response.json()
            print(f"✅ Found {len(companies)} companies")
            
            if companies:
                company = companies[0]
                company_name = company['Name']
                print(f"   Company Name: {company_name}")
                print(f"   GUID: {company.get('GUID', 'N/A')}")
                print(f"   Email: {company.get('Email', 'N/A')}")
                
                # Step 2: Test divisions with company context
                print(f"\n2. Testing divisions for company: {company_name}")
                try:
                    response = requests.get(f"{base_url}/divisions/{company_name}")
                    if response.status_code == 200:
                        divisions = response.json()
                        print(f"✅ Found {len(divisions)} divisions")
                        for div in divisions[:3]:  # Show first 3
                            print(f"   - {div['Name']} (Parent: {div.get('Parent', 'N/A')})")
                    else:
                        print(f"❌ Divisions failed: {response.status_code}")
                        print(f"   Response: {response.text}")
                except Exception as e:
                    print(f"❌ Error getting divisions: {e}")
                
                # Step 3: Test ledgers with company context
                print(f"\n3. Testing ledgers for company: {company_name}")
                try:
                    response = requests.get(f"{base_url}/ledgers/{company_name}")
                    if response.status_code == 200:
                        ledgers = response.json()
                        print(f"✅ Found {len(ledgers)} ledgers")
                        for ledger in ledgers[:3]:  # Show first 3
                            print(f"   - {ledger['Name']} (Group: {ledger.get('Parent', 'N/A')})")
                    else:
                        print(f"❌ Ledgers failed: {response.status_code}")
                        print(f"   Response: {response.text}")
                except Exception as e:
                    print(f"❌ Error getting ledgers: {e}")
                
                # Step 4: Test groups with company context
                print(f"\n4. Testing groups for company: {company_name}")
                try:
                    response = requests.get(f"{base_url}/groups/{company_name}")
                    if response.status_code == 200:
                        groups = response.json()
                        print(f"✅ Found {len(groups)} groups")
                        for group in groups[:3]:  # Show first 3
                            print(f"   - {group['Name']} (Parent: {group.get('Parent', 'N/A')})")
                    else:
                        print(f"❌ Groups failed: {response.status_code}")
                        print(f"   Response: {response.text}")
                except Exception as e:
                    print(f"❌ Error getting groups: {e}")
                
                # Step 5: Test vouchers with company context
                print(f"\n5. Testing vouchers for company: {company_name}")
                try:
                    response = requests.get(f"{base_url}/vouchers/{company_name}")
                    if response.status_code == 200:
                        vouchers = response.json()
                        print(f"✅ Found {len(vouchers)} vouchers")
                        for voucher in vouchers[:3]:  # Show first 3
                            print(f"   - Voucher #{voucher.get('VoucherNumber', 'N/A')} ({voucher.get('VoucherTypeName', 'N/A')}) - {voucher.get('Amount', 'N/A')}")
                    else:
                        print(f"❌ Vouchers failed: {response.status_code}")
                        print(f"   Response: {response.text}")
                except Exception as e:
                    print(f"❌ Error getting vouchers: {e}")
                
                # Step 6: Test voucher entries with company context
                print(f"\n6. Testing voucher entries for company: {company_name}")
                try:
                    response = requests.get(f"{base_url}/voucher-entries/{company_name}")
                    if response.status_code == 200:
                        voucher_entries = response.json()
                        print(f"✅ Voucher entries endpoint working")
                        print(f"   Message: {voucher_entries.get('message', 'N/A')}")
                        print(f"   Note: {voucher_entries.get('note', 'N/A')}")
                    else:
                        print(f"❌ Voucher entries failed: {response.status_code}")
                        print(f"   Response: {response.text}")
                except Exception as e:
                    print(f"❌ Error getting voucher entries: {e}")
                
            else:
                print("❌ No companies found")
        else:
            print(f"❌ Companies failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error getting companies: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")

if __name__ == "__main__":
    test_simple_api() 