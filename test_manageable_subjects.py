#!/usr/bin/env python3
"""
Test script for the new manageable subjects endpoint
This script demonstrates how to test the /subjects/manageable endpoint
"""

import requests
import json

# Service URLs
ADMIN_SERVICE_URL = "http://localhost:8000"
AUTH_SERVICE_URL = "http://localhost:8001"

def test_manageable_subjects():
    """Test the manageable subjects endpoint"""
    
    print("🧪 Testing Manageable Subjects Endpoint")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing administration service health check...")
    try:
        response = requests.get(f"{ADMIN_SERVICE_URL}/healthz")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Login as admin user
    print("\n2. Testing admin login...")
    login_data = {
        "email": "admin@example.com",
        "password": "admin"
    }
    
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/authn", json=login_data)
        if response.status_code == 200:
            auth_data = response.json()
            session_id = auth_data["session_id"]
            print(f"   Login successful! Session ID: {session_id[:8]}...")
            
            # Test 3: Get manageable subjects
            print("\n3. Testing manageable subjects endpoint...")
            headers = {
                "Authorization": f"Bearer {session_id}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{ADMIN_SERVICE_URL}/subjects/manageable", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                subjects = response.json()
                print(f"   Found {len(subjects)} manageable subjects:")
                for subject in subjects:
                    print(f"     - ID: {subject['ID']}, Name: {subject.get('NAME_STRUCTURE', 'N/A')}")
            else:
                print(f"   Error: {response.text}")
                
        else:
            print(f"   Login failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Test without authentication
    print("\n4. Testing manageable subjects without authentication...")
    try:
        response = requests.get(f"{ADMIN_SERVICE_URL}/subjects/manageable")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_manageable_subjects()
