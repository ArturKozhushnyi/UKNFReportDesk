BEGIN;

-- ============================================================================
-- Migration: 003_update_password_hash_column.sql
-- Purpose: Update PASSWORD_HASH column size to accommodate sha256_crypt hashes
-- ============================================================================

-- Update PASSWORD_HASH column size from varchar(64) to varchar(128)
-- to accommodate sha256_crypt hashes which are longer than bcrypt hashes
ALTER TABLE "USERS" 
ALTER COLUMN "PASSWORD_HASH" TYPE varchar(128);

COMMIT;
