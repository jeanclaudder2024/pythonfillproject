#!/usr/bin/env python3
"""
Debug the database query to see what's happening
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

def debug_database_query():
    """Debug the database query"""
    print("Debugging Database Query")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
    
    print(f"SUPABASE_URL: {SUPABASE_URL}")
    print(f"SUPABASE_KEY: {SUPABASE_KEY[:20]}..." if SUPABASE_KEY else "SUPABASE_KEY: Not found")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("ERROR: Supabase credentials not found!")
        return False
    
    try:
        # Try to connect
        print("\n1. Testing Supabase connection...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("SUCCESS: Connected to Supabase!")
        
        # Test with the exact same query as in the FastAPI service
        print("\n2. Testing vessel query (same as FastAPI)...")
        vessel_imo = "IMO1861018"
        
        print(f"Querying for IMO: {vessel_imo}")
        result = supabase.table("vessels").select("*").eq("imo", vessel_imo).execute()
        
        print(f"Query result: {result}")
        print(f"Result data: {result.data}")
        print(f"Result count: {result.count}")
        
        if result.data and len(result.data) > 0:
            vessel = result.data[0]
            print(f"\nSUCCESS: Found vessel in database!")
            print(f"Vessel data: {vessel}")
            print(f"Available fields: {list(vessel.keys())}")
            
            # Show the mapping that would happen in FastAPI
            print(f"\n3. Testing data mapping (same as FastAPI)...")
            mapped_data = {
                "vessel_name": vessel.get('name', f"Vessel {vessel_imo}"),
                "imo": vessel_imo,
                "vessel_type": vessel.get('vessel_type', vessel.get('type', 'Cargo Vessel')),
                "flag": vessel.get('flag', vessel.get('flag_state', 'Panama')),
                "owner": vessel.get('owner', vessel.get('vessel_owner', 'Shipping Company')),
            }
            
            print(f"Mapped data: {mapped_data}")
            return True
        else:
            print(f"\nWARNING: No vessel found for IMO: {vessel_imo}")
            
            # Try to see what vessels exist
            print(f"\n4. Checking what vessels exist...")
            all_vessels = supabase.table("vessels").select("imo, name").limit(5).execute()
            if all_vessels.data:
                print(f"Found {len(all_vessels.data)} vessels:")
                for v in all_vessels.data:
                    print(f"  - {v.get('name', 'Unknown')} (IMO: {v.get('imo', 'Unknown')})")
            else:
                print("No vessels found in database")
            
            return False
        
    except Exception as e:
        print(f"\nERROR: Database query failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Database Query Debug")
    print("=" * 50)
    
    success = debug_database_query()
    
    print("\n" + "=" * 50)
    if success:
        print("SUCCESS: Database query is working!")
        print("The FastAPI service should be able to get real vessel data.")
    else:
        print("FAILED: Database query is not working.")
        print("Check the errors above.")
        print("\nPossible issues:")
        print("1. SUPABASE_KEY is still placeholder")
        print("2. Vessel IMO not found in database")
        print("3. Table name is wrong")
        print("4. Database permissions issue")

