#!/usr/bin/env python3
"""
Detailed test to check database connection and vessel data
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
import requests

def test_database_detailed():
    """Test database connection in detail"""
    print("Detailed Database Connection Test")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
    
    print(f"SUPABASE_URL: {SUPABASE_URL}")
    print(f"SUPABASE_KEY: {SUPABASE_KEY[:20]}..." if SUPABASE_KEY else "SUPABASE_KEY: Not found")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("\nERROR: Supabase credentials not found!")
        return False
    
    try:
        # Try to connect
        print("\n1. Testing Supabase connection...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("SUCCESS: Connected to Supabase!")
        
        # Test different table names
        print("\n2. Testing vessel table queries...")
        
        # Try different possible table names
        table_names = ["vessels", "vessel", "ships", "ship"]
        
        for table_name in table_names:
            try:
                print(f"   Testing table: {table_name}")
                result = supabase.table(table_name).select("*").limit(1).execute()
                
                if result.data:
                    print(f"   SUCCESS: Found {len(result.data)} records in {table_name}")
                    vessel = result.data[0]
                    print(f"   Sample vessel: {vessel.get('name', 'Unknown')} (IMO: {vessel.get('imo', 'Unknown')})")
                    
                    # Show all available fields
                    print(f"   Available fields: {list(vessel.keys())}")
                    return True
                else:
                    print(f"   INFO: Table {table_name} exists but is empty")
                    
            except Exception as e:
                print(f"   ERROR: Table {table_name} not found or error: {e}")
        
        print("\n3. Testing with specific IMO...")
        # Test with a specific IMO
        test_imo = "IMO1861018"
        for table_name in table_names:
            try:
                result = supabase.table(table_name).select("*").eq("imo", test_imo).execute()
                if result.data:
                    print(f"   SUCCESS: Found vessel {test_imo} in {table_name}")
                    vessel = result.data[0]
                    print(f"   Vessel data: {vessel}")
                    return True
            except Exception as e:
                print(f"   ERROR: Could not query {table_name} for IMO {test_imo}: {e}")
        
        return False
        
    except Exception as e:
        print(f"\nERROR: Failed to connect to database: {e}")
        return False

def test_fastapi_with_database():
    """Test the FastAPI service with database connection"""
    print("\n" + "=" * 60)
    print("Testing FastAPI Service with Database")
    print("=" * 60)
    
    try:
        # Test process-document with database connection
        form_data = {
            'template_id': 'icpo_template',
            'vessel_imo': 'IMO1861018'
        }
        dummy_file = ('dummy.docx', b'dummy content', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        files = {'template_file': dummy_file}
        
        print("Sending request to FastAPI service...")
        response = requests.post("http://localhost:8000/process-document", data=form_data, files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("SUCCESS: FastAPI service processed document")
                print(f"Document ID: {result['document_id']}")
                return True
            else:
                print(f"FAILED: FastAPI processing failed - {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"FAILED: FastAPI request failed - {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: FastAPI test failed - {e}")
        return False

if __name__ == "__main__":
    print("Database Connection and FastAPI Test")
    print("=" * 60)
    
    # Test database connection
    db_success = test_database_detailed()
    
    # Test FastAPI service
    api_success = test_fastapi_with_database()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print("=" * 60)
    
    if db_success:
        print("SUCCESS: Database connection is working!")
        print("Your system can get real vessel data from the database.")
    else:
        print("FAILED: Database connection is not working.")
        print("Check your Supabase credentials and table names.")
    
    if api_success:
        print("SUCCESS: FastAPI service is working!")
        print("Document processing is working correctly.")
    else:
        print("FAILED: FastAPI service has issues.")
        print("Check if the service is running and accessible.")
    
    if db_success and api_success:
        print("\nPERFECT: Both database and FastAPI are working!")
        print("Your system should now use real database data.")
    elif api_success:
        print("\nPARTIAL: FastAPI works but database connection failed.")
        print("System will use realistic fallback data.")
    else:
        print("\nISSUES: Both database and FastAPI have problems.")
        print("Check the errors above.")

