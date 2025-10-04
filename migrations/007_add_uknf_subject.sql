BEGIN;

-- ============================================================================
-- Migration: 007_add_uknf_subject.sql
-- Purpose: Add UKNF (Polish Financial Supervision Authority) subject to SUBJECTS table
-- ============================================================================

-- ============================================================================
-- Add UKNF Subject to SUBJECTS Table
-- ============================================================================

-- Insert the UKNF subject if it doesn't already exist
-- This uses a subquery to generate a random CODE_UKNF and checks for existing NIP
INSERT INTO "SUBJECTS" (
    "TYPE_STRUCTURE",
    "CODE_UKNF",
    "NAME_STRUCTURE",
    "LEI",
    "NIP",
    "KRS",
    "STREET",
    "NR_STRET",
    "NR_HOUSE",
    "POST_CODE",
    "TOWN",
    "PHONE",
    "EMAIL",
    "UKNF_ID",
    "STATUS_S",
    "KATEGORY_S",
    "SELEKTOR_S",
    "SUBSELEKTOR_S",
    "TRANS_S",
    "DATE_CREATE",
    "DATE_ACTRUALIZATION",
    "VALIDATED"
)
SELECT 
    'UKNF',
    -- Generate a random 32-character alphanumeric CODE_UKNF
    array_to_string(
        ARRAY(
            SELECT substr('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', 
                        floor(random() * 36)::int + 1, 1)
            FROM generate_series(1, 32)
        ), 
        ''
    ) as "CODE_UKNF",
    'Urząd Komisji Nadzoru Finansowego',
    '1733386591974',
    '7010902185',
    NULL,
    'Piękna',
    '20',
    NULL,
    '00-549',
    'WARSZAWA',
    '+48 (22) 262 58 00',
    'knf@knf.gov.pl',
    NULL,
    'actywny',
    'KNF',
    'KNF',
    'KNF',
    false,
    NOW(),
    NOW(),
    true
WHERE NOT EXISTS (
    -- Check if a subject with this NIP already exists
    SELECT 1 FROM "SUBJECTS" WHERE "NIP" = '7010902185'
);

-- ============================================================================
-- Verification Queries (for debugging - can be removed in production)
-- ============================================================================

-- Uncomment these queries to verify the migration results:
-- SELECT 'UKNF Subject:' as info, "ID", "TYPE_STRUCTURE", "CODE_UKNF", "NAME_STRUCTURE", "NIP", "VALIDATED"
-- FROM "SUBJECTS" WHERE "NIP" = '7010902185';
-- SELECT 'Total SUBJECTS count:' as info, COUNT(*) as count FROM "SUBJECTS";

COMMIT;
