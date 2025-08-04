#!/usr/bin/env python3
"""
Verify data import to Supabase tables
"""

import requests
import json

def main():
    print("=== Verifying Data Import to Supabase ===\n")
    
    project_url = "https://ppfwlhfehwelinfprviw.supabase.co"
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBwZndsaGZlaHdlbGluZnBydml3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDMxNzYxOCwiZXhwIjoyMDY5ODkzNjE4fQ._qiN-8ZAqg2Lz9TD2hENgCoKjEiFDFCafkymiDPRH7A"
    
    headers = {
        'apikey': api_key,
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    tables = ['tally_companies', 'tally_groups', 'tally_ledgers', 'tally_divisions', 'tally_vouchers']
    
    for table_name in tables:
        try:
            print(f"Checking {table_name}...")
            
            # Get count
            count_response = requests.get(
                f"{project_url}/rest/v1/{table_name}",
                headers=headers,
                params={'select': 'count'}
            )
            
            if count_response.status_code == 200:
                count_data = count_response.json()
                count = count_data[0]['count'] if count_data else 0
                print(f"  ✅ {table_name}: {count} records")
                
                # Show first few records
                if count > 0:
                    data_response = requests.get(
                        f"{project_url}/rest/v1/{table_name}",
                        headers=headers,
                        params={'select': '*', 'limit': 3}
                    )
                    
                    if data_response.status_code == 200:
                        sample_data = data_response.json()
                        print(f"  Sample data:")
                        for i, record in enumerate(sample_data[:2]):  # Show first 2 records
                            if table_name == 'tally_companies':
                                print(f"    {i+1}. Company: {record.get('company_name', 'N/A')}")
                            elif table_name == 'tally_groups':
                                print(f"    {i+1}. Group: {record.get('group_name', 'N/A')}")
                            elif table_name == 'tally_ledgers':
                                print(f"    {i+1}. Ledger: {record.get('ledger_name', 'N/A')} (Balance: {record.get('ledger_closing_balance', 'N/A')})")
                            elif table_name == 'tally_divisions':
                                print(f"    {i+1}. Division: {record.get('division_name', 'N/A')}")
                            elif table_name == 'tally_vouchers':
                                print(f"    {i+1}. Voucher: {record.get('voucher_number', 'N/A')} - {record.get('voucher_amount', 'N/A')}")
            else:
                print(f"  ❌ {table_name}: Error getting count - {count_response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {table_name}: Error - {e}")
        
        print()
    
    print("=== Verification Complete ===")

if __name__ == "__main__":
    main() 