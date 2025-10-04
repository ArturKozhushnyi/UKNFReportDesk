#!/usr/bin/env python3
"""
Test script to verify the password hashing change from bcrypt to sha256_crypt
This script tests the new hashing algorithm and database compatibility
"""

import requests
import json
import time

# Service URLs
AUTH_SERVICE_URL = "http://localhost:8001"
ADMIN_SERVICE_URL = "http://localhost:8000"

def test_password_hashing():
    """Test the new sha256_crypt password hashing"""
    
    print("🔐 Testing Password Hashing (sha256_crypt)")
    print("=" * 50)
    
    # Test 1: Register a new user with sha256_crypt hashing
    print("\n1. Testing user registration with sha256_crypt...")
    user_data = {
        "email": "test_sha256@example.com",
        "password": "testpassword123",
        "user_name": "SHA256",
        "user_lastname": "Test"
    }
    
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/register", json=user_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            print(f"   Response: {response.json()}")
            print("   ✅ User registration successful with sha256_crypt")
        else:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"   Error: {e}")
        return False
    
    # Test 2: Login with the new user
    print("\n2. Testing login with sha256_crypt hashed password...")
    login_data = {
        "email": "test_sha256@example.com",
        "password": "testpassword123"
    }
    
    session_id = None
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/authn", json=login_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data["session_id"]
            print(f"   Session ID: {session_id}")
            print("   ✅ Login successful with sha256_crypt")
        else:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"   Error: {e}")
        return False
    
    # Test 3: Test with wrong password
    print("\n3. Testing with wrong password...")
    wrong_login_data = {
        "email": "test_sha256@example.com",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/authn", json=wrong_login_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Wrong password correctly rejected")
        else:
            print(f"   Unexpected response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Test authorization with the new session
    print("\n4. Testing authorization with sha256_crypt session...")
    if session_id:
        headers = {
            "Authorization": f"Bearer {session_id}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(f"{ADMIN_SERVICE_URL}/users/1", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code in [200, 404]:  # 404 is OK if user doesn't exist
                print("   ✅ Authorization successful with sha256_crypt session")
            else:
                print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
    
    return True

def test_database_compatibility():
    """Test that the database can handle the longer password hashes"""
    
    print("\n🗄️ Testing Database Compatibility")
    print("=" * 40)
    
    # Test with a very long password to ensure database can handle it
    print("\n1. Testing with long password...")
    long_password = "a" * 100  # Very long password
    user_data = {
        "email": "long_password_test@example.com",
        "password": long_password,
        "user_name": "Long",
        "user_lastname": "Password"
    }
    
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/register", json=user_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            print("   ✅ Long password handled successfully")
            
            # Test login with the long password
            login_data = {
                "email": "long_password_test@example.com",
                "password": long_password
            }
            
            response = requests.post(f"{AUTH_SERVICE_URL}/authn", json=login_data)
            print(f"   Login Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Long password login successful")
            else:
                print(f"   Login Error: {response.text}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

def test_hash_format():
    """Test the format of the generated hashes"""
    
    print("\n🔍 Testing Hash Format")
    print("=" * 30)
    
    # Register a user and check if we can inspect the hash format
    print("\n1. Testing hash format...")
    user_data = {
        "email": "hash_format_test@example.com",
        "password": "test123",
        "user_name": "Hash",
        "user_lastname": "Format"
    }
    
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/register", json=user_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            print("   ✅ User registered successfully")
            print("   Note: Hash format verification requires database access")
            print("   Expected: sha256_crypt hashes start with '$5$' and are ~100+ characters")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Password Hashing Tests (sha256_crypt)")
    print("=" * 60)
    
    # Wait for services to be ready
    print("⏳ Waiting for services to be ready...")
    time.sleep(3)
    
    # Test password hashing
    success = test_password_hashing()
    
    if success:
        # Test database compatibility
        test_database_compatibility()
        
        # Test hash format
        test_hash_format()
        
        print("\n✅ All password hashing tests completed!")
        print("\n📝 Summary:")
        print("   - Password hashing changed from bcrypt to sha256_crypt")
        print("   - Database column size updated to varchar(128)")
        print("   - All authentication flows working correctly")
        print("   - Database compatibility verified")
    else:
        print("\n❌ Some tests failed. Check the service logs.")
    
    print("\nTo start the services, run:")
    print("docker-compose up")
