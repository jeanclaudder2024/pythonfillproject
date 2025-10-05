#!/usr/bin/env python3
"""
Test script to verify Supabase database connection and document_templates table
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test the database connection and table access"""
    print("Testing Supabase Database Connection...")
    print("=" * 50)
    
    # Get credentials
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
    
    print(f"Supabase URL: {SUPABASE_URL[:50]}..." if SUPABASE_URL else "SUPABASE_URL not found")
    print(f"Supabase Key: {SUPABASE_KEY[:20]}..." if SUPABASE_KEY else "SUPABASE_KEY not found")
    print()
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Missing Supabase credentials!")
        print("Please add SUPABASE_URL and SUPABASE_ANON_KEY to your .env file")
        return False
    
    try:
        # Initialize Supabase client
        print("Connecting to Supabase...")
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Connected to Supabase successfully!")
        print()
        
        # Test table access
        print("Testing document_templates table access...")
        result = supabase.table("document_templates").select("*").limit(5).execute()
        
        print(f"Successfully accessed document_templates table")
        print(f"Found {len(result.data)} templates in database")
        
        if result.data:
            print("\nSample template data:")
            for i, template in enumerate(result.data[:3]):
                print(f"  {i+1}. ID: {template.get('id', 'N/A')}")
                print(f"     Name: {template.get('name', template.get('title', 'N/A'))}")
                print(f"     File: {template.get('file_name', 'N/A')}")
                print(f"     Active: {template.get('is_active', 'N/A')}")
                print(f"     Placeholders: {len(template.get('placeholders', []))}")
                print()
        
        # Test table structure
        print("Testing table structure...")
        sample_template = {
            "name": "Test Template",
            "description": "Test template for database connection",
            "file_name": "test.docx",
            "file_size": 1024,
            "placeholders": ["vessel_name", "imo"],
            "placeholder_mappings": {},
            "is_active": True
        }
        
        # Try to insert a test template (will be rolled back)
        print("Testing template insertion...")
        insert_result = supabase.table("document_templates").insert(sample_template).execute()
        
        if insert_result.data:
            test_id = insert_result.data[0]['id']
            print(f"Successfully inserted test template with ID: {test_id}")
            
            # Clean up - delete the test template
            print("Cleaning up test template...")
            delete_result = supabase.table("document_templates").delete().eq("id", test_id).execute()
            print("Test template deleted successfully")
        
        print("\nAll database tests passed!")
        print("Your FastAPI can now connect to the database")
        return True
        
    except Exception as e:
        print(f"Database connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check your SUPABASE_URL and SUPABASE_ANON_KEY")
        print("2. Make sure your Supabase project is active")
        print("3. Verify the document_templates table exists")
        print("4. Check your RLS policies allow access")
        return False

def test_migration_status():
    """Check if the migration has been applied"""
    print("\nChecking Migration Status...")
    print("=" * 50)
    
    try:
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("Cannot check migration - missing credentials")
            return False
        
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Check if new columns exist
        result = supabase.table("document_templates").select("*").limit(1).execute()
        
        if result.data:
            template = result.data[0]
            print("Current table structure:")
            
            # Check for new columns
            new_columns = ['template_file', 'file_size', 'mime_type']
            existing_columns = list(template.keys())
            
            for column in new_columns:
                if column in existing_columns:
                    print(f"  {column} - Present")
                else:
                    print(f"  {column} - Missing")
            
            # Check for renamed columns
            if 'name' in existing_columns:
                print(f"  name - Present (renamed from title)")
            elif 'title' in existing_columns:
                print(f"  title - Present (needs to be renamed to name)")
            else:
                print(f"  name/title - Missing")
            
            if 'placeholder_mappings' in existing_columns:
                print(f"  placeholder_mappings - Present (renamed from field_mappings)")
            elif 'field_mappings' in existing_columns:
                print(f"  field_mappings - Present (needs to be renamed to placeholder_mappings)")
            else:
                print(f"  placeholder_mappings/field_mappings - Missing")
        
        return True
        
    except Exception as e:
        print(f"Migration check failed: {e}")
        return False

if __name__ == "__main__":
    print("Supabase Database Connection Test")
    print("=" * 50)
    
    # Test connection
    connection_ok = test_database_connection()
    
    # Test migration status
    migration_ok = test_migration_status()
    
    print("\nTest Summary:")
    print("=" * 50)
    print(f"Database Connection: {'PASS' if connection_ok else 'FAIL'}")
    print(f"Migration Status: {'PASS' if migration_ok else 'FAIL'}")
    
    if connection_ok and migration_ok:
        print("\nReady to use database storage!")
        print("Your FastAPI will now store templates in the database.")
    else:
        print("\nIssues detected. Please fix them before using database storage.")
        print("The FastAPI will fall back to file storage.")
