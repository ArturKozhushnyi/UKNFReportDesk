BEGIN;

-- ============================================================================
-- Migration: 010_add_subject_id_to_users.sql
-- Purpose: Add SUBJECT_ID foreign key column to USERS table
-- ============================================================================

-- ============================================================================
-- Add SUBJECT_ID Column to USERS Table
-- ============================================================================

-- Add the SUBJECT_ID column if it doesn't already exist
-- This uses a DO block to check for column existence before adding it
DO $$
BEGIN
    -- Check if the SUBJECT_ID column already exists
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'USERS' 
          AND column_name = 'SUBJECT_ID'
          AND table_schema = 'public'
    ) THEN
        -- Add the SUBJECT_ID column with the specified properties
        ALTER TABLE "USERS" 
        ADD COLUMN "SUBJECT_ID" BIGINT;
        
        -- Log the operation
        RAISE NOTICE 'Column SUBJECT_ID added to USERS table';
    ELSE
        -- Column already exists, log this information
        RAISE NOTICE 'Column SUBJECT_ID already exists in USERS table';
    END IF;
END $$;

-- ============================================================================
-- Add Foreign Key Constraint
-- ============================================================================

-- Add foreign key constraint if it doesn't exist
DO $$
BEGIN
    -- Check if the foreign key constraint already exists
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.table_constraints 
        WHERE constraint_name = 'USERS_SUBJECT_ID_FK'
          AND table_name = 'USERS'
          AND table_schema = 'public'
    ) THEN
        -- Add the foreign key constraint
        ALTER TABLE "USERS" 
        ADD CONSTRAINT "USERS_SUBJECT_ID_FK" 
        FOREIGN KEY ("SUBJECT_ID") 
        REFERENCES "SUBJECTS"("ID") 
        ON DELETE SET NULL;
        
        -- Log the operation
        RAISE NOTICE 'Foreign key constraint USERS_SUBJECT_ID_FK added';
    ELSE
        -- Constraint already exists, log this information
        RAISE NOTICE 'Foreign key constraint USERS_SUBJECT_ID_FK already exists';
    END IF;
END $$;

-- ============================================================================
-- Add Index for Performance
-- ============================================================================

-- Add index for SUBJECT_ID if it doesn't exist
CREATE INDEX IF NOT EXISTS "IDX_USERS_SUBJECT_ID" 
    ON "USERS"("SUBJECT_ID") 
    WHERE "SUBJECT_ID" IS NOT NULL;

-- ============================================================================
-- Verification Queries (for debugging - can be removed in production)
-- ============================================================================

-- Uncomment these queries to verify the migration results:
-- SELECT 
--     column_name, 
--     data_type, 
--     is_nullable, 
--     column_default
-- FROM information_schema.columns 
-- WHERE table_name = 'USERS' 
--   AND column_name = 'SUBJECT_ID'
--   AND table_schema = 'public';

-- SELECT 
--     constraint_name, 
--     constraint_type
-- FROM information_schema.table_constraints 
-- WHERE table_name = 'USERS' 
--   AND constraint_name = 'USERS_SUBJECT_ID_FK'
--   AND table_schema = 'public';

COMMIT;
