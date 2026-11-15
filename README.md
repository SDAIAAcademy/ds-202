<!-- academy:title -->
# Data Acquisition, Preparation and Quality

جمع البيانات وإعدادها وضمان جودتها

Data Science Track · SDAIA Academy · DS-202 · Level 200

Turn four raw sources into an analysis dataset that rebuilds with one command, with its provenance, its rules and an honest account of what is missing

Participants assemble an analysis dataset for a fictional food bank network from four sources: registrations with personal data, branch logs, a donations API and open population data. They record provenance, join with key and cardinality checks, clean Arabic and English text, dates and units, write validation rules that rerun on every build, and measure how missing data and measurement error move a headline estimate. Personal data are minimised and pseudonymised, and the dataset rebuilds from raw sources with one command.

**Format:** Intensive: 4 teaching days of four sessions and a capstone day, with guided pre-work and a tracked follow-up task

**Course page:** https://sdaiaacademy.github.io/ds-202/
<!-- /academy:title -->

## Outcomes

| | Outcomes | Level | Evidence |
|---|---|---|---|
| LO1 | Describe missing-data mechanisms and kinds of measurement error and the bias each can introduce, given six scenarios from the case | Awareness | mechanism and bias direction for each, at least five of six correct |
| LO2 | Prepare a provenance record per source covering origin, owner, coverage, sharing basis, refresh date and limits, given the four sources and their documentation | Applied | a provenance file that passes a reviewer's checklist |
| LO3 | Implement joins with key checks, cardinality tests and reconciliation counts so that no row is silently lost or duplicated, given tables with seeded duplicate, missing and mistyped keys | Applied | a join log of row counts per step and set-aside rows with reasons |
| LO4 | Configure validation rules for types, ranges, uniqueness, completeness and cross-field consistency that run on every rebuild, given the joined table and its data dictionary | Applied | a rule suite that passes on the clean build and fails readably on a corrupted batch |
| LO5 | Analyse how complete-case analysis, imputation and a sensitivity range change a headline estimate, given parcels per eligible household by district, with 18% of household sizes missing | Applied | a comparison table and a recommended estimate with its reason |
| LO6 | Build a rebuildable analysis dataset from raw sources with personal data minimised and pseudonymised, given a question set by the food bank and the four raw sources | Performance | a repository that rebuilds with one command, with provenance, rules and quality report, defended live |

<!-- academy:units -->
## Units

| Unit | Title | Sessions | Slides |
|---|---|---|---|
| Day 1 | Find and document the sources | Start from the question, not the files; Files, APIs and databases; Provenance and sharing basis; Coverage and sampling frames | [`slides/day1.html`](slides/day1.html) |
| Day 2 | Join and clean | Encodings and Arabic text; Keys and cardinality; Matching without a clean key; Types, units and dates | [`slides/day2.html`](slides/day2.html) |
| Day 3 | Missing data and measurement | Why data go missing; Imputation and its cost; Sensitivity ranges; Measurement error and proxies | [`slides/day3.html`](slides/day3.html) |
| Day 4 | Validate and protect | Quality dimensions as rules; Cross-field and cross-source checks; Minimise and pseudonymise; A data-quality report | [`slides/day4.html`](slides/day4.html) |
| Capstone | Capstone project presentations |  | [`slides/capstone.html`](slides/capstone.html) |
<!-- /academy:units -->

## Case study

**REPLACE: the name of the fictional organisation every lab works on.** REPLACE: two sentences on the case study and its synthetic data

<!-- academy:labs -->
## Labs

Every lab is a notebook in `labs/`. Open it in Google Colab from the course page, or run it locally with `uv`. Exercises raise `NotImplementedError` until they are done; the reference versions are in `labs/solutions/`.

| | Session | Lab | File |
|---|---|---|---|
| 1.1 | Day 1 · Session 1 | The question before the files | [`D1_1_list_variables_question.ipynb`](labs/D1_1_list_variables_question.ipynb) |
| 1.2 | Day 1 · Session 2 | Three ways in | [`D1_2_load_logs_page.ipynb`](labs/D1_2_load_logs_page.ipynb) |
| 1.3 | Day 1 · Session 3 | Two provenance records | [`D1_3_write_provenance_records.ipynb`](labs/D1_3_write_provenance_records.ipynb) |
| 1.4 | Day 1 · Session 4 | Who is not in the register | [`D1_4_compare_registrations_open.ipynb`](labs/D1_4_compare_registrations_open.ipynb) |
| 2.1 | Day 2 · Session 1 | One file, three encodings | [`D2_1_repair_mixed_encodings.ipynb`](labs/D2_1_repair_mixed_encodings.ipynb) |
| 2.2 | Day 2 · Session 2 | A join that loses nothing | [`D2_2_join_logs_registrations.ipynb`](labs/D2_2_join_logs_registrations.ipynb) |
| 2.3 | Day 2 · Session 3 | 300 records without a key | [`D2_3_match_300_records.ipynb`](labs/D2_3_match_300_records.ipynb) |
| 2.4 | Day 2 · Session 4 | One calendar, one unit | [`D2_4_standardise_three_date.ipynb`](labs/D2_4_standardise_three_date.ipynb) |
| 3.1 | Day 3 · Session 1 | Six gaps, six mechanisms | [`D3_1_classify_six_missingness.ipynb`](labs/D3_1_classify_six_missingness.ipynb) |
| 3.2 | Day 3 · Session 2 | Three estimates of one number | [`D3_2_estimate_parcels_per.ipynb`](labs/D3_2_estimate_parcels_per.ipynb) |
| 3.3 | Day 3 · Session 3 | How far could it move? | [`D3_3_bound_estimate_under.ipynb`](labs/D3_3_bound_estimate_under.ipynb) |
| 3.4 | Day 3 · Session 4 | When the answer itself is wrong | [`D3_4_simulate_self_report.ipynb`](labs/D3_4_simulate_self_report.ipynb) |
| 4.1 | Day 4 · Session 1 | Rules for the joined table | [`D4_1_write_type_range.ipynb`](labs/D4_1_write_type_range.ipynb) |
| 4.2 | Day 4 · Session 2 | Three rules across fields and sources | [`D4_2_add_three_consistency.ipynb`](labs/D4_2_add_three_consistency.ipynb) |
| 4.3 | Day 4 · Session 3 | A pseudonym that holds | [`D4_3_replace_national_id.ipynb`](labs/D4_3_replace_national_id.ipynb) |
| 4.4 | Day 4 · Session 4 | The quality report | [`D4_4_draft_quality_report.ipynb`](labs/D4_4_draft_quality_report.ipynb) |
<!-- /academy:labs -->

## Capstone

A rebuildable dataset for one of three synthetic questions, in a public repository whose README reports row counts per step, rule results and the estimate's sensitivity to missing data; eight-minute defence with a rebuild from raw files

**Submission:** REPLACE: what participants submit and how: a public repository link, or a shared folder for a course without code

## Prerequisites

- FN-101 Python for Data and AI Work
- FN-104 SQL and Data Wrangling
- FN-106 Responsible Data and AI Practice in the Kingdom
- Writes SQL joins and group-by queries without assistance

<!-- academy:tools -->
## Tools

Each line is a capability; the examples are interchangeable.

- **Analysis environment and notebooks:** Python with uv and JupyterLab or marimo, R with Quarto
- **Dataframes and analytical SQL engine:** DuckDB, Polars, pandas
- **Data validation rules:** Pandera, Great Expectations, SQL assertions
- **Record matching:** Splink, RapidFuzz, rules written in SQL
<!-- /academy:tools -->

<!-- academy:sources -->
## Sources

### National references

- [Personal Data Protection Law](https://sdaia.gov.sa/en/SDAIA/about/Documents/PersonalDataProtectionLaw.pdf)
- [Implementing Regulation of the Personal Data Protection Law](https://sdaia.gov.sa/en/SDAIA/about/Documents/ImplementingRegulationPersonalDataProtectionLaw.pdf)
- [Personal Data Destruction, Anonymization and Pseudonymisation Guideline](https://sdaia.gov.sa/Documents/PersonalDataDestructionAnonymizationAndEncryptionGuideline.pdf)
- [Data Classification Policy](https://sdaia.gov.sa/en/SDAIA/about/Documents/DataClassificationPolicy.pdf)
- [Data Sharing Policy](https://sdaia.gov.sa/en/SDAIA/about/Documents/DataSharingPolicyEN.pdf)
- [Open Data Policy](https://sdaia.gov.sa/en/SDAIA/about/Documents/OpenDataPolicy.pdf)

### Missing data and documentation

- [Stef van Buuren, Flexible Imputation of Missing Data, second edition (online book)](https://stefvanbuuren.name/fimd/)
- [Donald B. Rubin, Inference and missing data, Biometrika 63(3), 1976](https://www.jstor.org/stable/2335739)
- [Gebru and others, Datasheets for Datasets](https://arxiv.org/abs/1803.09010)

### Tools and standards

- [Pandera documentation](https://pandera.readthedocs.io/en/stable/)
- [Great Expectations documentation](https://docs.greatexpectations.io/docs/home/)
- [DuckDB documentation: CSV import](https://duckdb.org/docs/stable/data/csv/overview)
- [pandas documentation: DataFrame.merge and its validate argument](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html)
- [RapidFuzz documentation](https://rapidfuzz.github.io/RapidFuzz/)
- [Splink documentation](https://moj-analytical-services.github.io/splink/)
- [Python documentation: codecs, standard encodings](https://docs.python.org/3/library/codecs.html)
- [Python documentation: unicodedata](https://docs.python.org/3/library/unicodedata.html)
- [Unicode Standard Annex 15: Unicode Normalization Forms](https://unicode.org/reports/tr15/)
- [Python documentation: hmac](https://docs.python.org/3/library/hmac.html)
- [RFC 2104: HMAC, Keyed-Hashing for Message Authentication](https://datatracker.ietf.org/doc/html/rfc2104)
<!-- /academy:sources -->

### National references

- Personal Data Protection Law and its implementing regulations: REPLACE: the address of the official text
- PDPL guideline on destruction, anonymisation and pseudonymisation of personal data: REPLACE: the address of the official text
- NDMO Data Classification Policy: REPLACE: the address of the official text
- NDMO Data Sharing Policy: REPLACE: the address of the official text
- NDMO Open Data Policy: REPLACE: the address of the official text
