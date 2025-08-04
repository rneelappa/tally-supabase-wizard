#!/usr/bin/env python3
"""
Tally REST API Starter
Starts the FastAPI service for Tally Prime data access.
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import requests
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def check_tally_connection():
    """Check if Tally Prime is accessible."""
    try:
        response = requests.post(
            "http://localhost:9000",
            data="<ENVELOPE><HEADER><TALLYREQUEST>Export</TALLYREQUEST></HEADER></ENVELOPE>",
            headers={'Content-Type': 'application/xml'},
            timeout=5
        )
        print("✅ Tally Prime is accessible")
        return True
    except Exception as e:
        print(f"❌ Tally Prime is not accessible: {e}")
        print("Please make sure Tally Prime is running and accessible on http://localhost:9000")
        return False

def start_api_service():
    """Start the Tally REST API service."""
    print("🚀 Starting Tally REST API service...")
    
    try:
        # Start the API service
        process = subprocess.Popen([
            sys.executable, "tally_rest_api.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a moment for the service to start
        time.sleep(3)
        
        # Check if service is running
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Tally REST API service is running on http://localhost:8000")
                print("📖 API Documentation: http://localhost:8000/docs")
                print("🔍 Health Check: http://localhost:8000/health")
                print("\nAvailable endpoints:")
                print("  GET /companies     - Get all companies")
                print("  GET /divisions     - Get all divisions")
                print("  GET /ledgers       - Get all ledgers")
                print("  GET /vouchers      - Get all vouchers")
                print("  GET /metadata      - Get all metadata")
                print("\nPress Ctrl+C to stop the service")
                
                try:
                    process.wait()
                except KeyboardInterrupt:
                    print("\n🛑 Stopping Tally REST API service...")
                    process.terminate()
                    process.wait()
                    print("✅ Service stopped")
                
                return True
            else:
                print(f"❌ Service returned status code: {response.status_code}")
                process.terminate()
                return False
        except requests.exceptions.RequestException:
            print("❌ Service failed to start properly")
            process.terminate()
            return False
            
    except Exception as e:
        print(f"❌ Failed to start service: {e}")
        return False

def main():
    """Main function."""
    print("=" * 50)
    print("Tally REST API Starter")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check Tally connection
    if not check_tally_connection():
        print("\n⚠️  Warning: Tally Prime is not accessible.")
        print("The API service will start but may not be able to fetch data.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Start the service
    if not start_api_service():
        sys.exit(1)

if __name__ == "__main__":
    main() 