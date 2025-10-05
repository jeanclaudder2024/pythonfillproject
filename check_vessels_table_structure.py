#!/usr/bin/env python3
"""
Check the vessels table structure and data
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

def check_vessels_table():
    """Check vessels table structure and data"""
    print("Vessels Table Structure Check")
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
        
        # Check if vessels table exists and get its structure
        print("\n2. Checking vessels table structure...")
        try:
            # Try to get a few records to see the structure
            result = supabase.table("vessels").select("*").limit(3).execute()
            
            if result.data and len(result.data) > 0:
                print(f"SUCCESS: Found {len(result.data)} vessels in database")
                print(f"Table structure (columns):")
                
                # Get the first vessel to see all columns
                first_vessel = result.data[0]
                for column, value in first_vessel.items():
                    print(f"  - {column}: {type(value).__name__} = {value}")
                
                print(f"\n3. Testing with specific IMO...")
                vessel_imo = "IMO1861018"
                print(f"Searching for IMO: {vessel_imo}")
                
                # Try different possible column names for IMO
                imo_columns = ["imo", "IMO", "vessel_imo", "vessel_imo_number", "imo_number"]
                
                for imo_col in imo_columns:
                    try:
                        print(f"  Trying column '{imo_col}'...")
                        result = supabase.table("vessels").select("*").eq(imo_col, vessel_imo).execute()
                        if result.data and len(result.data) > 0:
                            print(f"  SUCCESS: Found vessel using column '{imo_col}'")
                            vessel = result.data[0]
                            print(f"  Vessel data: {vessel}")
                            return True
                        else:
                            print(f"  No vessel found with column '{imo_col}'")
                    except Exception as e:
                        print(f"  ERROR with column '{imo_col}': {e}")
                
                print(f"\n4. Showing all available vessels (first 5)...")
                all_vessels = supabase.table("vessels").select("*").limit(5).execute()
                if all_vessels.data:
                    for i, vessel in enumerate(all_vessels.data, 1):
                        print(f"  Vessel {i}:")
                        for key, value in vessel.items():
                            if 'imo' in key.lower() or 'name' in key.lower():
                                print(f"    {key}: {value}")
                else:
                    print("  No vessels found in database")
                
                return False
                
            else:
                print("WARNING: No vessels found in database")
                return False
                
        except Exception as e:
            print(f"ERROR: Cannot access vessels table: {e}")
            
            # Try to list all tables
            print("\n3. Trying to list available tables...")
            try:
                # This might not work with anon key, but let's try
                result = supabase.table("information_schema.tables").select("table_name").execute()
                if result.data:
                    print("Available tables:")
                    for table in result.data:
                        print(f"  - {table['table_name']}")
                else:
                    print("Cannot list tables (permission issue)")
            except Exception as e2:
                print(f"Cannot list tables: {e2}")
            
            return False
        
    except Exception as e:
        print(f"\nERROR: Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Vessels Table Structure Check")
    print("=" * 50)
    
    success = check_vessels_table()
    
    print("\n" + "=" * 50)
    if success:
        print("SUCCESS: Vessels table structure is correct!")
        print("The FastAPI service should be able to get real vessel data.")
    else:
        print("ISSUES FOUND:")
        print("1. Check if 'vessels' table exists")
        print("2. Check if IMO column name is correct")
        print("3. Check if vessel data exists in the table")
        print("4. Check database permissions")
