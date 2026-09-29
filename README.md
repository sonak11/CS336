# CS336 Project: HMDA 2017 New Jersey mortgage data

This repo holds our team's work for the ER diagram and PostgreSQL upload project, using 2017 New Jersey HMDA data. Task 1 (download the data and plan the entities) is done. Tasks 2 and 3 should build on the files below.

## Layout

```
data/
  hmda_2017_nj_all-records_labels.zip   original download (unzip to get the CSV)
docs/
  lar_record_codes.pdf                  what every code means
  lar_record_format.pdf                 field lengths / types
  panel_2010-2017.pdf                   lender panel file dictionary
  transmittal_sheet_2017.pdf            transmittal sheet dictionary
task1/
  attribute_checklist.md / .csv         every column: meaning, PostgreSQL type, entity, flags
  proposed_entities.md                  proposed entities, keys, relationships, crow's foot draft
  README_notes.md                       draft text for README.txt sections 1-4
  build_checklist.py                    regenerates the checklist from the CSV
  check_dependencies.py                 functional-dependency evidence for the entities
```

## Getting the CSV

The CSV is 266 MB, which is over GitHub's 100 MB file limit. The repo keeps the untouched 12 MB zip from the CFPB instead:

```bash
unzip data/hmda_2017_nj_all-records_labels.zip -d data/
```

```bash
shasum -a 256 data/hmda_2017_nj_all-records_labels.csv
```

The checksum should be `8fae1ea53bc4af1bc1db107584cab3ae77e80b24db347f3e6bd549e265cf01b5`. The file has 349,563 data rows plus a header and 78 columns.

It was downloaded from https://www.consumerfinance.gov/data-research/hmda/historic-data/ with these options:

- Year 2017, state New Jersey
- "All records" (applications, denials, originations and institution purchases)
- "Plain language labels and HMDA codes"

Direct link: https://files.consumerfinance.gov/hmda-historic-loan-data/hmda_2017_nj_all-records_labels.zip

## Handoff notes

### For Task 2 (ER diagram)

Start from [task1/proposed_entities.md](task1/proposed_entities.md). It has:

- 20 entities covering all 78 columns, and `locationID` as the only added attribute
- the cardinality of every relationship
- the data evidence behind each key choice
- a Mermaid crow's foot draft to redraw in draw.io

### For Task 3 (Preliminary table and SQL scripts)

The types are in [task1/attribute_checklist.md](task1/attribute_checklist.md). The CSV has a few properties that decide whether `diff` passes:

1. **Exact file format.** The header row is not quoted. Every data field is double-quoted, including blank fields, which appear as `""`. Lines end in LF (`\n`), and the file ends with a newline.
2. **Load everything as text first.** In CSV mode, PostgreSQL reads a quoted blank `""` as an empty string, not NULL. Loading straight into `integer` columns therefore fails. Either stage the data as text and cast with `NULLIF(col, '')::integer`, or use `COPY ... WITH (FORMAT csv, HEADER, FORCE_NULL (...))`.
3. **Use `\copy`, not `COPY`, on ilab.** Server-side `COPY ... FROM 'file'` needs superuser rights.
4. **`sequence_number` is blank in every row.** Fill it with 1..N in the original file order and make it the primary key without renaming it. The export must `ORDER BY sequence_number` and write it back as `""`.
5. **Columns that need special handling to round-trip:**
   - `rate_spread` is `numeric(4,2)`. Export it with `to_char(rate_spread, 'FM00.00')` to restore the leading zero (`01.50`).
   - `minority_population` and `tract_to_msamd_income` must be unconstrained `numeric`. `real` loses digits, and `double precision` prints `19.0` as `19`.
   - `census_tract_number` and `respondent_id` are `text`, because their leading zeros and hyphens matter.
6. **Quote every field on export.** Use `WITH (FORMAT csv, HEADER, FORCE_QUOTE *)`. `FORCE_QUOTE` never quotes NULLs, so select `COALESCE(col::text, '')` for every column to get `""` back. Keep the original column order, then check with `diff original.csv exported.csv`.

None of this has been tested against PostgreSQL yet, so treat it as guidance and let `diff` have the final say.
