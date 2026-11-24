---
course: "Data Acquisition, Preparation and Quality"
code: "DS-202"
version: "2027.2.0"
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-202/index.html"
---

# Data Acquisition, Preparation and Quality

جمع البيانات وإعدادها وضمان جودتها

Data Science Track · 4 teaching days + capstone day · 26 hours · Level 200

Turn four raw sources into an analysis dataset that rebuilds with one command, with its provenance, its rules and an honest account of what is missing

Participants assemble an analysis dataset for a fictional food bank network from four sources: registrations with personal data, branch logs, a donations API and open population data. They record provenance, join with key and cardinality checks, clean Arabic and English text, dates and units, write validation rules that rerun on every build, and measure how missing data and measurement error move a headline estimate. Personal data are minimised and pseudonymised, and the dataset rebuilds from raw sources with one command.

**Who it is for:** Practitioners. Graduates and early-career analysts who have completed the FN courses or passed the placement test, and analysts moving into data science.

**Format:** Intensive: 4 teaching days of four sessions and a capstone day, with guided pre-work and a tracked follow-up task

## The case study

**Ghilal Food Bank Network.** Ghilal Food Bank Network (شبكة غِلال لبنوك الطعام) is a fictional network of 14 branches serving the 30 districts of a fictional city, Madinat Al-Sidr. Its programmes director asks how many parcels an eligible household received per month in each district in the third quarter of 2026; participants assemble the answer from 40,000 registrations with personal data, 210,000 branch log rows, a local donations API and an open district population table. All data is synthetic and generated with a fixed seed, with planted encoding faults, duplicate and mistyped keys, gaps, unit errors and missing household sizes that each lab finds.

## The course

### Day 1: Find and document the sources

Slides: https://sdaiaacademy.github.io/ds-202/slides/day1.md

- **Session 1: Start from the question, not the files**
  - Take a question apart into unit, population, period and groups
  - List the fields a question needs, with a source for each
  - Name the fields left out and the gaps no source fills
  - [Lab 1.1: The question before the files (25 min)](https://sdaiaacademy.github.io/ds-202/labs/D1_1_list_variables_question.ipynb)
- **Session 2: Files, APIs and databases**
  - Load files as text whatever their encoding
  - Page through an API and reconcile with its total
  - Query a register in SQL and build a source inventory
  - Prove a paged retrieval complete; retry with a limit, then alert
  - [Lab 1.2: Three ways in (25 min)](https://sdaiaacademy.github.io/ds-202/labs/D1_2_load_logs_page.ipynb)
- **Session 3: Provenance and sharing basis**
  - Write a provenance record with its six fields and a classification level
  - State the sharing basis and its purpose
  - Pass and apply a reviewer checklist
  - [Lab 1.3: Two provenance records (25 min)](https://sdaiaacademy.github.io/ds-202/labs/D1_3_write_provenance_records.ipynb)
- **Session 4: Coverage and sampling frames**
  - Compare a register with an outside frame by district
  - Account for rows that match on one side only
  - Flag under-covered districts and word the caveat
  - [Lab 1.4: Who is not in the register (25 min)](https://sdaiaacademy.github.io/ds-202/labs/D1_4_compare_registrations_open.ipynb)

### Day 2: Join and clean

Slides: https://sdaiaacademy.github.io/ds-202/slides/day2.md

- **Session 1: Encodings and Arabic text**
  - Decode a file line by line and count each encoding
  - Repair names that were decoded twice
  - Normalise Arabic letters and digits into a key and log every repair
  - [Lab 2.1: One file, three encodings (25 min)](https://sdaiaacademy.github.io/ds-202/labs/D2_1_repair_mixed_encodings.ipynb)
- **Session 2: Keys and cardinality**
  - Repair mistyped keys by stated rules
  - Test many-to-one before joining
  - Reconcile rows in with rows out plus rows set aside
  - [Lab 2.2: A join that loses nothing (25 min)](https://sdaiaacademy.github.io/ds-202/labs/D2_2_join_logs_registrations.ipynb)
- **Session 3: Matching without a clean key**
  - Block and score candidate pairs
  - Measure false matches and missed matches on labelled pairs
  - Choose a threshold and state its cost
  - Build a master record field by field from records that disagree
  - [Lab 2.3: 300 records without a key (25 min)](https://sdaiaacademy.github.io/ds-202/labs/D2_3_match_300_records.ipynb)
- **Session 4: Types, units and dates**
  - Decide a date layout per source from evidence
  - Bring weights in two units to one, and catch mislabelled ones
  - Write a change log with a count per rule
  - [Lab 2.4: One calendar, one unit (25 min)](https://sdaiaacademy.github.io/ds-202/labs/D2_4_standardise_three_date.ipynb)

### Day 3: Missing data and measurement

Slides: https://sdaiaacademy.github.io/ds-202/slides/day3.md

- **Session 1: Why data go missing**
  - Tabulate missingness against observed fields
  - Tell the three mechanisms apart with evidence
  - Give the direction of bias each one causes
  - [Lab 3.1: Six gaps, six mechanisms (25 min)](https://sdaiaacademy.github.io/ds-202/labs/D3_1_classify_six_missingness.ipynb)
- **Session 2: Imputation and its cost**
  - Compute a complete-case estimate and say what it assumes
  - Impute a single value and a value within groups
  - Compare the estimates overall and by district
  - Weight a survey for nonresponse after a follow-up of nonrespondents
  - [Lab 3.2: Three estimates of one number (25 min)](https://sdaiaacademy.github.io/ds-202/labs/D3_2_estimate_parcels_per.ipynb)
- **Session 3: Sensitivity ranges**
  - Compute the logical bounds of an estimate
  - Build a plausible range by shifting the imputed values
  - Recommend one estimate with its range and its reason
  - [Lab 3.3: How far could it move? (25 min)](https://sdaiaacademy.github.io/ds-202/labs/D3_3_bound_estimate_under.ipynb)
- **Session 4: Measurement error and proxies**
  - Measure reporting error against an audit
  - Simulate random and one-directional error
  - Say what a proxy measures and what it does not
  - Link a series across a changed question, or report the break
  - [Lab 3.4: When the answer itself is wrong (25 min)](https://sdaiaacademy.github.io/ds-202/labs/D3_4_simulate_self_report.ipynb)

### Day 4: Validate and protect

Slides: https://sdaiaacademy.github.io/ds-202/slides/day4.md

- **Session 1: Quality dimensions as rules**
  - Translate a data dictionary into column rules
  - Name the quality dimension of each rule
  - Run the suite on a build and read its failures
  - [Lab 4.1: Rules for the joined table (25 min)](https://sdaiaacademy.github.io/ds-202/labs/D4_1_write_type_range.ipynb)
- **Session 2: Cross-field and cross-source checks**
  - Write rules across two fields
  - Write a rule across two sources
  - Produce a failure report a data owner can act on
  - [Lab 4.2: Three rules across fields and sources (25 min)](https://sdaiaacademy.github.io/ds-202/labs/D4_2_add_three_consistency.ipynb)
- **Session 3: Minimise and pseudonymise**
  - Re-link a plain hash with a list and by enumeration
  - Replace identifiers with a keyed hash
  - Measure uniqueness on quasi-identifiers and reduce it by generalising
  - [Lab 4.3: A pseudonym that holds (25 min)](https://sdaiaacademy.github.io/ds-202/labs/D4_3_replace_national_id.ipynb)
- **Session 4: A data-quality report**
  - Rebuild a dataset from raw sources with one command
  - Draft a data-quality report from the build outputs
  - Classify outputs and choose a capstone question
  - [Lab 4.4: The quality report (25 min)](https://sdaiaacademy.github.io/ds-202/labs/D4_4_draft_quality_report.ipynb)

### Capstone: Capstone project presentations

Slides: https://sdaiaacademy.github.io/ds-202/slides/capstone.md

## Capstone

A rebuildable dataset for one of three synthetic questions, in a public repository whose README reports row counts per step, rule results and the estimate's sensitivity to missing data; eight-minute defence with a rebuild from raw files

**What you submit:** A public GitHub repository link. The repository rebuilds the analysis dataset from the raw files of the capstone extract with one command, and holds the provenance file, the rule suite and the set-aside rows (log id, branch and reason, without the household key as typed); its README reports row counts per step, rule results and the sensitivity of the estimate to missing data. No raw personal field is committed, synthetic or not. Then an eight-minute defence with a live rebuild, in which the assessor corrupts one input file and you show which rule fails and why, and four minutes of questions.

**Rubric:**

- Provenance: 15%
- Joins and reconciliation: 25%
- Cleaning and validation: 25%
- Missing data and sensitivity: 20%
- Personal data and reproducibility: 15%

## Outcomes

- **LO1** Describe missing-data mechanisms and kinds of measurement error and the bias each can introduce, given six scenarios from the case (Awareness) Evidence: mechanism and bias direction for each, at least five of six correct
- **LO2** Prepare a provenance record per source covering origin, owner, coverage, sharing basis, refresh date and limits, given the four sources and their documentation (Applied) Evidence: a provenance file that passes a reviewer's checklist
- **LO3** Implement joins with key checks, cardinality tests and reconciliation counts so that no row is silently lost or duplicated, given tables with seeded duplicate, missing and mistyped keys (Applied) Evidence: a join log of row counts per step and set-aside rows with reasons
- **LO4** Configure validation rules for types, ranges, uniqueness, completeness and cross-field consistency that run on every rebuild, given the joined table and its data dictionary (Applied) Evidence: a rule suite that passes on the clean build and fails readably on a corrupted batch
- **LO5** Analyse how complete-case analysis, imputation and a sensitivity range change a headline estimate, given parcels per eligible household by district, with 18% of household sizes missing (Applied) Evidence: a comparison table and a recommended estimate with its reason
- **LO6** Build a rebuildable analysis dataset from raw sources with personal data minimised and pseudonymised, given a question set by the food bank and the four raw sources (Performance) Evidence: a repository that rebuilds with one command, with provenance, rules and quality report, defended live

## Tools

- **Analysis environment and notebooks:** Python with uv and JupyterLab or marimo, R with Quarto
- **Dataframes and analytical SQL engine:** DuckDB, Polars, pandas
- **Data validation rules:** Pandera, Great Expectations, SQL assertions
- **Record matching:** Splink, RapidFuzz, rules written in SQL

## Prerequisites

- FN-101 Python for Data and AI Work
- FN-104 SQL and Data Wrangling
- FN-106 Responsible Data and AI Practice in the Kingdom
- Writes SQL joins and group-by queries without assistance
- Setup: a laptop CPU with uv, or Google Colab. No key, account or model is needed. Run 00_setup_check and the two-hour pre-work notebook before Day 1; see labs/README.md.

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

---

SDAIA Academy · Data Science Track · Data Acquisition, Preparation and Quality

Course version 2027.2.0 · engine 1.0.0 · built 2026-11-24 · commit 1cc3909
