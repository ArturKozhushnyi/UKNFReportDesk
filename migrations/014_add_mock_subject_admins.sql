BEGIN;

-- ============================================================================
-- Migration: 014_add_mock_subject_admins.sql
-- Purpose: Create dedicated admin users for UKNF and Bank Pekao subjects
-- Description: Sets up complete admin infrastructure (users, groups, resources, permissions)
-- ============================================================================

-- ============================================================================
-- UKNF Subject Administration Setup (Subject ID: 1)
-- ============================================================================

-- Step 1: Create admin group for UKNF
INSERT INTO "GROUPS" ("GROUP_NAME")
SELECT 'admins_of_UKNF'
WHERE NOT EXISTS (
    SELECT 1 FROM "GROUPS" WHERE "GROUP_NAME" = 'admins_of_UKNF'
);

-- Step 2: Create admin resource for UKNF subject
INSERT INTO "RESOURCES" ("ID")
SELECT 'subject:admin:1'
WHERE NOT EXISTS (
    SELECT 1 FROM "RESOURCES" WHERE "ID" = 'subject:admin:1'
);

-- Step 3: Link UKNF subject to its admin resource
UPDATE "SUBJECTS"
SET "RESOURCE_ID" = 'subject:admin:1'
WHERE "ID" = 1
  AND "RESOURCE_ID" IS NULL;

-- Step 4: Grant permission - link UKNF admin group to UKNF admin resource
INSERT INTO "RESOURCES_ALLOW_LIST" ("RESOURCE_ID", "GROUP_ID", "USER_ID")
SELECT 
    'subject:admin:1',
    g."ID",
    NULL
FROM "GROUPS" g
WHERE g."GROUP_NAME" = 'admins_of_UKNF'
  AND NOT EXISTS (
      SELECT 1 
      FROM "RESOURCES_ALLOW_LIST" ral
      WHERE ral."RESOURCE_ID" = 'subject:admin:1'
        AND ral."GROUP_ID" = g."ID"
  );

-- Step 5: Create UKNF admin user
-- Password: 'password123'
-- Hash: sha256_crypt with 535000 rounds
INSERT INTO "USERS" (
    "EMAIL",
    "PASSWORD_HASH",
    "USER_NAME",
    "USER_LASTNAME",
    "IS_USER_ACTIVE",
    "SUBJECT_ID",
    "UKNF_ID",
    "DATE_CREATE",
    "DATE_ACTRUALIZATION"
)
SELECT 
    'admin_uknf@example.com',
    '$5$rounds=535000$N42Av7Pqlfaybfnx$O9RVUM/Mj/rFh1LNEcFzkzDYfiaVerRm7j78qHKdSn0',
    'UKNF',
    'Administrator',
    true,
    1,  -- Subject ID for UKNF
    (SELECT "UKNF_ID" FROM "SUBJECTS" WHERE "ID" = 1),
    NOW(),
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM "USERS" WHERE "EMAIL" = 'admin_uknf@example.com'
);

-- Step 6: Add UKNF admin user to UKNF admin group
INSERT INTO "USERS_GROUPS" ("USER_ID", "GROUP_ID")
SELECT 
    u."ID",
    g."ID"
FROM "USERS" u
CROSS JOIN "GROUPS" g
WHERE u."EMAIL" = 'admin_uknf@example.com'
  AND g."GROUP_NAME" = 'admins_of_UKNF'
  AND NOT EXISTS (
      SELECT 1 
      FROM "USERS_GROUPS" ug 
      WHERE ug."USER_ID" = u."ID" 
        AND ug."GROUP_ID" = g."ID"
  );

-- ============================================================================
-- Bank Pekao Subject Administration Setup (Subject ID: 2)
-- ============================================================================

-- Step 7: Create admin group for Bank Pekao
INSERT INTO "GROUPS" ("GROUP_NAME")
SELECT 'admins_of_Bank_Polska_Kasa_Opieki_Spółka_Akcyjna'
WHERE NOT EXISTS (
    SELECT 1 
    FROM "GROUPS" 
    WHERE "GROUP_NAME" = 'admins_of_Bank_Polska_Kasa_Opieki_Spółka_Akcyjna'
);

-- Step 8: Create admin resource for Bank Pekao subject
INSERT INTO "RESOURCES" ("ID")
SELECT 'subject:admin:2'
WHERE NOT EXISTS (
    SELECT 1 FROM "RESOURCES" WHERE "ID" = 'subject:admin:2'
);

-- Step 9: Link Bank Pekao subject to its admin resource
UPDATE "SUBJECTS"
SET "RESOURCE_ID" = 'subject:admin:2'
WHERE "ID" = 2
  AND "RESOURCE_ID" IS NULL;

-- Step 10: Grant permission - link Bank Pekao admin group to Bank Pekao admin resource
INSERT INTO "RESOURCES_ALLOW_LIST" ("RESOURCE_ID", "GROUP_ID", "USER_ID")
SELECT 
    'subject:admin:2',
    g."ID",
    NULL
FROM "GROUPS" g
WHERE g."GROUP_NAME" = 'admins_of_Bank_Polska_Kasa_Opieki_Spółka_Akcyjna'
  AND NOT EXISTS (
      SELECT 1 
      FROM "RESOURCES_ALLOW_LIST" ral
      WHERE ral."RESOURCE_ID" = 'subject:admin:2'
        AND ral."GROUP_ID" = g."ID"
  );

-- Step 11: Create Bank Pekao admin user
-- Password: 'password456'
-- Hash: sha256_crypt with 535000 rounds
INSERT INTO "USERS" (
    "EMAIL",
    "PASSWORD_HASH",
    "USER_NAME",
    "USER_LASTNAME",
    "IS_USER_ACTIVE",
    "SUBJECT_ID",
    "UKNF_ID",
    "DATE_CREATE",
    "DATE_ACTRUALIZATION"
)
SELECT 
    'admin_pekao@example.com',
    '$5$rounds=535000$qnOdaNIg6QuuTIzk$UZg6WU4mYEwa9Dyejp9Q6KX2tCRGadWbA7Zbcm6d393',
    'Bank Pekao',
    'Administrator',
    true,
    2,  -- Subject ID for Bank Pekao
    (SELECT "UKNF_ID" FROM "SUBJECTS" WHERE "ID" = 2),
    NOW(),
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM "USERS" WHERE "EMAIL" = 'admin_pekao@example.com'
);

-- Step 12: Add Bank Pekao admin user to Bank Pekao admin group
INSERT INTO "USERS_GROUPS" ("USER_ID", "GROUP_ID")
SELECT 
    u."ID",
    g."ID"
FROM "USERS" u
CROSS JOIN "GROUPS" g
WHERE u."EMAIL" = 'admin_pekao@example.com'
  AND g."GROUP_NAME" = 'admins_of_Bank_Polska_Kasa_Opieki_Spółka_Akcyjna'
  AND NOT EXISTS (
      SELECT 1 
      FROM "USERS_GROUPS" ug 
      WHERE ug."USER_ID" = u."ID" 
        AND ug."GROUP_ID" = g."ID"
  );

-- ============================================================================
-- Verification Queries (for debugging - commented out)
-- ============================================================================

-- Uncomment to verify UKNF admin setup:
-- SELECT 
--     u."ID" as user_id,
--     u."EMAIL",
--     u."SUBJECT_ID",
--     g."GROUP_NAME",
--     ral."RESOURCE_ID",
--     s."NAME_STRUCTURE"
-- FROM "USERS" u
-- JOIN "USERS_GROUPS" ug ON u."ID" = ug."USER_ID"
-- JOIN "GROUPS" g ON ug."GROUP_ID" = g."ID"
-- JOIN "RESOURCES_ALLOW_LIST" ral ON g."ID" = ral."GROUP_ID"
-- JOIN "SUBJECTS" s ON ral."RESOURCE_ID" = s."RESOURCE_ID"
-- WHERE u."EMAIL" = 'admin_uknf@example.com';

-- Uncomment to verify Bank Pekao admin setup:
-- SELECT 
--     u."ID" as user_id,
--     u."EMAIL",
--     u."SUBJECT_ID",
--     g."GROUP_NAME",
--     ral."RESOURCE_ID",
--     s."NAME_STRUCTURE"
-- FROM "USERS" u
-- JOIN "USERS_GROUPS" ug ON u."ID" = ug."USER_ID"
-- JOIN "GROUPS" g ON ug."GROUP_ID" = g."ID"
-- JOIN "RESOURCES_ALLOW_LIST" ral ON g."ID" = ral."GROUP_ID"
-- JOIN "SUBJECTS" s ON ral."RESOURCE_ID" = s."RESOURCE_ID"
-- WHERE u."EMAIL" = 'admin_pekao@example.com';

-- Uncomment to see all admin groups and their resources:
-- SELECT 
--     g."GROUP_NAME",
--     ral."RESOURCE_ID",
--     s."ID" as subject_id,
--     s."NAME_STRUCTURE",
--     COUNT(ug."USER_ID") as member_count
-- FROM "GROUPS" g
-- JOIN "RESOURCES_ALLOW_LIST" ral ON g."ID" = ral."GROUP_ID"
-- LEFT JOIN "SUBJECTS" s ON ral."RESOURCE_ID" = s."RESOURCE_ID"
-- LEFT JOIN "USERS_GROUPS" ug ON g."ID" = ug."GROUP_ID"
-- WHERE g."GROUP_NAME" LIKE 'admins_of_%'
-- GROUP BY g."GROUP_NAME", ral."RESOURCE_ID", s."ID", s."NAME_STRUCTURE"
-- ORDER BY s."ID";

COMMIT;

-- ============================================================================
-- Post-Migration Notes
-- ============================================================================

-- Created Admin Users:
-- 1. admin_uknf@example.com
--    Password: password123
--    Subject: UKNF (ID: 1)
--    Group: admins_of_UKNF
--    Resource: subject:admin:1
--
-- 2. admin_pekao@example.com
--    Password: password456
--    Subject: Bank Polska Kasa Opieki S.A. (ID: 2)
--    Group: admins_of_Bank_Polska_Kasa_Opieki_Spółka_Akcyjna
--    Resource: subject:admin:2

-- Testing Login:
-- curl -X POST http://localhost:8001/authn \
--   -H "Content-Type: application/json" \
--   -d '{"email": "admin_uknf@example.com", "password": "password123"}'

-- curl -X POST http://localhost:8001/authn \
--   -H "Content-Type: application/json" \
--   -d '{"email": "admin_pekao@example.com", "password": "password456"}'

-- Testing Authorization:
-- # Get session_id from login, then:
-- curl -X POST http://localhost:8001/authz \
--   -H "Content-Type: application/json" \
--   -d '{"session_id": "<session_id>", "resource_id": "subject:admin:1"}'

-- ============================================================================
-- Idempotency Features
-- ============================================================================

-- This script is fully idempotent and can be run multiple times:
-- 1. All INSERTs use WHERE NOT EXISTS to prevent duplicates
-- 2. UPDATE uses condition to only update if RESOURCE_ID is NULL
-- 3. Dynamic ID lookups ensure correct relationships
-- 4. Entire script wrapped in transaction for atomicity
-- 5. No data is deleted or modified if it already exists

-- ============================================================================
-- Security Notes
-- ============================================================================

-- IMPORTANT: These are MOCK/TEST admin users for development purposes.
-- 
-- For production use:
-- 1. Change passwords immediately after deployment
-- 2. Use strong, unique passwords (not 'password123' or 'password456')
-- 3. Consider using temporary passwords with forced reset
-- 4. Enable MFA/2FA for admin accounts
-- 5. Regularly rotate admin credentials
-- 6. Monitor admin account activity
-- 7. Use these hashes were generated with sha256_crypt (passlib compatible)

-- Password Hash Generation (for reference):
-- from passlib.context import CryptContext
-- pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
-- hash1 = pwd_context.hash("password123")
-- hash2 = pwd_context.hash("password456")

