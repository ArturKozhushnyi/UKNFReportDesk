BEGIN;

-- ============================================================================
-- Migration: 002_add_admin_permissions.sql
-- Purpose: Create administrator group and define API resources with permissions
-- ============================================================================

-- ============================================================================
-- Step 1: Create Administrator Group
-- ============================================================================

-- Insert administrator group if it doesn't exist
INSERT INTO "GROUPS" ("GROUP_NAME")
SELECT 'administrator'
WHERE NOT EXISTS (
    SELECT 1 FROM "GROUPS" WHERE "GROUP_NAME" = 'administrator'
);

-- ============================================================================
-- Step 2: Define API Resources
-- ============================================================================

-- Insert API resources if they don't exist
INSERT INTO "RESOURCES" ("ID")
VALUES 
    ('api:subjects:create'),
    ('api:subjects:read'),
    ('api:users:read')
ON CONFLICT ("ID") DO NOTHING;

-- ============================================================================
-- Step 3: Grant Administrator Permissions
-- ============================================================================

-- Grant administrator group permission to all API resources
-- This uses a subquery to get the administrator group ID and ensures no duplicates
INSERT INTO "RESOURCES_ALLOW_LIST" ("RESOURCE_ID", "GROUP_ID")
SELECT 
    r."ID" as "RESOURCE_ID",
    g."ID" as "GROUP_ID"
FROM "RESOURCES" r
CROSS JOIN "GROUPS" g
WHERE g."GROUP_NAME" = 'administrator'
  AND r."ID" IN ('api:subjects:create', 'api:subjects:read', 'api:users:read')
  AND NOT EXISTS (
      -- Check if this permission already exists
      SELECT 1 
      FROM "RESOURCES_ALLOW_LIST" ral 
      WHERE ral."RESOURCE_ID" = r."ID" 
        AND ral."GROUP_ID" = g."ID"
  );

-- ============================================================================
-- Verification Queries (for debugging - can be removed in production)
-- ============================================================================

-- Uncomment these queries to verify the migration results:
-- SELECT 'Administrator Group:' as info, "ID", "GROUP_NAME" FROM "GROUPS" WHERE "GROUP_NAME" = 'administrator';
-- SELECT 'API Resources:' as info, "ID" FROM "RESOURCES" WHERE "ID" LIKE 'api:%';
-- SELECT 'Admin Permissions:' as info, ral."RESOURCE_ID", ral."GROUP_ID", g."GROUP_NAME"
-- FROM "RESOURCES_ALLOW_LIST" ral
-- JOIN "GROUPS" g ON ral."GROUP_ID" = g."ID"
-- WHERE g."GROUP_NAME" = 'administrator';

COMMIT;
