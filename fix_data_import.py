#!/usr/bin/env python3
"""
Fix data import by mapping Tally data to existing Supabase table schema
"""

import logging
from tally_http_client import TallyHTTPClient
from supabase_manager import SupabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def map_tally_to_supabase_schema(tally_data, table_name):
    """Map Tally data to Supabase table schema"""
    mapped_data = []
    
    for record in tally_data:
        mapped_record = {
            'user_id': 'faa3bf60-717e-4dd8-8159-e9dc1fe9b8d0'  # Your user ID
        }
        
        if table_name == 'tally_companies':
            mapped_record.update({
                'company_name': record.get('Name', ''),
                'company_path': record.get('GUID', ''),
                'company_email': record.get('Email', ''),
                'company_phone': record.get('Phone', ''),
                'company_address': record.get('State', ''),
                'company_tax_number': record.get('CompanyNumber', '')
            })
        elif table_name == 'tally_divisions':
            mapped_record.update({
                'company_name': record.get('CompanyName', ''),
                'division_name': record.get('Name', ''),
                'division_path': record.get('GUID', ''),
                'division_type': record.get('Category', '')
            })
        elif table_name == 'tally_groups':
            mapped_record.update({
                'company_name': record.get('CompanyName', ''),
                'group_name': record.get('Name', ''),
                'group_path': record.get('GUID', ''),
                'group_parent': record.get('Parent', '')
            })
        elif table_name == 'tally_ledgers':
            mapped_record.update({
                'company_name': record.get('CompanyName', ''),
                'ledger_name': record.get('Name', ''),
                'ledger_path': record.get('GUID', ''),
                'ledger_parent': record.get('Parent', ''),
                'ledger_opening_balance': float(record.get('OpeningBalance', 0) or 0),
                'ledger_closing_balance': float(record.get('ClosingBalance', 0) or 0)
            })
        elif table_name == 'tally_vouchers':
            mapped_record.update({
                'company_name': record.get('CompanyName', ''),
                'voucher_number': record.get('VoucherNumber', ''),
                'voucher_date': record.get('Date', ''),
                'voucher_type': record.get('VoucherTypeName', ''),
                'voucher_narration': record.get('Narration', ''),
                'voucher_reference': record.get('Reference', ''),
                'voucher_amount': float(record.get('Amount', 0) or 0)
            })
        elif table_name == 'tally_voucher_entries':
            mapped_record.update({
                'company_name': record.get('CompanyName', ''),
                'voucher_number': record.get('VoucherNumber', ''),
                'voucher_date': record.get('VoucherDate', ''),
                'voucher_type': record.get('VoucherType', ''),
                'ledger_name': record.get('LedgerName', ''),
                'amount': float(record.get('Amount', 0) or 0),
                'narration': record.get('Narration', ''),
                'party_ledger_name': record.get('PartyLedgerName', '')
            })
        
        mapped_data.append(mapped_record)
    
    return mapped_data

def main():
    print("=== Fixing Data Import with Correct Schema Mapping ===\n")
    
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
    
    # 3. Extract Tally data
    print("\n3. Extracting Tally data...")
    try:
        # Get companies first
        companies = tally_client.get_companies()
        print(f"Found {len(companies)} companies")
        
        if not companies:
            print("❌ No companies found in Tally")
            return
        
        # Use the first company
        company_name = companies[0].get('Name', '')
        print(f"Using company: {company_name}")
        
        if not company_name:
            print("❌ Company name is empty")
            return
        
        # Add company name to all records for context
        for company in companies:
            company['CompanyName'] = company_name
        
        # Get divisions
        divisions = tally_client.get_divisions(company_name)
        print(f"Found {len(divisions)} divisions")
        for division in divisions:
            division['CompanyName'] = company_name
        
        # Get groups
        groups = tally_client.get_groups(company_name)
        print(f"Found {len(groups)} groups")
        for group in groups:
            group['CompanyName'] = company_name
        
        # Get ledgers
        ledgers = tally_client.get_ledgers(company_name)
        print(f"Found {len(ledgers)} ledgers")
        for ledger in ledgers:
            ledger['CompanyName'] = company_name
        
        # Get vouchers
        vouchers = tally_client.get_vouchers(company_name)
        print(f"Found {len(vouchers)} vouchers")
        for voucher in vouchers:
            voucher['CompanyName'] = company_name
        
        # Get voucher entries
        voucher_entries = tally_client.get_voucher_entries(company_name)
        print(f"Found {len(voucher_entries)} voucher entries")
        for entry in voucher_entries:
            entry['CompanyName'] = company_name
        
        # 4. Map data to Supabase schema
        print("\n4. Mapping data to Supabase schema...")
        
        mapped_companies = map_tally_to_supabase_schema(companies, 'tally_companies')
        mapped_divisions = map_tally_to_supabase_schema(divisions, 'tally_divisions')
        mapped_groups = map_tally_to_supabase_schema(groups, 'tally_groups')
        mapped_ledgers = map_tally_to_supabase_schema(ledgers, 'tally_ledgers')
        mapped_vouchers = map_tally_to_supabase_schema(vouchers, 'tally_vouchers')
        mapped_voucher_entries = map_tally_to_supabase_schema(voucher_entries, 'tally_voucher_entries')
        
        print(f"Mapped data summary:")
        print(f"  Companies: {len(mapped_companies)} records")
        print(f"  Divisions: {len(mapped_divisions)} records")
        print(f"  Groups: {len(mapped_groups)} records")
        print(f"  Ledgers: {len(mapped_ledgers)} records")
        print(f"  Vouchers: {len(mapped_vouchers)} records")
        print(f"  Voucher Entries: {len(mapped_voucher_entries)} records")
        
        # 5. Import to Supabase
        print("\n5. Importing data to Supabase...")
        
        # Import companies
        if mapped_companies:
            print("Importing companies...")
            if supabase_manager.insert_data('tally_companies', mapped_companies):
                print("✅ Companies imported successfully")
            else:
                print("❌ Failed to import companies")
        
        # Import divisions
        if mapped_divisions:
            print("Importing divisions...")
            if supabase_manager.insert_data('tally_divisions', mapped_divisions):
                print("✅ Divisions imported successfully")
            else:
                print("❌ Failed to import divisions")
        
        # Import groups
        if mapped_groups:
            print("Importing groups...")
            if supabase_manager.insert_data('tally_groups', mapped_groups):
                print("✅ Groups imported successfully")
            else:
                print("❌ Failed to import groups")
        
        # Import ledgers
        if mapped_ledgers:
            print("Importing ledgers...")
            if supabase_manager.insert_data('tally_ledgers', mapped_ledgers):
                print("✅ Ledgers imported successfully")
            else:
                print("❌ Failed to import ledgers")
        
        # Import vouchers
        if mapped_vouchers:
            print("Importing vouchers...")
            if supabase_manager.insert_data('tally_vouchers', mapped_vouchers):
                print("✅ Vouchers imported successfully")
            else:
                print("❌ Failed to import vouchers")
        
        # Import voucher entries
        if mapped_voucher_entries:
            print("Importing voucher entries...")
            if supabase_manager.insert_data('tally_voucher_entries', mapped_voucher_entries):
                print("✅ Voucher entries imported successfully")
            else:
                print("❌ Failed to import voucher entries")
        
        print("\n✅ Data import completed!")
            
    except Exception as e:
        print(f"❌ Error during data extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 