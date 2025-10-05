#!/usr/bin/env python3
"""
Test script to debug template upload issues
"""

import requests
import os
from pathlib import Path

def test_template_upload():
    """Test template upload functionality"""
    print("Testing Template Upload...")
    print("=" * 50)
    
    # Check if we have a test template file
    test_template_path = Path("template/ICPO TEMPLATE.docx")
    
    if not test_template_path.exists():
        print(f"Test template not found: {test_template_path}")
        print("Available templates:")
        template_dir = Path("template")
        if template_dir.exists():
            for file in template_dir.glob("*.docx"):
                print(f"  - {file}")
        return False
    
    print(f"Using test template: {test_template_path}")
    
    # Prepare the upload data
    url = "http://localhost:8000/upload-template"
    
    with open(test_template_path, "rb") as f:
        files = {
            "template_file": ("test_template.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        }
        data = {
            "name": "Test Upload Template",
            "description": "Testing template upload functionality"
        }
        
        print("Sending upload request...")
        try:
            response = requests.post(url, files=files, data=data)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Content: {response.text}")
            
            if response.status_code == 200:
                print("Upload successful!")
                result = response.json()
                print(f"Template ID: {result.get('template', {}).get('id', 'N/A')}")
                return True
            else:
                print("Upload failed!")
                return False
                
        except Exception as e:
            print(f"Request failed: {e}")
            return False

def test_templates_endpoint():
    """Test templates endpoint"""
    print("\nTesting Templates Endpoint...")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8000/templates")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            templates = response.json()
            print(f"Found {len(templates)} templates")
            
            for i, template in enumerate(templates[:3]):
                print(f"  {i+1}. {template.get('name', 'N/A')} - {template.get('file_name', 'N/A')}")
            
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Request failed: {e}")
        return False

def test_health_endpoint():
    """Test health endpoint"""
    print("\nTesting Health Endpoint...")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Request failed: {e}")
        return False

if __name__ == "__main__":
    print("Template Upload Debug Test")
    print("=" * 50)
    
    # Test health
    health_ok = test_health_endpoint()
    
    # Test templates endpoint
    templates_ok = test_templates_endpoint()
    
    # Test upload
    upload_ok = test_template_upload()
    
    print("\nTest Summary:")
    print("=" * 50)
    print(f"Health Endpoint: {'PASS' if health_ok else 'FAIL'}")
    print(f"Templates Endpoint: {'PASS' if templates_ok else 'FAIL'}")
    print(f"Upload Test: {'PASS' if upload_ok else 'FAIL'}")
    
    if not upload_ok:
        print("\nTroubleshooting Tips:")
        print("1. Check if FastAPI service is running")
        print("2. Check server logs for error messages")
        print("3. Verify template file format (.docx)")
        print("4. Check file permissions")
        print("5. Verify database connection (if using database storage)")
