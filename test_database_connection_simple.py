#!/usr/bin/env python3
"""
Simple test to check database connection
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

def test_database_connection():
    """Test database connection"""
    print("Testing Database Connection")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
    
    print(f"SUPABASE_URL: {SUPABASE_URL}")
    print(f"SUPABASE_KEY: {SUPABASE_KEY[:20]}..." if SUPABASE_KEY else "SUPABASE_KEY: Not found")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("\nERROR: Supabase credentials not found!")
        print("Please edit the .env file and add your Supabase credentials:")
        print("SUPABASE_URL=https://your-project-id.supabase.co")
        print("SUPABASE_ANON_KEY=your-anon-key-here")
        return False
    
    try:
        # Try to connect
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("\nSUCCESS: Connected to Supabase!")
        
        # Test query
        print("\nTesting vessel query...")
        result = supabase.table("vessels").select("*").limit(1).execute()
        
        if result.data:
            print(f"SUCCESS: Found {len(result.data)} vessels in database")
            vessel = result.data[0]
            print(f"Sample vessel: {vessel.get('name', 'Unknown')} (IMO: {vessel.get('imo', 'Unknown')})")
            return True
        else:
            print("WARNING: No vessels found in database")
            return True
            
    except Exception as e:
        print(f"\nERROR: Failed to connect to database: {e}")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    
    if success:
        print("\n" + "=" * 50)
        print("SUCCESS: Database connection is working!")
        print("Your system can now get real vessel data from the database.")
    else:
        print("\n" + "=" * 50)
        print("FAILED: Database connection is not working.")
        print("Please check your Supabase credentials in the .env file.")

