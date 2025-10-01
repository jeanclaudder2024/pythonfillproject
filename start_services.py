#!/usr/bin/env python3
"""
Service startup script for the advanced document processing system
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed"""
    try:
        import fastapi
        import uvicorn
        import supabase
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_environment():
    """Check if environment variables are set"""
    required_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        return False
    
    print("✅ Environment variables are configured")
    return True

def start_fastapi_service():
    """Start the FastAPI service"""
    print("🚀 Starting FastAPI Document Processing Service...")
    print("📍 Service will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("\n" + "="*60)
    
    try:
        # Start the FastAPI service
        subprocess.run([
            sys.executable, "fastapi_service.py"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Service stopped by user")
    except Exception as e:
        print(f"❌ Error starting service: {e}")

def main():
    print("🔧 Advanced Document Processing System")
    print("="*50)
    
    # Check requirements
    if not check_requirements():
        return
    
    # Check environment
    if not check_environment():
        return
    
    # Create necessary directories
    Path("outputs").mkdir(exist_ok=True)
    Path("uploads").mkdir(exist_ok=True)
    
    print("✅ System checks passed")
    print("\n🎯 Starting services...")
    
    # Start the FastAPI service
    start_fastapi_service()

if __name__ == "__main__":
    main()
