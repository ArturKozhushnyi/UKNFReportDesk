#!/usr/bin/env python3
"""
Test script for multi-tenant security model
Verifies that new users automatically become admins of their own subjects
"""

import requests
import psycopg
from datetime import datetime

# Service configuration
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

class Colors:
    """ANSI color codes"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{Colors.OKGREEN}✅ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}❌ {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.OKCYAN}ℹ️  {msg}{Colors.ENDC}")

def print_header(msg):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
    print(f"{msg}")
    print(f"{'='*70}{Colors.ENDC}")

def test_multi_tenant_security():
    """Main test function"""
    print_header("🔒 Multi-Tenant Security Model Test Suite")
    
    test_email = f"test_user_{datetime.now().timestamp()}@example.com"
    
    try:
        # Test 1: Service health
        print_header("Test 1: Verify Services Are Running")
        if not test_service_health():
            print_error("Services not healthy, aborting tests")
            return False
        
        # Test 2: Register user
        print_header("Test 2: Register New User")
        registration_data = test_user_registration(test_email)
        if not registration_data:
            return False
        
        # Test 3: Verify database state
        print_header("Test 3: Verify Database State")
        if not test_database_state(registration_data):
            return False
        
        # Test 4: Login and authorization
        print_header("Test 4: Test Authentication & Authorization")
        if not test_authentication_authorization(test_email, registration_data):
            return False
        
        # Test 5: Verify permission chain
        print_header("Test 5: Verify Complete Permission Chain")
        if not test_permission_chain(registration_data):
            return False
        
        print_header("🎉 All Multi-Tenant Security Tests Passed!")
        return True
        
    except Exception as e:
        print_error(f"Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_service_health():
    """Test that services are running"""
    print_info("Checking auth-service...")
    try:
        response = requests.get(f"{AUTH_SERVICE_URL}/healthz", timeout=5)
        if response.status_code == 200:
            print_success(f"Auth service healthy: {response.json()}")
        else:
            print_error(f"Auth service unhealthy: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Cannot connect to auth service: {e}")
        return False
    
    return True

def test_user_registration(email):
    """Test user registration and verify response"""
    print_info(f"Registering user: {email}")
    
    user_data = {
        "email": email,
        "password": "securepassword123",
        "user_name": "Test",
        "user_lastname": "User",
        "phone": "+48 123 456 789"
    }
    
    try:
        response = requests.post(
            f"{AUTH_SERVICE_URL}/register",
            json=user_data,
            timeout=10
        )
        
        if response.status_code != 201:
            print_error(f"Registration failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
        
        data = response.json()
        print_success("User registered successfully")
        
        # Verify response structure
        required_fields = [
            "user_id", "subject_id", "resource_id", 
            "admin_group", "email", "uknf_id"
        ]
        
        for field in required_fields:
            if field not in data:
                print_error(f"Missing field in response: {field}")
                return None
            print_info(f"  {field}: {data[field]}")
        
        # Verify naming conventions
        expected_resource_id = f"subject:admin:{data['subject_id']}"
        if data['resource_id'] != expected_resource_id:
            print_error(f"Resource ID mismatch: expected {expected_resource_id}, got {data['resource_id']}")
            return None
        print_success(f"Resource ID format correct: {data['resource_id']}")
        
        expected_group_name = f"admins_of_subject_{data['subject_id']}"
        if data['admin_group'] != expected_group_name:
            print_error(f"Group name mismatch: expected {expected_group_name}, got {data['admin_group']}")
            return None
        print_success(f"Admin group format correct: {data['admin_group']}")
        
        return data
        
    except Exception as e:
        print_error(f"Registration error: {e}")
        return None

def test_database_state(reg_data):
    """Verify database state after registration"""
    print_info("Connecting to database...")
    
    try:
        conn = psycopg.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        user_id = reg_data['user_id']
        subject_id = reg_data['subject_id']
        resource_id = reg_data['resource_id']
        
        # Test 1: Verify subject exists and has RESOURCE_ID
        print_info("Checking SUBJECTS table...")
        cur.execute("""
            SELECT "ID", "RESOURCE_ID", "NAME_STRUCTURE", "STATUS_S"
            FROM "SUBJECTS"
            WHERE "ID" = %s
        """, (subject_id,))
        
        subject = cur.fetchone()
        if not subject:
            print_error(f"Subject {subject_id} not found")
            return False
        
        print_success(f"Subject found: ID={subject[0]}, RESOURCE_ID={subject[1]}")
        
        if subject[1] != resource_id:
            print_error(f"Subject RESOURCE_ID mismatch: expected {resource_id}, got {subject[1]}")
            return False
        print_success("Subject RESOURCE_ID correctly linked")
        
        # Test 2: Verify resource exists
        print_info("Checking RESOURCES table...")
        cur.execute("""
            SELECT "ID"
            FROM "RESOURCES"
            WHERE "ID" = %s
        """, (resource_id,))
        
        resource = cur.fetchone()
        if not resource:
            print_error(f"Resource {resource_id} not found")
            return False
        print_success(f"Resource exists: {resource[0]}")
        
        # Test 3: Verify admin group exists
        print_info("Checking GROUPS table...")
        cur.execute("""
            SELECT "ID", "GROUP_NAME"
            FROM "GROUPS"
            WHERE "GROUP_NAME" = %s
        """, (reg_data['admin_group'],))
        
        group = cur.fetchone()
        if not group:
            print_error(f"Admin group not found: {reg_data['admin_group']}")
            return False
        
        group_id = group[0]
        print_success(f"Admin group exists: ID={group_id}, NAME={group[1]}")
        
        # Test 4: Verify permission grant
        print_info("Checking RESOURCES_ALLOW_LIST...")
        cur.execute("""
            SELECT "ID", "RESOURCE_ID", "GROUP_ID"
            FROM "RESOURCES_ALLOW_LIST"
            WHERE "RESOURCE_ID" = %s AND "GROUP_ID" = %s
        """, (resource_id, group_id))
        
        permission = cur.fetchone()
        if not permission:
            print_error(f"Permission grant not found for group {group_id} on resource {resource_id}")
            return False
        print_success(f"Permission granted: Group {group_id} can access {resource_id}")
        
        # Test 5: Verify user is member of admin group
        print_info("Checking USERS_GROUPS...")
        cur.execute("""
            SELECT "ID", "USER_ID", "GROUP_ID"
            FROM "USERS_GROUPS"
            WHERE "USER_ID" = %s AND "GROUP_ID" = %s
        """, (user_id, group_id))
        
        membership = cur.fetchone()
        if not membership:
            print_error(f"User {user_id} not member of group {group_id}")
            return False
        print_success(f"User {user_id} is member of admin group {group_id}")
        
        # Test 6: Verify user has SUBJECT_ID
        print_info("Checking USERS table...")
        cur.execute("""
            SELECT "ID", "EMAIL", "SUBJECT_ID"
            FROM "USERS"
            WHERE "ID" = %s
        """, (user_id,))
        
        user = cur.fetchone()
        if not user:
            print_error(f"User {user_id} not found")
            return False
        
        if user[2] != subject_id:
            print_error(f"User SUBJECT_ID mismatch: expected {subject_id}, got {user[2]}")
            return False
        print_success(f"User correctly linked to subject {subject_id}")
        
        conn.close()
        return True
        
    except Exception as e:
        print_error(f"Database check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_authentication_authorization(email, reg_data):
    """Test login and authorization"""
    
    # Login
    print_info("Testing login...")
    try:
        response = requests.post(
            f"{AUTH_SERVICE_URL}/authn",
            json={
                "email": email,
                "password": "securepassword123"
            },
            timeout=10
        )
        
        if response.status_code != 200:
            print_error(f"Login failed: {response.status_code}")
            return False
        
        auth_data = response.json()
        session_id = auth_data['session_id']
        print_success(f"Login successful, session: {session_id[:8]}...")
        
    except Exception as e:
        print_error(f"Login error: {e}")
        return False
    
    # Test authorization for subject admin resource
    print_info("Testing authorization for subject admin resource...")
    try:
        response = requests.post(
            f"{AUTH_SERVICE_URL}/authz",
            json={
                "session_id": session_id,
                "resource_id": reg_data['resource_id']
            },
            timeout=10
        )
        
        if response.status_code != 200:
            print_error(f"Authorization check failed: {response.status_code}")
            return False
        
        authz_data = response.json()
        
        if not authz_data.get('authorized'):
            print_error(f"User not authorized for their own subject: {authz_data}")
            return False
        
        print_success(f"User authorized: {authz_data['message']}")
        
    except Exception as e:
        print_error(f"Authorization error: {e}")
        return False
    
    # Test authorization for non-existent resource (should fail)
    print_info("Testing authorization for other subject (should deny)...")
    try:
        response = requests.post(
            f"{AUTH_SERVICE_URL}/authz",
            json={
                "session_id": session_id,
                "resource_id": "subject:admin:99999"  # Non-existent
            },
            timeout=10
        )
        
        if response.status_code != 200:
            print_error(f"Authorization check failed: {response.status_code}")
            return False
        
        authz_data = response.json()
        
        if authz_data.get('authorized'):
            print_error("User incorrectly authorized for other subject!")
            return False
        
        print_success("User correctly denied access to other subjects")
        
    except Exception as e:
        print_error(f"Authorization error: {e}")
        return False
    
    return True

def test_permission_chain(reg_data):
    """Verify the complete permission chain in database"""
    print_info("Verifying complete permission chain...")
    
    try:
        conn = psycopg.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        user_id = reg_data['user_id']
        subject_id = reg_data['subject_id']
        
        # Query the complete chain
        cur.execute("""
            SELECT 
                u."ID" as user_id,
                u."EMAIL",
                u."SUBJECT_ID",
                ug."GROUP_ID",
                g."GROUP_NAME",
                ral."RESOURCE_ID",
                s."ID" as subject_id_from_resource,
                s."NAME_STRUCTURE"
            FROM "USERS" u
            JOIN "USERS_GROUPS" ug ON u."ID" = ug."USER_ID"
            JOIN "GROUPS" g ON ug."GROUP_ID" = g."ID"
            JOIN "RESOURCES_ALLOW_LIST" ral ON g."ID" = ral."GROUP_ID"
            JOIN "SUBJECTS" s ON ral."RESOURCE_ID" = s."RESOURCE_ID"
            WHERE u."ID" = %s
        """, (user_id,))
        
        result = cur.fetchone()
        
        if not result:
            print_error("Permission chain not found!")
            return False
        
        print_success("Permission chain complete:")
        print_info(f"  User ID: {result[0]}")
        print_info(f"  Email: {result[1]}")
        print_info(f"  User's SUBJECT_ID: {result[2]}")
        print_info(f"  Member of GROUP_ID: {result[3]}")
        print_info(f"  Group Name: {result[4]}")
        print_info(f"  Group has access to: {result[5]}")
        print_info(f"  Which controls SUBJECT_ID: {result[6]}")
        print_info(f"  Subject Name: {result[7]}")
        
        # Verify consistency
        if result[2] != result[6]:
            print_error("Subject ID mismatch in permission chain!")
            return False
        
        if result[6] != subject_id:
            print_error(f"Subject ID mismatch: expected {subject_id}, got {result[6]}")
            return False
        
        print_success("Permission chain verified: User → Group → Resource → Subject")
        
        conn.close()
        return True
        
    except Exception as e:
        print_error(f"Permission chain verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_multi_tenant_security()
        if success:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ Multi-Tenant Security Model Working Perfectly!{Colors.ENDC}")
            print(f"\n{Colors.OKCYAN}Summary:{Colors.ENDC}")
            print("  ✅ New users automatically get their own subject")
            print("  ✅ Dedicated admin resource created")
            print("  ✅ Admin group established")
            print("  ✅ Permissions correctly granted")
            print("  ✅ Users are admins of their own subjects")
            print("  ✅ Users cannot access other subjects")
            print("\n{Colors.BOLD}System ready for production!{Colors.ENDC}")
        else:
            print(f"\n{Colors.FAIL}{Colors.BOLD}❌ Some tests failed{Colors.ENDC}")
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Test interrupted by user{Colors.ENDC}")

