#!/usr/bin/env python3
"""
Test Script for Subject Management Feature
Tests subject editing and history tracking functionality
"""

import requests
import json
import time
from datetime import datetime


# Configuration
BASE_URL = "http://localhost:3000"
AUTH_URL = f"{BASE_URL}/auth"
ADMIN_URL = f"{BASE_URL}/admin"

# Test credentials
UKNF_ADMIN = {
    "email": "admin_uknf@example.com",
    "password": "password123"
}

PEKAO_ADMIN = {
    "email": "admin_pekao@example.com",
    "password": "password456"
}

# ANSI color codes for pretty output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print a styled header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.YELLOW}ℹ {text}{Colors.RESET}")


def login(credentials):
    """Login and return session_id"""
    try:
        response = requests.post(
            f"{AUTH_URL}/authn",
            json=credentials,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get('session_id')
            print_success(f"Logged in as {credentials['email']}")
            return session_id
        else:
            print_error(f"Login failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Login error: {str(e)}")
        return None


def get_subject(session_id, subject_id):
    """Get subject details"""
    try:
        response = requests.get(
            f"{ADMIN_URL}/subjects/{subject_id}",
            headers={"Authorization": f"Bearer {session_id}"},
            timeout=5
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print_error(f"Failed to get subject: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Error getting subject: {str(e)}")
        return None


def update_subject(session_id, subject_id, updates):
    """Update subject details"""
    try:
        response = requests.put(
            f"{ADMIN_URL}/subjects/{subject_id}",
            headers={
                "Authorization": f"Bearer {session_id}",
                "Content-Type": "application/json"
            },
            json=updates,
            timeout=5
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print_error(f"Failed to update subject: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Error updating subject: {str(e)}")
        return None


def get_subject_history(session_id, subject_id):
    """Get subject change history"""
    try:
        response = requests.get(
            f"{ADMIN_URL}/subjects/{subject_id}/history",
            headers={"Authorization": f"Bearer {session_id}"},
            timeout=5
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print_error(f"Failed to get history: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Error getting history: {str(e)}")
        return None


def test_authorized_edit():
    """Test 1: Authorized user can edit their own subject"""
    print_header("TEST 1: Authorized Subject Edit")
    
    # Login as UKNF admin
    session_id = login(UKNF_ADMIN)
    if not session_id:
        return False
    
    subject_id = 1  # UKNF subject
    
    # Get initial subject state
    print_info("Getting initial subject state...")
    initial_subject = get_subject(session_id, subject_id)
    if not initial_subject:
        return False
    
    print(f"   Initial Phone: {initial_subject.get('PHONE')}")
    print(f"   Initial Email: {initial_subject.get('EMAIL')}")
    
    # Prepare updates
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    updates = {
        "PHONE": f"+48 22 TEST {timestamp}",
        "EMAIL": f"test_{timestamp}@uknf.gov.pl",
        "STREET": f"Test Street {timestamp}"
    }
    
    print_info(f"Updating subject with new values...")
    updated_subject = update_subject(session_id, subject_id, updates)
    if not updated_subject:
        return False
    
    print_success("Subject updated successfully!")
    print(f"   New Phone: {updated_subject.get('PHONE')}")
    print(f"   New Email: {updated_subject.get('EMAIL')}")
    print(f"   New Street: {updated_subject.get('STREET')}")
    
    # Verify changes
    if (updated_subject.get('PHONE') == updates['PHONE'] and
        updated_subject.get('EMAIL') == updates['EMAIL'] and
        updated_subject.get('STREET') == updates['STREET']):
        print_success("All fields updated correctly!")
        return True
    else:
        print_error("Field values don't match updates!")
        return False


def test_unauthorized_edit():
    """Test 2: Unauthorized user cannot edit another subject"""
    print_header("TEST 2: Unauthorized Subject Edit (Should Fail)")
    
    # Login as Pekao admin
    session_id = login(PEKAO_ADMIN)
    if not session_id:
        return False
    
    uknf_subject_id = 1  # Try to edit UKNF subject
    
    # Try to update UKNF subject
    print_info("Attempting to edit UKNF subject as Pekao admin...")
    updates = {
        "PHONE": "UNAUTHORIZED CHANGE"
    }
    
    result = update_subject(session_id, uknf_subject_id, updates)
    
    if result is None:
        print_success("Update correctly denied! Authorization working.")
        return True
    else:
        print_error("SECURITY ISSUE: Unauthorized user was able to edit subject!")
        return False


def test_history_tracking():
    """Test 3: History tracking captures all changes"""
    print_header("TEST 3: History Tracking")
    
    # Login as UKNF admin
    session_id = login(UKNF_ADMIN)
    if not session_id:
        return False
    
    subject_id = 1
    
    # Get initial history count
    print_info("Getting initial history...")
    initial_history = get_subject_history(session_id, subject_id)
    if initial_history is None:
        return False
    
    initial_count = len(initial_history)
    print(f"   Initial history records: {initial_count}")
    
    # Make first update
    print_info("Making first update...")
    time.sleep(1)  # Small delay to ensure different timestamps
    timestamp1 = datetime.now().strftime("%Y%m%d_%H%M%S_1")
    updates1 = {
        "PHONE": f"+48 22 UPDATE1 {timestamp1}",
    }
    updated1 = update_subject(session_id, subject_id, updates1)
    if not updated1:
        return False
    print_success(f"First update applied: {updates1['PHONE']}")
    
    # Make second update
    print_info("Making second update...")
    time.sleep(1)
    timestamp2 = datetime.now().strftime("%Y%m%d_%H%M%S_2")
    updates2 = {
        "PHONE": f"+48 22 UPDATE2 {timestamp2}",
        "EMAIL": f"update2_{timestamp2}@test.com"
    }
    updated2 = update_subject(session_id, subject_id, updates2)
    if not updated2:
        return False
    print_success(f"Second update applied: {updates2['PHONE']}, {updates2['EMAIL']}")
    
    # Get updated history
    print_info("Retrieving updated history...")
    time.sleep(1)  # Give trigger time to execute
    final_history = get_subject_history(session_id, subject_id)
    if final_history is None:
        return False
    
    final_count = len(final_history)
    new_records = final_count - initial_count
    
    print(f"   Final history records: {final_count}")
    print(f"   New records added: {new_records}")
    
    if new_records >= 2:
        print_success(f"History tracking working! {new_records} new records captured.")
        
        # Display latest history entries
        print_info("Latest history entries:")
        for i, record in enumerate(final_history[:3]):
            print(f"\n   Entry {i+1}:")
            print(f"      Operation: {record.get('OPERATION_TYPE')}")
            print(f"      Modified At: {record.get('MODIFIED_AT')}")
            print(f"      Modified By: User ID {record.get('MODIFIED_BY')}")
            print(f"      Old Phone: {record.get('PHONE')}")
            print(f"      Old Email: {record.get('EMAIL')}")
        
        return True
    else:
        print_error(f"Expected at least 2 new history records, got {new_records}")
        return False


def test_history_contains_user_id():
    """Test 4: History records contain the user ID who made changes"""
    print_header("TEST 4: History Contains User ID")
    
    # Login as UKNF admin
    session_id = login(UKNF_ADMIN)
    if not session_id:
        return False
    
    subject_id = 1
    
    # Get history
    print_info("Retrieving history...")
    history = get_subject_history(session_id, subject_id)
    if not history:
        return False
    
    # Check if recent records have MODIFIED_BY field
    records_with_user_id = [r for r in history if r.get('MODIFIED_BY') is not None]
    
    print(f"   Total history records: {len(history)}")
    print(f"   Records with user ID: {len(records_with_user_id)}")
    
    if len(records_with_user_id) > 0:
        print_success("User ID tracking is working!")
        print_info("Sample record with user ID:")
        sample = records_with_user_id[0]
        print(f"   Modified By: User ID {sample.get('MODIFIED_BY')}")
        print(f"   Modified At: {sample.get('MODIFIED_AT')}")
        print(f"   Operation: {sample.get('OPERATION_TYPE')}")
        return True
    else:
        print_error("No history records contain user ID!")
        return False


def test_partial_updates():
    """Test 5: Partial updates only change specified fields"""
    print_header("TEST 5: Partial Updates")
    
    # Login as UKNF admin
    session_id = login(UKNF_ADMIN)
    if not session_id:
        return False
    
    subject_id = 1
    
    # Get current state
    print_info("Getting current subject state...")
    before = get_subject(session_id, subject_id)
    if not before:
        return False
    
    original_email = before.get('EMAIL')
    original_street = before.get('STREET')
    
    print(f"   Current Email: {original_email}")
    print(f"   Current Street: {original_street}")
    
    # Update only phone number
    print_info("Updating only phone number...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    updates = {
        "PHONE": f"+48 22 PARTIAL {timestamp}"
    }
    
    updated = update_subject(session_id, subject_id, updates)
    if not updated:
        return False
    
    # Verify other fields unchanged
    if (updated.get('EMAIL') == original_email and
        updated.get('STREET') == original_street and
        updated.get('PHONE') == updates['PHONE']):
        print_success("Partial update successful!")
        print(f"   ✓ Phone changed to: {updated.get('PHONE')}")
        print(f"   ✓ Email unchanged: {updated.get('EMAIL')}")
        print(f"   ✓ Street unchanged: {updated.get('STREET')}")
        return True
    else:
        print_error("Other fields were unexpectedly modified!")
        return False


def run_all_tests():
    """Run all test cases"""
    print_header("SUBJECT MANAGEMENT FEATURE - TEST SUITE")
    print(f"{Colors.CYAN}Testing backend subject editing and history tracking{Colors.RESET}")
    print(f"{Colors.CYAN}Base URL: {BASE_URL}{Colors.RESET}\n")
    
    tests = [
        ("Authorized Edit", test_authorized_edit),
        ("Unauthorized Edit (Security)", test_unauthorized_edit),
        ("History Tracking", test_history_tracking),
        ("User ID in History", test_history_contains_user_id),
        ("Partial Updates", test_partial_updates),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test crashed: {str(e)}")
            results.append((test_name, False))
        
        time.sleep(1)  # Small delay between tests
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.RESET}")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED!{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    import sys
    exit_code = run_all_tests()
    sys.exit(exit_code)

