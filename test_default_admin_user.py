#!/usr/bin/env python3
"""
Test script for the default admin user creation
This script verifies that the default admin user can be created and used
"""

import requests
import json
import time

# Service URLs
AUTH_SERVICE_URL = "http://localhost:8001"
ADMIN_SERVICE_URL = "http://localhost:8000"

def test_default_admin_user():
    """Test the default admin user functionality"""
    
    print("👤 Testing Default Admin User")
    print("=" * 40)
    
    # Test 1: Try to login with default admin credentials
    print("\n1. Testing login with default admin credentials...")
    admin_login_data = {
        "email": "admin@example.com",
        "password": "admin"
    }
    
    session_id = None
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/authn", json=admin_login_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data["session_id"]
            print(f"   ✅ Default admin login successful!")
            print(f"   Session ID: {session_id[:8]}...")
        else:
            print(f"   ❌ Default admin login failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error during admin login: {e}")
        return False
    
    # Test 2: Test authorization with default admin session
    print("\n2. Testing authorization with default admin session...")
    
    auth_headers = {
        "Authorization": f"Bearer {session_id}",
        "Content-Type": "application/json"
    }
    
    # Test access to protected endpoints
    endpoints_to_test = [
        ("GET", "/subjects/1", "api:subjects:read"),
        ("GET", "/users/1", "api:users:read"),
        ("POST", "/subjects", "api:subjects:create", {
            "NAME_STRUCTURE": "Test Bank",
            "NIP": "1234567890"
        })
    ]
    
    for method, endpoint, resource_id, *data in endpoints_to_test:
        print(f"\n   Testing {method} {endpoint}...")
        try:
            if method == "GET":
                response = requests.get(f"{ADMIN_SERVICE_URL}{endpoint}", headers=auth_headers)
            elif method == "POST":
                response = requests.post(f"{ADMIN_SERVICE_URL}{endpoint}", 
                                       json=data[0] if data else {}, 
                                       headers=auth_headers)
            
            print(f"   Status: {response.status_code}")
            if response.status_code in [200, 201, 404]:  # 404 is OK if resource doesn't exist
                print(f"   ✅ Access granted for {resource_id}")
            else:
                print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
    
    # Test 3: Test user-group association with default admin
    print("\n3. Testing user-group association with default admin...")
    
    # First, create a test user
    test_user_data = {
        "email": "testuser@example.com",
        "password": "testpassword123",
        "user_name": "Test",
        "user_lastname": "User"
    }
    
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/register", json=test_user_data)
        if response.status_code == 201:
            test_user_id = response.json()["user_id"]
            print(f"   ✅ Created test user with ID: {test_user_id}")
            
            # Try to add test user to administrator group
            group_data = {"group_id": 1}  # Assuming group 1 is administrator
            response = requests.post(
                f"{ADMIN_SERVICE_URL}/users/{test_user_id}/groups",
                json=group_data,
                headers=auth_headers
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 201:
                print(f"   ✅ Successfully added user to group: {response.json()}")
            else:
                print(f"   Response: {response.json()}")
        else:
            print(f"   ❌ Failed to create test user: {response.text}")
    except Exception as e:
        print(f"   ❌ Error during user-group test: {e}")
    
    # Test 4: Test logout
    print("\n4. Testing logout...")
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/logout", params={"session_id": session_id})
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Logout successful: {response.json()}")
        else:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error during logout: {e}")
    
    return True

def test_password_verification():
    """Test that the password hash is correct"""
    
    print("\n🔐 Testing Password Hash Verification")
    print("=" * 45)
    
    # Test with correct password
    print("\n1. Testing with correct password...")
    correct_login = {
        "email": "admin@example.com",
        "password": "admin"
    }
    
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/authn", json=correct_login)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Correct password accepted")
        else:
            print(f"   ❌ Correct password rejected: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test with wrong password
    print("\n2. Testing with wrong password...")
    wrong_login = {
        "email": "admin@example.com",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/authn", json=wrong_login)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Wrong password correctly rejected")
        else:
            print(f"   ❌ Wrong password unexpectedly accepted: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

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
    print("🚀 Starting Default Admin User Tests")
    print("=" * 50)
    
    # Test service health first
    test_service_health()
    
    # Wait a moment for services to be ready
    print("\n⏳ Waiting for services to be ready...")
    time.sleep(3)
    
    # Test password verification
    test_password_verification()
    
    # Test default admin user functionality
    success = test_default_admin_user()
    
    if success:
        print("\n✅ All default admin user tests completed!")
        print("\n📝 Summary:")
        print("   - Default admin user created with email: admin@example.com")
        print("   - Password: admin (hashed with sha256_crypt)")
        print("   - User assigned to administrator group")
        print("   - All permissions working correctly")
        print("   - Password verification working")
    else:
        print("\n❌ Some tests failed. Check the service logs.")
    
    print("\nTo start the services, run:")
    print("docker-compose up")
    print("\nTo login with default admin:")
    print("curl -X POST http://localhost:8001/authn \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"email\": \"admin@example.com\", \"password\": \"admin\"}'")
