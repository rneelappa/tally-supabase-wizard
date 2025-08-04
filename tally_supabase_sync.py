#!/usr/bin/env python3
"""
Tally Supabase Synchronization Module
Updated to use the working TallyHTTPClient
"""

import logging
from typing import Dict, List, Any, Optional
from tally_http_client import TallyHTTPClient

logger = logging.getLogger(__name__)

class TallySupabaseSync:
    def __init__(self, tally_client: TallyHTTPClient):
        self.tally_client = tally_client
        
    def analyze_tally_data(self) -> Dict[str, Any]:
        """Analyze Tally data structure and return metadata."""
        logger.info("Analyzing Tally data structure...")
        
        try:
            # Test connection first
            if not self.tally_client.test_connection():
                logger.error("Failed to connect to Tally")
                return {"error": "Failed to connect to Tally"}
            
            # Get companies
            companies = self.tally_client.get_companies()
            logger.info(f"Found {len(companies)} companies")
            
            if not companies:
                logger.warning("No companies found in Tally")
                return {"error": "No companies found in Tally"}
            
            # Use the first company for detailed analysis
            company_name = companies[0]["Name"]
            logger.info(f"Using company: {company_name}")
            
            # Get all data types for this company
            divisions = self.tally_client.get_divisions(company_name)
            ledgers = self.tally_client.get_ledgers(company_name)
            groups = self.tally_client.get_groups(company_name)
            vouchers = self.tally_client.get_vouchers(company_name)
            
            # Compile metadata
            metadata = {
                "companies": companies,
                "divisions": divisions,
                "ledgers": ledgers,
                "groups": groups,
                "vouchers": vouchers,
                "summary": {
                    "total_companies": len(companies),
                    "total_divisions": len(divisions),
                    "total_ledgers": len(ledgers),
                    "total_groups": len(groups),
                    "total_vouchers": len(vouchers),
                    "primary_company": company_name
                }
            }
            
            logger.info("Retrieved complete metadata")
            return metadata
            
        except Exception as e:
            logger.error(f"Error analyzing Tally data: {e}")
            return {"error": str(e)}
    
    def get_sync_recommendations(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate synchronization recommendations based on Tally data."""
        if "error" in metadata:
            return {"error": metadata["error"]}
        
        summary = metadata.get("summary", {})
        recommendations = {
            "sync_strategy": "incremental",
            "priority_order": [
                "companies",
                "groups", 
                "ledgers",
                "divisions",
                "vouchers"
            ],
            "estimated_records": {
                "companies": summary.get("total_companies", 0),
                "groups": summary.get("total_groups", 0),
                "ledgers": summary.get("total_ledgers", 0),
                "divisions": summary.get("total_divisions", 0),
                "vouchers": summary.get("total_vouchers", 0)
            },
            "notes": []
        }
        
        # Add specific recommendations
        if summary.get("total_vouchers", 0) > 1000:
            recommendations["notes"].append("Large number of vouchers detected. Consider date-based filtering for initial sync.")
        
        if summary.get("total_ledgers", 0) > 500:
            recommendations["notes"].append("Large chart of accounts. Consider grouping ledgers by type.")
        
        if summary.get("total_divisions", 0) == 0:
            recommendations["notes"].append("No divisions/cost centres found. This is normal for many Tally setups.")
        
        return recommendations
    
    def validate_data_quality(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the quality of Tally data."""
        if "error" in metadata:
            return {"error": metadata["error"]}
        
        issues = []
        warnings = []
        
        # Check companies
        companies = metadata.get("companies", [])
        if not companies:
            issues.append("No companies found")
        elif len(companies) > 1:
            warnings.append(f"Multiple companies found ({len(companies)}). Only the first will be used for detailed analysis.")
        
        # Check ledgers
        ledgers = metadata.get("ledgers", [])
        if not ledgers:
            issues.append("No ledgers found")
        else:
            # Check for ledgers without names
            unnamed_ledgers = [l for l in ledgers if not l.get("Name")]
            if unnamed_ledgers:
                warnings.append(f"Found {len(unnamed_ledgers)} ledgers without names")
        
        # Check groups
        groups = metadata.get("groups", [])
        if not groups:
            warnings.append("No groups found (this may be normal)")
        
        # Check vouchers
        vouchers = metadata.get("vouchers", [])
        if not vouchers:
            warnings.append("No vouchers found in current period")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "data_quality_score": max(0, 100 - len(issues) * 20 - len(warnings) * 5)
        }
    
    def prepare_sync_data(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for synchronization with Supabase."""
        if "error" in metadata:
            return {"error": metadata["error"]}
        
        # Transform data for Supabase
        sync_data = {
            "companies": [],
            "groups": [],
            "ledgers": [],
            "divisions": [],
            "vouchers": []
        }
        
        # Transform companies
        for company in metadata.get("companies", []):
            sync_data["companies"].append({
                "tally_guid": company.get("GUID"),
                "name": company.get("Name"),
                "email": company.get("Email"),
                "state": company.get("State"),
                "pincode": company.get("Pincode"),
                "phone": company.get("Phone"),
                "company_number": company.get("CompanyNumber")
            })
        
        # Transform groups
        for group in metadata.get("groups", []):
            sync_data["groups"].append({
                "tally_guid": group.get("GUID"),
                "name": group.get("Name"),
                "parent": group.get("Parent")
            })
        
        # Transform ledgers
        for ledger in metadata.get("ledgers", []):
            sync_data["ledgers"].append({
                "tally_guid": ledger.get("GUID"),
                "name": ledger.get("Name"),
                "parent": ledger.get("Parent"),
                "opening_balance": ledger.get("OpeningBalance"),
                "closing_balance": ledger.get("ClosingBalance")
            })
        
        # Transform divisions
        for division in metadata.get("divisions", []):
            sync_data["divisions"].append({
                "tally_guid": division.get("GUID"),
                "name": division.get("Name"),
                "parent": division.get("Parent"),
                "category": division.get("Category")
            })
        
        # Transform vouchers
        for voucher in metadata.get("vouchers", []):
            sync_data["vouchers"].append({
                "voucher_number": voucher.get("VoucherNumber"),
                "date": voucher.get("Date"),
                "voucher_type": voucher.get("VoucherTypeName"),
                "narration": voucher.get("Narration"),
                "reference": voucher.get("Reference"),
                "amount": voucher.get("Amount")
            })
        
        return sync_data


def main():
    """Test the Tally Supabase Sync module."""
    print("Testing Tally Supabase Sync...")
    
    # Create Tally client
    tally_client = TallyHTTPClient()
    
    # Create sync instance
    sync = TallySupabaseSync(tally_client)
    
    # Analyze data
    metadata = sync.analyze_tally_data()
    
    if "error" in metadata:
        print(f"❌ Error: {metadata['error']}")
        return
    
    # Get recommendations
    recommendations = sync.get_sync_recommendations(metadata)
    print(f"📋 Sync Recommendations: {recommendations}")
    
    # Validate data quality
    quality = sync.validate_data_quality(metadata)
    print(f"🔍 Data Quality: {quality}")
    
    # Prepare sync data
    sync_data = sync.prepare_sync_data(metadata)
    print(f"📊 Prepared {len(sync_data['companies'])} companies, {len(sync_data['ledgers'])} ledgers for sync")


if __name__ == "__main__":
    main() 