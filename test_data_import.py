#!/usr/bin/env python3
"""
Test script to check Tally data extraction and Supabase import
"""

import logging
from tally_http_client import TallyHTTPClient
from supabase_manager import SupabaseManager
from tally_supabase_sync import TallySupabaseSync

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("=== Testing Tally Data Extraction and Supabase Import ===\n")
    
    # 1. Test Tally connection
    print("1. Testing Tally connection...")
    tally_client = TallyHTTPClient("localhost", 9000)
    
    if not tally_client.test_connection():
        print("❌ Failed to connect to Tally")
        return
    
    print("✅ Connected to Tally successfully")
    
    # 2. Test Supabase connection
    print("\n2. Testing Supabase connection...")
    project_url = "https://ppfwlhfehwelinfprviw.supabase.co"
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBwZndsaGZlaHdlbGluZnBydml3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDMxNzYxOCwiZXhwIjoyMDY5ODkzNjE4fQ._qiN-8ZAqg2Lz9TD2hENgCoKjEiFDFCafkymiDPRH7A"
    
    supabase_manager = SupabaseManager(project_url, api_key)
    
    if not supabase_manager.test_connection():
        print("❌ Failed to connect to Supabase")
        return
    
    print("✅ Connected to Supabase successfully")
    
    # 3. Check existing tables
    print("\n3. Checking existing tables...")
    tables = supabase_manager.get_existing_tables()
    print(f"Found tables: {tables}")
    
    # 4. Extract Tally data
    print("\n4. Extracting Tally data...")
    try:
        # Get companies first
        companies = tally_client.get_companies()
        print(f"Found {len(companies)} companies")
        
        if not companies:
            print("❌ No companies found in Tally")
            return
        
        # Use the first company - fix the key name
        company_name = companies[0].get('Name', '')  # Changed from 'name' to 'Name'
        print(f"Using company: {company_name}")
        
        if not company_name:
            print("❌ Company name is empty")
            print(f"Company data: {companies[0]}")
            return
        
        # Get divisions
        divisions = tally_client.get_divisions(company_name)
        print(f"Found {len(divisions)} divisions")
        
        # Get groups
        groups = tally_client.get_groups(company_name)
        print(f"Found {len(groups)} groups")
        
        # Get ledgers
        ledgers = tally_client.get_ledgers(company_name)
        print(f"Found {len(ledgers)} ledgers")
        
        # Get vouchers (without limit parameter)
        vouchers = tally_client.get_vouchers(company_name)
        print(f"Found {len(vouchers)} vouchers")
        
        # Prepare data for import
        tally_data = {
            'tally_companies': companies,
            'tally_divisions': divisions,
            'tally_groups': groups,
            'tally_ledgers': ledgers,
            'tally_vouchers': vouchers
        }
        
        print(f"\nData summary:")
        for table_name, data in tally_data.items():
            print(f"  {table_name}: {len(data)} records")
        
        # 5. Import to Supabase
        print("\n5. Importing data to Supabase...")
        success = supabase_manager.sync_tally_data(tally_data)
        
        if success:
            print("✅ Data imported successfully!")
        else:
            print("❌ Failed to import data")
            
    except Exception as e:
        print(f"❌ Error during data extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 