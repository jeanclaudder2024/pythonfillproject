#!/usr/bin/env python3
"""
Simple test to verify the system is working
"""

import requests
import time

def test_system():
    """Test the system"""
    print("Testing Fixed Templates System")
    print("=" * 50)
    
    # Wait a moment for service to start
    time.sleep(2)
    
    try:
        # Test 1: Check if service is running
        print("1. Checking if service is running...")
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("SUCCESS: Service is running")
        else:
            print(f"FAILED: Service returned {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: Service not running - {e}")
        return False
    
    # Test 2: Get templates
    print("\n2. Getting available templates...")
    try:
        response = requests.get("http://localhost:8000/templates", timeout=5)
        if response.status_code == 200:
            templates = response.json()
            print(f"SUCCESS: Found {len(templates)} templates")
            for template in templates:
                print(f"  - {template['name']} (Active: {template['is_active']})")
        else:
            print(f"FAILED: Could not get templates - {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: Could not get templates - {e}")
        return False
    
    # Test 3: Process document
    print("\n3. Processing document...")
    try:
        form_data = {
            'template_id': 'icpo_template',
            'vessel_imo': 'IMO1861018'
        }
        dummy_file = ('dummy.docx', b'dummy content', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        files = {'template_file': dummy_file}
        
        response = requests.post("http://localhost:8000/process-document", data=form_data, files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                document_id = result['document_id']
                print(f"SUCCESS: Document processed")
                print(f"Document ID: {document_id}")
                
                # Test 4: Download
                print("\n4. Testing download...")
                download_response = requests.get(f"http://localhost:8000/download/{document_id}")
                if download_response.status_code == 200:
                    print(f"SUCCESS: Document downloaded")
                    print(f"File size: {len(download_response.content)} bytes")
                    return True
                else:
                    print(f"FAILED: Download failed - {download_response.status_code}")
                    return False
            else:
                print(f"FAILED: Processing failed - {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"FAILED: Processing failed - {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: Processing failed - {e}")
        return False

if __name__ == "__main__":
    print("Simple System Test")
    print("=" * 50)
    
    success = test_system()
    
    print("\n" + "=" * 50)
    if success:
        print("SUCCESS: System is working!")
        print("Your fixed templates system is ready to use.")
        print("\nTo connect to your database:")
        print("1. Create a .env file in the autofill folder")
        print("2. Add your Supabase credentials:")
        print("   SUPABASE_URL=https://your-project-id.supabase.co")
        print("   SUPABASE_ANON_KEY=your-anon-key-here")
        print("3. Restart the service")
    else:
        print("FAILED: System has issues")
        print("Check the errors above")