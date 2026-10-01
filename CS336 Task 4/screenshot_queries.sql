-- screenshot_queries.sql
-- One query per screenshot. Together they show all 78 attributes of Preliminary.
-- Run on ilab inside psql:  \i screenshot_queries.sql   (or paste one query at a time)
-- Each result opens in the pager: screenshot the first screen, then press q
-- for the next query. Widen the terminal to at least 170 columns (full screen,
-- smaller font) so rows don't wrap.
-- sequence_number is first in every query so rows can be matched across screenshots.
\pset pager always

-- Screenshot 1 of 18 (about 153 characters wide)
SELECT sequence_number,
       as_of_year,
       respondent_id,
       agency_name,
       agency_abbr,
       agency_code,
       loan_type_name,
       loan_type
FROM Preliminary
ORDER BY sequence_number;

-- Screenshot 2 of 18 (about 132 characters wide)
SELECT sequence_number,
       property_type_name,
       property_type,
       loan_purpose_name,
       loan_purpose
FROM Preliminary
ORDER BY sequence_number;

-- Screenshot 3 of 18 (about 145 characters wide)
SELECT sequence_number,
       owner_occupancy_name,
       owner_occupancy,
       loan_amount_000s,
       preapproval_name,
       preapproval
FROM Preliminary
ORDER BY sequence_number;

-- Screenshot 4 of 18 (about 167 characters wide)
SELECT sequence_number,
       action_taken_name,
       action_taken,
       msamd_name,
       msamd,
       state_name,
       state_abbr
FROM Preliminary
ORDER BY sequence_number;

-- Screenshot 5 of 18 (about 170 characters wide)
SELECT sequence_number,
       state_code,
       county_name,
       county_code,
       census_tract_number,
       applicant_ethnicity_name
FROM Preliminary
ORDER BY sequence_number;

-- Screenshot 6 of 18 (about 148 characters wide)
SELECT sequence_number,
       applicant_ethnicity,
       co_applicant_ethnicity_name,
       co_applicant_ethnicity
FROM Preliminary
ORDER BY sequence_number;

-- Screenshot 7 of 18 (about 164 characters wide)
SELECT sequence_number,
       applicant_race_name_1,
       applicant_race_1,
       applicant_race_name_2
FROM Preliminary
ORDER BY sequence_number;

-- Screenshot 8 of 18 (about 162 characters wide)
SELECT sequence_number,
       applicant_race_2,
       applicant_race_name_3,
       applicant_race_3,
       applicant_race_name_4,
       applicant_race_4
FROM Preliminary
ORDER BY sequence_number;

-- Screenshot 9 of 18 (about 166 characters wide)
SELECT sequence_number,
       applicant_race_name_5,
       applicant_race_5,
       co_applicant_race_name_1,
       co_applicant_race_1
FROM Preliminary
ORDER BY sequence_number;

-- Screenshot 10 of 18 (about 149 characters wide)
SELECT sequence_number,
       co_applicant_race_name_2,
       co_applicant_race_2,
       co_applicant_race_name_3,
       co_applicant_race_3
FROM Preliminary
ORDER BY sequence_number;

-- Screenshot 11 of 18 (about 132 characters wide)
SELECT sequence_number,
       co_applicant_race_name_4,
       co_applicant_race_4,
       co_applicant_race_name_5,
       co_applicant_race_5
FROM Preliminary
ORDER BY sequence_number;

-- Screenshot 12 of 18 (about 117 characters wide)
SELECT sequence_number,
       applicant_sex_name,
       applicant_sex
FROM Preliminary
ORDER BY sequence_number;

-- Screenshot 13 of 18 (about 144 characters wide)
SELECT sequence_number,
       co_applicant_sex_name,
       co_applicant_sex,
       applicant_income_000s
FROM Preliminary
ORDER BY sequence_number;

-- Screenshot 14 of 18 (about 162 characters wide)
SELECT sequence_number,
       purchaser_type_name,
       purchaser_type,
       denial_reason_name_1
FROM Preliminary
ORDER BY sequence_number;

-- Screenshot 15 of 18 (about 169 characters wide)
SELECT sequence_number,
       denial_reason_1,
       denial_reason_name_2,
       denial_reason_2,
       denial_reason_name_3,
       denial_reason_3
FROM Preliminary
ORDER BY sequence_number;

-- Screenshot 16 of 18 (about 158 characters wide)
SELECT sequence_number,
       rate_spread,
       hoepa_status_name,
       hoepa_status,
       lien_status_name,
       lien_status,
       edit_status_name,
       edit_status,
       population
FROM Preliminary
ORDER BY sequence_number;

-- Screenshot 17 of 18 (about 155 characters wide)
SELECT sequence_number,
       minority_population,
       hud_median_family_income,
       tract_to_msamd_income,
       number_of_owner_occupied_units,
       number_of_1_to_4_family_units
FROM Preliminary
ORDER BY sequence_number;

-- Screenshot 18 of 18 (about 46 characters wide)
SELECT sequence_number,
       application_date_indicator
FROM Preliminary
ORDER BY sequence_number;
