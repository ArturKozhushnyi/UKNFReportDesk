BEGIN;

-- ============================================================================
-- Migration: 005_add_default_admin_user.sql
-- Purpose: Create default administrator user and assign to administrator group
-- ============================================================================

-- ============================================================================
-- Step 1: Create Default Administrator User
-- ============================================================================

-- Insert the default admin user if it doesn't exist
-- Password: 'admin' (hashed with sha256_crypt)
-- Hash: $5$rounds=535000$fWhbdoj5oqsLxqiB$e0fXgoukkr7Qe.IV3vOYP0jyTMhnXyeL8faco8Z3hyD
INSERT INTO "USERS" (
    "EMAIL",
    "PASSWORD_HASH",
    "USER_NAME",
    "USER_LASTNAME",
    "IS_USER_ACTIVE",
    "DATE_CREATE",
    "DATE_ACTRUALIZATION"
)
SELECT 
    'admin@example.com',
    '$5$rounds=535000$fWhbdoj5oqsLxqiB$e0fXgoukkr7Qe.IV3vOYP0jyTMhnXyeL8faco8Z3hyD',
    'Default',
    'Administrator',
    true,
    NOW(),
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM "USERS" WHERE "EMAIL" = 'admin@example.com'
);

-- ============================================================================
-- Step 2: Assign Admin User to Administrator Group
-- ============================================================================

-- Add the admin user to the administrator group
-- This uses subqueries to get the user ID and group ID dynamically
INSERT INTO "USERS_GROUPS" ("USER_ID", "GROUP_ID")
SELECT 
    u."ID" as "USER_ID",
    g."ID" as "GROUP_ID"
FROM "USERS" u
CROSS JOIN "GROUPS" g
WHERE u."EMAIL" = 'admin@example.com'
  AND g."GROUP_NAME" = 'administrator'
  AND NOT EXISTS (
      -- Check if this user-group assignment already exists
      SELECT 1 
      FROM "USERS_GROUPS" ug 
      WHERE ug."USER_ID" = u."ID" 
        AND ug."GROUP_ID" = g."ID"
  );

-- ============================================================================
-- Verification Queries (for debugging - can be removed in production)
-- ============================================================================

-- Uncomment these queries to verify the migration results:
-- SELECT 'Admin User:' as info, "ID", "EMAIL", "USER_NAME", "USER_LASTNAME", "IS_USER_ACTIVE" 
-- FROM "USERS" WHERE "EMAIL" = 'admin@example.com';
-- SELECT 'Admin User-Group Assignment:' as info, ug."USER_ID", ug."GROUP_ID", u."EMAIL", g."GROUP_NAME"
-- FROM "USERS_GROUPS" ug
-- JOIN "USERS" u ON ug."USER_ID" = u."ID"
-- JOIN "GROUPS" g ON ug."GROUP_ID" = g."ID"
-- WHERE u."EMAIL" = 'admin@example.com' AND g."GROUP_NAME" = 'administrator';

COMMIT;
