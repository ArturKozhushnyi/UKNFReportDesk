#!/usr/bin/env python3
"""
Test script for the authorization integration between administration-service and auth-service
This script demonstrates the complete authorization workflow
"""

import requests
import json
import time

# Service URLs
AUTH_SERVICE_URL = "http://localhost:8001"
ADMIN_SERVICE_URL = "http://localhost:8000"

def test_authorization_integration():
    """Test the complete authorization integration workflow"""
    
    print("🔐 Testing Authorization Integration")
    print("=" * 60)
    
    # Step 1: Register a test user
    print("\n1. Registering test user...")
    user_data = {
        "email": "admin@example.com",
        "password": "adminpassword123",
        "user_name": "Admin",
        "user_lastname": "User"
    }
    
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/register", json=user_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Step 2: Login to get session
    print("\n2. Logging in to get session...")
    login_data = {
        "email": "admin@example.com",
        "password": "adminpassword123"
    }
    
    session_id = None
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/authn", json=login_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data["session_id"]
            print(f"   Session ID: {session_id}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    if not session_id:
        print("   ❌ Failed to get session ID. Cannot continue with authorization tests.")
        return
    
    # Step 3: Test protected endpoints without authorization
    print("\n3. Testing protected endpoints WITHOUT authorization...")
    
    # Test POST /subjects without auth
    print("\n   Testing POST /subjects without authorization...")
    try:
        response = requests.post(f"{ADMIN_SERVICE_URL}/subjects", json={
            "NAME_STRUCTURE": "Test Bank",
            "NIP": "1234567890"
        })
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test GET /subjects/{id} without auth
    print("\n   Testing GET /subjects/1 without authorization...")
    try:
        response = requests.get(f"{ADMIN_SERVICE_URL}/subjects/1")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test GET /users/{id} without auth
    print("\n   Testing GET /users/1 without authorization...")
    try:
        response = requests.get(f"{ADMIN_SERVICE_URL}/users/1")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Step 4: Test protected endpoints WITH authorization
    print("\n4. Testing protected endpoints WITH authorization...")
    
    headers = {
        "Authorization": f"Bearer {session_id}",
        "Content-Type": "application/json"
    }
    
    # Test POST /subjects with auth
    print("\n   Testing POST /subjects with authorization...")
    try:
        response = requests.post(f"{ADMIN_SERVICE_URL}/subjects", 
                               json={
                                   "NAME_STRUCTURE": "Test Bank with Auth",
                                   "NIP": "9876543210",
                                   "CODE_UKNF": "TEST001"
                               },
                               headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            subject_data = response.json()
            print(f"   Created subject ID: {subject_data['ID']}")
            subject_id = subject_data['ID']
        else:
            print(f"   Response: {response.json()}")
            subject_id = 1  # Fallback for testing
    except Exception as e:
        print(f"   Error: {e}")
        subject_id = 1
    
    # Test GET /subjects/{id} with auth
    print(f"\n   Testing GET /subjects/{subject_id} with authorization...")
    try:
        response = requests.get(f"{ADMIN_SERVICE_URL}/subjects/{subject_id}", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Subject data: {response.json()}")
        else:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test GET /users/{id} with auth
    print("\n   Testing GET /users/1 with authorization...")
    try:
        response = requests.get(f"{ADMIN_SERVICE_URL}/users/1", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   User data: {response.json()}")
        else:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Step 5: Test with invalid session
    print("\n5. Testing with invalid session...")
    
    invalid_headers = {
        "Authorization": "Bearer invalid-session-id",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{ADMIN_SERVICE_URL}/subjects/1", headers=invalid_headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Step 6: Test malformed authorization header
    print("\n6. Testing malformed authorization header...")
    
    malformed_headers = {
        "Authorization": "InvalidFormat session-id",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{ADMIN_SERVICE_URL}/subjects/1", headers=malformed_headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ Authorization integration testing completed!")

def test_service_health():
    """Test that both services are running and healthy"""
    
    print("🏥 Testing Service Health")
    print("=" * 40)
    
    # Test auth-service health
    print("\n1. Testing auth-service health...")
    try:
        response = requests.get(f"{AUTH_SERVICE_URL}/healthz")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test administration-service health
    print("\n2. Testing administration-service health...")
    try:
        response = requests.get(f"{ADMIN_SERVICE_URL}/healthz")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Authorization Integration Tests")
    print("=" * 70)
    
    # Test service health first
    test_service_health()
    
    # Wait a moment for services to be ready
    print("\n⏳ Waiting for services to be ready...")
    time.sleep(2)
    
    # Test authorization integration
    test_authorization_integration()
    
    print("\n🎉 All tests completed!")
    print("\nTo start the services, run:")
    print("docker-compose up")
    print("\nTo test individual endpoints:")
    print("curl -H 'Authorization: Bearer <session_id>' http://localhost:8000/subjects/1")
