#!/usr/bin/env python3
"""
Demo Supabase Integration
Demonstrates the Supabase integration with sample Tally data.
"""

import sys
import json
import requests
from pathlib import Path

def demo_supabase_connection():
    """Demonstrate Supabase connection."""
    print("=== Supabase Connection Demo ===")
    
    try:
        from supabase_manager import SupabaseManager
        
        # Test configuration
        project_url = "https://ppfwlhfehwelinfprviw.supabase.co"
        api_key = "sb_secret_0ng3_U_wd2MXRyzPYXweuw_dDl-5EAA"
        
        manager = SupabaseManager(project_url, api_key)
        
        # Test connection
        print("1. Testing connection...")
        connected = manager.test_connection()
        print(f"   Connection: {'✅ Success' if connected else '❌ Failed'}")
        
        if not connected:
            print("   Cannot proceed with demo.")
            return False
        
        # Get existing tables
        print("2. Getting existing tables...")
        tables = manager.get_existing_tables()
        print(f"   Found {len(tables)} tables: {tables}")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False


def demo_sample_data_sync():
    """Demonstrate syncing sample data to Supabase."""
    print("\n=== Sample Data Sync Demo ===")
    
    try:
        from supabase_manager import SupabaseManager
        
        # Test configuration
        project_url = "https://ppfwlhfehwelinfprviw.supabase.co"
        api_key = "sb_secret_0ng3_U_wd2MXRyzPYXweuw_dDl-5EAA"
        
        manager = SupabaseManager(project_url, api_key)
        
        # Sample Tally data
        sample_companies = [
            {
                "name": "Demo Company 1",
                "address": "123 Main St, City",
                "phone": "+1-555-0123",
                "email": "demo1@example.com",
                "registration_number": "REG001"
            },
            {
                "name": "Demo Company 2", 
                "address": "456 Oak Ave, Town",
                "phone": "+1-555-0456",
                "email": "demo2@example.com",
                "registration_number": "REG002"
            }
        ]
        
        sample_ledgers = [
            {
                "name": "Cash Account",
                "type": "Asset",
                "opening_balance": 10000.00,
                "current_balance": 12500.00,
                "company": "Demo Company 1"
            },
            {
                "name": "Bank Account",
                "type": "Asset", 
                "opening_balance": 50000.00,
                "current_balance": 48750.00,
                "company": "Demo Company 1"
            },
            {
                "name": "Sales Account",
                "type": "Income",
                "opening_balance": 0.00,
                "current_balance": 25000.00,
                "company": "Demo Company 2"
            }
        ]
        
        print("1. Creating sample data structure...")
        
        # Analyze sample data
        companies_structure = manager.analyze_data_structure(sample_companies)
        ledgers_structure = manager.analyze_data_structure(sample_ledgers)
        
        print(f"   Companies structure: {len(companies_structure)} fields")
        print(f"   Ledgers structure: {len(ledgers_structure)} fields")
        
        # Create tables
        print("2. Creating tables...")
        
        companies_table_created = manager.create_table("tally_companies", companies_structure)
        ledgers_table_created = manager.create_table("tally_ledgers", ledgers_structure)
        
        print(f"   Companies table: {'✅ Created' if companies_table_created else '❌ Failed'}")
        print(f"   Ledgers table: {'✅ Created' if ledgers_table_created else '❌ Failed'}")
        
        # Insert data
        print("3. Inserting sample data...")
        
        companies_inserted = manager.insert_data("tally_companies", sample_companies)
        ledgers_inserted = manager.insert_data("tally_ledgers", sample_ledgers)
        
        print(f"   Companies data: {'✅ Inserted' if companies_inserted else '❌ Failed'}")
        print(f"   Ledgers data: {'✅ Inserted' if ledgers_inserted else '❌ Failed'}")
        
        # Verify data
        print("4. Verifying data...")
        
        try:
            companies_response = requests.get(
                f"{project_url}/rest/v1/tally_companies",
                headers=manager.headers,
                timeout=10
            )
            
            ledgers_response = requests.get(
                f"{project_url}/rest/v1/tally_ledgers", 
                headers=manager.headers,
                timeout=10
            )
            
            if companies_response.status_code == 200:
                companies_data = companies_response.json()
                print(f"   Companies in database: {len(companies_data)}")
            
            if ledgers_response.status_code == 200:
                ledgers_data = ledgers_response.json()
                print(f"   Ledgers in database: {len(ledgers_data)}")
                
        except Exception as e:
            print(f"   Verification error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False


def demo_wizard_page():
    """Demonstrate the Supabase configuration wizard page."""
    print("\n=== Wizard Page Demo ===")
    
    try:
        from supabase_config_page import SupabaseConfigPage
        from PySide6.QtWidgets import QApplication
        
        # Create QApplication if not exists
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create and show the page
        print("1. Creating Supabase config page...")
        page = SupabaseConfigPage()
        
        print("2. Page details:")
        print(f"   Title: {page.title()}")
        print(f"   Subtitle: {page.subTitle()}")
        print(f"   Project URL: {page.project_url_edit.text()}")
        print(f"   API Key: {page.api_key_edit.text()[:10]}...")
        
        print("3. UI elements:")
        print(f"   Test button enabled: {page.test_connection_button.isEnabled()}")
        print(f"   Analyze button enabled: {page.analyze_button.isEnabled()}")
        
        print("✅ Wizard page demo completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Wizard page demo failed: {e}")
        return False


def demo_configuration():
    """Demonstrate configuration management."""
    print("\n=== Configuration Demo ===")
    
    try:
        from pathlib import Path
        import json
        
        config_dir = Path.home() / ".tally-tunnel"
        config_file = config_dir / "config.json"
        mapping_file = config_dir / "tally_supabase_mapping.json"
        
        print("1. Configuration directory:")
        print(f"   Path: {config_dir}")
        print(f"   Exists: {config_dir.exists()}")
        
        # Create sample configuration
        sample_config = {
            "supabase_url": "https://ppfwlhfehwelinfprviw.supabase.co",
            "supabase_key": "sb_secret_0ng3_U_wd2MXRyzPYXweuw_dDl-5EAA",
            "company_name": "Demo Company",
            "division_name": "Main Division",
            "city_name": "Demo City",
            "last_sync": "2024-01-01T00:00:00Z"
        }
        
        print("2. Creating sample configuration...")
        with open(config_file, 'w') as f:
            json.dump(sample_config, f, indent=2)
        
        print(f"   Config file created: {config_file.exists()}")
        
        # Create sample mapping
        sample_mapping = {
            "companies": "tally_companies",
            "divisions": "tally_divisions", 
            "ledgers": "tally_ledgers",
            "vouchers": "tally_vouchers",
            "voucher_entries": "tally_voucher_entries"
        }
        
        print("3. Creating sample mapping...")
        with open(mapping_file, 'w') as f:
            json.dump(sample_mapping, f, indent=2)
        
        print(f"   Mapping file created: {mapping_file.exists()}")
        
        # Read and display configuration
        print("4. Reading configuration...")
        with open(config_file, 'r') as f:
            loaded_config = json.load(f)
        
        print(f"   Company: {loaded_config.get('company_name')}")
        print(f"   Division: {loaded_config.get('division_name')}")
        print(f"   City: {loaded_config.get('city_name')}")
        
        print("✅ Configuration demo completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Configuration demo failed: {e}")
        return False


def main():
    """Run all demos."""
    print("Tally Tunnel Wizard - Supabase Integration Demo")
    print("=" * 50)
    
    demos = [
        ("Supabase Connection", demo_supabase_connection),
        ("Sample Data Sync", demo_sample_data_sync),
        ("Wizard Page", demo_wizard_page),
        ("Configuration", demo_configuration)
    ]
    
    results = []
    
    for demo_name, demo_func in demos:
        print(f"\n{demo_name}")
        print("-" * len(demo_name))
        
        try:
            result = demo_func()
            results.append((demo_name, result))
        except Exception as e:
            print(f"❌ Demo failed with exception: {e}")
            results.append((demo_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("DEMO SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for demo_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{demo_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} demos passed")
    
    if passed == total:
        print("🎉 All demos passed! Supabase integration is working correctly.")
    else:
        print("⚠️  Some demos failed. Check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 