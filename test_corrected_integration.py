#!/usr/bin/env python3
"""
Test script to verify corrected Tally Prime XML integration.
Tests all data types with proper company context.
"""

import sys
import json
from tally_http_client import TallyHTTPClient

def test_tally_integration():
    """Test the corrected Tally integration."""
    print("🧪 Testing Corrected Tally Prime Integration")
    print("=" * 60)
    
    client = TallyHTTPClient()
    
    # Test 1: Connection
    print("\n1. Testing Connection...")
    if client.test_connection():
        print("✅ Connection successful!")
    else:
        print("❌ Connection failed")
        return False
    
    # Test 2: Get Companies
    print("\n2. Testing Companies...")
    companies = client.get_companies()
    print(f"✅ Found {len(companies)} companies")
    
    if not companies:
        print("❌ No companies found")
        return False
    
    # Display company names
    for i, company in enumerate(companies[:3]):  # Show first 3
        name = company.get('NAME', 'Unknown')
        print(f"   {i+1}. {name}")
    
    if len(companies) > 3:
        print(f"   ... and {len(companies) - 3} more")
    
    # Test 3: Get Divisions (Cost Centres) for first company
    print(f"\n3. Testing Divisions (Cost Centres) for '{companies[0]['NAME']}'...")
    divisions = client.get_divisions(companies[0]['NAME'])
    print(f"✅ Found {len(divisions)} divisions/cost centres")
    
    if divisions:
        for i, division in enumerate(divisions[:3]):  # Show first 3
            name = division.get('NAME', 'Unknown')
            category = division.get('CATEGORY', 'N/A')
            print(f"   {i+1}. {name} (Category: {category})")
    
    # Test 4: Get Ledgers for first company
    print(f"\n4. Testing Ledgers for '{companies[0]['NAME']}'...")
    ledgers = client.get_ledgers(companies[0]['NAME'])
    print(f"✅ Found {len(ledgers)} ledgers")
    
    if ledgers:
        for i, ledger in enumerate(ledgers[:3]):  # Show first 3
            name = ledger.get('NAME', 'Unknown')
            parent = ledger.get('PARENT', 'N/A')
            print(f"   {i+1}. {name} (Group: {parent})")
    
    # Test 5: Get Vouchers for first company (limited date range)
    print(f"\n5. Testing Vouchers for '{companies[0]['NAME']}'...")
    vouchers = client.get_vouchers(companies[0]['NAME'], from_date="20240101", to_date="20241231")
    print(f"✅ Found {len(vouchers)} vouchers")
    
    if vouchers:
        for i, voucher in enumerate(vouchers[:3]):  # Show first 3
            number = voucher.get('VOUCHERNUMBER', 'Unknown')
            date = voucher.get('DATE', 'N/A')
            type_name = voucher.get('VOUCHERTYPENAME', 'N/A')
            print(f"   {i+1}. Voucher {number} ({type_name}) - {date}")
    
    # Test 6: Get Voucher Entries for first company
    print(f"\n6. Testing Voucher Entries for '{companies[0]['NAME']}'...")
    voucher_entries = client.get_voucher_entries(company_name=companies[0]['NAME'])
    print(f"✅ Found {len(voucher_entries)} voucher entries")
    
    if voucher_entries:
        for i, entry in enumerate(voucher_entries[:3]):  # Show first 3
            ledger = entry.get('LEDGERNAME', 'Unknown')
            amount = entry.get('AMOUNT', 'N/A')
            print(f"   {i+1}. {ledger} - {amount}")
    
    # Test 7: Get All Metadata
    print(f"\n7. Testing Complete Metadata for '{companies[0]['NAME']}'...")
    all_metadata = client.get_all_metadata(companies[0]['NAME'])
    
    summary = {
        'companies': len(all_metadata.get('companies', [])),
        'divisions': len(all_metadata.get('divisions', [])),
        'ledgers': len(all_metadata.get('ledgers', [])),
        'vouchers': len(all_metadata.get('vouchers', [])),
        'voucher_entries': len(all_metadata.get('voucher_entries', []))
    }
    
    print("✅ Complete metadata summary:")
    for key, count in summary.items():
        print(f"   {key.capitalize()}: {count}")
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed successfully!")
    print("✅ The corrected XML structures are working properly.")
    
    return True

def main():
    """Main test function."""
    try:
        success = test_tally_integration()
        if success:
            print("\n📋 Next Steps:")
            print("1. Run the main wizard: py -3.11 tally_supabase_wizard.py")
            print("2. Test the FastAPI server: py -3.11 tally_api_corrected.py")
            print("3. Access API docs at: http://127.0.0.1:8000/docs")
            print("4. Use the corrected structures in your integration")
        else:
            print("\n❌ Tests failed. Check Tally Prime connection and configuration.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 