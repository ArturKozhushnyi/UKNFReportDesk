BEGIN;

-- ============================================================================
-- Migration: 004_add_user_group_permissions.sql
-- Purpose: Add permissions for user-group association endpoint
-- ============================================================================

-- ============================================================================
-- Step 1: Define the Resource
-- ============================================================================

-- Insert the new resource for user-group association if it doesn't exist
INSERT INTO "RESOURCES" ("ID")
VALUES ('api:users:add_to_group')
ON CONFLICT ("ID") DO NOTHING;

-- ============================================================================
-- Step 2: Grant Administrator Permission
-- ============================================================================

-- Grant administrator group permission to the new resource
-- This uses a subquery to get the administrator group ID and ensures no duplicates
INSERT INTO "RESOURCES_ALLOW_LIST" ("RESOURCE_ID", "GROUP_ID")
SELECT 
    r."ID" as "RESOURCE_ID",
    g."ID" as "GROUP_ID"
FROM "RESOURCES" r
CROSS JOIN "GROUPS" g
WHERE g."GROUP_NAME" = 'administrator'
  AND r."ID" = 'api:users:add_to_group'
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
-- SELECT 'New Resource:' as info, "ID" FROM "RESOURCES" WHERE "ID" = 'api:users:add_to_group';
-- SELECT 'Admin Permission for User-Group:' as info, ral."RESOURCE_ID", ral."GROUP_ID", g."GROUP_NAME"
-- FROM "RESOURCES_ALLOW_LIST" ral
-- JOIN "GROUPS" g ON ral."GROUP_ID" = g."ID"
-- WHERE g."GROUP_NAME" = 'administrator' AND ral."RESOURCE_ID" = 'api:users:add_to_group';

COMMIT;
