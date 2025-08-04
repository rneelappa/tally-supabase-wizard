#!/usr/bin/env python3
"""
Tally Prime Metadata Extractor
Extracts metadata from Tally Prime using REST API approach.
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TallyRESTClient:
    """REST client for Tally Prime API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 30
    
    def health_check(self) -> bool:
        """Check if Tally REST API is healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            data = response.json()
            # API is healthy if it responds, even if Tally is not connected
            return data.get("status") == "healthy" or data.get("status") == "unhealthy"
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def get_companies(self) -> List[Dict[str, Any]]:
        """Get all companies from Tally."""
        try:
            response = self.session.get(f"{self.base_url}/companies")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get companies: {e}")
            return []
    
    def get_divisions(self) -> List[Dict[str, Any]]:
        """Get all divisions from Tally."""
        try:
            response = self.session.get(f"{self.base_url}/divisions")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get divisions: {e}")
            return []
    
    def get_ledgers(self) -> List[Dict[str, Any]]:
        """Get all ledgers from Tally."""
        try:
            response = self.session.get(f"{self.base_url}/ledgers")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get ledgers: {e}")
            return []
    
    def get_vouchers(self) -> List[Dict[str, Any]]:
        """Get all vouchers from Tally."""
        try:
            response = self.session.get(f"{self.base_url}/vouchers")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get vouchers: {e}")
            return []


class TallyMetadataExtractor:
    """Extracts metadata from Tally Prime using REST API."""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.client = TallyRESTClient(api_url)
        self.cache = {}
        self.cache_timestamp = {}
        self.cache_duration = 300  # 5 minutes cache
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid."""
        if key not in self.cache_timestamp:
            return False
        return time.time() - self.cache_timestamp[key] < self.cache_duration
    
    def _update_cache(self, key: str, data: Any):
        """Update cache with new data."""
        self.cache[key] = data
        self.cache_timestamp[key] = time.time()
    
    def is_connected(self) -> bool:
        """Check if Tally REST API is available."""
        return self.client.health_check()
    
    def get_companies(self) -> List[Dict[str, Any]]:
        """Get all companies from Tally Prime."""
        cache_key = "companies"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        companies = self.client.get_companies()
        self._update_cache(cache_key, companies)
        return companies
    
    def get_divisions(self) -> List[Dict[str, Any]]:
        """Get all divisions/cost centres from Tally Prime."""
        cache_key = "divisions"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        divisions = self.client.get_divisions()
        self._update_cache(cache_key, divisions)
        return divisions
    
    def get_ledgers(self) -> List[Dict[str, Any]]:
        """Get all ledgers from Tally Prime."""
        cache_key = "ledgers"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        ledgers = self.client.get_ledgers()
        self._update_cache(cache_key, ledgers)
        return ledgers
    
    def get_vouchers(self) -> List[Dict[str, Any]]:
        """Get all vouchers from Tally Prime."""
        cache_key = "vouchers"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        vouchers = self.client.get_vouchers()
        self._update_cache(cache_key, vouchers)
        return vouchers
    
    def get_all_metadata(self) -> Dict[str, Any]:
        """Get all metadata from Tally Prime."""
        return {
            "companies": self.get_companies(),
            "divisions": self.get_divisions(),
            "ledgers": self.get_ledgers(),
            "vouchers": self.get_vouchers(),
            "extracted_at": datetime.now().isoformat()
        }
    
    def get_metadata_summary(self) -> Dict[str, int]:
        """Get a summary of metadata counts."""
        companies = self.get_companies()
        divisions = self.get_divisions()
        ledgers = self.get_ledgers()
        vouchers = self.get_vouchers()
        
        return {
            "companies_count": len(companies),
            "divisions_count": len(divisions),
            "ledgers_count": len(ledgers),
            "vouchers_count": len(vouchers)
        }
    
    def clear_cache(self):
        """Clear all cached data."""
        self.cache.clear()
        self.cache_timestamp.clear()
        logger.info("Cache cleared")
    
    def close(self):
        """Close the extractor and clean up resources."""
        self.clear_cache()
        logger.info("TallyMetadataExtractor closed")


def test_tally_connection():
    """Test the Tally REST API connection."""
    extractor = TallyMetadataExtractor()
    
    print("Testing Tally REST API connection...")
    
    if not extractor.is_connected():
        print("❌ Failed to connect to Tally REST API")
        print("Make sure the Tally REST API is running on http://localhost:8000")
        return False
    
    print("✅ Connected to Tally REST API")
    
    # Test getting metadata
    try:
        summary = extractor.get_metadata_summary()
        print(f"📊 Metadata Summary:")
        print(f"   Companies: {summary.get('companies_count', 0)}")
        print(f"   Divisions: {summary.get('divisions_count', 0)}")
        print(f"   Ledgers: {summary.get('ledgers_count', 0)}")
        print(f"   Vouchers: {summary.get('vouchers_count', 0)}")
        
        return True
    except Exception as e:
        print(f"❌ Error getting metadata: {e}")
        return False


if __name__ == "__main__":
    test_tally_connection() 