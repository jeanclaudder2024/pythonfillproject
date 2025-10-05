#!/usr/bin/env python3
"""
Test database columns to see what the actual column names are
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

def test_database_columns():
    """Test database columns"""
    print("Database Columns Test")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
    
    print(f"SUPABASE_URL: {SUPABASE_URL}")
    print(f"SUPABASE_KEY: {SUPABASE_KEY[:20]}..." if SUPABASE_KEY else "SUPABASE_KEY: Not found")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("ERROR: Supabase credentials not found!")
        print("Please update the SUPABASE_ANON_KEY in the .env file")
        return False
    
    try:
        # Try to connect
        print("\n1. Testing Supabase connection...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("SUCCESS: Connected to Supabase!")
        
        # Check vessels table
        print("\n2. Checking vessels table...")
        try:
            # Get a few records to see the structure
            result = supabase.table("vessels").select("*").limit(1).execute()
            
            if result.data and len(result.data) > 0:
                vessel = result.data[0]
                print(f"SUCCESS: Found vessels table")
                print(f"Columns in vessels table:")
                
                for column, value in vessel.items():
                    print(f"  - {column}: {type(value).__name__} = {value}")
                
                # Check for IMO-related columns
                print(f"\n3. Looking for IMO-related columns...")
                imo_columns = []
                for column in vessel.keys():
                    if 'imo' in column.lower():
                        imo_columns.append(column)
                
                if imo_columns:
                    print(f"Found IMO columns: {imo_columns}")
                    
                    # Test with the first IMO column
                    imo_col = imo_columns[0]
                    print(f"\n4. Testing with column '{imo_col}'...")
                    
                    # Get a sample IMO value
                    sample_imo = vessel.get(imo_col)
                    if sample_imo:
                        print(f"Sample IMO value: {sample_imo}")
                        
                        # Test query with this column
                        test_result = supabase.table("vessels").select("*").eq(imo_col, sample_imo).execute()
                        if test_result.data:
                            print(f"SUCCESS: Query works with column '{imo_col}'")
                            print(f"Found {len(test_result.data)} vessel(s)")
                            return True
                        else:
                            print(f"WARNING: No results with column '{imo_col}'")
                    else:
                        print(f"WARNING: No IMO value found in column '{imo_col}'")
                else:
                    print(f"WARNING: No IMO-related columns found")
                    print(f"Available columns: {list(vessel.keys())}")
                
                return False
                
            else:
                print("WARNING: No vessels found in database")
                return False
                
        except Exception as e:
            print(f"ERROR: Cannot access vessels table: {e}")
            return False
        
    except Exception as e:
        print(f"\nERROR: Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Database Columns Test")
    print("=" * 50)
    
    success = test_database_columns()
    
    print("\n" + "=" * 50)
    if success:
        print("SUCCESS: Database columns are correct!")
        print("The FastAPI service should be able to get real vessel data.")
    else:
        print("ISSUES FOUND:")
        print("1. Check if SUPABASE_ANON_KEY is correct")
        print("2. Check if 'vessels' table exists")
        print("3. Check if IMO column name is correct")
        print("4. Check if vessel data exists in the table")
        print("5. Check database permissions")
