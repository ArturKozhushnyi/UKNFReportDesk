#!/usr/bin/env python3
"""
Test script to verify the admin users can see subjects in Manage Subjects
"""

import requests
import json

# Service URLs
ADMIN_SERVICE_URL = "http://localhost:8000"
AUTH_SERVICE_URL = "http://localhost:8001"

def test_admin_access():
    """Test that admin users can access their respective subjects"""
    
    print("🧪 Testing Admin User Access to Manageable Subjects")
    print("=" * 60)
    
    # Test UKNF Admin
    print("\n1. Testing UKNF Admin (should see all subjects)...")
    login_data = {
        "email": "admin_uknf@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/authn", json=login_data)
        if response.status_code == 200:
            auth_data = response.json()
            session_id = auth_data["session_id"]
            print(f"   ✅ UKNF Admin login successful!")
            print(f"   Session ID: {session_id[:8]}...")
            
            # Test manageable subjects endpoint
            headers = {"Authorization": f"Bearer {session_id}"}
            response = requests.get(f"{ADMIN_SERVICE_URL}/subjects/manageable", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                subjects = response.json()
                print(f"   ✅ UKNF Admin can see {len(subjects)} subjects:")
                for subject in subjects:
                    print(f"     - ID: {subject['ID']}, Name: {subject.get('NAME_STRUCTURE', 'N/A')}")
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
        else:
            print(f"   ❌ UKNF Admin login failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ UKNF Admin test error: {e}")
    
    # Test Bank Pekao Admin
    print("\n2. Testing Bank Pekao Admin (should see only Bank Pekao subject)...")
    login_data = {
        "email": "admin_pekao@example.com",
        "password": "password456"
    }
    
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/authn", json=login_data)
        if response.status_code == 200:
            auth_data = response.json()
            session_id = auth_data["session_id"]
            print(f"   ✅ Bank Pekao Admin login successful!")
            print(f"   Session ID: {session_id[:8]}...")
            
            # Test manageable subjects endpoint
            headers = {"Authorization": f"Bearer {session_id}"}
            response = requests.get(f"{ADMIN_SERVICE_URL}/subjects/manageable", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                subjects = response.json()
                print(f"   ✅ Bank Pekao Admin can see {len(subjects)} subjects:")
                for subject in subjects:
                    print(f"     - ID: {subject['ID']}, Name: {subject.get('NAME_STRUCTURE', 'N/A')}")
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
        else:
            print(f"   ❌ Bank Pekao Admin login failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Bank Pekao Admin test error: {e}")

if __name__ == "__main__":
    test_admin_access()
