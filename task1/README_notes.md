# README.txt notes from Task 1

This is draft text for the final `README.txt`. Section numbers match the assignment. Sections 0 and 5 are left for the team to fill in.

---

## 1. Known issues (data quirks, not code bugs)

These are properties of the source file that the code has to handle. None of them are bugs in our code.

- `sequence_number`, `edit_status`, `edit_status_name` and `application_date_indicator` are blank in all 349,563 rows of the 2017 NJ file. We fill `sequence_number` with 1..N in file order to create the primary key. The export script writes it back out as blank so the output matches the original.
- `msamd_name` is blank in 115 rows where `msamd` has a value (codes 35620 and 37980). This is a CFPB labeling gap, and we keep it as-is.
- `loan_amount_000s` reaches 6 digits and `applicant_income_000s` reaches 7, even though the format PDF lists maximum lengths of 5 and 4.

## 2. Collaboration and resources

- **CFPB HMDA historic data page** (https://www.consumerfinance.gov/data-research/hmda/historic-data/): source of `hmda_2017_nj_all-records_labels.zip` ("All records", "Plain language labels and HMDA codes", New Jersey, 2017).
- **CFPB data dictionaries** in `docs/`: `lar_record_codes.pdf` (code meanings), `lar_record_format.pdf` (field lengths and types), `panel_2010-2017.pdf`, `transmittal_sheet_2017.pdf`.
- **AI assistance:** Claude (Anthropic) helped with Task 1. It wrote the profiling and dependency-check scripts, drafted the attribute/type checklist, and drafted the entity proposal. Every number in these files comes from running the scripts in `task1/` on the downloaded CSV.

## 3. Useful insights and how we divided attributes into entities

### Rules we used for grouping attributes

1. **One entity per real-world thing.** The attributes of a loan application, the people applying, the lender, its regulator, and the place the property is in each describe a different real-world object, so each gets its own entity.
2. **Group by functional dependency.** If knowing A always tells you B, then B belongs to the entity keyed by A. We checked each dependency on the full file with `task1/check_dependencies.py`. Some examples:
   - `agency_code` determines `agency_name` and `agency_abbr`, with 0 exceptions.
   - (`county_code`, `census_tract_number`) determines all six census statistics, with 0 exceptions.
   - Every `*_code` determines its `*_name` label, with 0 exceptions.
3. **Each code/label pair is its own lookup entity** (for example `loan_type` with `loan_type_name`). The label is a fact about the code, not about the application.
4. **Follow the data even when it contradicts intuition.** We expected the census tract to determine the MSA/MD, but 127 tracts are reported with two different MSA/MD codes. So `msamd` is attached to the Application rather than the Location.
5. **Use a surrogate key only where the natural key fails.** A lender is identified by `respondent_id` together with `agency_code`, because two lenders report under two agencies. A location's natural key (county, tract) is blank in hundreds of rows. That's the one place we added an attribute, `locationID`, which the assignment allows.
6. **Don't add or rename attributes yet.** The applicant race 1–5 and denial reason 1–3 repeating groups stay as they are. Splitting them would change the original attributes, and they'll be handled when we normalize in the next part of the project.

### Insights the data supports

The figures below come from the 294,616 applications with `action_taken` 1–5. Purchased loans and preapproval-only records are excluded.

- **Overall denial rate is 16.7%.** The most common first reasons are debt-to-income ratio (10,360), credit history (8,816) and collateral (7,021).
- **Denial rates differ by race and ethnicity:**
  - Black applicants: 25.0%
  - American Indian/Alaska Native applicants: 32.0%
  - White applicants: 15.0%
  - Asian applicants: 14.1%
  - Hispanic/Latino applicants: 19.9%, compared with 15.6% for non-Hispanic applicants
- **The data can't tell us the cause of those gaps.** Income plays a large role: the denial rate is 30.4% under $50k and 11.3% at $200k and above. The data has no credit scores, so it can support fair-lending *questions* but not conclusions.
- **Neighborhood matters.** Applications in tracts that are 80% or more minority are denied 23.1% of the time. In tracts under 20% minority, the rate is 15.0%.
- **Loan purpose matters.** Home improvement loans are denied 37.9% of the time, refinancing 19.9%, and home purchase 10.3%.
- **Higher-priced loans are concentrated.** Only 5.2% of originations have a reported `rate_spread`. The share is 19.6% of FHA originations but 2.1% of conventional ones. By race, it's 14.3% of loans to Black borrowers, 5.3% to White borrowers, and 2.1% to Asian borrowers.
- **The secondary market is a big player.** Of the 169,196 originated loans, Fannie Mae bought 33,052, Freddie Mac 23,001 and Ginnie Mae 18,230 within 2017.
- **The market is concentrated.** The top 10 lenders account for 32.9% of all records. HUD-supervised (non-bank) lenders filed 56% of records.
- **Geography.** Bergen, Ocean and Monmouth counties have the most activity. The median originated loan is $251k.

## 4. Problems faced (Task 1)

- **Some types that look numeric can't be stored as numbers.** `rate_spread` (`01.50`) and `census_tract_number` (`0103.00`) have significant leading zeros, and `respondent_id` mixes leading zeros with hyphens. Storing any of them as a plain number would change the CSV on export.
- **Floating-point precision.** `minority_population` and `tract_to_msamd_income` have up to 17 decimal places, plus whole-number values written like `19.0`. `real` loses digits, and `double precision` prints `19.0` as `19`. Only unconstrained `numeric` keeps the text exactly.
- **Choosing keys.** It took data checks, not just the PDFs, to find that `respondent_id` isn't unique by itself and that tract doesn't determine MSA/MD.
- **File size.** The CSV is 266 MB, which is over GitHub's 100 MB limit, so the repo stores the original 12 MB zip.
- **Time spent on Task 1:** about ___ hours (fill in).
