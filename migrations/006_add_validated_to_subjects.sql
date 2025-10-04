BEGIN;

-- ============================================================================
-- Migration: 006_add_validated_to_subjects.sql
-- Purpose: Add VALIDATED column to SUBJECTS table
-- ============================================================================

-- ============================================================================
-- Add VALIDATED Column to SUBJECTS Table
-- ============================================================================

-- Add the VALIDATED column if it doesn't already exist
-- This uses a DO block to check for column existence before adding it
DO $$
BEGIN
    -- Check if the VALIDATED column already exists
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'SUBJECTS' 
          AND column_name = 'VALIDATED'
          AND table_schema = 'public'
    ) THEN
        -- Add the VALIDATED column with the specified properties
        ALTER TABLE "SUBJECTS" 
        ADD COLUMN "VALIDATED" BOOLEAN NOT NULL DEFAULT false;
        
        -- Log the operation
        RAISE NOTICE 'Column VALIDATED added to SUBJECTS table';
    ELSE
        -- Column already exists, log this information
        RAISE NOTICE 'Column VALIDATED already exists in SUBJECTS table';
    END IF;
END $$;

-- ============================================================================
-- Verification Query (for debugging - can be removed in production)
-- ============================================================================

-- Uncomment this query to verify the column was added:
-- SELECT 
--     column_name, 
--     data_type, 
--     is_nullable, 
--     column_default
-- FROM information_schema.columns 
-- WHERE table_name = 'SUBJECTS' 
--   AND column_name = 'VALIDATED'
--   AND table_schema = 'public';

COMMIT;
