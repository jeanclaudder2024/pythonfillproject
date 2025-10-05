#!/usr/bin/env python3
"""
Test complete flow: Upload template -> Process document -> Download
"""

import requests
import json
import time
from pathlib import Path

def test_complete_flow():
    """Test the complete document processing flow"""
    print("Testing Complete Document Processing Flow")
    print("=" * 60)
    
    # Step 1: Upload a template
    print("Step 1: Uploading template...")
    template_file_path = Path("template/ICPO TEMPLATE.docx")
    
    if not template_file_path.exists():
        print(f"ERROR: Template file not found: {template_file_path}")
        return False
    
    try:
        with open(template_file_path, "rb") as f:
            files = {
                "template_file": ("ICPO TEMPLATE.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            }
            data = {
                "name": "Complete Flow Test Template",
                "description": "Testing complete upload and processing flow"
            }
            
            response = requests.post("http://localhost:8000/upload-template", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    template_id = result['template']['id']
                    print(f"SUCCESS: Template uploaded with ID: {template_id}")
                    print(f"Placeholders found: {len(result['template']['placeholders'])}")
                else:
                    print(f"FAILED: Upload failed - {result.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"FAILED: Upload failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
    except Exception as e:
        print(f"ERROR: Upload failed - {e}")
        return False
    
    # Step 2: Process document
    print("\nStep 2: Processing document...")
    try:
        form_data = {
            'template_id': template_id,
            'vessel_imo': 'IMO1861018'
        }
        dummy_file = ('dummy.docx', b'dummy content', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        files = {'template_file': dummy_file}
        
        response = requests.post("http://localhost:8000/process-document", data=form_data, files=files, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                document_id = result['document_id']
                download_url = result['download_url']
                print(f"SUCCESS: Document processed with ID: {document_id}")
                print(f"Download URL: {download_url}")
            else:
                print(f"FAILED: Processing failed - {result.get('message', 'Unknown error')}")
                print(f"Error details: {result.get('error', 'No details')}")
                return False
        else:
            print(f"FAILED: Processing failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: Processing failed - {e}")
        return False
    
    # Step 3: Test download
    print("\nStep 3: Testing download...")
    try:
        response = requests.get(f"http://localhost:8000/download/{document_id}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            content_length = response.headers.get('content-length', '0')
            print(f"SUCCESS: Download working")
            print(f"Content Type: {content_type}")
            print(f"Content Length: {content_length} bytes")
            
            # Save the file to test
            output_file = Path("outputs") / f"test_download_{document_id}.pdf"
            output_file.parent.mkdir(exist_ok=True)
            
            with open(output_file, "wb") as f:
                f.write(response.content)
            
            print(f"File saved to: {output_file}")
            return True
        else:
            print(f"FAILED: Download failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: Download failed - {e}")
        return False

def test_all_templates():
    """Test processing with all available templates"""
    print("\nTesting All Available Templates")
    print("=" * 60)
    
    try:
        # Get all templates
        response = requests.get("http://localhost:8000/templates")
        if response.status_code != 200:
            print("Failed to get templates")
            return
        
        templates = response.json()
        print(f"Found {len(templates)} templates to test")
        
        success_count = 0
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
        
        print(f"\nSUMMARY: {success_count}/{len(templates)} templates processed successfully")
        
    except Exception as e:
        print(f"Error testing templates: {e}")

if __name__ == "__main__":
    print("Complete Flow Test")
    print("=" * 60)
    
    # Test complete flow
    flow_success = test_complete_flow()
    
    # Test all templates
    test_all_templates()
    
    print("\n" + "=" * 60)
    print("FINAL SUMMARY:")
    print("=" * 60)
    
    if flow_success:
        print("SUCCESS: Complete flow is working!")
        print("✅ Template upload works")
        print("✅ Document processing works") 
        print("✅ Document download works")
        print("\nYour React admin panel should now work correctly!")
    else:
        print("FAILED: Issues detected in the flow")
        print("❌ Check the errors above")
        print("\nTroubleshooting:")
        print("1. Make sure FastAPI service is running")
        print("2. Check template files are valid")
        print("3. Verify database connection")
        print("4. Check file permissions")
