#!/usr/bin/env python3
"""
Test script for the complete manageable subjects flow
This script tests the full authentication and API flow
"""

import requests
import json

# Service URLs
ADMIN_SERVICE_URL = "http://localhost:8000"
AUTH_SERVICE_URL = "http://localhost:8001"

def test_complete_flow():
    """Test the complete manageable subjects flow"""
    
    print("🧪 Testing Complete Manageable Subjects Flow")
    print("=" * 60)
    
    # Step 1: Login as admin user
    print("\n1. Logging in as admin user...")
    login_data = {
        "email": "admin@example.com",
        "password": "admin"
    }
    
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/authn", json=login_data)
        if response.status_code == 200:
            auth_data = response.json()
            session_id = auth_data["session_id"]
            print(f"   ✅ Login successful!")
            print(f"   Session ID: {session_id[:8]}...")
            
            # Step 2: Get user details
            print("\n2. Getting user details...")
            headers = {
                "Authorization": f"Bearer {session_id}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{AUTH_SERVICE_URL}/me?session_id={session_id}")
            if response.status_code == 200:
                user_data = response.json()
                print(f"   ✅ User details retrieved:")
                print(f"   User ID: {user_data['user_id']}")
                print(f"   Email: {user_data['email']}")
                print(f"   Subject ID: {user_data.get('subjectId', 'None')}")
            else:
                print(f"   ❌ Failed to get user details: {response.status_code} - {response.text}")
                return
            
            # Step 3: Test manageable subjects endpoint directly
            print("\n3. Testing manageable subjects endpoint directly...")
            print(f"   Using session ID: {session_id[:8]}...")
            response = requests.get(f"{ADMIN_SERVICE_URL}/subjects/manageable", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                subjects = response.json()
                print(f"   ✅ Found {len(subjects)} manageable subjects:")
                for subject in subjects:
                    print(f"     - ID: {subject['ID']}, Name: {subject.get('NAME_STRUCTURE', 'N/A')}")
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
            
            # Step 4: Test through nginx proxy
            print("\n4. Testing through nginx proxy...")
            response = requests.get(f"http://localhost:3000/admin/subjects/manageable", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                subjects = response.json()
                print(f"   ✅ Proxy working! Found {len(subjects)} manageable subjects")
            else:
                print(f"   ❌ Proxy error: {response.status_code} - {response.text}")
                
        else:
            print(f"   ❌ Login failed: {response.status_code} - {response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_complete_flow()
