#!/usr/bin/env python3
import requests

# Test the endpoint directly
session_id = "604504ec-8c5a-4b2e-9f3d-1a2b3c4d5e6f"  # Use a real session ID
headers = {"Authorization": f"Bearer {session_id}"}

print("Testing with requests library:")
response = requests.get("http://localhost:8000/subjects/manageable", headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
