#!/usr/bin/env python3
"""
Test script to verify deployment works
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    try:
        import fastapi
        print("OK: FastAPI imported successfully")
        
        import uvicorn
        print("OK: Uvicorn imported successfully")
        
        import main
        print("OK: main.py imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_app_creation():
    """Test that the FastAPI app can be created"""
    try:
        from main import app
        print("OK: FastAPI app created successfully")
        return True
    except Exception as e:
        print(f"❌ App creation error: {e}")
        return False

if __name__ == "__main__":
    print("Testing deployment...")
    
    success = True
    success &= test_imports()
    success &= test_app_creation()
    
    if success:
        print("\nSUCCESS: All tests passed! Ready for deployment!")
        sys.exit(0)
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)
