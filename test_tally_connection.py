#!/usr/bin/env python3
"""
Simple Tally Prime connection test to diagnose timeout issues.
"""

import requests
import socket
import time

def test_basic_connection():
    """Test basic connection to Tally Prime."""
    print("🔍 Testing Tally Prime Connection")
    print("=" * 50)
    
    # Test 1: Check if port 9000 is open
    print("\n1. Testing Port 9000...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', 9000))
        sock.close()
        
        if result == 0:
            print("✅ Port 9000 is open and accessible")
        else:
            print("❌ Port 9000 is not accessible")
            print("   Make sure Tally Prime is running and XML access is enabled")
            return False
    except Exception as e:
        print(f"❌ Error testing port: {e}")
        return False
    
    # Test 2: Test basic HTTP connection
    print("\n2. Testing HTTP Connection...")
    try:
        response = requests.get("http://localhost:9000", timeout=5)
        print(f"✅ HTTP connection successful - Status: {response.status_code}")
        print(f"   Response length: {len(response.text)} characters")
    except requests.exceptions.ConnectionError:
        print("❌ HTTP connection failed - Connection refused")
        print("   Tally Prime may not be configured for XML access")
        return False
    except requests.exceptions.Timeout:
        print("❌ HTTP connection timed out")
        print("   Tally Prime may be running but not responding to HTTP requests")
        return False
    except Exception as e:
        print(f"❌ HTTP connection error: {e}")
        return False
    
    # Test 3: Test simple XML request
    print("\n3. Testing Simple XML Request...")
    simple_xml = """
    <ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>Test</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES />
          <TDL>
            <TDLMESSAGE>
              <COLLECTION NAME="Test">
                <TYPE>Company</TYPE>
                <FETCH>NAME</FETCH>
              </COLLECTION>
            </TDLMESSAGE>
          </TDL>
        </DESC>
      </BODY>
    </ENVELOPE>
    """
    
    try:
        headers = {'Content-Type': 'application/xml'}
        response = requests.post(
            "http://localhost:9000", 
            data=simple_xml.encode('utf-8'), 
            headers=headers,
            timeout=10
        )
        
        print(f"✅ XML request successful - Status: {response.status_code}")
        print(f"   Response length: {len(response.text)} characters")
        
        if response.text.strip():
            print("   Response preview:")
            print(f"   {response.text[:200]}...")
        else:
            print("   Empty response received")
            
    except requests.exceptions.Timeout:
        print("❌ XML request timed out")
        print("   This suggests Tally Prime is not properly configured for XML access")
        return False
    except Exception as e:
        print(f"❌ XML request error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ Connection test completed successfully!")
    return True

def check_tally_configuration():
    """Provide configuration guidance."""
    print("\n📋 Tally Prime Configuration Checklist:")
    print("=" * 50)
    print("1. ✅ Tally Prime is running")
    print("2. 🔧 Go to Gateway of Tally")
    print("3. 🔧 Press F12 (Configure)")
    print("4. 🔧 Go to Data Configuration")
    print("5. 🔧 Set 'Allow ODBC/XML Access' = Yes")
    print("6. 🔧 Set 'Port Number' = 9000")
    print("7. 🔧 Set 'Allow XML Access' = Yes")
    print("8. 🔧 Make sure a company is open/selected")
    print("9. 🔧 Ensure Tally is not in Data Entry mode")
    print("\n💡 Common Issues:")
    print("   - XML access not enabled in Data Configuration")
    print("   - Wrong port number (should be 9000)")
    print("   - No company open in Tally")
    print("   - Tally in Data Entry mode")
    print("   - Firewall blocking port 9000")

def main():
    """Main test function."""
    print("🧪 Tally Prime Connection Diagnostic")
    print("=" * 50)
    
    success = test_basic_connection()
    
    if not success:
        check_tally_configuration()
        print("\n🔧 After fixing configuration, run this test again:")
        print("   py -3.11 test_tally_connection.py")
    else:
        print("\n🎉 Tally Prime is properly configured!")
        print("   You can now run the full integration test:")
        print("   py -3.11 test_corrected_integration.py")

if __name__ == "__main__":
    main() 