#!/usr/bin/env python3
"""
Test Supabase Integration
Comprehensive testing of Supabase connection and Tally data synchronization.
"""

import sys
import json
from pathlib import Path

def test_supabase_manager():
    """Test Supabase manager functionality."""
    print("=== Testing Supabase Manager ===")
    
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
            print("   Cannot proceed with other tests.")
            return False
        
        # Test getting tables
        print("2. Getting existing tables...")
        tables = manager.get_existing_tables()
        print(f"   Found {len(tables)} tables: {tables}")
        
        # Test connection info
        print("3. Getting connection info...")
        info = manager.get_connection_info()
        print(f"   Project URL: {info['project_url']}")
        print(f"   API Key: {info['api_key']}")
        print(f"   Connected: {info['connected']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Supabase Manager test failed: {e}")
        return False


def test_tally_supabase_sync():
    """Test Tally to Supabase synchronization."""
    print("\n=== Testing Tally to Supabase Sync ===")
    
    try:
        from tally_supabase_sync import TallySupabaseSync
        
        # Test configuration
        supabase_url = "https://ppfwlhfehwelinfprviw.supabase.co"
        supabase_key = "sb_secret_0ng3_U_wd2MXRyzPYXweuw_dDl-5EAA"
        
        sync = TallySupabaseSync(supabase_url, supabase_key)
        
        # Test connections
        print("1. Testing connections...")
        tally_connected = sync.validate_tally_connection()
        supabase_connected = sync.validate_supabase_connection()
        
        print(f"   Tally Prime: {'✅ Connected' if tally_connected else '❌ Not connected'}")
        print(f"   Supabase: {'✅ Connected' if supabase_connected else '❌ Not connected'}")
        
        if not tally_connected or not supabase_connected:
            print("   Cannot proceed with sync tests.")
            return False
        
        # Test structure analysis
        print("2. Analyzing Tally structure...")
        structure = sync.analyze_tally_structure()
        
        print("   Data structure analysis:")
        for data_type, info in structure.items():
            if isinstance(info, dict) and 'count' in info:
                print(f"     {data_type}: {info['count']} records")
        
        # Test sync plan
        print("3. Creating sync plan...")
        plan = sync.preview_sync_plan(structure)
        
        print(f"   Tables to create: {plan['tables_to_create']}")
        print(f"   Tables to update: {plan['tables_to_update']}")
        print(f"   Estimated records: {plan['estimated_records']}")
        
        # Test mapping
        print("4. Testing table mapping...")
        mapping = sync.create_table_mapping(structure)
        print(f"   Mapping: {mapping}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tally Supabase Sync test failed: {e}")
        return False


def test_supabase_config_page():
    """Test Supabase configuration page."""
    print("\n=== Testing Supabase Config Page ===")
    
    try:
        from supabase_config_page import SupabaseConfigPage
        from PySide6.QtWidgets import QApplication
        
        # Create QApplication if not exists
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Test page creation
        print("1. Creating Supabase config page...")
        page = SupabaseConfigPage()
        print("   ✅ Page created successfully")
        
        # Test UI elements
        print("2. Testing UI elements...")
        assert page.project_url_edit is not None
        assert page.api_key_edit is not None
        assert page.test_connection_button is not None
        print("   ✅ UI elements created successfully")
        
        # Test default values
        print("3. Testing default values...")
        expected_url = "https://ppfwlhfehwelinfprviw.supabase.co"
        expected_key = "sb_secret_0ng3_U_wd2MXRyzPYXweuw_dDl-5EAA"
        
        assert page.project_url_edit.text() == expected_url
        assert page.api_key_edit.text() == expected_key
        print("   ✅ Default values set correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Supabase Config Page test failed: {e}")
        return False


def test_configuration_persistence():
    """Test configuration persistence."""
    print("\n=== Testing Configuration Persistence ===")
    
    try:
        from pathlib import Path
        import json
        
        config_dir = Path.home() / ".tally-tunnel"
        config_file = config_dir / "config.json"
        mapping_file = config_dir / "tally_supabase_mapping.json"
        sync_log_file = config_dir / "sync_log.json"
        
        print("1. Checking configuration directory...")
        assert config_dir.exists()
        print("   ✅ Configuration directory exists")
        
        # Test config file
        if config_file.exists():
            print("2. Reading existing config...")
            with open(config_file, 'r') as f:
                config = json.load(f)
            print(f"   ✅ Config loaded: {list(config.keys())}")
        
        # Test mapping file creation
        print("3. Testing mapping file...")
        test_mapping = {
            'companies': 'tally_companies',
            'ledgers': 'tally_ledgers'
        }
        
        with open(mapping_file, 'w') as f:
            json.dump(test_mapping, f)
        
        assert mapping_file.exists()
        print("   ✅ Mapping file created successfully")
        
        # Clean up
        mapping_file.unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration persistence test failed: {e}")
        return False


def test_dependencies():
    """Test required dependencies."""
    print("=== Testing Dependencies ===")
    
    dependencies = [
        ('PySide6', 'PySide6'),
        ('requests', 'requests'),
        ('supabase', 'supabase'),
        ('tally_metadata_extractor', 'tally_metadata_extractor'),
        ('supabase_manager', 'supabase_manager'),
        ('tally_supabase_sync', 'tally_supabase_sync'),
        ('supabase_config_page', 'supabase_config_page')
    ]
    
    all_ok = True
    
    for module_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"   ✅ {module_name}")
        except ImportError as e:
            print(f"   ❌ {module_name}: {e}")
            all_ok = False
    
    return all_ok


def main():
    """Run all tests."""
    print("Tally Tunnel Wizard - Supabase Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Supabase Manager", test_supabase_manager),
        ("Tally Supabase Sync", test_tally_supabase_sync),
        ("Supabase Config Page", test_supabase_config_page),
        ("Configuration Persistence", test_configuration_persistence)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * len(test_name))
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Supabase integration is ready.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 