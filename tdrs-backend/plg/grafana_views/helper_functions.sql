-- Helper functions for Grafana view date validation
-- Run this script before creating the views
--
-- These functions safely validate date strings without throwing errors,
-- which is necessary because TO_DATE() throws an error on invalid dates
-- like '20230931' (September 31st doesn't exist).

-- Validates an 8-digit date string in YYYYMMDD format (e.g., '20230915')
-- Returns TRUE if the string represents a valid calendar date, FALSE otherwise
CREATE OR REPLACE FUNCTION is_valid_date_yyyymmdd(date_str TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    -- Check format first (8 digits)
    IF date_str IS NULL OR date_str = '' OR date_str !~ '^[0-9]{8}$' THEN
        RETURN FALSE;
    END IF;

    -- Attempt to parse - will throw exception if invalid date
    PERFORM TO_DATE(date_str, 'YYYYMMDD');
    RETURN TRUE;

EXCEPTION WHEN OTHERS THEN
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql IMMUTABLE;


-- Validates a 6-digit year/month string in YYYYMM format (e.g., '202309')
-- Returns TRUE if the string represents a valid year/month, FALSE otherwise
CREATE OR REPLACE FUNCTION is_valid_yyyymm(yyyymm TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    -- Check format first (6 digits)
    IF yyyymm IS NULL OR yyyymm = '' OR yyyymm !~ '^[0-9]{6}$' THEN
        RETURN FALSE;
    END IF;

    -- Attempt to parse with day 01 - will throw exception if invalid month
    PERFORM TO_DATE(yyyymm || '01', 'YYYYMMDD');
    RETURN TRUE;

EXCEPTION WHEN OTHERS THEN
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql IMMUTABLE;
