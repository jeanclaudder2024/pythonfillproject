#!/usr/bin/env python3
"""
Fix the .env file format
"""

import os

def fix_env_file():
    """Fix the .env file format"""
    print("Fixing .env file format")
    print("=" * 50)
    
    # Create a properly formatted .env file
    env_content = """# Supabase Configuration
SUPABASE_URL=https://ozjhdxvwqbzcvcywhwjg.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here

# Optional: OpenAI API Key
OPENAI_API_KEY=your-openai-api-key-here
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("SUCCESS: Created properly formatted .env file")
        print()
        print("Now you need to:")
        print("1. Edit the .env file")
        print("2. Replace 'your-anon-key-here' with your real Supabase anon key")
        print("3. Replace 'your-service-role-key-here' with your real service role key")
        print("4. Replace 'your-secret-key-here' with your real Flask secret key")
        print("5. Replace 'your-openai-api-key-here' with your real OpenAI key")
        print()
        print("The SUPABASE_URL is already correct!")
        
    except Exception as e:
        print(f"ERROR: Could not create .env file: {e}")

if __name__ == "__main__":
    fix_env_file()

