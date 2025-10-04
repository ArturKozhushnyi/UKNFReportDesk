#!/usr/bin/env python3
"""
Test script for the auth-service
This script demonstrates how to use the authentication service endpoints
"""

import requests
import json

# Service URLs
AUTH_SERVICE_URL = "http://localhost:8001"
ADMIN_SERVICE_URL = "http://localhost:8000"

def test_auth_service():
    """Test the authentication service endpoints"""
    
    print("🧪 Testing Authentication Service")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{AUTH_SERVICE_URL}/healthz")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Register a new user
    print("\n2. Testing user registration...")
    user_data = {
        "email": "test@example.com",
        "password": "securepassword123",
        "user_name": "Test",
        "user_lastname": "User"
    }
    
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/register", json=user_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Login
    print("\n3. Testing user login...")
    login_data = {
        "email": "test@example.com",
        "password": "securepassword123"
    }
    
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/authn", json=login_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            session_id = response.json()["session_id"]
            print(f"   Session ID: {session_id}")
            
            # Test 4: Authorization check
            print("\n4. Testing authorization...")
            authz_data = {
                "session_id": session_id,
                "resource_id": "test_resource"
            }
            
            try:
                response = requests.post(f"{AUTH_SERVICE_URL}/authz", json=authz_data)
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.json()}")
            except Exception as e:
                print(f"   Error: {e}")
            
            # Test 5: Logout
            print("\n5. Testing logout...")
            try:
                response = requests.post(f"{AUTH_SERVICE_URL}/logout", params={"session_id": session_id})
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.json()}")
            except Exception as e:
                print(f"   Error: {e}")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ Auth service testing completed!")

def test_administration_service():
    """Test the administration service"""
    
    print("\n🏛️ Testing Administration Service")
    print("=" * 50)
    
    # Test health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{ADMIN_SERVICE_URL}/healthz")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{ADMIN_SERVICE_URL}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting UKNF Report Desk Service Tests")
    print("=" * 60)
    
    # Test administration service first
    test_administration_service()
    
    # Test auth service
    test_auth_service()
    
    print("\n🎉 All tests completed!")
    print("\nTo start the services, run:")
    print("docker-compose up")
