"""Profile the HMDA 2017 NJ CSV and write the Task 1 attribute checklist.

Usage (from the repo root, after unzipping data/hmda_2017_nj_all-records_labels.zip):
    python3 task1/build_checklist.py

Writes task1/attribute_checklist.csv and task1/attribute_checklist.md.
Only uses the Python standard library.
"""
import csv
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "hmda_2017_nj_all-records_labels.csv"
OUT_CSV = ROOT / "task1" / "attribute_checklist.csv"
OUT_MD = ROOT / "task1" / "attribute_checklist.md"

# column -> (proposed PostgreSQL type, entity, meaning, flags)
META = {
    "as_of_year": ("integer", "Application", "Reporting year of the record (always 2017).", ""),
    "respondent_id": ("text", "Respondent", "10-character ID of the reporting lender. Unique only together with agency_code.",
                      "Leading zeros and hyphens (0000451965, 62-1532940); integer would destroy them."),
    "agency_name": ("text", "Agency", "Full name of the lender's federal regulator.", ""),
    "agency_abbr": ("text", "Agency", "Regulator abbreviation (HUD, CFPB, FDIC, NCUA, OCC, FRS).", ""),
    "agency_code": ("integer", "Agency", "Regulator code: 1 OCC, 2 FRS, 3 FDIC, 5 NCUA, 7 HUD, 9 CFPB.", ""),
    "loan_type_name": ("text", "LoanType", "Label for loan_type.", ""),
    "loan_type": ("integer", "LoanType", "1 Conventional, 2 FHA, 3 VA, 4 FSA/RHS.", ""),
    "property_type_name": ("text", "PropertyType", "Label for property_type.", ""),
    "property_type": ("integer", "PropertyType", "1 one-to-four family, 2 manufactured, 3 multifamily.", ""),
    "loan_purpose_name": ("text", "LoanPurpose", "Label for loan_purpose.", ""),
    "loan_purpose": ("integer", "LoanPurpose", "1 home purchase, 2 home improvement, 3 refinancing.", ""),
    "owner_occupancy_name": ("text", "OwnerOccupancy", "Label for owner_occupancy.", ""),
    "owner_occupancy": ("integer", "OwnerOccupancy", "1 owner-occupied principal dwelling, 2 not owner-occupied, 3 N/A.", "Code 3 = not applicable."),
    "loan_amount_000s": ("integer", "Application", "Loan amount in thousands of dollars.",
                         "Blank in some rows -> NULL. Max is 6 digits although the PDF says 5."),
    "preapproval_name": ("text", "Preapproval", "Label for preapproval.", ""),
    "preapproval": ("integer", "Preapproval", "1 requested, 2 not requested, 3 not applicable.", "Code 3 = not applicable."),
    "action_taken_name": ("text", "ActionTaken", "Label for action_taken.", ""),
    "action_taken": ("integer", "ActionTaken", "Outcome: 1 originated, 2 approved not accepted, 3 denied, 4 withdrawn, 5 incomplete, 6 purchased, 7 preapproval denied, 8 preapproval approved not accepted.", ""),
    "msamd_name": ("text", "MSA_MD", "Name of the Metropolitan Statistical Area / Metropolitan Division.",
                   "Blank for rural loans AND for msamd 35620/37980 even though the code is present."),
    "msamd": ("integer", "MSA_MD", "5-digit MSA/MD code.", "Blank -> NULL. No leading zeros in this file."),
    "state_name": ("text", "State", "State name (always New Jersey).", ""),
    "state_abbr": ("text", "State", "State postal abbreviation (always NJ).", ""),
    "state_code": ("integer", "State", "2-digit FIPS state code (always 34).", ""),
    "county_name": ("text", "County", "County name.", "Blank -> NULL."),
    "county_code": ("integer", "County", "FIPS county code within the state.",
                    "Stored unpadded in the CSV (\"3\", not \"003\"), so integer round-trips exactly. Blank -> NULL."),
    "census_tract_number": ("text", "Location", "Census tract identifier.",
                            "Format NNNN.NN with significant leading zeros (0103.00); numeric would print 103.00. Blank -> NULL."),
    "applicant_ethnicity_name": ("text", "Applicant", "Label for applicant_ethnicity.", ""),
    "applicant_ethnicity": ("integer", "Applicant", "1 Hispanic/Latino, 2 not Hispanic/Latino, 3 not provided, 4 N/A.", "Codes 3/4 are missing-value codes."),
    "co_applicant_ethnicity_name": ("text", "CoApplicant", "Label for co_applicant_ethnicity.", ""),
    "co_applicant_ethnicity": ("integer", "CoApplicant", "Same codes as applicant plus 5 = no co-applicant.", "Codes 3/4/5 are missing-value codes."),
    "applicant_race_name_1": ("text", "Applicant", "Label for applicant_race_1.", ""),
    "applicant_race_1": ("integer", "Applicant", "Race code 1-7 (1 AIAN, 2 Asian, 3 Black, 4 NHPI, 5 White, 6 not provided, 7 N/A).", "Codes 6/7 are missing-value codes."),
}
for i in range(2, 6):
    META[f"applicant_race_name_{i}"] = ("text", "Applicant", f"Label for applicant_race_{i}.", "Mostly blank -> NULL.")
    META[f"applicant_race_{i}"] = ("integer", "Applicant", f"Additional race #{i} (codes 1-5).", "Mostly blank -> NULL.")
META["co_applicant_race_name_1"] = ("text", "CoApplicant", "Label for co_applicant_race_1.", "")
META["co_applicant_race_1"] = ("integer", "CoApplicant", "Race code 1-8 (8 = no co-applicant).", "Codes 6/7/8 are missing-value codes.")
for i in range(2, 6):
    META[f"co_applicant_race_name_{i}"] = ("text", "CoApplicant", f"Label for co_applicant_race_{i}.", "Mostly blank -> NULL.")
    META[f"co_applicant_race_{i}"] = ("integer", "CoApplicant", f"Additional co-applicant race #{i} (codes 1-5).", "Mostly blank -> NULL.")
META.update({
    "applicant_sex_name": ("text", "Applicant", "Label for applicant_sex.", ""),
    "applicant_sex": ("integer", "Applicant", "1 male, 2 female, 3 not provided, 4 N/A.", "Codes 3/4 are missing-value codes."),
    "co_applicant_sex_name": ("text", "CoApplicant", "Label for co_applicant_sex.", ""),
    "co_applicant_sex": ("integer", "CoApplicant", "Same codes plus 5 = no co-applicant.", "Codes 3/4/5 are missing-value codes."),
    "applicant_income_000s": ("integer", "Applicant", "Gross annual income in thousands of dollars.",
                              "Blank -> NULL (about 14% of rows, mostly purchased loans). Max is 7 digits although the PDF says 4."),
    "purchaser_type_name": ("text", "PurchaserType", "Label for purchaser_type.", ""),
    "purchaser_type": ("integer", "PurchaserType", "Who bought the loan; 0 = not originated/not sold in 2017.", "Code 0 is a real value, not missing."),
})
for i in range(1, 4):
    META[f"denial_reason_name_{i}"] = ("text", "Denial", f"Label for denial_reason_{i}.", "Blank unless the application was denied -> NULL.")
    META[f"denial_reason_{i}"] = ("integer", "Denial", f"Denial reason #{i} (1 DTI, 2 employment, 3 credit history, 4 collateral, 5 cash, 6 unverifiable, 7 incomplete, 8 MI denied, 9 other).",
                                  "Blank unless the application was denied -> NULL.")
META.update({
    "rate_spread": ("numeric(4,2)", "Application", "APR spread over the average prime offer rate, in percentage points (only for higher-priced originations).",
                    "Zero-padded to DD.DD (01.50); numeric prints 1.50, so the export must use to_char(rate_spread, 'FM00.00'). Blank -> NULL."),
    "hoepa_status_name": ("text", "HOEPAStatus", "Label for hoepa_status.", ""),
    "hoepa_status": ("integer", "HOEPAStatus", "1 HOEPA (high-cost) loan, 2 not HOEPA.", ""),
    "lien_status_name": ("text", "LienStatus", "Label for lien_status.", ""),
    "lien_status": ("integer", "LienStatus", "1 first lien, 2 subordinate, 3 not secured, 4 N/A (purchased loans).", "Code 4 = not applicable."),
    "edit_status_name": ("text", "EditStatus", "Label for edit_status.", "Blank in every row -> NULL."),
    "edit_status": ("integer", "EditStatus", "Edit-check failure code (blank = none; 5, 6, 7).", "Blank in every row -> NULL."),
    "sequence_number": ("integer PRIMARY KEY", "Application", "Per-lender record number. Becomes the table's primary key.",
                        "Blank in every row. Task 3 fills it 1..N in file order, and the export must write it back as \"\" and ORDER BY it."),
    "population": ("integer", "Location", "Total population of the census tract.", "Blank -> NULL."),
    "minority_population": ("numeric", "Location", "Minority share of the tract population, in percent.",
                            "Up to 17 decimal places (14.149999618530273) and also 19.0-style values. real loses digits and double precision prints 19.0 as 19, so use unconstrained numeric. Blank -> NULL."),
    "hud_median_family_income": ("integer", "Location", "FFIEC/HUD median family income (dollars) for the tract's MSA/MD.", "Blank -> NULL."),
    "tract_to_msamd_income": ("numeric", "Location", "Tract median family income as a % of the MSA/MD median.",
                              "Same precision issue as minority_population, so use unconstrained numeric. Blank -> NULL."),
    "number_of_owner_occupied_units": ("integer", "Location", "Owner-occupied dwellings in the tract.", "Blank -> NULL."),
    "number_of_1_to_4_family_units": ("integer", "Location", "One-to-four family dwellings in the tract.", "Blank -> NULL."),
    "application_date_indicator": ("integer", "Application", "0 = on/after 2004-01-01, 1 = before, 2 = N/A.", "Blank in every row -> NULL."),
})


def main():
    with open(CSV_PATH, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert set(header) == set(META), set(header) ^ set(META)
        empty = Counter()
        maxlen = Counter()
        distinct = {c: set() for c in header}
        samples = {}
        rows = 0
        for row in reader:
            rows += 1
            for c, v in zip(header, row):
                if v == "":
                    empty[c] += 1
                else:
                    maxlen[c] = max(maxlen[c], len(v))
                    if len(distinct[c]) <= 1000:
                        distinct[c].add(v)
                    samples.setdefault(c, v)

    fields = ["position", "column", "meaning", "postgres_type", "entity", "blank_rows",
              "distinct_values", "max_length", "example", "flags"]
    records = []
    for i, c in enumerate(header, 1):
        pg, ent, meaning, flags = META[c]
        d = len(distinct[c])
        records.append({
            "position": i, "column": c, "meaning": meaning, "postgres_type": pg, "entity": ent,
            "blank_rows": empty[c], "distinct_values": ">1000" if d > 1000 else d,
            "max_length": maxlen[c], "example": samples.get(c, ""), "flags": flags,
        })

    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(records)

    with open(OUT_MD, "w") as f:
        f.write("# Attribute and type checklist\n\n")
        f.write(f"Generated by `task1/build_checklist.py` from `data/hmda_2017_nj_all-records_labels.csv` "
                f"({rows:,} data rows, {len(header)} columns). Columns are in original CSV order, "
                "and the Preliminary table must keep this order.\n\n")
        f.write("| # | column | proposed type | entity | blank rows | distinct | max len | example | flags |\n")
        f.write("|---|---|---|---|---:|---:|---:|---|---|\n")
        for r in records:
            f.write(f"| {r['position']} | `{r['column']}` | `{r['postgres_type']}` | {r['entity']} | "
                    f"{r['blank_rows']:,} | {r['distinct_values']} | {r['max_length']} | "
                    f"`{r['example']}` | {r['flags']} |\n")
        f.write("\nThe meaning of every column is in `attribute_checklist.csv`.\n")
    print(f"{rows} rows, {len(header)} columns -> {OUT_CSV.name}, {OUT_MD.name}")


if __name__ == "__main__":
    main()
