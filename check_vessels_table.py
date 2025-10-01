#!/usr/bin/env python3
"""
Script to check the vessels table structure in your Supabase database
"""

import os
import requests
from dotenv import load_dotenv

def check_vessels_table():
    """Check the structure of the vessels table"""
    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials in .env file")
        return
    
    try:
        # Try to fetch a few vessels to understand the structure
        response = requests.get(
            f"{supabase_url}/rest/v1/vessels",
            headers={
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json"
            },
            params={"select": "*", "limit": 1}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data:
                vessel = data[0]
                print("✅ Vessels table structure:")
                print("   Columns and types:")
                for key, value in vessel.items():
                    value_type = type(value).__name__
                    print(f"     {key}: {value_type}")
                
                # Check if id is integer or UUID
                if 'id' in vessel:
                    id_value = vessel['id']
                    id_type = type(id_value).__name__
                    print(f"\n🔍 ID column type: {id_type}")
                    print(f"   Sample ID value: {id_value}")
                    
                    if id_type == 'int':
                        print("   ✅ ID is integer - foreign key constraint should work")
                    elif id_type == 'str' and len(str(id_value)) > 10:
                        print("   ⚠️  ID appears to be UUID - need to change foreign key to UUID")
                    else:
                        print(f"   ❓ Unknown ID type: {id_type}")
            else:
                print("⚠️  No vessels found in database")
        else:
            print(f"❌ Error fetching vessels: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error checking vessels table: {e}")

def main():
    print("🔍 Checking Vessels Table Structure")
    print("=" * 40)
    check_vessels_table()
    
    print("\n📝 Next Steps:")
    print("1. If ID is integer: Migration should work as-is")
    print("2. If ID is UUID: Change vessel_id to UUID in migration")
    print("3. Run the migration after confirming the structure")

if __name__ == "__main__":
    main()
