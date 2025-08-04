#!/usr/bin/env python3
"""
Tally to Supabase Synchronization
Analyzes Tally data structure and syncs to Supabase database.
"""

import sys
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

from tally_metadata_extractor import TallyMetadataExtractor
from supabase_manager import SupabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TallySupabaseSync:
    """Handles synchronization between Tally Prime and Supabase."""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.tally_extractor = TallyMetadataExtractor()
        self.supabase_manager = SupabaseManager(supabase_url, supabase_key)
        self.config_dir = Path.home() / ".tally-tunnel"
        self.config_dir.mkdir(exist_ok=True)
        self.sync_log_file = self.config_dir / "sync_log.json"
    
    def analyze_tally_structure(self) -> Dict[str, Any]:
        """Analyze Tally data structure to understand available data."""
        logger.info("Analyzing Tally data structure...")
        
        structure = {
            'companies': [],
            'divisions': [],
            'ledgers': [],
            'vouchers': [],
            'voucher_entries': [],
            'metadata': {}
        }
        
        try:
            # Get companies
            companies = self.tally_extractor.get_companies()
            if companies:
                structure['companies'] = self.analyze_data_sample(companies)
                logger.info(f"Found {len(companies)} companies")
            
            # Get divisions
            divisions = self.tally_extractor.get_divisions()
            if divisions:
                structure['divisions'] = self.analyze_data_sample(divisions)
                logger.info(f"Found {len(divisions)} divisions")
            
            # Get ledgers
            ledgers = self.tally_extractor.get_ledgers()
            if ledgers:
                structure['ledgers'] = self.analyze_data_sample(ledgers)
                logger.info(f"Found {len(ledgers)} ledgers")
            
            # Get vouchers
            vouchers = self.tally_extractor.get_vouchers()
            if vouchers:
                structure['vouchers'] = self.analyze_data_sample(vouchers)
                logger.info(f"Found {len(vouchers)} vouchers")
            
            # Get voucher entries
            voucher_entries = self.tally_extractor.get_voucher_entries()
            if voucher_entries:
                structure['voucher_entries'] = self.analyze_data_sample(voucher_entries)
                logger.info(f"Found {len(voucher_entries)} voucher entries")
            
            # Get all metadata
            all_metadata = self.tally_extractor.get_all_metadata()
            if all_metadata:
                structure['metadata'] = all_metadata
                logger.info("Retrieved complete metadata")
            
            return structure
            
        except Exception as e:
            logger.error(f"Error analyzing Tally structure: {e}")
            return structure
    
    def analyze_data_sample(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a sample of data to understand structure."""
        if not data:
            return {'count': 0, 'fields': {}, 'sample': None}
        
        sample = data[0] if data else {}
        fields = {}
        
        for field_name, value in sample.items():
            field_info = {
                'type': self.infer_field_type(value),
                'nullable': True,
                'sample_values': []
            }
            
            # Collect sample values from first few records
            for record in data[:10]:
                if field_name in record:
                    field_info['sample_values'].append(record[field_name])
            
            fields[field_name] = field_info
        
        return {
            'count': len(data),
            'fields': fields,
            'sample': sample
        }
    
    def infer_field_type(self, value: Any) -> str:
        """Infer field type from value."""
        if value is None:
            return 'TEXT'
        elif isinstance(value, bool):
            return 'BOOLEAN'
        elif isinstance(value, int):
            return 'INTEGER'
        elif isinstance(value, float):
            return 'NUMERIC'
        elif isinstance(value, str):
            # Try to parse as date/datetime
            try:
                datetime.fromisoformat(value.replace('Z', '+00:00'))
                return 'TIMESTAMP WITH TIME ZONE'
            except:
                return 'TEXT'
        elif isinstance(value, (list, dict)):
            return 'JSONB'
        else:
            return 'TEXT'
    
    def create_table_mapping(self, tally_structure: Dict[str, Any]) -> Dict[str, str]:
        """Create mapping between Tally data types and Supabase table names."""
        mapping = {}
        
        # Map Tally data types to table names
        if tally_structure.get('companies'):
            mapping['companies'] = 'tally_companies'
        
        if tally_structure.get('divisions'):
            mapping['divisions'] = 'tally_divisions'
        
        if tally_structure.get('ledgers'):
            mapping['ledgers'] = 'tally_ledgers'
        
        if tally_structure.get('vouchers'):
            mapping['vouchers'] = 'tally_vouchers'
        
        if tally_structure.get('voucher_entries'):
            mapping['voucher_entries'] = 'tally_voucher_entries'
        
        return mapping
    
    def sync_data_to_supabase(self, tally_structure: Dict[str, Any], mapping: Dict[str, str]) -> bool:
        """Sync Tally data to Supabase tables."""
        logger.info("Starting data synchronization to Supabase...")
        
        success = True
        sync_results = {}
        
        for tally_type, table_name in mapping.items():
            logger.info(f"Syncing {tally_type} to {table_name}...")
            
            try:
                # Get data based on type
                if tally_type == 'companies':
                    data = self.tally_extractor.get_companies()
                elif tally_type == 'divisions':
                    data = self.tally_extractor.get_divisions()
                elif tally_type == 'ledgers':
                    data = self.tally_extractor.get_ledgers()
                elif tally_type == 'vouchers':
                    data = self.tally_extractor.get_vouchers()
                elif tally_type == 'voucher_entries':
                    data = self.tally_extractor.get_voucher_entries()
                else:
                    continue
                
                if not data:
                    logger.warning(f"No data found for {tally_type}")
                    sync_results[tally_type] = {'status': 'no_data', 'count': 0}
                    continue
                
                # Sync to Supabase
                if self.supabase_manager.sync_tally_data({table_name: data}):
                    sync_results[tally_type] = {'status': 'success', 'count': len(data)}
                    logger.info(f"Successfully synced {len(data)} records to {table_name}")
                else:
                    sync_results[tally_type] = {'status': 'failed', 'count': len(data)}
                    success = False
                    logger.error(f"Failed to sync {tally_type} to {table_name}")
                
            except Exception as e:
                logger.error(f"Error syncing {tally_type}: {e}")
                sync_results[tally_type] = {'status': 'error', 'error': str(e)}
                success = False
        
        # Save sync results
        self.save_sync_log(sync_results)
        
        return success
    
    def save_sync_log(self, sync_results: Dict[str, Any]):
        """Save synchronization results to log file."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'results': sync_results
        }
        
        try:
            if self.sync_log_file.exists():
                with open(self.sync_log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(log_entry)
            
            with open(self.sync_log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save sync log: {e}")
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current synchronization status."""
        try:
            if self.sync_log_file.exists():
                with open(self.sync_log_file, 'r') as f:
                    logs = json.load(f)
                if logs:
                    return logs[-1]  # Return latest log entry
        except Exception as e:
            logger.error(f"Failed to read sync log: {e}")
        
        return {'timestamp': None, 'results': {}}
    
    def validate_supabase_connection(self) -> bool:
        """Validate Supabase connection."""
        return self.supabase_manager.test_connection()
    
    def validate_tally_connection(self) -> bool:
        """Validate Tally connection."""
        try:
            companies = self.tally_extractor.get_companies()
            return len(companies) > 0
        except Exception as e:
            logger.error(f"Tally connection validation failed: {e}")
            return False
    
    def get_supabase_info(self) -> Dict[str, Any]:
        """Get Supabase connection and table information."""
        return self.supabase_manager.get_connection_info()
    
    def preview_sync_plan(self, tally_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Preview what will be synced to Supabase."""
        mapping = self.create_table_mapping(tally_structure)
        
        plan = {
            'tables_to_create': [],
            'tables_to_update': [],
            'data_summary': {},
            'estimated_records': 0
        }
        
        existing_tables = self.supabase_manager.get_existing_tables()
        
        for tally_type, table_name in mapping.items():
            data_info = tally_structure.get(tally_type, {})
            record_count = data_info.get('count', 0)
            
            plan['data_summary'][table_name] = {
                'source': tally_type,
                'record_count': record_count,
                'fields': data_info.get('fields', {})
            }
            
            plan['estimated_records'] += record_count
            
            if table_name in existing_tables:
                plan['tables_to_update'].append(table_name)
            else:
                plan['tables_to_create'].append(table_name)
        
        return plan


def main():
    """Test the Tally to Supabase synchronization."""
    # Supabase configuration
    supabase_url = "https://ppfwlhfehwelinfprviw.supabase.co"
    supabase_key = "sb_secret_0ng3_U_wd2MXRyzPYXweuw_dDl-5EAA"
    
    sync = TallySupabaseSync(supabase_url, supabase_key)
    
    print("=== Tally to Supabase Synchronization Test ===")
    
    # Test connections
    print("\n1. Testing connections...")
    tally_connected = sync.validate_tally_connection()
    supabase_connected = sync.validate_supabase_connection()
    
    print(f"Tally Prime: {'✅ Connected' if tally_connected else '❌ Not connected'}")
    print(f"Supabase: {'✅ Connected' if supabase_connected else '❌ Not connected'}")
    
    if not tally_connected or not supabase_connected:
        print("Cannot proceed without both connections.")
        return
    
    # Analyze Tally structure
    print("\n2. Analyzing Tally data structure...")
    structure = sync.analyze_tally_structure()
    
    print("Data structure analysis:")
    for data_type, info in structure.items():
        if isinstance(info, dict) and 'count' in info:
            print(f"  {data_type}: {info['count']} records")
    
    # Preview sync plan
    print("\n3. Previewing sync plan...")
    plan = sync.preview_sync_plan(structure)
    
    print("Sync plan:")
    print(f"  Tables to create: {plan['tables_to_create']}")
    print(f"  Tables to update: {plan['tables_to_update']}")
    print(f"  Estimated total records: {plan['estimated_records']}")
    
    print("\nData summary:")
    for table_name, info in plan['data_summary'].items():
        print(f"  {table_name}: {info['record_count']} records from {info['source']}")
    
    # Ask for confirmation
    print("\n4. Ready to sync?")
    response = input("Do you want to proceed with synchronization? (y/N): ")
    
    if response.lower() == 'y':
        print("\n5. Starting synchronization...")
        mapping = sync.create_table_mapping(structure)
        success = sync.sync_data_to_supabase(structure, mapping)
        
        if success:
            print("✅ Synchronization completed successfully!")
        else:
            print("❌ Synchronization failed. Check logs for details.")
    else:
        print("Synchronization cancelled.")


if __name__ == "__main__":
    main() 