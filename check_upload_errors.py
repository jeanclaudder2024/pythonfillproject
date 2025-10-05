#!/usr/bin/env python3
"""
Check for upload errors and debug issues
"""

import requests
import json
from pathlib import Path

def check_api_status():
    """Check if API is responding"""
    print("Checking API Status...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("OK - API is running and healthy")
            return True
        else:
            print(f"FAIL - API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("FAIL - Cannot connect to API - is it running?")
        return False
    except Exception as e:
        print(f"FAIL - API check failed: {e}")
        return False

def check_templates_endpoint():
    """Check templates endpoint"""
    print("\nChecking Templates Endpoint...")
    try:
        response = requests.get("http://localhost:8000/templates", timeout=10)
        if response.status_code == 200:
            templates = response.json()
            print(f"OK - Templates endpoint working - found {len(templates)} templates")
            return True
        else:
            print(f"FAIL - Templates endpoint failed - status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"FAIL - Templates endpoint error: {e}")
        return False

def test_upload_with_different_files():
    """Test upload with different file types"""
    print("\nTesting Upload with Different Files...")
    
    # Find available template files
    template_dir = Path("template")
    if not template_dir.exists():
        print("FAIL - No template directory found")
        return False
    
    template_files = list(template_dir.glob("*.docx"))
    if not template_files:
        print("FAIL - No .docx files found in template directory")
        return False
    
    print(f"Found {len(template_files)} template files:")
    for file in template_files:
        print(f"  - {file.name} ({file.stat().st_size} bytes)")
    
    # Test upload with first file
    test_file = template_files[0]
    print(f"\nTesting upload with: {test_file.name}")
    
    try:
        with open(test_file, "rb") as f:
            files = {
                "template_file": (test_file.name, f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            }
            data = {
                "name": f"Test Upload - {test_file.stem}",
                "description": f"Testing upload with {test_file.name}"
            }
            
            response = requests.post("http://localhost:8000/upload-template", files=files, data=data, timeout=30)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print("OK - Upload successful!")
                print(f"Template ID: {result.get('template', {}).get('id', 'N/A')}")
                print(f"Placeholders found: {len(result.get('template', {}).get('placeholders', []))}")
                return True
            else:
                print("FAIL - Upload failed!")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"FAIL - Upload test failed: {e}")
        return False

def check_file_permissions():
    """Check file permissions and accessibility"""
    print("\nChecking File Permissions...")
    
    template_dir = Path("template")
    if not template_dir.exists():
        print("FAIL - Template directory does not exist")
        return False
    
    if not template_dir.is_dir():
        print("FAIL - Template path is not a directory")
        return False
    
    print("OK - Template directory exists and is accessible")
    
    # Check if we can read files
    template_files = list(template_dir.glob("*.docx"))
    if template_files:
        test_file = template_files[0]
        try:
            with open(test_file, "rb") as f:
                content = f.read(100)  # Read first 100 bytes
                print(f"OK - Can read template files (tested: {test_file.name})")
                return True
        except Exception as e:
            print(f"FAIL - Cannot read template file: {e}")
            return False
    else:
        print("FAIL - No template files found")
        return False

def check_database_connection():
    """Check if database connection is working"""
    print("\nChecking Database Connection...")
    
    try:
        # Try to get templates to see if database is accessible
        response = requests.get("http://localhost:8000/templates", timeout=10)
        if response.status_code == 200:
            templates = response.json()
            if templates:
                # Check if templates have database-like structure
                first_template = templates[0]
                if 'id' in first_template and 'created_at' in first_template:
                    print("OK - Database connection appears to be working")
                    return True
                else:
                    print("WARNING - Templates found but may be from file storage")
                    return True
            else:
                print("WARNING - No templates found - database may be empty")
                return True
        else:
            print(f"FAIL - Cannot access templates - status {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL - Database check failed: {e}")
        return False

if __name__ == "__main__":
    print("Template Upload Error Debug Tool")
    print("=" * 50)
    
    # Run all checks
    api_ok = check_api_status()
    templates_ok = check_templates_endpoint()
    permissions_ok = check_file_permissions()
    database_ok = check_database_connection()
    upload_ok = test_upload_with_different_files()
    
    print("\n" + "=" * 50)
    print("DEBUG SUMMARY:")
    print("=" * 50)
    print(f"API Status: {'OK' if api_ok else 'FAIL'}")
    print(f"Templates Endpoint: {'OK' if templates_ok else 'FAIL'}")
    print(f"File Permissions: {'OK' if permissions_ok else 'FAIL'}")
    print(f"Database Connection: {'OK' if database_ok else 'FAIL'}")
    print(f"Upload Test: {'OK' if upload_ok else 'FAIL'}")
    
    if all([api_ok, templates_ok, permissions_ok, upload_ok]):
        print("\nSUCCESS - All tests passed! Upload should be working.")
        print("If you're still having issues, check:")
        print("1. Browser console for JavaScript errors")
        print("2. Network tab for failed requests")
        print("3. CORS settings")
    else:
        print("\nWARNING - Some tests failed. Check the errors above.")
        print("Common solutions:")
        print("1. Make sure FastAPI service is running")
        print("2. Check file permissions")
        print("3. Verify template files are valid .docx files")
        print("4. Check database connection")
