#!/usr/bin/env python3
"""
Setup script for database integration
This script helps you configure the connection to your Supabase database
"""

import os
import requests
from dotenv import load_dotenv

def test_database_connection():
    """Test the database connection"""
    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials in .env file")
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
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Database connection successful!")
            print(f"📊 Found {len(data)} vessels in database")
            
            if data:
                print("\nSample vessels:")
                for vessel in data:
                    print(f"  - {vessel.get('name', 'Unknown')} (IMO: {vessel.get('imo', 'N/A')})")
            
            return True
        else:
            print(f"❌ Database connection failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        return False

def check_required_tables():
    """Check if required tables exist"""
    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials")
        return False
    
    required_tables = ['vessels', 'ports', 'companies', 'refineries']
    
    print("🔍 Checking required tables...")
    
    for table in required_tables:
        try:
            response = requests.get(
                f"{supabase_url}/rest/v1/{table}",
                headers={
                    "apikey": supabase_key,
                    "Authorization": f"Bearer {supabase_key}",
                    "Content-Type": "application/json"
                },
                params={"select": "id", "limit": 1}
            )
            
            if response.status_code == 200:
                print(f"✅ Table '{table}' exists")
            else:
                print(f"⚠️  Table '{table}' not accessible (status: {response.status_code})")
                
        except Exception as e:
            print(f"❌ Error checking table '{table}': {str(e)}")
    
    return True

def main():
    print("🚀 Database Integration Setup")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("\n📝 Please create a .env file with your Supabase credentials:")
        print("   Copy env_template.txt to .env and fill in your values")
        return
    
    print("✅ .env file found")
    
    # Test database connection
    print("\n🔌 Testing database connection...")
    if test_database_connection():
        print("\n🔍 Checking required tables...")
        check_required_tables()
        
        print("\n🎉 Setup complete! You can now run the enhanced app:")
        print("   python enhanced_app.py")
    else:
        print("\n❌ Setup failed. Please check your .env file and try again.")

if __name__ == "__main__":
    main()
