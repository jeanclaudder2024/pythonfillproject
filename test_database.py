#!/usr/bin/env python3
"""
Simple test script for database integration
"""

import os
import requests
from dotenv import load_dotenv

def test_database_connection():
    """Test the database connection"""
    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    print("Testing database connection...")
    print(f"Supabase URL: {supabase_url}")
    print(f"Supabase Key: {'*' * 20 if supabase_key else 'NOT SET'}")
    
    if not supabase_url or not supabase_key:
        print("ERROR: Missing Supabase credentials in .env file")
        return False
    
    try:
        # Test connection by fetching vessels
        response = requests.get(
            f"{supabase_url}/rest/v1/vessels",
            headers={
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json"
            },
            params={"select": "id,name,imo", "limit": 5}
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Database connection successful!")
            print(f"Found {len(data)} vessels in database")
            
            if data:
                print("\nSample vessels:")
                for vessel in data:
                    print(f"  - {vessel.get('name', 'Unknown')} (IMO: {vessel.get('imo', 'N/A')})")
            
            return True
        else:
            print(f"ERROR: Database connection failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: Database connection error: {str(e)}")
        return False

def main():
    print("Database Integration Test")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("ERROR: .env file not found!")
        print("Please create a .env file with your Supabase credentials")
        return
    
    print("SUCCESS: .env file found")
    
    # Test database connection
    if test_database_connection():
        print("\nSUCCESS: Setup complete! You can now run the enhanced app:")
        print("   python enhanced_app.py")
    else:
        print("\nERROR: Setup failed. Please check your .env file and try again.")

if __name__ == "__main__":
    main()
