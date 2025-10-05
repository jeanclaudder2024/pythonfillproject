#!/usr/bin/env python3
"""
Test specific failing template to see detailed error
"""

import requests
import json

def test_failing_template():
    """Test the specific failing template"""
    print("Testing Failing Template...")
    print("=" * 50)
    
    # Test with the failing template
    template_id = "c11edba0-e499-46ef-ae32-07c2fef883bf"  # test2 template
    vessel_imo = "IMO1861018"
    
    print(f"Testing template ID: {template_id}")
    print(f"Vessel IMO: {vessel_imo}")
    
    try:
        # Prepare form data
        form_data = {
            'template_id': template_id,
            'vessel_imo': vessel_imo
        }
        
        # Create a dummy file for the template_file parameter
        dummy_file = ('dummy.docx', b'dummy content', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        files = {
            'template_file': dummy_file
        }
        
        print("Sending request to process-document...")
        
        response = requests.post(
            "http://localhost:8000/process-document",
            data=form_data,
            files=files,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS - Document processed!")
            print(f"Document ID: {result.get('document_id', 'N/A')}")
        else:
            print("FAIL - Document processing failed!")
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            print(f"Error: {error_data.get('message', 'Unknown error')}")
            print(f"Details: {error_data.get('error', 'No details')}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_failing_template()
