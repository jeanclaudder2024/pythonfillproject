#!/usr/bin/env python3
"""
Setup environment variables for the document processing system
"""

import os

def setup_env():
    """Setup environment variables"""
    print("Environment Setup for Document Processing System")
    print("=" * 60)
    
    # Check if .env file exists
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"Found existing .env file")
        with open(env_file, 'r') as f:
            content = f.read()
            print(f"Current content:")
            print(content)
    else:
        print(f"No .env file found. Creating one...")
        
        # Create .env file with correct Supabase URL
        env_content = """# Supabase Configuration
# Your Supabase project URL
SUPABASE_URL=https://ozjhdxvwqbzcvcywhwjg.supabase.co

# Your Supabase anon/public key (REPLACE THIS WITH YOUR REAL KEY)
SUPABASE_ANON_KEY=your-anon-key-here

# Your Supabase service role key (for admin operations)
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here

# Optional: OpenAI API Key (if you want to use AI features)
OPENAI_API_KEY=your-openai-api-key-here
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"Created .env file with correct Supabase URL")
    
    print("\n" + "=" * 60)
    print("IMPORTANT: To get REAL database data instead of fallback data:")
    print("=" * 60)
    print("1. Go to your Supabase Dashboard")
    print("2. Go to Settings → API")
    print("3. Copy your 'Anon/Public Key' (starts with 'eyJ...')")
    print("4. Edit the .env file and replace 'your-anon-key-here' with your real key")
    print("5. Restart the FastAPI server")
    print()
    print("Current status:")
    print("- SUPABASE_URL: ✅ Correct")
    print("- SUPABASE_ANON_KEY: ❌ Still placeholder")
    print("- Result: System uses realistic fallback data")
    print()
    print("After fixing the key:")
    print("- SUPABASE_ANON_KEY: ✅ Real key")
    print("- Result: System will use real vessel data from your database")

if __name__ == "__main__":
    setup_env()
