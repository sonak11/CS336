CS336 Project: 2017 New Jersey HMDA Database (ER Diagram and PostgreSQL Upload)
================================================================================


Submitted files
  ER_Diagram.pdf          ER diagram (draw.io, crow's foot / Oracle notation)
  create_table.sql        creates the Preliminary table (called by load.sql)
  load.sql                import script: run with \i load.sql (create_table.sql and the
                          CSV must be in the same folder)
  export.sql              export script: writes exported.csv
  screenshot_01-18.png    SELECT results showing all 78 attributes
  diff_identical.png      diff of the original CSV against exported.csv on ilab




0. Team members
---------------
- Sonakshi Sharma   netID: ss4910   Task 1: data download, attribute checklist, entity plan
- Sankeerth Bharadwaj netID: sb2738  Task 2: ER diagram
- Kenneth Wang    netID: ksw94  Task 3: table creation and import script
- James Kurian           netID: jjk369     Task 4: export testing, screenshots, README




1. Known issues
---------------
None known. The import and export run on ilab, and `diff` between the original CSV and
exported.csv prints nothing (349,563 rows, 78 columns). See diff_identical.png.


Notes on the source data that the code handles (these are properties of the CFPB file,
not bugs):
- sequence_number, edit_status, edit_status_name and application_date_indicator are
  blank in all 349,563 rows. The import fills sequence_number with 1..N in file order
  and makes it the primary key. The export removes those numbers and writes the column
  back blank, as in the original, so the output is identical to the source CSV.
- msamd_name is blank in 115 rows where msamd has a value (codes 35620 and 37980). This
  is a CFPB labeling gap, and we keep it as-is.
- loan_amount_000s reaches 6 digits and applicant_income_000s reaches 7, even though the
  format PDF lists maximum lengths of 5 and 4.




2. Collaboration and resources
------------------------------
- CFPB HMDA historic data page
  (https://www.consumerfinance.gov/data-research/hmda/historic-data/): source of
  hmda_2017_nj_all-records_labels.zip ("All records", "Plain language labels and HMDA
  codes", New Jersey, 2017).
- CFPB data dictionaries: lar_record_codes.pdf (code meanings), lar_record_format.pdf
  (field lengths and types), panel_2010-2017.pdf, transmittal_sheet_2017.pdf.
- PostgreSQL documentation: COPY, including the FORCE_QUOTE and FORCE_NULL options
  (https://www.postgresql.org/docs/current/sql-copy.html), and psql, including \copy
  and \i (https://www.postgresql.org/docs/current/app-psql.html).
- draw.io ER diagram guide linked in the assignment
  (https://drawio-app.com/blog/entity-relationship-diagrams-with-draw-io/).
- AI assistance:
  - Task 1 (Sonakshi): Claude (Anthropic) wrote the profiling and dependency-check
    scripts, drafted the attribute/type checklist, and drafted the entity proposal.
    Every number in those files comes from running the scripts on the downloaded CSV.
  - Task 2 (Sankeerth): [describe any AI use, or write "None"]
  - Task 3 (Kenneth): [describe any AI use, or write "None"]
  - Task 4 (James): Claude (Anthropic) tested the import and export scripts on a local
    PostgreSQL copy, helped write the Readme




3. Useful insights and how we divided attributes into entities
--------------------------------------------------------------
Rules we used for grouping attributes:
1. One entity per real-world thing. The loan application, the applicant, the
   co-applicant, the lender (respondent), its regulator (agency), and the place the
   property is in each describe a different real-world object, so each gets its own
   entity.
2. Group by functional dependency. If knowing A always tells you B, then B belongs to
   the entity keyed by A. We checked each dependency on the full file. For example:
   - agency_code determines agency_name and agency_abbr, with 0 exceptions.
   - (county_code, census_tract_number) determines all six census statistics, with
     0 exceptions.
   - Every code determines its *_name label, with 0 exceptions.
3. Each code/label pair is its own lookup entity (for example loan_type with
   loan_type_name). The label is a fact about the code, not about the application.
4. Follow the data even when it contradicts intuition. We expected the census tract to
   determine the MSA/MD, but 127 tracts are reported with two different MSA/MD codes, so
   msamd is attached to the Application rather than the Location.
5. Use a surrogate key only where the natural key fails. A lender is identified by
   respondent_id together with agency_code, because some lenders report under two
   agencies. A location's natural key (county, tract) is blank in hundreds of rows, so
   we added locationID, the one extra attribute the assignment allows.
6. Don't add or rename attributes yet. The applicant race 1-5 and denial reason 1-3
   repeating groups stay as they are and will be handled when we normalize in the next
   part of the project.


The result is 20 entities: Agency, Respondent, Application, Applicant, CoApplicant,
Denial, Location, State, County, MSA_MD, and 10 code lookups (LoanType, PropertyType,
LoanPurpose, OwnerOccupancy, Preapproval, ActionTaken, PurchaserType, HoepaStatus,
LienStatus, EditStatus).


Insights the data supports (from the 294,616 applications with action_taken 1-5;
purchased loans and preapproval-only records are excluded):
- The overall denial rate is 16.7%. The most common first reasons are debt-to-income
  ratio (10,360), credit history (8,816) and collateral (7,021).
- Denial rates differ by race and ethnicity: Black applicants 25.0%, American
  Indian/Alaska Native 32.0%, White 15.0%, Asian 14.1%. Hispanic/Latino applicants are
  denied 19.9% of the time, compared with 15.6% for non-Hispanic applicants.
- The data can't tell us the cause of those gaps. Income plays a large role: the denial
  rate is 30.4% under $50k and 11.3% at $200k and above. The data has no credit scores,
  so it can support fair-lending questions but not conclusions.
- Neighborhood matters. Applications in tracts that are 80% or more minority are denied
  23.1% of the time; in tracts under 20% minority, 15.0%.
- Loan purpose matters. Home improvement loans are denied 37.9% of the time,
  refinancing 19.9%, and home purchase 10.3%.
- Higher-priced loans are concentrated. Only 5.2% of originations report a rate_spread:
  19.6% of FHA originations but 2.1% of conventional ones. By race, it's 14.3% of loans
  to Black borrowers, 5.3% to White borrowers, and 2.1% to Asian borrowers.
- The secondary market is a big player. Of the 169,196 originated loans, Fannie Mae
  bought 33,052, Freddie Mac 23,001 and Ginnie Mae 18,230 within 2017.
- The market is concentrated. The top 10 lenders account for 32.9% of all records, and
  HUD-supervised (non-bank) lenders filed 56% of records.
- Geography: Bergen, Ocean and Monmouth counties have the most activity. The median
  originated loan is $251k.




4. Problems faced and time spent
--------------------------------
Sonakshi (Task 1),
- Some values that look numeric can't be stored as numbers. rate_spread (01.50) and
  census_tract_number (0103.00) have significant leading zeros, and respondent_id mixes
  leading zeros with hyphens. Storing them as plain numbers would change the CSV on
  export.
- Floating-point precision. minority_population and tract_to_msamd_income have up to
  17 decimal places, plus whole numbers written like 19.0. real loses digits, and double
  precision prints 19.0 as 19. Only unconstrained numeric keeps the text exactly.
- Choosing keys took data checks, not just the PDFs: respondent_id isn't unique by
  itself, and tract doesn't determine MSA/MD.
- The CSV is 266 MB, over GitHub's 100 MB limit, so the repo stores the original zip.


Sankeerth (Task 2),
- [problems faced]


Kenneth (Task 3), 
- [problems faced]


James (Task 4), 
- The assignment asks for an export that both removes sequence_number and is identical
  to the original. This was resolved by finding that sequence_number is blank in the
  source file, so the export writes it back blank.
- The first version of load.sql left four code columns (agency_code, msamd, state_code,
  county_code) as text, which would have cost points for incorrect types.
- Converting blank cells to NULL with an UPDATE after loading hit ilab's statement
  timeout. Using FORCE_NULL in \copy converts them during the load instead.
- Some text values are up to 81 characters wide, so the attributes had to be split
  across 18 queries for the screenshots to be readable without wrapping.
- Getting connected to ilab and moving files there with scp.




5. Database used for grading
----------------------------
The Preliminary table is in Sonakshi’s ilab database (netID: ss4910).