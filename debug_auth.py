#!/usr/bin/env python3
import requests
import psycopg

# Test the authorization logic
AUTH_SERVICE_URL = "http://localhost:8001"
ADMIN_SERVICE_URL = "http://localhost:8000"

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "mydatabase",
    "user": "myuser",
    "password": "mysecretpassword"
}

def debug_auth():
    # Login and get session
    login_data = {
        "email": "admin@example.com",
        "password": "admin"
    }
    
    response = requests.post(f"{AUTH_SERVICE_URL}/authn", json=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    auth_data = response.json()
    session_id = auth_data["session_id"]
    print(f"Session ID: {session_id}")
    
    # Get user details
    response = requests.get(f"{AUTH_SERVICE_URL}/me?session_id={session_id}")
    if response.status_code != 200:
        print(f"Get user details failed: {response.text}")
        return
    
    user_data = response.json()
    user_id = user_data["user_id"]
    print(f"User ID: {user_id}")
    
    # Check database directly
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            # Check if user is in administrator group
            cur.execute("""
                SELECT u."ID", u."EMAIL", ug."GROUP_ID", g."GROUP_NAME" 
                FROM "USERS" u 
                LEFT JOIN "USERS_GROUPS" ug ON u."ID" = ug."USER_ID" 
                LEFT JOIN "GROUPS" g ON ug."GROUP_ID" = g."ID" 
                WHERE u."ID" = %s
            """, (user_id,))
            
            rows = cur.fetchall()
            print(f"User groups: {rows}")
            
            # Check if user is in administrator group specifically
            cur.execute("""
                SELECT COUNT(*) 
                FROM "USERS_GROUPS" ug 
                JOIN "GROUPS" g ON ug."GROUP_ID" = g."ID" 
                WHERE ug."USER_ID" = %s AND g."GROUP_NAME" = 'administrator'
            """, (user_id,))
            
            admin_count = cur.fetchone()[0]
            print(f"Is admin: {admin_count > 0}")

if __name__ == "__main__":
    debug_auth()
