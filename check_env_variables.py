#!/usr/bin/env python3
"""
Check environment variables without exposing sensitive data
"""

import os
from dotenv import load_dotenv

def check_env_variables():
    """Check environment variables"""
    print("Checking Environment Variables")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    FLASK_SECRET = os.getenv("FLASK_SECRET_KEY")
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")
    
    print(f"SUPABASE_URL: {SUPABASE_URL}")
    print(f"SUPABASE_KEY: {'Found' if SUPABASE_KEY else 'Not found'} (Length: {len(SUPABASE_KEY) if SUPABASE_KEY else 0})")
    print(f"SUPABASE_SERVICE_KEY: {'Found' if SUPABASE_SERVICE_KEY else 'Not found'}")
    print(f"FLASK_SECRET: {'Found' if FLASK_SECRET else 'Not found'}")
    print(f"OPENAI_KEY: {'Found' if OPENAI_KEY else 'Not found'}")
    
    # Check if URL looks correct
    if SUPABASE_URL:
        if SUPABASE_URL.startswith("https://") and "supabase.co" in SUPABASE_URL:
            print(f"\nSUPABASE_URL format: CORRECT")
        else:
            print(f"\nSUPABASE_URL format: INCORRECT")
            print("Should be: https://your-project-id.supabase.co")
    
    # Check if key looks correct
    if SUPABASE_KEY:
        if SUPABASE_KEY.startswith("eyJ"):
            print(f"SUPABASE_KEY format: CORRECT (JWT token)")
        else:
            print(f"SUPABASE_KEY format: INCORRECT")
            print("Should start with 'eyJ' (JWT token)")
    
    print(f"\nAll credentials found: {all([SUPABASE_URL, SUPABASE_KEY])}")

if __name__ == "__main__":
    check_env_variables()

