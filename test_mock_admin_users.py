#!/usr/bin/env python3
"""
Test script for mock subject admin users
Verifies that UKNF and Bank Pekao admin users can login and access their subjects
"""

import requests
import psycopg

# Service configuration
AUTH_SERVICE_URL = "http://localhost:8001"

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "mydatabase",
    "user": "myuser",
    "password": "mysecretpassword"
}

# Admin credentials
ADMINS = {
    "uknf": {
        "email": "admin_uknf@example.com",
        "password": "password123",
        "subject_id": 1,
        "resource_id": "subject:admin:1",
        "group_name": "admins_of_UKNF"
    },
    "pekao": {
        "email": "admin_pekao@example.com",
        "password": "password456",
        "subject_id": 2,
        "resource_id": "subject:admin:2",
        "group_name": "admins_of_Bank_Polska_Kasa_Opieki_Spółka_Akcyjna"
    }
}

class Colors:
    """ANSI color codes"""
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    CYAN = '\033[96m'

def print_success(msg):
    print(f"{Colors.OKGREEN}✅ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}❌ {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.CYAN}ℹ️  {msg}{Colors.ENDC}")

def print_header(msg):
    print(f"\n{Colors.BOLD}{'='*70}")
    print(f"{msg}")
    print(f"{'='*70}{Colors.ENDC}")

def test_database_setup():
    """Verify database setup for mock admins"""
    print_header("Test 1: Verify Database Setup")
    
    try:
        conn = psycopg.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        all_ok = True
        
        for name, admin in ADMINS.items():
            print_info(f"\nChecking {name.upper()} admin setup...")
            
            # Check user exists
            cur.execute("""
                SELECT "ID", "EMAIL", "SUBJECT_ID", "IS_USER_ACTIVE"
                FROM "USERS"
                WHERE "EMAIL" = %s
            """, (admin["email"],))
            
            user = cur.fetchone()
            if not user:
                print_error(f"User {admin['email']} not found")
                all_ok = False
                continue
            
            user_id = user[0]
            print_success(f"User exists: ID={user_id}, SUBJECT_ID={user[2]}, Active={user[3]}")
            
            if user[2] != admin["subject_id"]:
                print_error(f"Wrong SUBJECT_ID: expected {admin['subject_id']}, got {user[2]}")
                all_ok = False
            
            # Check group exists
            cur.execute("""
                SELECT "ID" FROM "GROUPS"
                WHERE "GROUP_NAME" = %s
            """, (admin["group_name"],))
            
            group = cur.fetchone()
            if not group:
                print_error(f"Group {admin['group_name']} not found")
                all_ok = False
                continue
            
            group_id = group[0]
            print_success(f"Group exists: {admin['group_name']} (ID={group_id})")
            
            # Check user is member of group
            cur.execute("""
                SELECT 1 FROM "USERS_GROUPS"
                WHERE "USER_ID" = %s AND "GROUP_ID" = %s
            """, (user_id, group_id))
            
            if not cur.fetchone():
                print_error(f"User not member of group")
                all_ok = False
            else:
                print_success(f"User is member of admin group")
            
            # Check resource exists
            cur.execute("""
                SELECT "ID" FROM "RESOURCES"
                WHERE "ID" = %s
            """, (admin["resource_id"],))
            
            if not cur.fetchone():
                print_error(f"Resource {admin['resource_id']} not found")
                all_ok = False
            else:
                print_success(f"Resource exists: {admin['resource_id']}")
            
            # Check permission granted
            cur.execute("""
                SELECT 1 FROM "RESOURCES_ALLOW_LIST"
                WHERE "RESOURCE_ID" = %s AND "GROUP_ID" = %s
            """, (admin["resource_id"], group_id))
            
            if not cur.fetchone():
                print_error(f"Permission not granted")
                all_ok = False
            else:
                print_success(f"Permission granted: group → resource")
            
            # Check subject has resource link
            cur.execute("""
                SELECT "RESOURCE_ID" FROM "SUBJECTS"
                WHERE "ID" = %s
            """, (admin["subject_id"],))
            
            subject = cur.fetchone()
            if not subject or subject[0] != admin["resource_id"]:
                print_error(f"Subject not linked to resource correctly")
                all_ok = False
            else:
                print_success(f"Subject linked to resource")
        
        conn.close()
        return all_ok
        
    except Exception as e:
        print_error(f"Database check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_admin_login(name, admin):
    """Test admin user login"""
    print_info(f"\nTesting login for {name.upper()} admin...")
    
    try:
        response = requests.post(
            f"{AUTH_SERVICE_URL}/authn",
            json={
                "email": admin["email"],
                "password": admin["password"]
            },
            timeout=10
        )
        
        if response.status_code != 200:
            print_error(f"Login failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
        
        data = response.json()
        session_id = data.get("session_id")
        
        if not session_id:
            print_error("No session_id in response")
            return None
        
        print_success(f"Login successful: {admin['email']}")
        print_info(f"  Session ID: {session_id[:8]}...")
        
        return session_id
        
    except Exception as e:
        print_error(f"Login error: {e}")
        return None

def test_admin_authorization(name, admin, session_id):
    """Test admin authorization for their subject"""
    print_info(f"\nTesting authorization for {name.upper()} admin...")
    
    try:
        # Test access to their own subject (should succeed)
        print_info(f"  Testing access to {admin['resource_id']}...")
        response = requests.post(
            f"{AUTH_SERVICE_URL}/authz",
            json={
                "session_id": session_id,
                "resource_id": admin["resource_id"]
            },
            timeout=10
        )
        
        if response.status_code != 200:
            print_error(f"Authorization check failed: {response.status_code}")
            return False
        
        data = response.json()
        
        if not data.get("authorized"):
            print_error(f"Not authorized for own subject!")
            print_error(f"  Response: {data}")
            return False
        
        print_success(f"Authorized for own subject: {data['message']}")
        
        # Test access to other subject (should fail)
        other_resource = "subject:admin:2" if name == "uknf" else "subject:admin:1"
        other_name = "Bank Pekao" if name == "uknf" else "UKNF"
        
        print_info(f"  Testing access to {other_resource} ({other_name})...")
        response = requests.post(
            f"{AUTH_SERVICE_URL}/authz",
            json={
                "session_id": session_id,
                "resource_id": other_resource
            },
            timeout=10
        )
        
        if response.status_code != 200:
            print_error(f"Authorization check failed: {response.status_code}")
            return False
        
        data = response.json()
        
        if data.get("authorized"):
            print_error(f"Incorrectly authorized for other subject!")
            return False
        
        print_success(f"Correctly denied access to other subject")
        
        return True
        
    except Exception as e:
        print_error(f"Authorization test error: {e}")
        return False

def test_permission_chain(name, admin):
    """Verify complete permission chain in database"""
    print_info(f"\nVerifying permission chain for {name.upper()} admin...")
    
    try:
        conn = psycopg.connect(**DB_CONFIG)
        cur = conn.cursor()
        
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
            WHERE u."EMAIL" = %s
        """, (admin["email"],))
        
        result = cur.fetchone()
        
        if not result:
            print_error("Permission chain not found!")
            conn.close()
            return False
        
        print_success("Permission chain verified:")
        print_info(f"  User ID: {result[0]}")
        print_info(f"  Email: {result[1]}")
        print_info(f"  User SUBJECT_ID: {result[2]}")
        print_info(f"  Member of GROUP_ID: {result[3]}")
        print_info(f"  Group: {result[4]}")
        print_info(f"  Group controls: {result[5]}")
        print_info(f"  Subject ID: {result[6]}")
        print_info(f"  Subject: {result[7]}")
        
        # Verify consistency
        if result[2] != result[6]:
            print_error("Subject ID mismatch!")
            conn.close()
            return False
        
        if result[6] != admin["subject_id"]:
            print_error(f"Wrong subject ID: expected {admin['subject_id']}, got {result[6]}")
            conn.close()
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print_error(f"Permission chain verification failed: {e}")
        return False

def test_service_health():
    """Check if auth service is running"""
    print_header("Pre-Test: Service Health Check")
    
    try:
        response = requests.get(f"{AUTH_SERVICE_URL}/healthz", timeout=5)
        if response.status_code == 200:
            print_success(f"Auth service healthy: {response.json()}")
            return True
        else:
            print_error(f"Auth service unhealthy: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Cannot connect to auth service: {e}")
        return False

def main():
    """Main test function"""
    print_header("🔐 Mock Subject Admin Users Test Suite")
    
    # Check service health
    if not test_service_health():
        print_error("\n❌ Auth service not available. Start services with: docker-compose up -d")
        return False
    
    # Test database setup
    if not test_database_setup():
        print_error("\n❌ Database setup incomplete. Run migration: 014_add_mock_subject_admins.sql")
        return False
    
    # Test each admin
    all_tests_passed = True
    
    for name, admin in ADMINS.items():
        print_header(f"Testing {name.upper()} Administrator")
        
        # Test login
        session_id = test_admin_login(name, admin)
        if not session_id:
            all_tests_passed = False
            continue
        
        # Test authorization
        if not test_admin_authorization(name, admin, session_id):
            all_tests_passed = False
            continue
        
        # Verify permission chain
        if not test_permission_chain(name, admin):
            all_tests_passed = False
            continue
        
        print_success(f"\n✅ All tests passed for {name.upper()} admin")
    
    # Summary
    print_header("Test Summary")
    
    if all_tests_passed:
        print(f"{Colors.OKGREEN}{Colors.BOLD}✅ ALL TESTS PASSED!{Colors.ENDC}\n")
        print(f"{Colors.CYAN}Mock admin users are working correctly:{Colors.ENDC}")
        print(f"  ✅ UKNF admin can login and access UKNF subject")
        print(f"  ✅ Bank Pekao admin can login and access Bank Pekao subject")
        print(f"  ✅ Admins cannot access each other's subjects")
        print(f"  ✅ Permission chains are complete and correct")
        print(f"\n{Colors.BOLD}Admin Credentials:{Colors.ENDC}")
        print(f"  UKNF: admin_uknf@example.com / password123")
        print(f"  Bank Pekao: admin_pekao@example.com / password456")
        print(f"\n{Colors.WARNING}⚠️  Remember: Change passwords before production!{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}{Colors.BOLD}❌ SOME TESTS FAILED{Colors.ENDC}")
        print(f"\nCheck the errors above and verify:")
        print(f"  1. Migration 014 has been applied")
        print(f"  2. Auth service is running")
        print(f"  3. Database is accessible")
    
    return all_tests_passed

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Test interrupted by user{Colors.ENDC}")
        exit(130)
    except Exception as e:
        print(f"\n{Colors.FAIL}Test suite crashed: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        exit(1)

