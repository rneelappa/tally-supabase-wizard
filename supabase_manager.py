#!/usr/bin/env python3
"""
Supabase Manager for Tally Tunnel Wizard
Handles Supabase database operations and Tally data synchronization.
"""

import os
import sys
import json
import logging
import requests
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SupabaseManager:
    """Manages Supabase database operations and Tally data synchronization."""
    
    def __init__(self, project_url: str, api_key: str):
        self.project_url = project_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'apikey': api_key,
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
        self.config_dir = Path.home() / ".tally-tunnel"
        self.config_dir.mkdir(exist_ok=True)
        self.mapping_file = self.config_dir / "tally_supabase_mapping.json"
        self.load_mapping()
    
    def load_mapping(self):
        """Load table and field mapping from local file."""
        if self.mapping_file.exists():
            try:
                with open(self.mapping_file, 'r') as f:
                    self.mapping = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load mapping: {e}")
                self.mapping = {}
        else:
            self.mapping = {}
    
    def save_mapping(self):
        """Save table and field mapping to local file."""
        try:
            with open(self.mapping_file, 'w') as f:
                json.dump(self.mapping, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save mapping: {e}")
    
    def test_connection(self) -> bool:
        """Test Supabase connection."""
        try:
            response = requests.get(
                f"{self.project_url}/rest/v1/",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
            return False
    
    def get_existing_tables(self) -> List[str]:
        """Get list of existing tables in Supabase."""
        try:
            # Try to get tables by attempting to access common system tables
            # This is a workaround since we can't use direct SQL queries
            common_tables = [
                'tally_companies', 'tally_divisions', 'tally_ledgers', 
                'tally_vouchers', 'tally_voucher_entries', 'companies', 
                'divisions', 'ledgers', 'vouchers', 'voucher_entries'
            ]
            
            existing_tables = []
            
            for table_name in common_tables:
                try:
                    response = requests.get(
                        f"{self.project_url}/rest/v1/{table_name}",
                        headers=self.headers,
                        params={'select': 'count'},
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        existing_tables.append(table_name)
                        logger.info(f"Found existing table: {table_name}")
                    
                except Exception:
                    continue
            
            return existing_tables
                
        except Exception as e:
            logger.error(f"Error getting existing tables: {e}")
            return []
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get schema for a specific table."""
        try:
            # Try to get a sample record to understand the schema
            response = requests.get(
                f"{self.project_url}/rest/v1/{table_name}",
                headers=self.headers,
                params={'limit': 1},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    sample_record = data[0]
                    schema = []
                    for field_name, value in sample_record.items():
                        schema.append({
                            'column_name': field_name,
                            'data_type': self.infer_data_type(value),
                            'is_nullable': True
                        })
                    return schema
                else:
                    logger.warning(f"Table {table_name} exists but has no data")
                    return []
            else:
                logger.error(f"Failed to get schema for {table_name}: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting schema for {table_name}: {e}")
            return {}
    
    def create_table(self, table_name: str, columns: List[Dict[str, Any]]) -> bool:
        """Create a new table in Supabase."""
        try:
            # For Supabase, we'll try to insert a sample record to create the table structure
            # This is a simplified approach - in production, you'd use Supabase's migration system
            
            # Create a sample record with the expected structure
            sample_record = {}
            for col in columns:
                col_name = col['name']
                col_type = col['type']
                
                # Set default values based on type
                if col_type == 'INTEGER':
                    sample_record[col_name] = 0
                elif col_type == 'NUMERIC':
                    sample_record[col_name] = 0.0
                elif col_type == 'BOOLEAN':
                    sample_record[col_name] = False
                elif col_type == 'TIMESTAMP WITH TIME ZONE':
                    sample_record[col_name] = "2024-01-01T00:00:00Z"
                else:
                    sample_record[col_name] = ""
            
            # Try to insert the sample record
            response = requests.post(
                f"{self.project_url}/rest/v1/{table_name}",
                headers=self.headers,
                json=sample_record,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Table {table_name} structure created successfully")
                
                # Delete the sample record
                if response.status_code == 201 and 'id' in response.json():
                    delete_response = requests.delete(
                        f"{self.project_url}/rest/v1/{table_name}",
                        headers=self.headers,
                        params={'id': 'eq.' + str(response.json()['id'])},
                        timeout=10
                    )
                
                return True
            else:
                logger.error(f"Failed to create table {table_name}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating table {table_name}: {e}")
            return False
    
    def alter_table(self, table_name: str, columns: List[Dict[str, Any]]) -> bool:
        """Alter existing table to match Tally schema."""
        try:
            # For Supabase REST API, we can't easily alter tables
            # Instead, we'll check if the table can handle the new data structure
            # by attempting to insert a sample record
            
            existing_schema = self.get_table_schema(table_name)
            existing_columns = {col['column_name']: col for col in existing_schema}
            
            # Check if we need to add new columns
            new_columns = []
            for col in columns:
                col_name = col['name']
                if col_name not in existing_columns:
                    new_columns.append(col)
            
            if new_columns:
                logger.warning(f"Table {table_name} needs new columns: {[col['name'] for col in new_columns]}")
                logger.warning("Supabase REST API doesn't support schema alterations. Please use Supabase dashboard.")
                return False
            else:
                logger.info(f"Table {table_name} schema is compatible")
                return True
                
        except Exception as e:
            logger.error(f"Error checking table {table_name}: {e}")
            return False
    
    def map_tally_type_to_sql(self, tally_type: str) -> str:
        """Map Tally data types to SQL types."""
        type_mapping = {
            'string': 'TEXT',
            'text': 'TEXT',
            'varchar': 'VARCHAR(255)',
            'number': 'NUMERIC',
            'integer': 'INTEGER',
            'int': 'INTEGER',
            'decimal': 'NUMERIC(10,2)',
            'date': 'DATE',
            'datetime': 'TIMESTAMP WITH TIME ZONE',
            'boolean': 'BOOLEAN',
            'bool': 'BOOLEAN',
            'json': 'JSONB',
            'array': 'JSONB'
        }
        
        tally_type_lower = tally_type.lower()
        return type_mapping.get(tally_type_lower, 'TEXT')
    
    def insert_data(self, table_name: str, data: List[Dict[str, Any]]) -> bool:
        """Insert data into Supabase table."""
        try:
            if not data:
                logger.info(f"No data to insert for table {table_name}")
                return True
            
            # Insert in batches to avoid payload size limits
            batch_size = 100
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                
                response = requests.post(
                    f"{self.project_url}/rest/v1/{table_name}",
                    headers=self.headers,
                    json=batch,
                    timeout=30
                )
                
                if response.status_code not in [200, 201]:
                    logger.error(f"Failed to insert batch {i//batch_size + 1} for {table_name}: {response.status_code}")
                    return False
                
                logger.info(f"Inserted batch {i//batch_size + 1} for {table_name}")
                time.sleep(0.1)  # Small delay to avoid rate limiting
            
            return True
            
        except Exception as e:
            logger.error(f"Error inserting data into {table_name}: {e}")
            return False
    
    def clear_table(self, table_name: str) -> bool:
        """Clear all data from a table."""
        try:
            response = requests.delete(
                f"{self.project_url}/rest/v1/{table_name}",
                headers=self.headers,
                params={'select': '*'},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Table {table_name} cleared successfully")
                return True
            else:
                logger.error(f"Failed to clear table {table_name}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error clearing table {table_name}: {e}")
            return False
    
    def sync_tally_data(self, tally_data: Dict[str, Any]) -> bool:
        """Sync Tally data to Supabase tables."""
        try:
            success = True
            
            for table_name, data in tally_data.items():
                if not data:
                    continue
                
                # Ensure table exists and has correct schema
                if not self.ensure_table_schema(table_name, data):
                    success = False
                    continue
                
                # Clear existing data
                if not self.clear_table(table_name):
                    success = False
                    continue
                
                # Insert new data
                if not self.insert_data(table_name, data):
                    success = False
                    continue
                
                logger.info(f"Successfully synced {len(data)} records to {table_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error syncing Tally data: {e}")
            return False
    
    def ensure_table_schema(self, table_name: str, sample_data: List[Dict[str, Any]]) -> bool:
        """Ensure table exists with correct schema based on sample data."""
        try:
            if not sample_data:
                return True
            
            # Analyze sample data to determine column types
            columns = self.analyze_data_structure(sample_data)
            
            # Check if table exists
            existing_tables = self.get_existing_tables()
            
            if table_name in existing_tables:
                # Table exists, check if schema needs updating
                return self.alter_table(table_name, columns)
            else:
                # Table doesn't exist, create it
                return self.create_table(table_name, columns)
                
        except Exception as e:
            logger.error(f"Error ensuring table schema for {table_name}: {e}")
            return False
    
    def analyze_data_structure(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze data structure to determine column types."""
        if not data:
            return []
        
        columns = []
        sample = data[0] if data else {}
        
        for field_name, value in sample.items():
            col_type = self.infer_data_type(value)
            columns.append({
                'name': field_name,
                'type': col_type,
                'nullable': True
            })
        
        return columns
    
    def infer_data_type(self, value: Any) -> str:
        """Infer SQL data type from Python value."""
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
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information for display."""
        return {
            'project_url': self.project_url,
            'api_key': self.api_key[:10] + '...' if len(self.api_key) > 10 else self.api_key,
            'connected': self.test_connection(),
            'tables': self.get_existing_tables()
        }


def main():
    """Test the Supabase manager."""
    # Test configuration
    project_url = "https://ppfwlhfehwelinfprviw.supabase.co"
    api_key = "sb_secret_0ng3_U_wd2MXRyzPYXweuw_dDl-5EAA"
    
    manager = SupabaseManager(project_url, api_key)
    
    print("Testing Supabase connection...")
    if manager.test_connection():
        print("✅ Connected to Supabase successfully")
        
        print("\nExisting tables:")
        tables = manager.get_existing_tables()
        if tables:
            for table in tables:
                print(f"  - {table}")
        else:
            print("  No tables found")
        
        print(f"\nConnection info: {manager.get_connection_info()}")
    else:
        print("❌ Failed to connect to Supabase")


if __name__ == "__main__":
    main() 