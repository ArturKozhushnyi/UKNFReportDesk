BEGIN;

-- ============================================================================
-- Migration: 008_add_bank_pekao_subject.sql
-- Purpose: Add Bank Pekao SA (Bank Polska Kasa Opieki Spółka Akcyjna) to SUBJECTS table
-- ============================================================================

-- ============================================================================
-- Add Bank Pekao SA Subject to SUBJECTS Table
-- ============================================================================

-- Insert Bank Pekao SA subject if it doesn't already exist
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
    'BANK',
    -- Generate a random 32-character alphanumeric CODE_UKNF
    array_to_string(
        ARRAY(
            SELECT substr('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', 
                        floor(random() * 36)::int + 1, 1)
            FROM generate_series(1, 32)
        ), 
        ''
    ) as "CODE_UKNF",
    'Bank Polska Kasa Opieki Spółka Akcyjna',
    '5493000LKS7B3UTF7H35',
    '5260006841',
    '0000014843',
    'Żubra',
    '1',
    NULL,
    '01-066',
    'WARSZAWA',
    '+48 22 656 00 00',
    'info@pekao.com.pl',
    "732826",
    'actywny',
    'Bank',
    'Bank',
    'Bank Komercyjny',
    false,
    NOW(),
    NOW(),
    true
WHERE NOT EXISTS (
    -- Check if a subject with this NIP already exists
    SELECT 1 FROM "SUBJECTS" WHERE "NIP" = '5260006841'
);

-- ============================================================================
-- Verification Queries (for debugging - can be removed in production)
-- ============================================================================

-- Uncomment these queries to verify the migration results:
-- SELECT 'Bank Pekao Subject:' as info, "ID", "TYPE_STRUCTURE", "CODE_UKNF", "NAME_STRUCTURE", "NIP", "VALIDATED"
-- FROM "SUBJECTS" WHERE "NIP" = '5260006841';
-- SELECT 'Total SUBJECTS count:' as info, COUNT(*) as count FROM "SUBJECTS";

COMMIT;
