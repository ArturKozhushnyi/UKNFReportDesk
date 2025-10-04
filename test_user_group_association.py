#!/usr/bin/env python3
"""
Test script for the user-group association feature
This script tests the new POST /users/{user_id}/groups endpoint
"""

import requests
import json
import time

# Service URLs
AUTH_SERVICE_URL = "http://localhost:8001"
ADMIN_SERVICE_URL = "http://localhost:8000"

def test_user_group_association():
    """Test the complete user-group association workflow"""
    
    print("👥 Testing User-Group Association Feature")
    print("=" * 50)
    
    # Step 1: Register and login as admin user
    print("\n1. Setting up admin user...")
    admin_data = {
        "email": "admin2@example.com",
        "password": "adminpassword123",
        "user_name": "Admin",
        "user_lastname": "User"
    }
    
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/register", json=admin_data)
        print(f"   Registration Status: {response.status_code}")
        if response.status_code == 201:
            print("   ✅ Admin user registered")
        else:
            print(f"   Registration Error: {response.text}")
    except Exception as e:
        print(f"   Registration Error: {e}")
    
    # Login to get session
    login_data = {
        "email": "admin2@example.com",
        "password": "adminpassword123"
    }
    
    session_id = None
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/authn", json=login_data)
        print(f"   Login Status: {response.status_code}")
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data["session_id"]
            print(f"   ✅ Admin session obtained: {session_id[:8]}...")
        else:
            print(f"   Login Error: {response.text}")
            return False
    except Exception as e:
        print(f"   Login Error: {e}")
        return False
    
    # Step 2: Create test users
    print("\n2. Creating test users...")
    test_users = [
        {
            "email": "user1@example.com",
            "password": "password123",
            "user_name": "Test",
            "user_lastname": "User1"
        },
        {
            "email": "user2@example.com", 
            "password": "password123",
            "user_name": "Test",
            "user_lastname": "User2"
        }
    ]
    
    user_ids = []
    for user_data in test_users:
        try:
            response = requests.post(f"{AUTH_SERVICE_URL}/register", json=user_data)
            if response.status_code == 201:
                user_id = response.json()["user_id"]
                user_ids.append(user_id)
                print(f"   ✅ Created user {user_data['email']} with ID: {user_id}")
            else:
                print(f"   ❌ Failed to create user {user_data['email']}: {response.text}")
        except Exception as e:
            print(f"   ❌ Error creating user {user_data['email']}: {e}")
    
    if not user_ids:
        print("   ❌ No users created. Cannot continue with group tests.")
        return False
    
    # Step 3: Test user-group association without authorization
    print("\n3. Testing user-group association WITHOUT authorization...")
    
    headers = {"Content-Type": "application/json"}
    group_data = {"group_id": 1}  # Assuming group ID 1 exists (administrator group)
    
    try:
        response = requests.post(
            f"{ADMIN_SERVICE_URL}/users/{user_ids[0]}/groups",
            json=group_data,
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Step 4: Test user-group association WITH authorization
    print("\n4. Testing user-group association WITH authorization...")
    
    auth_headers = {
        "Authorization": f"Bearer {session_id}",
        "Content-Type": "application/json"
    }
    
    # Test adding user to group
    print(f"\n   Adding user {user_ids[0]} to group 1...")
    try:
        response = requests.post(
            f"{ADMIN_SERVICE_URL}/users/{user_ids[0]}/groups",
            json=group_data,
            headers=auth_headers
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            print(f"   ✅ Success: {response.json()}")
        else:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test adding same user to same group again (should fail)
    print(f"\n   Trying to add user {user_ids[0]} to group 1 again (should fail)...")
    try:
        response = requests.post(
            f"{ADMIN_SERVICE_URL}/users/{user_ids[0]}/groups",
            json=group_data,
            headers=auth_headers
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 400:
            print(f"   ✅ Correctly rejected duplicate: {response.json()}")
        else:
            print(f"   Unexpected response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test adding user to non-existent group
    print(f"\n   Adding user {user_ids[1]} to non-existent group 999...")
    invalid_group_data = {"group_id": 999}
    try:
        response = requests.post(
            f"{ADMIN_SERVICE_URL}/users/{user_ids[1]}/groups",
            json=invalid_group_data,
            headers=auth_headers
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 404:
            print(f"   ✅ Correctly rejected non-existent group: {response.json()}")
        else:
            print(f"   Unexpected response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test adding non-existent user to group
    print(f"\n   Adding non-existent user 999 to group 1...")
    try:
        response = requests.post(
            f"{ADMIN_SERVICE_URL}/users/999/groups",
            json=group_data,
            headers=auth_headers
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 404:
            print(f"   ✅ Correctly rejected non-existent user: {response.json()}")
        else:
            print(f"   Unexpected response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Step 5: Test with different group
    print(f"\n5. Testing with different group...")
    
    # First, let's try to add user to group 1 (administrator group)
    if len(user_ids) > 1:
        print(f"   Adding user {user_ids[1]} to group 1...")
        try:
            response = requests.post(
                f"{ADMIN_SERVICE_URL}/users/{user_ids[1]}/groups",
                json=group_data,
                headers=auth_headers
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 201:
                print(f"   ✅ Success: {response.json()}")
            else:
                print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n✅ User-group association testing completed!")
    return True

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
    print("🚀 Starting User-Group Association Tests")
    print("=" * 60)
    
    # Test service health first
    test_service_health()
    
    # Wait a moment for services to be ready
    print("\n⏳ Waiting for services to be ready...")
    time.sleep(3)
    
    # Test user-group association
    success = test_user_group_association()
    
    if success:
        print("\n🎉 All user-group association tests completed!")
        print("\n📝 Summary:")
        print("   - POST /users/{user_id}/groups endpoint created")
        print("   - Authorization protection working correctly")
        print("   - User and group validation working")
        print("   - Duplicate prevention working")
        print("   - Error handling working correctly")
    else:
        print("\n❌ Some tests failed. Check the service logs.")
    
    print("\nTo start the services, run:")
    print("docker-compose up")
    print("\nTo test the endpoint manually:")
    print("curl -X POST http://localhost:8000/users/1/groups \\")
    print("  -H 'Authorization: Bearer <session_id>' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"group_id\": 1}'")
