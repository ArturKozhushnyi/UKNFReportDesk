#!/usr/bin/env python3
"""
Test script for SUBJECTS audit trail system
Tests the automated history tracking for UPDATE and DELETE operations
"""

import psycopg
from datetime import datetime
import time

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "mydatabase",
    "user": "myuser",
    "password": "mysecretpassword"
}

class Colors:
    """ANSI color codes for terminal output"""
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
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"{msg}")
    print(f"{'='*60}{Colors.ENDC}")

def test_audit_system():
    """Main test function"""
    print_header("🔍 SUBJECTS Audit Trail System Test")
    
    try:
        # Connect to database
        print_info("Connecting to database...")
        conn = psycopg.connect(**DB_CONFIG)
        conn.autocommit = False
        
        with conn.cursor() as cur:
            # Test 1: Verify system installation
            print_header("Test 1: Verify System Installation")
            test_installation(cur)
            
            # Test 2: Test UPDATE operation with user context
            print_header("Test 2: UPDATE Operation with User Context")
            test_update_with_user(cur, conn)
            
            # Test 3: Test UPDATE operation without user context
            print_header("Test 3: UPDATE Operation without User Context")
            test_update_without_user(cur, conn)
            
            # Test 4: Test DELETE operation
            print_header("Test 4: DELETE Operation")
            test_delete_operation(cur, conn)
            
            # Test 5: Test multiple changes to same subject
            print_header("Test 5: Multiple Changes to Same Subject")
            test_multiple_changes(cur, conn)
            
            # Test 6: Query history data
            print_header("Test 6: Query History Data")
            test_query_history(cur)
            
        conn.close()
        print_header("🎉 All Tests Completed Successfully!")
        
    except Exception as e:
        print_error(f"Test failed with error: {e}")
        raise

def test_installation(cur):
    """Verify that the audit system is properly installed"""
    
    # Check if SUBJECTS_HISTORY table exists
    cur.execute("""
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
          AND table_name = 'SUBJECTS_HISTORY'
    """)
    if cur.fetchone()[0] == 1:
        print_success("SUBJECTS_HISTORY table exists")
    else:
        print_error("SUBJECTS_HISTORY table not found")
        return False
    
    # Check if trigger exists
    cur.execute("""
        SELECT COUNT(*) 
        FROM pg_trigger t
        JOIN pg_class c ON t.tgrelid = c.oid
        WHERE c.relname = 'SUBJECTS' 
          AND t.tgname = 'subjects_history_trigger'
    """)
    if cur.fetchone()[0] >= 1:
        print_success("subjects_history_trigger exists")
    else:
        print_error("subjects_history_trigger not found")
        return False
    
    # Check if function exists
    cur.execute("""
        SELECT COUNT(*) 
        FROM information_schema.routines 
        WHERE routine_schema = 'public' 
          AND routine_name = 'log_subjects_changes'
    """)
    if cur.fetchone()[0] == 1:
        print_success("log_subjects_changes() function exists")
    else:
        print_error("log_subjects_changes() function not found")
        return False
    
    # Check indexes
    cur.execute("""
        SELECT COUNT(*) 
        FROM pg_indexes 
        WHERE tablename = 'SUBJECTS_HISTORY'
    """)
    index_count = cur.fetchone()[0]
    print_success(f"Found {index_count} indexes on SUBJECTS_HISTORY")
    
    return True

def test_update_with_user(cur, conn):
    """Test UPDATE operation with user context"""
    
    try:
        # Create test subject
        print_info("Creating test subject...")
        cur.execute("""
            INSERT INTO "SUBJECTS" (
                "NAME_STRUCTURE", 
                "UKNF_ID", 
                "STATUS_S",
                "DATE_CREATE",
                "DATE_ACTRUALIZATION"
            )
            VALUES (
                'Test Subject 1', 
                'TEST_AUDIT_001', 
                'active',
                NOW(),
                NOW()
            )
            RETURNING "ID"
        """)
        subject_id = cur.fetchone()[0]
        conn.commit()
        print_success(f"Created test subject with ID: {subject_id}")
        
        # Set user context and update
        print_info("Setting user context and updating subject...")
        cur.execute("SET LOCAL app.current_user_id = 1")
        cur.execute("""
            UPDATE "SUBJECTS" 
            SET "NAME_STRUCTURE" = 'Modified Test Subject 1',
                "STATUS_S" = 'inactive'
            WHERE "ID" = %s
        """, (subject_id,))
        conn.commit()
        print_success("Updated subject")
        
        # Verify history record
        print_info("Checking history record...")
        cur.execute("""
            SELECT 
                "HISTORY_ID",
                "OPERATION_TYPE",
                "MODIFIED_BY",
                "ID",
                "NAME_STRUCTURE",
                "STATUS_S"
            FROM "SUBJECTS_HISTORY"
            WHERE "ID" = %s
            ORDER BY "MODIFIED_AT" DESC
            LIMIT 1
        """, (subject_id,))
        
        history = cur.fetchone()
        if history:
            print_success(f"History record created: HISTORY_ID={history[0]}")
            print_info(f"  Operation Type: {history[1]}")
            print_info(f"  Modified By: {history[2]}")
            print_info(f"  Old Name: {history[4]}")
            print_info(f"  Old Status: {history[5]}")
            
            # Verify fields
            assert history[1] == 'UPDATE', "Operation type should be UPDATE"
            assert history[2] == 1, "Modified by should be user 1"
            assert history[4] == 'Test Subject 1', "Old name should be preserved"
            assert history[5] == 'active', "Old status should be preserved"
            print_success("All assertions passed")
        else:
            print_error("No history record found")
            return False
        
        # Cleanup
        cur.execute('DELETE FROM "SUBJECTS" WHERE "ID" = %s', (subject_id,))
        cur.execute('DELETE FROM "SUBJECTS_HISTORY" WHERE "ID" = %s', (subject_id,))
        conn.commit()
        print_info("Cleaned up test data")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print_error(f"Test failed: {e}")
        raise

def test_update_without_user(cur, conn):
    """Test UPDATE operation without user context"""
    
    try:
        # Create test subject
        cur.execute("""
            INSERT INTO "SUBJECTS" (
                "NAME_STRUCTURE", 
                "UKNF_ID",
                "DATE_CREATE",
                "DATE_ACTRUALIZATION"
            )
            VALUES (
                'Test Subject 2', 
                'TEST_AUDIT_002',
                NOW(),
                NOW()
            )
            RETURNING "ID"
        """)
        subject_id = cur.fetchone()[0]
        conn.commit()
        print_success(f"Created test subject with ID: {subject_id}")
        
        # Update without setting user context
        print_info("Updating subject without user context...")
        cur.execute("""
            UPDATE "SUBJECTS" 
            SET "NAME_STRUCTURE" = 'Modified Without User'
            WHERE "ID" = %s
        """, (subject_id,))
        conn.commit()
        print_success("Updated subject")
        
        # Verify history record
        cur.execute("""
            SELECT "OPERATION_TYPE", "MODIFIED_BY"
            FROM "SUBJECTS_HISTORY"
            WHERE "ID" = %s
        """, (subject_id,))
        
        history = cur.fetchone()
        if history:
            print_success("History record created")
            print_info(f"  Operation Type: {history[0]}")
            print_info(f"  Modified By: {history[1] if history[1] else 'NULL (as expected)'}")
            
            assert history[0] == 'UPDATE', "Operation type should be UPDATE"
            assert history[1] is None, "Modified by should be NULL when context not set"
            print_success("MODIFIED_BY is correctly NULL")
        else:
            print_error("No history record found")
            return False
        
        # Cleanup
        cur.execute('DELETE FROM "SUBJECTS" WHERE "ID" = %s', (subject_id,))
        cur.execute('DELETE FROM "SUBJECTS_HISTORY" WHERE "ID" = %s', (subject_id,))
        conn.commit()
        
        return True
        
    except Exception as e:
        conn.rollback()
        print_error(f"Test failed: {e}")
        raise

def test_delete_operation(cur, conn):
    """Test DELETE operation"""
    
    try:
        # Create test subject
        cur.execute("""
            INSERT INTO "SUBJECTS" (
                "NAME_STRUCTURE", 
                "UKNF_ID",
                "EMAIL",
                "PHONE",
                "DATE_CREATE",
                "DATE_ACTRUALIZATION"
            )
            VALUES (
                'Subject To Delete', 
                'TEST_AUDIT_003',
                'delete@test.com',
                '+48 123 456 789',
                NOW(),
                NOW()
            )
            RETURNING "ID"
        """)
        subject_id = cur.fetchone()[0]
        conn.commit()
        print_success(f"Created test subject with ID: {subject_id}")
        
        # Delete with user context
        print_info("Deleting subject with user context...")
        cur.execute("SET LOCAL app.current_user_id = 1")
        cur.execute('DELETE FROM "SUBJECTS" WHERE "ID" = %s', (subject_id,))
        conn.commit()
        print_success("Deleted subject")
        
        # Verify subject is deleted
        cur.execute('SELECT COUNT(*) FROM "SUBJECTS" WHERE "ID" = %s', (subject_id,))
        if cur.fetchone()[0] == 0:
            print_success("Subject successfully deleted from main table")
        else:
            print_error("Subject still exists in main table")
            return False
        
        # Verify history record exists
        cur.execute("""
            SELECT 
                "OPERATION_TYPE",
                "MODIFIED_BY",
                "NAME_STRUCTURE",
                "EMAIL",
                "PHONE"
            FROM "SUBJECTS_HISTORY"
            WHERE "ID" = %s
        """, (subject_id,))
        
        history = cur.fetchone()
        if history:
            print_success("History record preserved after deletion")
            print_info(f"  Operation Type: {history[0]}")
            print_info(f"  Modified By: {history[1]}")
            print_info(f"  Name: {history[2]}")
            print_info(f"  Email: {history[3]}")
            print_info(f"  Phone: {history[4]}")
            
            assert history[0] == 'DELETE', "Operation type should be DELETE"
            assert history[1] == 1, "Modified by should be user 1"
            assert history[2] == 'Subject To Delete', "Name should be preserved"
            print_success("All data preserved correctly in history")
        else:
            print_error("No history record found")
            return False
        
        # Cleanup history
        cur.execute('DELETE FROM "SUBJECTS_HISTORY" WHERE "ID" = %s', (subject_id,))
        conn.commit()
        
        return True
        
    except Exception as e:
        conn.rollback()
        print_error(f"Test failed: {e}")
        raise

def test_multiple_changes(cur, conn):
    """Test multiple changes to the same subject"""
    
    try:
        # Create test subject
        cur.execute("""
            INSERT INTO "SUBJECTS" (
                "NAME_STRUCTURE", 
                "UKNF_ID", 
                "STATUS_S",
                "DATE_CREATE",
                "DATE_ACTRUALIZATION"
            )
            VALUES (
                'Multi Change Subject', 
                'TEST_AUDIT_004', 
                'pending',
                NOW(),
                NOW()
            )
            RETURNING "ID"
        """)
        subject_id = cur.fetchone()[0]
        conn.commit()
        print_success(f"Created test subject with ID: {subject_id}")
        
        # Perform multiple updates
        changes = [
            ('active', 'First update'),
            ('inactive', 'Second update'),
            ('active', 'Third update')
        ]
        
        for i, (status, desc) in enumerate(changes, 1):
            print_info(f"Change {i}: {desc}")
            cur.execute("SET LOCAL app.current_user_id = 1")
            cur.execute("""
                UPDATE "SUBJECTS" 
                SET "STATUS_S" = %s
                WHERE "ID" = %s
            """, (status, subject_id))
            conn.commit()
            time.sleep(0.1)  # Small delay to ensure different timestamps
        
        print_success("Completed 3 updates")
        
        # Verify history count
        cur.execute("""
            SELECT COUNT(*) 
            FROM "SUBJECTS_HISTORY" 
            WHERE "ID" = %s
        """, (subject_id,))
        
        count = cur.fetchone()[0]
        print_info(f"Found {count} history records")
        
        if count == 3:
            print_success("Correct number of history records")
        else:
            print_error(f"Expected 3 records, found {count}")
            return False
        
        # Verify chronological order
        cur.execute("""
            SELECT "STATUS_S", "MODIFIED_AT"
            FROM "SUBJECTS_HISTORY"
            WHERE "ID" = %s
            ORDER BY "MODIFIED_AT" ASC
        """, (subject_id,))
        
        history_records = cur.fetchall()
        expected_statuses = ['pending', 'active', 'inactive']
        
        print_info("Verifying chronological order...")
        for i, (status, modified_at) in enumerate(history_records):
            if status == expected_statuses[i]:
                print_success(f"  Record {i+1}: Status '{status}' at {modified_at}")
            else:
                print_error(f"  Record {i+1}: Expected '{expected_statuses[i]}', got '{status}'")
                return False
        
        # Cleanup
        cur.execute('DELETE FROM "SUBJECTS" WHERE "ID" = %s', (subject_id,))
        cur.execute('DELETE FROM "SUBJECTS_HISTORY" WHERE "ID" = %s', (subject_id,))
        conn.commit()
        
        return True
        
    except Exception as e:
        conn.rollback()
        print_error(f"Test failed: {e}")
        raise

def test_query_history(cur):
    """Test various history queries"""
    
    print_info("Testing history query patterns...")
    
    # Query 1: Recent changes
    print_info("\n1. Querying recent changes (last 24 hours)...")
    cur.execute("""
        SELECT 
            COUNT(*) as change_count
        FROM "SUBJECTS_HISTORY"
        WHERE "MODIFIED_AT" >= NOW() - INTERVAL '24 hours'
    """)
    count = cur.fetchone()[0]
    print_success(f"   Found {count} changes in last 24 hours")
    
    # Query 2: Changes by operation type
    print_info("\n2. Grouping by operation type...")
    cur.execute("""
        SELECT 
            "OPERATION_TYPE",
            COUNT(*) as count
        FROM "SUBJECTS_HISTORY"
        GROUP BY "OPERATION_TYPE"
        ORDER BY count DESC
    """)
    for op_type, count in cur.fetchall():
        print_success(f"   {op_type}: {count} operations")
    
    # Query 3: Most modified subjects
    print_info("\n3. Finding most modified subjects...")
    cur.execute("""
        SELECT 
            "ID",
            COUNT(*) as modification_count
        FROM "SUBJECTS_HISTORY"
        GROUP BY "ID"
        ORDER BY modification_count DESC
        LIMIT 5
    """)
    results = cur.fetchall()
    if results:
        for subject_id, mod_count in results:
            print_success(f"   Subject {subject_id}: {mod_count} modifications")
    else:
        print_info("   No history records yet")
    
    # Query 4: Index usage
    print_info("\n4. Checking index statistics...")
    cur.execute("""
        SELECT 
            indexrelname as indexname,
            idx_scan as index_scans,
            idx_tup_read as tuples_read
        FROM pg_stat_user_indexes
        WHERE relname = 'SUBJECTS_HISTORY'
        ORDER BY idx_scan DESC
    """)
    for idx_name, scans, tuples in cur.fetchall():
        print_success(f"   {idx_name}: {scans} scans, {tuples} tuples read")
    
    return True

if __name__ == "__main__":
    try:
        test_audit_system()
    except KeyboardInterrupt:
        print_error("\n\nTest interrupted by user")
    except Exception as e:
        print_error(f"\n\nTest suite failed: {e}")
        import traceback
        traceback.print_exc()

