#!/usr/bin/env python3
"""
Test script for the FastAPI service
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   Database: {data.get('database')}")
            print(f"   Processor: {data.get('processor')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Root endpoint working")
            print(f"   Message: {data.get('message')}")
            print(f"   Version: {data.get('version')}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False

def test_templates_endpoint():
    """Test the templates endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/templates")
        if response.status_code == 200:
            data = response.json()
            print("✅ Templates endpoint working")
            print(f"   Found {len(data)} templates")
            return True
        else:
            print(f"❌ Templates endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Templates endpoint error: {e}")
        return False

def test_vessels_endpoint():
    """Test the vessels endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/vessels")
        if response.status_code == 200:
            data = response.json()
            print("✅ Vessels endpoint working")
            print(f"   Found {len(data)} vessels")
            if data:
                print(f"   Sample vessel: {data[0].get('name')} (IMO: {data[0].get('imo')})")
            return True
        else:
            print(f"❌ Vessels endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Vessels endpoint error: {e}")
        return False

def main():
    print("Testing FastAPI Document Processing Service")
    print("=" * 50)
    
    # Wait a moment for service to start
    print("Waiting for service to start...")
    time.sleep(2)
    
    tests = [
        ("Health Check", test_health_check),
        ("Root Endpoint", test_root_endpoint),
        ("Templates Endpoint", test_templates_endpoint),
        ("Vessels Endpoint", test_vessels_endpoint),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"   ERROR: {test_name} failed")
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All tests passed! The FastAPI service is working correctly.")
        print("\nYou can now:")
        print("   1. Visit http://localhost:8000/docs for API documentation")
        print("   2. Use the React admin panel to manage templates")
        print("   3. Generate documents from vessel detail pages")
    else:
        print("WARNING: Some tests failed. Please check the service logs.")

if __name__ == "__main__":
    main()
