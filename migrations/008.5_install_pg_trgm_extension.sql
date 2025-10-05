BEGIN;

-- ============================================================================
-- Migration: 008.5_install_pg_trgm_extension.sql
-- Purpose: Install pg_trgm extension for fuzzy text search capabilities
-- ============================================================================

-- ============================================================================
-- Install pg_trgm Extension
-- ============================================================================

-- Create the pg_trgm extension if it doesn't exist
-- This extension provides trigram matching for fuzzy text search
DO $$
BEGIN
    -- Check if pg_trgm extension exists
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_extension 
        WHERE extname = 'pg_trgm'
    ) THEN
        -- Try to create the extension
        BEGIN
            CREATE EXTENSION pg_trgm;
            RAISE NOTICE 'pg_trgm extension created successfully';
            RAISE NOTICE 'Trigram matching and fuzzy search capabilities are now available';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Failed to create pg_trgm extension: %', SQLERRM;
            RAISE NOTICE 'Error details: %', SQLSTATE;
            RAISE NOTICE '';
            RAISE NOTICE 'To fix this issue:';
            RAISE NOTICE '1. Install postgresql-contrib package on your system';
            RAISE NOTICE '2. For Docker: Use postgres:15 or postgres:15-contrib image';
            RAISE NOTICE '3. For Ubuntu/Debian: sudo apt-get install postgresql-contrib-15';
            RAISE NOTICE '4. For CentOS/RHEL: sudo yum install postgresql15-contrib';
            RAISE NOTICE '';
            RAISE NOTICE 'The migration will continue without trigram support.';
            RAISE NOTICE 'Tag search will use regular indexes instead.';
        END;
    ELSE
        RAISE NOTICE 'pg_trgm extension already exists';
    END IF;
END $$;

-- ============================================================================
-- Verification
-- ============================================================================

-- Verify the extension is available
DO $$
DECLARE
    ext_exists BOOLEAN;
BEGIN
    SELECT EXISTS(
        SELECT 1 
        FROM pg_extension 
        WHERE extname = 'pg_trgm'
    ) INTO ext_exists;
    
    IF ext_exists THEN
        RAISE NOTICE 'pg_trgm extension verification: SUCCESS';
        RAISE NOTICE 'Available functions: similarity(), show_trgm(), word_similarity()';
    ELSE
        RAISE NOTICE 'pg_trgm extension verification: NOT AVAILABLE';
        RAISE NOTICE 'Fuzzy search features will be limited';
    END IF;
END $$;

COMMIT;
