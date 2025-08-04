#!/usr/bin/env python3
"""
Test script to check the FastAPI endpoints that are currently running.
"""

import requests
import json

def test_api_endpoints():
    """Test the FastAPI endpoints."""
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing FastAPI Endpoints")
    print("=" * 60)
    
    # Test 1: Root endpoint
    print("\n1. Testing Root Endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Root endpoint working")
            print(f"   Message: {data.get('message', 'N/A')}")
            print(f"   Available endpoints: {len(data.get('endpoints', {}))}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 2: Companies endpoint
    print("\n2. Testing Companies Endpoint...")
    try:
        response = requests.get(f"{base_url}/companies")
        if response.status_code == 200:
            companies = response.json()
            print(f"✅ Companies endpoint working - Found {len(companies)} companies")
            if companies:
                for i, company in enumerate(companies[:3]):
                    name = company.get('NAME', 'Unknown')
                    print(f"   {i+1}. {name}")
                if len(companies) > 3:
                    print(f"   ... and {len(companies) - 3} more")
            else:
                print("   No companies found (Tally may not be running)")
        else:
            print(f"❌ Companies endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Companies endpoint error: {e}")
    
    # Test 3: Test with a sample company name
    print("\n3. Testing Company-Specific Endpoints...")
    
    # First get companies to find a company name
    try:
        response = requests.get(f"{base_url}/companies")
        if response.status_code == 200:
            companies = response.json()
            if companies:
                company_name = companies[0].get('NAME', 'Test Company')
                print(f"   Using company: {company_name}")
                
                # Test divisions endpoint
                print(f"\n   Testing Divisions for '{company_name}'...")
                try:
                    response = requests.get(f"{base_url}/divisions/{company_name}")
                    if response.status_code == 200:
                        divisions = response.json()
                        print(f"   ✅ Divisions endpoint working - Found {len(divisions)} divisions")
                        if divisions:
                            for i, division in enumerate(divisions[:2]):
                                name = division.get('NAME', 'Unknown')
                                category = division.get('CATEGORY', 'N/A')
                                print(f"     {i+1}. {name} ({category})")
                    else:
                        print(f"   ❌ Divisions endpoint failed: {response.status_code}")
                        print(f"     Response: {response.text}")
                except Exception as e:
                    print(f"   ❌ Divisions endpoint error: {e}")
                
                # Test ledgers endpoint
                print(f"\n   Testing Ledgers for '{company_name}'...")
                try:
                    response = requests.get(f"{base_url}/ledgers/{company_name}")
                    if response.status_code == 200:
                        ledgers = response.json()
                        print(f"   ✅ Ledgers endpoint working - Found {len(ledgers)} ledgers")
                        if ledgers:
                            for i, ledger in enumerate(ledgers[:2]):
                                name = ledger.get('NAME', 'Unknown')
                                parent = ledger.get('PARENT', 'N/A')
                                print(f"     {i+1}. {name} (Group: {parent})")
                    else:
                        print(f"   ❌ Ledgers endpoint failed: {response.status_code}")
                        print(f"     Response: {response.text}")
                except Exception as e:
                    print(f"   ❌ Ledgers endpoint error: {e}")
                
                # Test groups endpoint
                print(f"\n   Testing Groups for '{company_name}'...")
                try:
                    response = requests.get(f"{base_url}/groups/{company_name}")
                    if response.status_code == 200:
                        groups = response.json()
                        print(f"   ✅ Groups endpoint working - Found {len(groups)} groups")
                        if groups:
                            for i, group in enumerate(groups[:2]):
                                name = group.get('NAME', 'Unknown')
                                parent = group.get('PARENT', 'N/A')
                                print(f"     {i+1}. {name} (Parent: {parent})")
                    else:
                        print(f"   ❌ Groups endpoint failed: {response.status_code}")
                        print(f"     Response: {response.text}")
                except Exception as e:
                    print(f"   ❌ Groups endpoint error: {e}")
                
            else:
                print("   No companies found - cannot test company-specific endpoints")
        else:
            print("   Companies endpoint failed - cannot test company-specific endpoints")
    except Exception as e:
        print(f"   Error getting companies: {e}")
    
    print("\n" + "=" * 60)
    print("📋 API Documentation:")
    print(f"   Swagger UI: {base_url}/docs")
    print(f"   ReDoc: {base_url}/redoc")
    print("\n📋 Next Steps:")
    print("1. Start Tally Prime with XML access enabled")
    print("2. Create or open a company in Tally")
    print("3. Run the integration test: py -3.11 test_corrected_integration.py")
    print("4. Or test the main wizard: py -3.11 tally_supabase_wizard.py")

def main():
    """Main test function."""
    try:
        test_api_endpoints()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")

if __name__ == "__main__":
    main() 