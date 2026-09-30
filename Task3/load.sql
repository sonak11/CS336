-- load.sql
\i create_table.sql

-- Row counter that is filled in by COPY itself, so numbering follows file order exactly
ALTER TABLE Preliminary ADD COLUMN _rowid BIGSERIAL;

\copy Preliminary (as_of_year, respondent_id, agency_name, agency_abbr, agency_code, loan_type_name, loan_type, property_type_name, property_type, loan_purpose_name, loan_purpose, owner_occupancy_name, owner_occupancy, loan_amount_000s, preapproval_name, preapproval, action_taken_name, action_taken, msamd_name, msamd, state_name, state_abbr, state_code, county_name, county_code, census_tract_number, applicant_ethnicity_name, applicant_ethnicity, co_applicant_ethnicity_name, co_applicant_ethnicity, applicant_race_name_1, applicant_race_1, applicant_race_name_2, applicant_race_2, applicant_race_name_3, applicant_race_3, applicant_race_name_4, applicant_race_4, applicant_race_name_5, applicant_race_5, co_applicant_race_name_1, co_applicant_race_1, co_applicant_race_name_2, co_applicant_race_2, co_applicant_race_name_3, co_applicant_race_3, co_applicant_race_name_4, co_applicant_race_4, co_applicant_race_name_5, co_applicant_race_5, applicant_sex_name, applicant_sex, co_applicant_sex_name, co_applicant_sex, applicant_income_000s, purchaser_type_name, purchaser_type, denial_reason_name_1, denial_reason_1, denial_reason_name_2, denial_reason_2, denial_reason_name_3, denial_reason_3, rate_spread, hoepa_status_name, hoepa_status, lien_status_name, lien_status, edit_status_name, edit_status, sequence_number, population, minority_population, hud_median_family_income, tract_to_msamd_income, number_of_owner_occupied_units, number_of_1_to_4_family_units, application_date_indicator) FROM 'hmda_2017_nj_all-records_labels.csv' WITH (FORMAT csv, HEADER true);

-- sequence_number = 1..N in file order (still TEXT at this point)
UPDATE Preliminary SET sequence_number = _rowid::TEXT;
ALTER TABLE Preliminary DROP COLUMN _rowid;

-- -------------------- INTEGER columns --------------------
ALTER TABLE Preliminary
    ALTER COLUMN as_of_year                     TYPE INTEGER USING NULLIF(as_of_year, '')::INTEGER,
    ALTER COLUMN loan_type                      TYPE INTEGER USING NULLIF(loan_type, '')::INTEGER,
    ALTER COLUMN property_type                  TYPE INTEGER USING NULLIF(property_type, '')::INTEGER,
    ALTER COLUMN loan_purpose                   TYPE INTEGER USING NULLIF(loan_purpose, '')::INTEGER,
    ALTER COLUMN owner_occupancy                TYPE INTEGER USING NULLIF(owner_occupancy, '')::INTEGER,
    ALTER COLUMN loan_amount_000s               TYPE INTEGER USING NULLIF(loan_amount_000s, '')::INTEGER,
    ALTER COLUMN preapproval                    TYPE INTEGER USING NULLIF(preapproval, '')::INTEGER,
    ALTER COLUMN action_taken                   TYPE INTEGER USING NULLIF(action_taken, '')::INTEGER,
    ALTER COLUMN applicant_ethnicity            TYPE INTEGER USING NULLIF(applicant_ethnicity, '')::INTEGER,
    ALTER COLUMN co_applicant_ethnicity         TYPE INTEGER USING NULLIF(co_applicant_ethnicity, '')::INTEGER,
    ALTER COLUMN applicant_race_1               TYPE INTEGER USING NULLIF(applicant_race_1, '')::INTEGER,
    ALTER COLUMN applicant_race_2               TYPE INTEGER USING NULLIF(applicant_race_2, '')::INTEGER,
    ALTER COLUMN applicant_race_3               TYPE INTEGER USING NULLIF(applicant_race_3, '')::INTEGER,
    ALTER COLUMN applicant_race_4               TYPE INTEGER USING NULLIF(applicant_race_4, '')::INTEGER,
    ALTER COLUMN applicant_race_5               TYPE INTEGER USING NULLIF(applicant_race_5, '')::INTEGER,
    ALTER COLUMN co_applicant_race_1            TYPE INTEGER USING NULLIF(co_applicant_race_1, '')::INTEGER,
    ALTER COLUMN co_applicant_race_2            TYPE INTEGER USING NULLIF(co_applicant_race_2, '')::INTEGER,
    ALTER COLUMN co_applicant_race_3            TYPE INTEGER USING NULLIF(co_applicant_race_3, '')::INTEGER,
    ALTER COLUMN co_applicant_race_4            TYPE INTEGER USING NULLIF(co_applicant_race_4, '')::INTEGER,
    ALTER COLUMN co_applicant_race_5            TYPE INTEGER USING NULLIF(co_applicant_race_5, '')::INTEGER,
    ALTER COLUMN applicant_sex                  TYPE INTEGER USING NULLIF(applicant_sex, '')::INTEGER,
    ALTER COLUMN co_applicant_sex               TYPE INTEGER USING NULLIF(co_applicant_sex, '')::INTEGER,
    ALTER COLUMN applicant_income_000s          TYPE INTEGER USING NULLIF(applicant_income_000s, '')::INTEGER,
    ALTER COLUMN purchaser_type                 TYPE INTEGER USING NULLIF(purchaser_type, '')::INTEGER,
    ALTER COLUMN denial_reason_1                TYPE INTEGER USING NULLIF(denial_reason_1, '')::INTEGER,
    ALTER COLUMN denial_reason_2                TYPE INTEGER USING NULLIF(denial_reason_2, '')::INTEGER,
    ALTER COLUMN denial_reason_3                TYPE INTEGER USING NULLIF(denial_reason_3, '')::INTEGER,
    ALTER COLUMN hoepa_status                   TYPE INTEGER USING NULLIF(hoepa_status, '')::INTEGER,
    ALTER COLUMN lien_status                    TYPE INTEGER USING NULLIF(lien_status, '')::INTEGER,
    ALTER COLUMN edit_status                    TYPE INTEGER USING NULLIF(edit_status, '')::INTEGER,
    ALTER COLUMN sequence_number                TYPE INTEGER USING NULLIF(sequence_number, '')::INTEGER,
    ALTER COLUMN population                     TYPE INTEGER USING NULLIF(population, '')::INTEGER,
    ALTER COLUMN hud_median_family_income       TYPE INTEGER USING NULLIF(hud_median_family_income, '')::INTEGER,
    ALTER COLUMN number_of_owner_occupied_units TYPE INTEGER USING NULLIF(number_of_owner_occupied_units, '')::INTEGER,
    ALTER COLUMN number_of_1_to_4_family_units  TYPE INTEGER USING NULLIF(number_of_1_to_4_family_units, '')::INTEGER,
    ALTER COLUMN application_date_indicator     TYPE INTEGER USING NULLIF(application_date_indicator, '')::INTEGER;

-- -------------------- NUMERIC (decimal) columns --------------------
ALTER TABLE Preliminary
    ALTER COLUMN rate_spread            TYPE NUMERIC(4,2) USING NULLIF(rate_spread, '')::NUMERIC,
    ALTER COLUMN minority_population    TYPE NUMERIC USING NULLIF(minority_population, '')::NUMERIC,
    ALTER COLUMN tract_to_msamd_income  TYPE NUMERIC USING NULLIF(tract_to_msamd_income, '')::NUMERIC;

-- -------------------- Primary key --------------------
ALTER TABLE Preliminary
    ADD CONSTRAINT preliminary_pkey PRIMARY KEY (sequence_number);
