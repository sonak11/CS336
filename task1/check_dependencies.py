"""Check the functional dependencies behind the proposed entities.

Usage (from the repo root, after unzipping the data):
    python3 task1/check_dependencies.py

For each "A -> B" it prints how many distinct A values exist and how many of
them map to more than one B value (violations). Zero violations supports
putting B in the entity keyed by A.
"""
import csv
from collections import defaultdict
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "hmda_2017_nj_all-records_labels.csv"

CHECKS = [
    (["agency_code"], ["agency_name", "agency_abbr"]),
    (["respondent_id"], ["agency_code"]),
    (["respondent_id", "agency_code"], ["agency_name"]),
    (["state_code"], ["state_name", "state_abbr"]),
    (["county_code"], ["county_name"]),
    (["msamd"], ["msamd_name"]),
    (["msamd"], ["hud_median_family_income"]),
    (["census_tract_number"], ["county_code"]),
    (["county_code", "census_tract_number"],
     ["population", "minority_population", "hud_median_family_income", "tract_to_msamd_income",
      "number_of_owner_occupied_units", "number_of_1_to_4_family_units"]),
    (["county_code", "census_tract_number"], ["msamd"]),
]
for code in ["loan_type", "property_type", "loan_purpose", "owner_occupancy", "preapproval",
             "action_taken", "purchaser_type", "hoepa_status", "lien_status", "edit_status",
             "applicant_ethnicity", "co_applicant_ethnicity", "applicant_sex", "co_applicant_sex"]:
    CHECKS.append(([code], [code + "_name"]))
for prefix, n in [("applicant_race", 5), ("co_applicant_race", 5), ("denial_reason", 3)]:
    for i in range(1, n + 1):
        CHECKS.append(([f"{prefix}_{i}"], [f"{prefix}_name_{i}"]))


def main():
    with open(CSV_PATH, newline="") as f:
        rows = list(csv.DictReader(f))
    for lhs, rhs in CHECKS:
        seen = defaultdict(set)
        for r in rows:
            seen[tuple(r[c] for c in lhs)].add(tuple(r[c] for c in rhs))
        bad = [k for k, v in seen.items() if len(v) > 1]
        example = f"  e.g. {bad[0]} -> {sorted(seen[bad[0]])[:3]}" if bad else ""
        print(f"{'+'.join(lhs)} -> {', '.join(rhs)}: {len(seen)} keys, {len(bad)} violations{example}")


if __name__ == "__main__":
    main()
