#!/usr/bin/env python3
"""
Test the fixed templates system
"""

import requests
import json

def test_fixed_templates():
    """Test the fixed templates system"""
    print("Testing Fixed Templates System")
    print("=" * 50)
    
    # Test 1: Get templates
    print("1. Testing /templates endpoint...")
    try:
        response = requests.get("http://localhost:8000/templates")
        if response.status_code == 200:
            templates = response.json()
            print(f"SUCCESS: Found {len(templates)} fixed templates")
            for template in templates:
                print(f"  - {template['name']} (ID: {template['id']})")
                print(f"    Placeholders: {len(template['placeholders'])}")
                print(f"    Active: {template['is_active']}")
        else:
            print(f"FAILED: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    
    # Test 2: Process document
    print("\n2. Testing /process-document endpoint...")
    try:
        # Use the first template
        template_id = templates[0]['id']
        vessel_imo = "IMO1861018"
        
        form_data = {
            'template_id': template_id,
            'vessel_imo': vessel_imo
        }
        dummy_file = ('dummy.docx', b'dummy content', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        files = {'template_file': dummy_file}
        
        response = requests.post("http://localhost:8000/process-document", data=form_data, files=files, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                document_id = result['document_id']
                print(f"SUCCESS: Document processed with ID: {document_id}")
                print(f"Template: {result.get('template_name', 'N/A')}")
                print(f"PDF Available: {result.get('pdf_available', False)}")
                
                # Test 3: Download
                print("\n3. Testing /download endpoint...")
                download_response = requests.get(f"http://localhost:8000/download/{document_id}")
                if download_response.status_code == 200:
                    print("SUCCESS: Download working")
                    print(f"Content Type: {download_response.headers.get('content-type', 'N/A')}")
                    print(f"Content Length: {download_response.headers.get('content-length', 'N/A')} bytes")
                    return True
                else:
                    print(f"FAILED: Download failed with status {download_response.status_code}")
                    return False
            else:
                print(f"FAILED: Processing failed - {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"FAILED: Processing failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_all_fixed_templates():
    """Test all fixed templates"""
    print("\nTesting All Fixed Templates")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8000/templates")
        if response.status_code != 200:
            print("Failed to get templates")
            return
        
        templates = response.json()
        print(f"Testing {len(templates)} fixed templates...")
        
        success_count = 0
        for i, template in enumerate(templates):
            template_id = template['id']
            template_name = template['name']
            placeholders = template['placeholders']
            
            print(f"\n{i+1}. Testing: {template_name}")
            print(f"   ID: {template_id}")
            print(f"   Placeholders: {len(placeholders)}")
            print(f"   Active: {template['is_active']}")
            
            if not template['is_active']:
                print(f"   SKIPPED: Template file not found")
                continue
            
            try:
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
                    result = response.json()
                    if result.get('success'):
                        print(f"   RESULT: SUCCESS - Document ID: {result.get('document_id', 'N/A')}")
                        success_count += 1
                    else:
                        print(f"   RESULT: FAILED - {result.get('message', 'Unknown error')}")
                else:
                    print(f"   RESULT: FAILED - HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   RESULT: ERROR - {e}")
        
        print(f"\nSUMMARY: {success_count}/{len(templates)} fixed templates processed successfully")
        
    except Exception as e:
        print(f"Error testing templates: {e}")

if __name__ == "__main__":
    print("Fixed Templates Test")
    print("=" * 50)
    
    # Test complete flow
    flow_success = test_fixed_templates()
    
    # Test all templates
    test_all_fixed_templates()
    
    print("\n" + "=" * 50)
    print("FINAL SUMMARY:")
    print("=" * 50)
    
    if flow_success:
        print("SUCCESS: Fixed templates system is working!")
        print("✅ Templates endpoint works")
        print("✅ Document processing works") 
        print("✅ Document download works")
        print("\nThis system is much more reliable than dynamic processing!")
    else:
        print("FAILED: Issues detected in the fixed templates system")
        print("❌ Check the errors above")
