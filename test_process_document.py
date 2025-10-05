#!/usr/bin/env python3
"""
Test script to debug process-document endpoint 500 error
"""

import requests
import json

def test_process_document():
    """Test the process-document endpoint"""
    print("Testing Process Document Endpoint...")
    print("=" * 50)
    
    # First, get available templates
    print("1. Getting available templates...")
    try:
        response = requests.get("http://localhost:8000/templates")
        if response.status_code == 200:
            templates = response.json()
            print(f"Found {len(templates)} templates")
            
            if not templates:
                print("No templates available for testing")
                return False
            
            # Use the first template
            template = templates[0]
            template_id = template['id']
            template_name = template.get('name', 'Unknown')
            print(f"Using template: {template_name} (ID: {template_id})")
            
        else:
            print(f"Failed to get templates: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error getting templates: {e}")
        return False
    
    # Test process-document endpoint
    print("\n2. Testing process-document endpoint...")
    try:
        # Prepare form data
        form_data = {
            'template_id': template_id,
            'vessel_imo': 'IMO1861018'
        }
        
        # Create a dummy file for the template_file parameter (even though we don't use it)
        dummy_file = ('dummy.docx', b'dummy content', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        files = {
            'template_file': dummy_file
        }
        
        print(f"Sending request to process-document...")
        print(f"Template ID: {template_id}")
        print(f"Vessel IMO: IMO1861018")
        
        response = requests.post(
            "http://localhost:8000/process-document",
            data=form_data,
            files=files,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS - Document processed!")
            print(f"Document ID: {result.get('document_id', 'N/A')}")
            print(f"Download URL: {result.get('download_url', 'N/A')}")
            return True
        else:
            print("FAIL - Document processing failed!")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"FAIL - Process document test failed: {e}")
        return False

def test_with_different_templates():
    """Test with different templates to see which ones work"""
    print("\nTesting with Different Templates...")
    print("=" * 50)
    
    try:
        # Get all templates
        response = requests.get("http://localhost:8000/templates")
        if response.status_code != 200:
            print("Failed to get templates")
            return
        
        templates = response.json()
        print(f"Testing {len(templates)} templates...")
        
        for i, template in enumerate(templates):
            template_id = template['id']
            template_name = template.get('name', f'Template {i+1}')
            placeholders = template.get('placeholders', [])
            
            print(f"\n{i+1}. Testing: {template_name}")
            print(f"   ID: {template_id}")
            print(f"   Placeholders: {len(placeholders)}")
            
            try:
                # Test process-document
                form_data = {
                    'template_id': template_id,
                    'vessel_imo': 'IMO1861018'
                }
                dummy_file = ('dummy.docx', b'dummy content', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                files = {'template_file': dummy_file}
                
                response = requests.post(
                    "http://localhost:8000/process-document",
                    data=form_data,
                    files=files,
                    timeout=30
                )
                
                if response.status_code == 200:
                    print(f"   RESULT: SUCCESS")
                else:
                    print(f"   RESULT: FAILED ({response.status_code})")
                    print(f"   ERROR: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"   RESULT: ERROR - {e}")
                
    except Exception as e:
        print(f"Error testing templates: {e}")

if __name__ == "__main__":
    print("Process Document Debug Test")
    print("=" * 50)
    
    # Test single template
    success = test_process_document()
    
    # Test all templates
    test_with_different_templates()
    
    print("\n" + "=" * 50)
    print("DEBUG SUMMARY:")
    print("=" * 50)
    
    if success:
        print("SUCCESS - Process document is working!")
    else:
        print("FAIL - Process document has issues.")
        print("\nCommon causes of 500 errors:")
        print("1. Template file not found in database/storage")
        print("2. Missing dependencies (python-docx, docx2pdf)")
        print("3. File permission issues")
        print("4. Memory issues with large files")
        print("5. Database connection problems")
