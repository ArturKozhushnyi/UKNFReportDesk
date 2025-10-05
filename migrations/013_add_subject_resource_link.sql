BEGIN;

-- ============================================================================
-- Migration: 013_add_subject_resource_link.sql
-- Purpose: Add resource-based access control for subject-level permissions
-- Description: Links each subject to a unique resource for multi-tenant security
-- ============================================================================

-- ============================================================================
-- Step 1: Add RESOURCE_ID Column to SUBJECTS Table
-- ============================================================================

DO $$
BEGIN
    -- Check if the RESOURCE_ID column already exists
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'SUBJECTS' 
          AND column_name = 'RESOURCE_ID'
          AND table_schema = 'public'
    ) THEN
        -- Add the RESOURCE_ID column
        ALTER TABLE "SUBJECTS" 
        ADD COLUMN "RESOURCE_ID" VARCHAR(50);
        
        RAISE NOTICE 'Column RESOURCE_ID added to SUBJECTS table';
    ELSE
        RAISE NOTICE 'Column RESOURCE_ID already exists in SUBJECTS table';
    END IF;
END $$;

-- ============================================================================
-- Step 2: Add Foreign Key Constraint
-- ============================================================================

DO $$
BEGIN
    -- Check if the foreign key constraint already exists
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_constraint 
        WHERE conname = 'SUBJECTS_RESOURCE_ID_FK'
    ) THEN
        -- Add foreign key constraint
        ALTER TABLE "SUBJECTS" 
        ADD CONSTRAINT "SUBJECTS_RESOURCE_ID_FK" 
        FOREIGN KEY ("RESOURCE_ID") 
        REFERENCES "RESOURCES"("ID") 
        ON DELETE SET NULL;
        
        RAISE NOTICE 'Foreign key constraint SUBJECTS_RESOURCE_ID_FK added';
    ELSE
        RAISE NOTICE 'Foreign key constraint SUBJECTS_RESOURCE_ID_FK already exists';
    END IF;
END $$;

-- ============================================================================
-- Step 3: Add Index for Performance
-- ============================================================================

CREATE INDEX IF NOT EXISTS "IDX_SUBJECTS_RESOURCE_ID" 
    ON "SUBJECTS"("RESOURCE_ID");

-- ============================================================================
-- Step 4: Add Comments for Documentation
-- ============================================================================

COMMENT ON COLUMN "SUBJECTS"."RESOURCE_ID" IS 
    'Links subject to a resource for access control. Format: subject:admin:<subject_id>';

-- ============================================================================
-- Verification Queries (for debugging - commented out)
-- ============================================================================

-- Uncomment to verify the migration:
-- SELECT 
--     column_name, 
--     data_type, 
--     is_nullable,
--     column_default
-- FROM information_schema.columns 
-- WHERE table_name = 'SUBJECTS' 
--   AND column_name = 'RESOURCE_ID'
--   AND table_schema = 'public';

-- -- Check foreign key constraint
-- SELECT 
--     conname,
--     contype,
--     confrelid::regclass AS foreign_table
-- FROM pg_constraint 
-- WHERE conname = 'SUBJECTS_RESOURCE_ID_FK';

-- ============================================================================
-- Usage Examples
-- ============================================================================

-- Example 1: Create a subject with linked resource
-- -- First, create the resource
-- INSERT INTO "RESOURCES" ("ID") 
-- VALUES ('subject:admin:1');
-- 
-- -- Then, create or update the subject
-- INSERT INTO "SUBJECTS" (
--     "NAME_STRUCTURE", 
--     "UKNF_ID",
--     "RESOURCE_ID",
--     "DATE_CREATE"
-- )
-- VALUES (
--     'Test Company', 
--     'UKNF-001',
--     'subject:admin:1',
--     NOW()
-- );

-- Example 2: Grant a group admin access to a subject
-- -- The group gets permission to the subject's resource
-- INSERT INTO "RESOURCES_ALLOW_LIST" (
--     "RESOURCE_ID",
--     "GROUP_ID"
-- )
-- VALUES (
--     'subject:admin:1',
--     5  -- Admin group ID
-- );

-- Example 3: Query subjects with their admin resources
-- SELECT 
--     s."ID",
--     s."NAME_STRUCTURE",
--     s."RESOURCE_ID",
--     r."ID" as resource_exists
-- FROM "SUBJECTS" s
-- LEFT JOIN "RESOURCES" r ON s."RESOURCE_ID" = r."ID"
-- ORDER BY s."ID";

-- Example 4: Find all groups that can administer a subject
-- SELECT 
--     s."ID" as subject_id,
--     s."NAME_STRUCTURE",
--     g."ID" as group_id,
--     g."GROUP_NAME"
-- FROM "SUBJECTS" s
-- JOIN "RESOURCES_ALLOW_LIST" ral ON s."RESOURCE_ID" = ral."RESOURCE_ID"
-- JOIN "GROUPS" g ON ral."GROUP_ID" = g."ID"
-- WHERE s."ID" = 1;

-- Example 5: Find all subjects a user can administer
-- SELECT DISTINCT
--     s."ID" as subject_id,
--     s."NAME_STRUCTURE",
--     s."UKNF_ID"
-- FROM "SUBJECTS" s
-- JOIN "RESOURCES_ALLOW_LIST" ral ON s."RESOURCE_ID" = ral."RESOURCE_ID"
-- JOIN "USERS_GROUPS" ug ON ral."GROUP_ID" = ug."GROUP_ID"
-- WHERE ug."USER_ID" = 1;  -- Replace with actual user ID

COMMIT;

-- ============================================================================
-- Post-Migration Notes
-- ============================================================================

-- 1. Multi-Tenant Security Model:
--    Each subject now has a dedicated resource (subject:admin:<id>)
--    Groups can be granted permission to manage specific subjects
--    Users become admins of subjects by joining the appropriate group

-- 2. Resource Naming Convention:
--    Format: 'subject:admin:<subject_id>'
--    Example: 'subject:admin:123' for subject ID 123
--    This pattern allows for easy identification and management

-- 3. Permission Flow:
--    SUBJECT → has → RESOURCE_ID
--    RESOURCE → listed in → RESOURCES_ALLOW_LIST
--    GROUP → linked via → RESOURCES_ALLOW_LIST
--    USER → member of → GROUP (via USERS_GROUPS)
--    Therefore: USER can administer SUBJECT

-- 4. Automatic Setup (in application):
--    When a new user registers:
--    a) Create new subject
--    b) Create resource 'subject:admin:<subject_id>'
--    c) Link subject to resource
--    d) Create admin group 'admins_of_subject_<subject_id>'
--    e) Grant group permission to resource
--    f) Add user to admin group
--    Result: User is automatically admin of their own subject

-- 5. Performance Considerations:
--    - Index on RESOURCE_ID for fast lookups
--    - Nullable to support legacy subjects without resources
--    - ON DELETE SET NULL preserves subject data if resource deleted

-- 6. Migration Strategy:
--    - Existing subjects will have NULL RESOURCE_ID
--    - Can be backfilled later if needed
--    - New subjects will automatically get resources assigned

