---
course: "Data Acquisition, Preparation and Quality"
code: "DS-202"
version: "2027.2.0"
scope: "course"
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-202/"
---

# Data Acquisition, Preparation and Quality

Turn four raw sources into an analysis dataset that rebuilds with one command, with its provenance, its rules and an honest account of what is missing

Participants assemble an analysis dataset for a fictional food bank network from four sources: registrations with personal data, branch logs, a donations API and open population data. They record provenance, join with key and cardinality checks, clean Arabic and English text, dates and units, write validation rules that rerun on every build, and measure how missing data and measurement error move a headline estimate. Personal data are minimised and pseudonymised, and the dataset rebuilds from raw sources with one command.

- **Audience:** Practitioners. Graduates and early-career analysts who have completed the FN courses or passed the placement test, and analysts moving into data science.
- **Prerequisites:** FN-101 Python for Data and AI Work; FN-104 SQL and Data Wrangling; FN-106 Responsible Data and AI Practice in the Kingdom; Writes SQL joins and group-by queries without assistance; Setup: a laptop CPU with uv, or Google Colab. No key, account or model is needed. Run 00_setup_check and the two-hour pre-work notebook before Day 1; see labs/README.md.
- **Case study:** Ghilal Food Bank Network: Ghilal Food Bank Network (شبكة غِلال لبنوك الطعام) is a fictional network of 14 branches serving the 30 districts of a fictional city, Madinat Al-Sidr. Its programmes director asks how many parcels an eligible household received per month in each district in the third quarter of 2026; participants assemble the answer from 40,000 registrations with personal data, 210,000 branch log rows, a local donations API and an open district population table. All data is synthetic and generated with a fixed seed, with planted encoding faults, duplicate and mistyped keys, gaps, unit errors and missing household sizes that each lab finds.

## Outcomes

- LO1 (Awareness): Describe missing-data mechanisms and kinds of measurement error and the bias each can introduce, given six scenarios from the case
- LO2 (Applied): Prepare a provenance record per source covering origin, owner, coverage, sharing basis, refresh date and limits, given the four sources and their documentation
- LO3 (Applied): Implement joins with key checks, cardinality tests and reconciliation counts so that no row is silently lost or duplicated, given tables with seeded duplicate, missing and mistyped keys
- LO4 (Applied): Configure validation rules for types, ranges, uniqueness, completeness and cross-field consistency that run on every rebuild, given the joined table and its data dictionary
- LO5 (Applied): Analyse how complete-case analysis, imputation and a sensitivity range change a headline estimate, given parcels per eligible household by district, with 18% of household sizes missing
- LO6 (Performance): Build a rebuildable analysis dataset from raw sources with personal data minimised and pseudonymised, given a question set by the food bank and the four raw sources

## Day 1: Find and document the sources

The question, the four sources, their provenance and who they leave out

#### [day1#title] Find and document the sources

*SDAIA Academy · Data Acquisition, Preparation and Quality*

Day 1: The question, the four sources, their provenance and who they leave out

Data Science Track · 4 teaching days + capstone day · 4 sessions · 4 labs · DS-202

#### [day1#agenda] Find and document the sources

*Today*

- **Session 1 · Start from the question, not the files**: The question fixes the unit, the population and the period; the variables follow
- **Session 2 · Files, APIs and databases**: Files, an API and a database each fail differently: count what arrived against what was sent
- **Session 3 · Provenance and sharing basis**: A record per source: origin, owner, coverage, sharing basis, refresh date and limits
- **Session 4 · Coverage and sampling frames**: A register lists who registered, not who is in need; an outside frame shows the gap

### Session 1: Start from the question, not the files

#### [day1#s1] Start from the question, not the files

*Session 1*

- Take a question apart into unit, population, period and groups
- List the fields a question needs, with a source for each
- Name the fields left out and the gaps no source fills

#### [day1#the-request] Ghilal Food Bank Network asks one question of four sources

*The case*

"In the third quarter of 2026, how many parcels did an eligible household receive per month in each district, and which districts are below our standard of two?"

- **The register.** 40,000 registrations with personal data. Widad Al-Ghunaim.
- **Branch logs.** 210,000 handout rows in 14 files. Hazem Al-Sulaim.
- **Donations API.** Every delivery of food to a branch. Talal Al-Wabil.
- **Open district table.** Population and households, 2022. The municipality.

#### [day1#four-parts] A question fixes four things, and each one removes a way to be wrong

*Before any file*

| Part | In this question | If you leave it open |
| --- | --- | --- |
| **Unit** | a household | you count handouts, and a household served twice counts twice |
| **Population** | active, eligible, registered before 1 July 2026 | September registrations get one month and look under-served |
| **Period** | 1 July to 30 September 2026 | each branch reports its own "last quarter" |
| **Groups** | the district of the household | you group by branch, and a branch is not a district |

#### [day1#eligibility-rule] Eligibility is income per member, so household size decides who is counted

*The rule of the network*

- Eligible: an active household whose monthly income per member is **at most 1,000 SAR**
- Income 6,000 SAR with 5 members: 1,200 per member, not eligible
- The same income with 7 members: 857 per member, eligible
- A household with no recorded size cannot be classified at all

- **Why this matters on Day 3.** Household size is blank for 18% of the population of the question. The denominator of the headline depends on a field that is often missing.

#### [day1#variables-first] From the answer to variables, from variables to fields, and only then to files

*Work backwards*

1. **1 · The answer** parcels per eligible household per month, by district
2. **2 · Variables** parcels, date, eligibility, district, a link between the two
3. **3 · Fields** one source field for each variable
4. **4 · Files** request only those fields

> **What goes wrong.** Starting from the files: every column looks useful, all of them are taken, and the question is bent to fit what happened to be there.

#### [day1#nine-fields] The answer needs 9 of the 34 fields

*Lab 1.1, step 2*

| Role | Field | Source |
| --- | --- | --- |
| numerator | parcels, handout_date | branch logs |
| link | household_id | logs and register |
| population | status, registered_on | register |
| eligibility | household_size, monthly_income_sar | register |
| groups | district_id | register |

**9 of 34** fields in the four sources that the headline needs

Two more, from the open table, are justified by the coverage check of Session 4.

#### [day1#not-taken] What the purpose does not need is not taken

*Minimisation, at the first step*

| Field | Why it stays behind |
| --- | --- |
| national_id | household_id already links the sources |
| head_name | no step of the answer uses a name |
| phone | nobody is contacted |
| collected_by | does not change a count of parcels |
| note | free text can hold anything |

> **The law, in one line.** The Personal Data Protection Law limits the content of personal data to the minimum necessary for the purpose. The cheapest moment to apply it is before the extract is requested.

#### [day1#gaps] Three things the question needs are in no source

*Lab 1.1, step 4*

- **Households that never registered.** The register lists who came. Session 4 measures how many did not.
- **Verified household sizes.** Sizes are reported by the household. An audit verified 600 of them.
- **A frame for D29 and D30.** Two districts established after the open table was made.

> **Write gaps down on Day 1.** A gap named before the analysis is a limit. A gap found by a reader afterwards is an error.

#### [day1#check-question] Which field do you ask for?

*Checkpoint*

**Question:** Widad offers to add any register field to your extract. The headline is parcels per eligible household per month, by district. Which one do you ask her to include?

- A. household_size, because eligibility is income per member
- B. national_id, to be sure of linking the right household
- C. phone, in case a household must be called to confirm
- D. every field, since unused columns can be dropped later

#### [day1#lab-1-1] The question before the files

Lab 1.1 · 25 min

Take the question of the programmes director apart, list the variables it needs with one source field for each, write down the fields you will not take and the gaps no source fills.

[D1_1_list_variables_question.ipynb](https://sdaiaacademy.github.io/ds-202/labs/D1_1_list_variables_question.ipynb)

- [ ] Take the question apart (5 min)
- [ ] The fields the question needs (10 min)
- [ ] The fields you will not take (5 min)
- [ ] What no source provides (5 min)
- [ ] ✱ Stretch: A second question, and what it adds

### Session 2: Files, APIs and databases

#### [day1#s2] Files, APIs and databases

*Session 2*

- Load files as text whatever their encoding
- Page through an API and reconcile with its total
- Query a register in SQL and build a source inventory
- Prove a paged retrieval complete; retry with a limit, then alert

#### [day1#three-doors] Files, an API and a database fail in three different ways

*How data arrive*

- **Files.** Nothing describes them. Encoding, date layout and units are in nobody's head but the sender's. A file can come twice or not at all.
- **An API.** Data come in pages, the service can be busy, and records change while you read. It usually states a total.
- **A database.** Types and keys are declared, but only the ones somebody declared. Your query decides what you see.

#### [day1#text-first] Load every column as text first; decide types later, in steps you can count

*Recap of FN-104, one step further*

- B01 reads as UTF-8. **B03 fails** at its first Arabic name: it is in Windows-1256
- B08 opens, but begins with three extra bytes, `EF BB BF`: a byte order mark that a spreadsheet wrote
- As text, nothing is lost: 14 files, **210,000 rows**, every repair still ahead and countable

> **What goes wrong.** The mark becomes part of the first column name, and `log_id` is "not found" in one file of fourteen.

#### [day1#paging] Follow next until it is null, and expect a busy answer

*Reading an API*

```python
# file: Lab 1.2 · fetch_all
records, url = [], "/v1/donations?page=1&per_page=200"
while url:
    page = G.get_json(base + url)   # retries a 503
    records += page["data"]
    total, url = page["total"], page["next"]
```

- The address of the next page comes from the answer; do not compute it
- 503 means "busy, ask again"; how often, and then what, follows the paging proof
- Keep the `total` the service reports: it is its claim about itself

#### [day1#api-total] The API sent 12 records more than its own total

*Measured in Lab 1.2*

**5,137 · 5,125** records received, and the total the API reports

- Donations kept arriving while the 26 pages were read
- Four pages begin with records the page before ended with: 12 ids arrive twice; distinct ids are exactly 5,125
- The inventory records the distinct count **and** the 12 that were dropped

#### [day1#cursor-proof] A page number shifts while records arrive; a cursor does not, and four checks prove you read it all

*Proving the end*

- **Page numbers.** "Rows 401 to 600" of a table that grows. A new record shifts the rows after it: rows repeat across pages, or are skipped.
- **A cursor.** The answer says "continue after this record". New arrivals do not move what is left to read.

1. **Chain:** every request sent the cursor the answer before returned
2. **End:** the last answer's next cursor is null
3. **Keys:** no id twice, or the repeats counted and dropped
4. **Count:** distinct ids equal the total the source states, or a count from a second route

#### [day1#paging-log] The stock-movements API reports 2,346 records: was the retrieval complete?

*Read the log, then decide*

| Request | Cursor sent | Records (ids) | Next cursor |
| --- | --- | --- | --- |
| 1 | none | 500 (1 to 500) | c1 |
| 2 | c1 | 500 (501 to 1,000) | c2 |
| 3 | c2 | 500 (1,001 to 1,500) | c3 |
| 4 | c4 | 346 (2,001 to 2,346) | null |

> **No.** The end check passes and the keys are unique, but request 4 sent `c4` where the answer before returned `c3`. Ids 1,501 to 2,000 were never asked for: 1,846 received of 2,346.

#### [day1#retry-backoff] Retry only what may pass next time, wait longer each time, and stop at a limit

*When the source is busy*

| Attempt | Answer | Wait before the next |
| --- | --- | --- |
| 1 | 503 busy | 1 s |
| 2 | 503 busy | 2 s |
| 3 | timeout | 4 s |
| 4 | 429 too many | 8 s, the cap |
| 5 | 503 busy | none: give up |

- **Retry:** 503, 429 and timeouts. **Never:** 400, 401, 404; asking again gives the same answer
- The wait doubles up to a cap, with a little random jitter so many clients do not retry in step
- Five attempts and 15 seconds of waiting, then the run stops

#### [day1#retry-alert] A failed ingestion stops the build and tells a person; it never continues with what it has

*When retries run out*

- **What goes wrong.** The loop catches the last error, logs "warning" and moves on. The build finishes green with a page missing, and the paging log that would show it is what nobody reads.
- **The alert.** Source, request and cursor, attempts and the last answer, the time of the last good extract, and the owner to call, by role. The build keeps yesterday's extract and says so.

#### [day1#register-sql] 40,000 rows describe 39,820 households

*The register, in SQL*

```sql
-- file: Lab 1.2 · register_counts
SELECT count(*),
       count(DISTINCT household_id),
       min(registered_on),
       max(registered_on)
FROM registrations;
```

**180** household ids that are in the register twice

- **Not an error, yet.** A household that registers again at another branch gets a second row. It becomes an error in the first join that assumes one row per id.

#### [day1#inventory] Three sources reconcile; the largest has nothing to reconcile against

*The source inventory*

| Source | Arrives as | Rows | The source says | Agrees |
| --- | --- | --- | --- | --- |
| register | database extract | 40,000 | 40,000 registrations | yes |
| branch logs | 14 files | 210,000 | nothing | unknown |
| donations | API, 26 pages | 5,125 | total = 5,125 | yes |
| open district table | one file | 28 | 28 districts of 2022 | yes |

> **What goes wrong.** A week uploaded twice and a week never uploaded both pass this table. The logs hold one of each.

#### [day1#check-total] Your count and the count of the source disagree

*Checkpoint*

**Question:** You paged through an API and hold 5,137 records. The API reports a total of 5,125. What goes into the source inventory?

- A. 5,137: it is what actually arrived
- B. 5,125: the API knows its own data
- C. 5,125 distinct ids, and a line that 12 repeats were dropped
- D. Either: twelve records cannot change the analysis

#### [day1#lab-1-2] Three ways in

Lab 1.2 · 25 min

Load the 14 branch log files whatever their encoding, page through the donations API until it ends and reconcile with its total, query the register in SQL, and write a source inventory.

[D1_2_load_logs_page.ipynb](https://sdaiaacademy.github.io/ds-202/labs/D1_2_load_logs_page.ipynb)

- [ ] Load the 14 log files, whatever their encoding (7 min)
- [ ] Page through the donations API and reconcile with its total (8 min)
- [ ] Query the register in SQL (6 min)
- [ ] The source inventory (4 min)
- [ ] ✱ Stretch: Does a smaller page size change what arrives?

### Session 3: Provenance and sharing basis

#### [day1#s3] Provenance and sharing basis

*Session 3*

- Write a provenance record with its six fields and a classification level
- State the sharing basis and its purpose
- Pass and apply a reviewer checklist

#### [day1#why-provenance] Somebody will ask where a number came from, and you will not be in the room

*A year from now*

- Which extract was this, and from which day?
- Who can say what a column means?
- Were we allowed to use it for this?
- What is it known not to cover?

- **A provenance record.** One short record per source, kept in the repository beside the code, changed in the same commit as the extract it describes.

#### [day1#six-fields] Six fields, and what a reviewer needs to read in each

*The record*

| Field | A reviewer needs |
| --- | --- |
| **origin** | the system, and how the extract was made |
| **owner** | the person to ask, by role |
| **coverage** | which units, which period, and who is not in it |
| **sharing basis** | the consent, agreement or approval, and its purpose |
| **refresh date** | the day your copy was taken |
| **limits** | what the data cannot be trusted for |

The labs add a seventh key, the classification level of the source.

#### [day1#sharing-basis] Holding an extract is not permission to use it for the next question

*On what basis*

- The register extract came under approval DS-2026-041, for **service coverage analysis, Q3 2026**
- The approval names a purpose, the people who may see the data, and that identified records go no further
- A new question next year is a new request to the data protection officer

- **In the Data Sharing Policy.** Among its principles: sharing serves a legitimate purpose, and access is authorised on a need-to-know and least-privilege basis.

#### [day1#classification] Three of the four sources are Restricted; one is Public

*The seventh key*

| Source | Level | Because |
| --- | --- | --- |
| register | Restricted | personal data of beneficiaries |
| branch logs | Restricted | household ids and names of collectors |
| donations API | Restricted | internal operations, no donor names |
| open district table | Public | published under an open licence |

The national policy has four levels: Top Secret, Secret, Restricted and Public. Anything joined to a Restricted source is at least Restricted.

#### [day1#three-dates] The open table has three dates, and only one is the refresh date

*Open data has provenance too*

- **2022.** The year the rows describe. It belongs in **coverage**.
- **15 March 2023.** The day it was published. It identifies the release, in **origin**.
- **2 October 2026.** The day our copy was downloaded: the **refresh date**.

> **And the gap between them is a limit.** A table about 2022 used in 2026 describes a city that has since grown, unevenly.

#### [day1#weak-record] A record written in a hurry fails eight checks

*Lab 1.3, step 3*

- **The draft.** origin: "files" · owner: "Hazem" · coverage: "this year" · sharing basis: "internal" · refresh date: "October" · limits: "messy" · classification: "Internal"
- **Repaired from the source note.** One row per handout, 1 January to 30 September 2026, all 14 branches. Copy of 2026-10-03. Four limits, among them: a week can be uploaded twice or be missing, and no file says so.

"Internal" is not one of the four levels. "This year" will be false in January.

#### [day1#limits-feed-later] A limit written on Day 1 is an explanation on Day 3

*Why limits earn their place*

- "The online form and the call script offer sizes 1 to 6 only": why sizes are missing for large households
- "No size field on the paper form of B03 and B11 before March 2025": why they are missing at two branches
- "Sizes are reported, not verified": why an audit was needed
- "A week can be missing, and no file says so": why a district can look under-served

#### [day1#check-provenance] Which coverage line passes a reviewer?

*Checkpoint*

**Question:** You are writing the coverage field of the register record. Which line lets a stranger decide what the data can answer?

- A. All households registered with the network
- B. Registrations 2021-01-03 to 2026-09-28; households that never registered are absent
- C. 40,000 rows, 11 columns, 4.4 MB
- D. Extract taken on 2026-10-04 from the register

#### [day1#lab-1-3] Two provenance records

Lab 1.3 · 25 min

Write the provenance records of the register and of the open district table from their source notes, repair a weak record with the reviewer checklist, and assemble the provenance file of the project.

[D1_3_write_provenance_records.ipynb](https://sdaiaacademy.github.io/ds-202/labs/D1_3_write_provenance_records.ipynb)

- [ ] The record of the register (9 min)
- [ ] The record of the open district table (7 min)
- [ ] Run the checklist and repair a weak record (5 min)
- [ ] Assemble provenance.json (4 min)
- [ ] ✱ Stretch: A record for the audit file

### Session 4: Coverage and sampling frames

#### [day1#s4] Coverage and sampling frames

*Session 4*

- Compare a register with an outside frame by district
- Account for rows that match on one side only
- Flag under-covered districts and word the caveat

#### [day1#frame-vs-register] The question is about households in need; the register lists households that came

*Three populations*

1. **In need** every low-income household of the city. Nobody has this list.
2. **The frame** a 2022 survey estimate of low-income households, by district
3. **The register** households that registered, by district

> **Coverage** is the register divided by the frame. It says how much of the population of interest the data can speak for.

#### [day1#outer-join] A join against an outside list has three outcomes; an inner join shows one

*Lab 1.4, step 2*

- **In both · 28.** Districts with a registered count and a frame.
- **Register only · 2.** D29 and D30: 2,523 registered households, no row in the frame.
- **Frame only · 0.** No district of the frame is without registrations.

With an inner join the table has 28 tidy rows, and 2,523 households leave the analysis without a message.

#### [day1#coverage-numbers] In four districts the register reaches about a third of the households in need

*Measured in Lab 1.4*

| Item | Value |
| --- | --- |
| D07 Al-Mahjar | 0.31 |
| D22 Al-Jabal | 0.34 |
| D26 Wadi Al-Sidr | 0.34 |
| D15 Al-Sahil | 0.36 |
| 23 other districts | 0.71 to 0.90 |
| D03 Al-Waha | 1.18 |

#### [day1#over-100] Coverage of 118% says the frame is old, not that the register is wrong

*A ratio above 1*

- D03: 1,113 registered households against an estimate of 940
- The frame describes 2022; the district has grown since
- The estimate is from a survey, with no published margin of error
- "Low income" in the survey is not the eligibility rule of the network

> **What goes wrong.** Reading the ratio as a fact about the register: "178 fabricated households". The denominator is the uncertain part.

#### [day1#missing-units] Under-coverage is whole households missing, and not at random

*A first kind of missing data*

- Missing **values**: the household is there, a field is blank. Day 3, Sessions 1 to 3
- Missing **units**: the household is not in the data at all
- Households far from a branch register less; they are also the ones served least
- The headline is therefore too kind to exactly the districts it is meant to find

- **No repair, only a report.** No imputation of a field brings back a household that was never listed. The coverage table goes beside the headline.

#### [day1#coverage-note] Three sentences go under the headline

*Lab 1.4, step 4*

- The figure describes registered households only; in D07, D15, D22 and D26 fewer than half of the estimated low-income households are registered
- For D29 and D30 the share of households in need that are registered is unknown: the frame has no row
- The frame is a 2022 survey estimate; coverage ratios are approximate

> **And two that must not.** "Low coverage means low need." "Coverage above 100% shows fabricated households."

#### [day1#check-coverage] A district that looks well served

*Checkpoint*

**Question:** District D22 shows a healthy number of parcels per registered household, and its coverage is 0.34. What may the report say about D22?

- A. D22 is well served and needs no attention
- B. Its true figure is the reported one multiplied by 0.34
- C. Nothing: with such coverage the district must be dropped
- D. Its registered households are served; most households in need are not registered

#### [day1#lab-1-4] Who is not in the register

Lab 1.4 · 25 min

Count registered households per district in SQL, join them to the open table with a full outer join, compute coverage ratios, flag the under-covered districts and choose the sentences that go under the headline.

[D1_4_compare_registrations_open.ipynb](https://sdaiaacademy.github.io/ds-202/labs/D1_4_compare_registrations_open.ipynb)

- [ ] Registered households per district, in SQL (5 min)
- [ ] Join to the open table and find what does not match (7 min)
- [ ] Coverage ratios and flags (8 min)
- [ ] The coverage note (5 min)
- [ ] ✱ Stretch: A second frame: all households

#### [day1#wrap-up] Three things to keep

*Day 1 · wrap-up*

- **The question chooses the fields.** Unit, population, period, groups. Nine fields of 34; five identifying fields stay behind.
- **Count before you read.** What arrived against what the source says: 5,125 of 5,125, 40,000 rows for 39,820 households, and logs that say nothing.
- **Write down what a source cannot do.** Six fields per source, and a coverage table that keeps four districts from looking well served.

#### [day1#next] Join and clean: every repair counted

*Next · Day 2*

- One register file in three states of encoding, and names that must match
- 210,000 log rows joined to the register without losing or adding a row
- 300 walk-in records with no key at all
- Three date layouts and two weight units that no file declares

## Day 2: Join and clean

Bytes, keys, people without keys, dates and units, each repair counted

#### [day2#title] Join and clean

*SDAIA Academy · Data Acquisition, Preparation and Quality*

Day 2: Bytes, keys, people without keys, dates and units, each repair counted

Data Science Track · 4 teaching days + capstone day · 4 sessions · 4 labs · DS-202

#### [day2#review-day-1] A count that nobody can check

*Review of Day 1*

**Question:** The inventory of Day 1 shows 210,000 log rows from 14 files, and the logs state no total of their own. What does that line of the inventory allow you to say?

- A. The logs are complete: 210,000 rows arrived
- B. 210,000 rows arrived; whether any are missing or doubled is unknown
- C. The logs are wrong: a round number is suspicious
- D. The logs cannot be used until the branches state totals

#### [day2#agenda] Join and clean

*Today*

- **Session 1 · Encodings and Arabic text**: One file, several encodings: decide line by line, repair, and match on a normalised key
- **Session 2 · Keys and cardinality**: Repair keys by rule, test the cardinality, and make the row counts add up
- **Session 3 · Matching without a clean key**: Block, score and choose a threshold on labelled pairs: a false match costs most
- **Session 4 · Types, units and dates**: Layout and unit belong to the source, not the value: decide per branch, convert, log

### Session 1: Encodings and Arabic text

#### [day2#s1] Encodings and Arabic text

*Session 1*

- Decode a file line by line and count each encoding
- Repair names that were decoded twice
- Normalise Arabic letters and digits into a key and log every repair

#### [day2#three-states] A line of the register is in one of three states, and no encoding reads them all

*One file, appended from 14 exports*

| State | What you see | Lines |
| --- | --- | --- |
| UTF-8, correct | ماجد محمد باوزير | most |
| Windows-1256 bytes (B03, B11) | fails as UTF-8 | 5,458 |
| UTF-8 that was decoded twice (B06) | ط¨ظ†ط¯ط± …: valid UTF-8, wrong letters | 2,732 names |

> **What goes wrong.** Reading the whole file as Windows-1256 raises no error: every byte is a letter in that code page. The 34,542 UTF-8 lines become nonsense, quietly.

#### [day2#line-by-line] Decide per line: valid UTF-8 is UTF-8; what is not is the legacy code page

*The decision rule*

```python
# file: Lab 2.1 · decode
def decode(b: bytes):
    try:
        return b.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return b.decode("cp1256"), "cp1256"
```

- Arabic in Windows-1256 is almost never valid UTF-8, so the test is safe in this direction
- Return the encoding with the text and **count** it
- The count has a shape: all 5,458 lines are from two branches. A scatter over all branches would mean the rule is wrong

#### [day2#decoded-twice] Undo the wrong step, and prove the rule leaves correct text alone

*The state that raises no error anywhere*

1. **1 · Typed** بندر stored as UTF-8 bytes
2. **2 · Misread** the branch system read the bytes as Windows-1256 and saved the result
3. **3 · Repair** `s.encode("cp1256").decode("utf-8")`

- Correct Arabic does not survive that round trip: the decode fails and the function returns the text unchanged
- So the function is safe on all 40,000 names, and changes 2,732, every one at B06

#### [day2#letters-and-keys] A key is a normalised copy for matching; the stored name is never replaced

*After the bytes, the letters*

| Rule | Example |
| --- | --- |
| drop marks and the stretch mark | مُحمّد → محمد |
| one alef; ى → ي; ة → ه | أحمد → احمد |
| join عبد to the next word | عبد الله → عبدالله |
| one space between words | trailing and double spaces go |

24,355 distinct Arabic names as typed are 21,252 distinct keys: about one "different" name in eight was a spelling variant.

#### [day2#digits-hide] An ID number typed in Arabic-Indic digits is a different string

*Digits are text too*

**39,851 → 39,820** distinct national ids, before and after the digit rule

- One branch typed 2,784 ID numbers as ١٠٩٠…
- 31 households registered there and again elsewhere: one person, two strings
- A count of distinct people, or a join on the id, was wrong with no error
- Normalise digits in every key before you compare it with anything

#### [day2#repair-log] A repair that is not counted cannot be checked, repeated or reversed

*The habit of the day*

- **A rule.** Written as code, applied to every row, never by hand to a few.
- **A count.** One line per rule in a log: how many rows it changed, and where.
- **The original.** Kept beside the repaired value, so a reviewer can disagree.

> **The same three in every lab today:** a repair log, a join log, a threshold table, a change log.

#### [day2#check-encoding] Which loader do you trust?

*Checkpoint*

**Question:** A file was appended from several systems. Four loaders are proposed. Which one do you run?

- A. Read it all as Windows-1256: it raises no error
- B. Read it as UTF-8 and replace undecodable bytes with a mark
- C. Let a detection library pick the encoding of the file
- D. Decode line by line, UTF-8 first, and count the lines of each encoding

#### [day2#lab-2-1] One file, three encodings

Lab 2.1 · 25 min

Decode the register extract line by line, repair the names that were decoded twice, normalise Arabic letters and digits into matching keys, and write the repair log that shows what the digits were hiding.

[D2_1_repair_mixed_encodings.ipynb](https://sdaiaacademy.github.io/ds-202/labs/D2_1_repair_mixed_encodings.ipynb)

- [ ] Decode the extract line by line and count (6 min)
- [ ] Repair the names that were decoded twice (6 min)
- [ ] Normalise letters and digits into keys (8 min)
- [ ] The repair log, and what the digits were hiding (5 min)
- [ ] ✱ Stretch: Names in Latin letters: case and hyphens

### Session 2: Keys and cardinality

#### [day2#s2] Keys and cardinality

*Session 2*

- Repair mistyped keys by stated rules
- Test many-to-one before joining
- Reconcile rows in with rows out plus rows set aside

#### [day2#three-silent-failures] A join can lose rows, add rows, and report neither

*Many handouts, one household*

- **Lost.** A key typed by hand does not match. In an inner join the handout disappears.
- **Added.** A household that is in the register twice gets every handout twice.
- **Unnoticed.** The result is a table of plausible size. Nothing compares it with what went in.

The remedy has three parts, in this order: repair keys by rule, test the cardinality, count rows at every step.

#### [day2#key-repair] A repair is safe when it cannot change which household is meant

*Lab 2.2, step 1*

| As typed | Rule | Safe because |
| --- | --- | --- |
| `h482913` | upper-case | case carries no information in this id |
| ` H482913 ` | strip spaces | nor do spaces |
| `H-482913` | remove the hyphen | nor a separator |
| `H48O913` | letter O to digit 0 | after the H only digits are possible |

> **Never a repair:** replacing an id by "the most similar one in the register". That picks a household, and it can pick the wrong one.

#### [day2#cardinality-test] Without the test, 209,620 rows went in and 210,585 came out

*Lab 2.2, step 2*

```python
# file: Lab 2.2
logs.merge(reg, on="household_id",
           how="left",
           validate="many_to_one")
# MergeError: Merge keys are not unique
# in right dataset
```

- A left join never loses a left row; it **adds** one for every extra match on the right
- 180 household ids are in the register twice: +965 rows, every one a handout counted double
- `validate` turns the assumption "one row per household" into a test that stops the join

#### [day2#set-aside] Rows without a household are set aside with a reason, not deleted

*What cannot be joined*

| Reason | Rows |
| --- | --- |
| key not in the register | 421 |
| blank key | 311 |
| set aside | 732 |

- They are handouts that happened: deleting them is an undercount with no trace
- The file goes to the owner of the logs; a corrected key enters the next build
- Unknown keys are spread over every branch: well-formed typing errors

#### [day2#join-log] The join log: every row that came in is on one of its lines

*The evidence of LO3*

| Step | Rows | Note |
| --- | --- | --- |
| log rows read | 210,000 | 14 branch files |
| exact copies dropped | 209,620 | 380 rows: a week of B02 uploaded twice |
| keys repaired | 209,620 | 2,446 keys by four rules |
| set aside | 732 | 421 unknown, 311 blank |
| joined to a household | 208,888 | many to one, tested |

210,000 = 380 copies + 732 set aside + 208,888 joined.

#### [day2#check-join] More rows out than in

*Checkpoint*

**Question:** A left join of 209,620 log rows to the register returns 210,585 rows and no error. What is the first thing you check?

- A. Whether household_id is unique in the register
- B. How many log keys have no match in the register
- C. Whether a branch file was loaded twice
- D. Nothing: drop duplicate rows from the result

#### [day2#lab-2-2] A join that loses nothing

Lab 2.2 · 25 min

Repair the household ids of the logs, test the join against the register for one-to-many breaks, join, and write a join log in which rows in equal rows out plus rows set aside, each with a reason.

[D2_2_join_logs_registrations.ipynb](https://sdaiaacademy.github.io/ds-202/labs/D2_2_join_logs_registrations.ipynb)

- [ ] Repair the keys and name what cannot be repaired (8 min)
- [ ] Test the cardinality before joining (5 min)
- [ ] Join and reconcile (7 min)
- [ ] The join log and the set-aside file (5 min)
- [ ] ✱ Stretch: Handouts dated before the registration

### Session 3: Matching without a clean key

#### [day2#s3] Matching without a clean key

*Session 3*

- Block and score candidate pairs
- Measure false matches and missed matches on labelled pairs
- Choose a threshold and state its cost
- Build a master record field by field from records that disagree

#### [day2#no-key] 300 handouts were written on paper, with a name and no id

*The problem*

- A satellite point of B04 and B05 in Ramadan: a name, a district, a phone for seven in ten
- 4,937 active households of the two branches to search
- Staff labelled 848 candidate pairs by hand: 255 true, 593 not

- **Two errors, two prices.** **Missed match:** a handout stays uncounted, and you can see it.
  **False match:** one family is credited with another's parcels, and it looks like a success.

#### [day2#block-score-decide] Block, score, decide

*Three steps*

1. **1 · Block** compare only pairs that agree on a reliable field: the district
2. **2 · Score** how alike are the two name keys, from 0 to 100
3. **3 · Decide** accept, reject, or send to a person

Blocking: 311,703 candidate pairs instead of 1,481,100, and all 255 true pairs survive it.

#### [day2#threshold-trade] A higher threshold buys fewer false matches with more missed ones

*Measured on the 848 labelled pairs*

| Rule | Accepted | False | False-match rate | Missed of 255 |
| --- | --- | --- | --- | --- |
| name score ≥ 70 | 309 | 86 | 27.8% | 32 |
| name score ≥ 85 | 149 | 11 | 7.4% | 117 |
| name score ≥ 95 | 117 | 4 | 3.4% | 142 |

> **No threshold gives both.** Even at 95, four accepted pairs are the wrong family, and more than half of the true pairs are missed.

#### [day2#second-field] A second field breaks the trade

*Lab 2.3, step 4*

**172 · 0** pairs accepted and false matches, when names are alike and phones agree on nine of ten digits

- Two fields that agree by accident are rare; one field that agrees by accident is common
- 83 true pairs are not accepted: mostly walk-ins who gave no phone
- They go to a **review queue** for a person, not through a lower threshold

#### [day2#three-outcomes] Accept, reject, or ask a person

*The decision has three outcomes*

- **Accept automatically.** The rule that showed no false match on labelled pairs. 172 of 300 walk-ins.
- **Review.** Likely names without a phone, or several candidates. A person decides, and the decision is recorded.
- **Leave unmatched.** 45 walk-ins are new households. An unmatched record is an honest result.

> **Report it like a join:** 300 records in, so many matched by rule, so many by review, so many unmatched.

#### [day2#master-record-rules] A match joins records that disagree: decide field by field which value survives

*After the match*

| Field | Trusted first | Then |
| --- | --- | --- |
| phone | the most recent the household gave | the older one |
| district | seen at a home visit | the latest form |
| size | verified at a visit | the register |
| income | the register | nothing else asks |

- **Precedence:** per field, the most trusted source that has a value; a blank never wins
- **Tie:** two sources of equal trust that disagree go to the most recent, or to review
- **Lineage:** every surviving value keeps its source and date

> **What goes wrong.** Keeping one whole row, the first or the newest: an old phone survives a new one.

#### [day2#master-record-example] Each field of the master record comes from a different source

*One household, three records*

| Field | Register, 2023 | Walk-in form, March 2026 | Home visit, Sept. 2026 |
| --- | --- | --- | --- |
| phone | ending 870 | **ending 225** | blank |
| district | D11 | D12 | **D12** |
| size | 5 | 7 | **6** |
| income | **4,800** | blank | blank |

The register alone says 5 members in D11 on an old phone. The master record says 6 members in D12 on the phone ending 225, and names the source of each value.

#### [day2#check-threshold] Which rule goes into the build?

*Checkpoint*

**Question:** A false match credits one family with another's parcels. On labelled pairs: name ≥ 70 accepts 309 with 86 false; name ≥ 95 accepts 117 with 4 false; name and phone accepts 172 with 0 false. Which do you automate?

- A. Name ≥ 70: it finds the most matches
- B. Name ≥ 95: 3.4% false is good enough
- C. Name and phone, with the rest sent to review
- D. None: match all 300 by hand

#### [day2#lab-2-3] 300 records without a key

Lab 2.3 · 25 min

Match 300 walk-in records to the register of two branches by normalised name, measure false and missed matches on staff-labelled pairs at three thresholds, add the phone as a second field, and choose the rule to run.

[D2_3_match_300_records.ipynb](https://sdaiaacademy.github.io/ds-202/labs/D2_3_match_300_records.ipynb)

- [ ] Normalise and block (5 min)
- [ ] Score the candidate pairs (6 min)
- [ ] False matches at three thresholds (7 min)
- [ ] Add the phone, measure again, choose (7 min)
- [ ] ✱ Stretch: The review queue

### Session 4: Types, units and dates

#### [day2#s4] Types, units and dates

*Session 4*

- Decide a date layout per source from evidence
- Bring weights in two units to one, and catch mislabelled ones
- Write a change log with a count per rule

#### [day2#value-has-no-evidence] 03/07/2026 is 3 July at one branch and 7 March at another

*The same string, two days*

- 8 branches write `2026-07-03`
- 4 branches write day first: `03/07/2026`
- 2 branches, on donated software, write month first: `07/03/2026`
- No file says which

**36,002 of 91,403** slash dates in which both parts are 12 or less: the value alone cannot be read

#### [day2#layout-per-source] A layout belongs to the source: one unambiguous date settles the whole file

*Where the evidence is*

1. **1 · Group by branch** a branch uses one layout
2. **2 · Look for a part above 12** if the first part ever exceeds 12 it is the day
3. **3 · Parse strictly** with that one format; a value that does not fit is an error

> **And then test the result.** Every branch has handouts in every month. A branch read with the wrong layout would have none after day 12.

#### [day2#guessing-cost] Guessing day first for a month-first branch loses 61% and corrupts 36%

*The stretch of Lab 2.4*

| Item | Value |
| --- | --- |
| lost: no such date | 11,625 |
| wrong, silently | 6,960 |
| right by luck | 620 |

The 19,205 handouts of B05, parsed day first with unreadable values turned into "no date". The 6,960 are the dangerous ones: a real-looking date, in the wrong month.

#### [day2#units-evidence] The weight per parcel shows which unit a number is in

*Lab 2.4, step 3*

| Branch, unit as labelled | Median per parcel | Reading |
| --- | --- | --- |
| B01, kg | 12.0 | kilograms: the packing standard |
| B05, lb | 26.4 | pounds, labelled as pounds |
| B13, kg (1,312 rows) | 26.4 | pounds labelled as kilograms |
| B09, kg (150 rows) | above 9,000 | grams typed into a kilogram field |

Between 15 and 19.8 per parcel there is no value at all: the two clouds do not touch, so a rule can separate them.

#### [day2#blanks-stay] 734 blank weights stay blank

*What cleaning must not do*

- All at B09, 4 to 17 May: the scale was away for repair
- A blank is not zero and is not 12 kg per parcel
- Filling it is a decision about missing data, with consequences for every average of weight
- The change log says "left missing", with the count

- **Tomorrow.** Day 3 asks why a value is missing before deciding what to do about it. This one has a known cause and a recorded date range.

#### [day2#change-log] The change log names every rule, its rows and its branches

*Lab 2.4, step 4*

| Change | Rows | Branches |
| --- | --- | --- |
| dates read as ISO | 118,217 | 8 branches |
| dates read day first | 52,731 | B03, B08, B10, B11 |
| dates read month first | 38,672 | B05, B13 |
| pounds to kilograms | 37,360 | B05, B13 |
| pounds labelled kg | 1,312 | B13 |
| grams to kilograms | 150 | B09 |
| weight missing, left missing | 734 | B09 |

#### [day2#check-date] A date that could be two days

*Checkpoint*

**Question:** A branch file holds `05/06/2026` and, further down, `09/27/2026`. How do you read the first date?

- A. 5 June: day first is the convention here
- B. 6 May: the file holds a second part above 12, so the month comes first
- C. It cannot be known: set it aside as ambiguous
- D. Either: let the date parser infer it

#### [day2#lab-2-4] One calendar, one unit

Lab 2.4 · 25 min

Find the date layout of each branch from its own rows, parse every date with it, bring pounds, grams and mislabelled weights to kilograms, and write the change log.

[D2_4_standardise_three_date.ipynb](https://sdaiaacademy.github.io/ds-202/labs/D2_4_standardise_three_date.ipynb)

- [ ] Find the date layout of each branch (7 min)
- [ ] Parse every date with the layout of its branch (5 min)
- [ ] Bring every weight to kilograms (8 min)
- [ ] The change log (5 min)
- [ ] ✱ Stretch: What guessing value by value would have done

#### [day2#wrap-up] Three things to keep

*Day 2 · wrap-up*

- **No error is not correct.** The wrong encoding, the wrong date order and a doubled household all run without a message.
- **Rows in = rows out + rows set aside.** 210,000 = 380 + 732 + 208,888. Each line has a reason.
- **Evidence lives in the source.** The layout, the unit and the encoding are decided per file or per line, and measured before they are trusted.

#### [day2#next] Missing data and measurement: how far can the headline move?

*Next · Day 3*

- Household size is blank for 18% of the population of the question
- Three reasons for a blank, and what each does to the estimate
- Three estimates of one number, then a range you can defend
- Sizes that are recorded, and wrong

## Day 3: Missing data and measurement

Why values are missing, what each remedy assumes, and how far the headline can move

#### [day3#title] Missing data and measurement

*SDAIA Academy · Data Acquisition, Preparation and Quality*

Day 3: Why values are missing, what each remedy assumes, and how far the headline can move

Data Science Track · 4 teaching days + capstone day · 4 sessions · 4 labs · DS-202

#### [day3#review-day-2] Rows that could not be joined

*Review of Day 2*

**Question:** After key repair, 732 log rows have no household: 421 carry an id that is not in the register and 311 are blank. What happens to them?

- A. They drop out in the join; no action is needed
- B. Each gets the most similar id in the register
- C. They go to a set-aside file with a reason, and the join log counts them
- D. They stay in the joined table with blank household fields

#### [day3#agenda] Missing data and measurement

*Today*

- **Session 1 · Why data go missing**: Three mechanisms of missingness, the evidence for each, and the bias each causes
- **Session 2 · Imputation and its cost**: Complete cases, one value, or similar households: three assumptions, three answers
- **Session 3 · Sensitivity ranges**: Logical bounds first, then a range under assumptions you can defend
- **Session 4 · Measurement error and proxies**: Random error, one-directional error, and what a proxy really measures

### Session 1: Why data go missing

#### [day3#s1] Why data go missing

*Session 1*

- Tabulate missingness against observed fields
- Tell the three mechanisms apart with evidence
- Give the direction of bias each one causes

#### [day3#why-before-what] Ask why a value is missing before deciding what to do about it

*The first question*

- Household size is blank for **18.1%** of the 35,665 households of the question
- Without a size, a household cannot be classified as eligible or not
- Dropping them, filling them, or reporting a range: each is right under one reason for the blank and wrong under another

- **Where reasons come from.** From the people who produced the data, the source note, and data from outside. Rarely from the column itself.

#### [day3#three-mechanisms] A blank can depend on nothing, on what you see, or on the value itself

*Three mechanisms*

| Mechanism | The blank depends on | Dropping the rows |
| --- | --- | --- |
| **MCAR** · completely at random | nothing | loses precision, adds no bias |
| **MAR** · at random given what is recorded | fields you can see: a branch, a date | biased, unless you work within those fields |
| **MNAR** · not at random | the missing value itself | biased, and the recorded data cannot show by how much |

The names are Rubin's (1976). They describe the relation between a blank and the data, not a property of a column: one column can hold all three.

#### [day3#two-patterns] One column, two patterns: a paper form and a list that stops at 6

*Measured in Lab 3.1*

| Group | Size missing |
| --- | --- |
| registered at a branch | 8.2% |
| registered by phone | 35.7% |
| registered online | 34.4% |
| B03, at the desk, before March 2025 | 43.4% |
| B03, at the desk, from March 2025 | 4.1% |

- The source note of Day 1 holds both reasons: the old paper form of B03 and B11 had no size field; the online form and the call script offer sizes 1 to 6
- A missing rate that differs between groups rules out MCAR. It does not tell MAR from MNAR

#### [day3#audit-evidence] The audit shows what the register cannot: blank sizes are large sizes

*Data from outside*

**7.2 · 5.3** verified members on average: households with a blank size, and households with a recorded one

- 600 home visits in September 2026; the size was verified
- Of the households with a blank size, 68% have 7 members or more; of the others, 25%
- The value itself decided whether it was recorded: **MNAR**
- No table of the register alone could have shown this

#### [day3#rows-not-cells] B12 sent no rows for nine days of August

*Missing data is not only blank cells*

- 10 to 18 August 2026: not one log row from B12, and rows on every other day of nine months
- No blank cell marks it. You find it only by counting rows per branch per day
- The households of its districts show fewer parcels than they received
- There is no field to impute: the remedy is to ask Hazem for the file, or to report the gap

- **A blank with a known cause.** 734 weights at B09 are blank from 4 to 17 May: the scale was away. Cause and dates are recorded, so it is MAR. Parcels were counted as usual.

#### [day3#six-scenarios] Six gaps: the mechanism, and where it pushes a number

*Lab 3.1, step 4 · the evidence of LO1*

| Gap | Mechanism | A statistic from the recorded data |
| --- | --- | --- |
| phone blank, about 3% everywhere | MCAR | mean size: unbiased |
| size blank on the old form of B03, B11 | MAR | eligible households there: too low |
| size blank for large households | MNAR | mean size: too low |
| weight blank at B09 in May | MAR | kilograms of B09 in May: too low |
| nine days of B12 without rows | MAR | parcels in its districts: too low |
| donor type null for anonymous individuals | MNAR | share of retailers: too high |

#### [day3#check-mechanism] Name the mechanism

*Checkpoint*

**Question:** An online form offers household sizes 1 to 6; larger households leave the field blank. You compute the mean household size from the recorded values. Which line is right?

- A. MAR, since it depends on the channel; the mean is unbiased
- B. MNAR, since the value decides; the mean is too low
- C. MCAR, since a form is not a person; the mean is unbiased
- D. MNAR, since the value decides; the mean is too high

#### [day3#lab-3-1] Six gaps, six mechanisms

Lab 3.1 · 25 min

Tabulate where household sizes are missing, read the audit of home visits, inspect three more gaps in the logs and the API, then classify the six patterns by mechanism and give the direction of bias for each.

[D3_1_classify_six_missingness.ipynb](https://sdaiaacademy.github.io/ds-202/labs/D3_1_classify_six_missingness.ipynb)

- [ ] Where household sizes are missing (7 min)
- [ ] What the audit shows (5 min)
- [ ] Three gaps in the logs and the API (6 min)
- [ ] Classify the six and give the direction of bias (7 min)
- [ ] ✱ Stretch: Why no test on the observed data can rule out the third mechanism

### Session 2: Imputation and its cost

#### [day3#s2] Imputation and its cost

*Session 2*

- Compute a complete-case estimate and say what it assumes
- Impute a single value and a value within groups
- Compare the estimates overall and by district
- Weight a survey for nonresponse after a follow-up of nonrespondents

#### [day3#no-neutral-option] Every way of handling a blank is an assumption about the households behind it

*There is no neutral option*

- **Complete cases.** Drop the rows. Assumes the dropped households are like the kept ones.
- **One value for all.** Fill with the median. Assumes every blank household is typical.
- **A value from similar households.** Fill from a group. Assumes that within the group, blank and recorded households are alike.

#### [day3#complete-case] Complete cases: 1.985, from the households that were easy to record

*Lab 3.2, step 1*

- 29,204 households take part; 6,461 do not
- The 6,461 are larger, more often eligible, and receive 2 or 3 parcels per visit
- Remove them, and the average of the eligible households that remain is too low
- 1.985 is below the standard of 2: the network "fails"

> **What goes wrong.** The code runs, no value was changed, and the result is reported as "the data". The assumption was never written down.

#### [day3#median-cost] The median gives every blank household five members

*Lab 3.2, step 2*

- Estimate: **2.003**. Everybody is classified; nobody is dropped
- But most blank households have 7 members or more: 6,000 SAR over 7 is 857, eligible; over the imputed 5 it is 1,200, "not eligible"
- Their parcels leave the numerator with them

- **And the spread shrinks.** 6,461 households at exactly one size: the distribution of sizes gets a spike that was never there.

#### [day3#within-groups] Use a recorded field that carries information about the missing one

*Lab 3.2, step 3*

| Usual parcels per handout | Households | Median recorded size |
| --- | --- | --- |
| never collected | 6,162 | 4 |
| 1 | 7,571 | 3 |
| 2 | 12,574 | 6 |
| 3 | 2,897 | 10 |

- The desk hands out 1, 2 or 3 parcels by the family card: the log knows something the register lost
- Each blank gets the median of its group: 3,218 households get 6, and 1,694 get 10
- Estimate: **2.060**

#### [day3#three-estimates] Three methods, three answers, and a different list of districts each time

*The comparison table of LO5*

| Method | Estimate | Districts below the standard of 2 |
| --- | --- | --- |
| complete case | 1.985 | 13 |
| median imputed | 2.003 | 11 |
| imputed within groups | 2.060 | 7 |

> **Six districts change side.** D04, D08, D09, D12, D17 and D24 are below the standard by one method and above it by another. A director who acts on the first table sends help to the wrong places.

#### [day3#synthetic-reveal] With no size missing, the estimate would have been 2.062

*What only synthetic data can show*

| Item | Value |
| --- | --- |
| complete case | −0.077 |
| median imputed | −0.059 |
| imputed within groups | −0.002 |

Distance from the value that complete data would have given. The generator knows the size every household would have reported; in real work this cell does not exist.

#### [day3#unit-nonresponse] A survey's nonrespondents are not filled in: you go back for a sample of them

*When whole answers are missing*

1. **Phase 1 · phone** 1,200 households sampled; 639 answer (53%)
2. **Phase 2 · follow-up** a random 1 in 4 of the 561 who did not: 140 visited at home, 123 answer
3. **Weight** each phase 2 answer stands for 561 ÷ 123 = 4.56 nonrespondents

> **Unit nonresponse** is a whole household with no answer, not a blank field. A small follow-up, chased hard, beats a large one chased lightly: it is the only evidence about the people who do not answer.

#### [day3#nonresponse-weights] Weights for distance help a little; only the follow-up sees that nonrespondents differ

*Three estimates of one share*

| Method | "Parcels lasted" | Assumes |
| --- | --- | --- |
| phone respondents only | 64.8% | nonrespondents answer like respondents |
| weighted by distance class | 63.4% | alike within near and far |
| two-phase, with the follow-up | 55.4% | the 123 speak for the 561 |

- Class weights: near households answered 63% of the time (weight 1.58), far ones 42% (weight 2.40)
- They fix the share of far households, not who answers within a class
- The follow-up shows nonrespondents in difficulty more often: MNAR, measured

#### [day3#check-imputation] Which estimate do you put first?

*Checkpoint*

**Question:** Sizes are blank mostly for large households, and branches hand out more parcels per visit to large households. Three estimates are on your desk. Which one do you present first, and why?

- A. Complete case: it changes no value
- B. Median: simple and easy to explain
- C. The mean of the three, to be fair to each
- D. Within groups: it uses a recorded field related to the size

#### [day3#lab-3-2] Three estimates of one number

Lab 3.2 · 25 min

Estimate parcels per eligible household with complete cases, with the median size and with the median of similar households, and compare the three overall and by district.

[D3_2_estimate_parcels_per.ipynb](https://sdaiaacademy.github.io/ds-202/labs/D3_2_estimate_parcels_per.ipynb)

- [ ] The complete-case estimate (5 min)
- [ ] Impute the median (5 min)
- [ ] Impute within groups (8 min)
- [ ] The comparison table, overall and by district (7 min)
- [ ] ✱ Stretch: Draw a donor at random, twenty times

### Session 3: Sensitivity ranges

#### [day3#s3] Sensitivity ranges

*Session 3*

- Compute the logical bounds of an estimate
- Build a plausible range by shifting the imputed values
- Recommend one estimate with its range and its reason

#### [day3#answerable-question] "Which estimate is right?" cannot be answered. "How far can it move?" can

*Change the question*

1. **1 · Logical bounds** assume nothing about the blank households
2. **2 · A plausible range** assumptions you can defend, stated
3. **3 · A recommendation** one estimate, its range, its reason

> **A sensitivity analysis** varies what you assumed and reports what happens to the conclusion. It does not make the missing data less missing.

#### [day3#logical-bounds] Whatever the 6,461 households are, the estimate lies between 1.775 and 2.133

*Lab 3.3, step 1*

- Each blank household is eligible or not; you do not know which
- **Lowest:** exactly those that collected few parcels are eligible
- **Highest:** exactly those that collected many are eligible
- No assumption about sizes can leave this interval

- **Honest, and too wide.** The bounds straddle the standard of 2. They take "every blank household that collected nothing is eligible" as seriously as anything else.

#### [day3#plausible-range] Shift the imputed sizes: the estimate stays between 2.02 and 2.07

*Lab 3.3, step 2*

| Scenario for the blank households | Estimate |
| --- | --- |
| imputed size − 1 | 2.073 |
| imputed within groups | 2.060 |
| imputed size + 1 | 2.039 |
| imputed size + 2 | 2.020 |
| phone and online blanks are at least 7 | 2.040 |

Recorded sizes never change. Only the guess is varied, by amounts the audit makes believable: blank households were about two members larger.

#### [day3#district-verdicts] Seven districts are below the standard under every scenario; three depend on it

*Lab 3.3, step 3*

- **Below · 7.** D07, D15, D22, D26 at 1.3 to 1.5. D11 and D19 near 1.75. D23 at 1.96 to 1.99.
- **Depends · 3.** D09, D17, D24: between 1.98 and 2.02. Reported as "cannot be classified with these data".
- **At or above · 20.** Above the standard whichever scenario is taken.

> **Three verdicts, not two.** "Depends on the assumption" is a finding. It tells the director where one more audit would change a decision.

#### [day3#what-range-misses] D23 is "below" under every assumption about sizes, and is not below

*The limit of a sensitivity range*

- D23 and D24 are served by branch B12
- B12 sent no rows for 10 to 18 August: handouts happened and are in no file
- The range varied household sizes. It never varied the missing rows
- The generator's own count puts D23 at 2.25 parcels per eligible household

> **What goes wrong.** A range covers the assumption you varied and nothing else. "Robust to missing sizes" is not "robust".

#### [day3#recommendation] A recommendation has four parts

*Lab 3.3, step 4*

- **The paragraph.** About 2.06 parcels per eligible household per month (2.02 to 2.07 under different assumptions about the 18% of households with no recorded size). Seven districts are below the standard under every assumption; for three the answer depends on it. We recommend filling blank sizes from similar households, because blank sizes are mostly large households.

- **An estimate**, not a list of three
- **Its range**, and what was varied
- **What holds across the range**, and what does not
- **The reason** for the method, in terms the director can check

#### [day3#check-range] What do you report for the district?

*Checkpoint*

**Question:** District D17 comes out at 1.98 under one scenario for the blank sizes and at 2.01 under another. The standard is 2. What does the report say about D17?

- A. It cannot be classified with these data; both values are shown
- B. Below the standard: 1.98 is the safe figure
- C. At the standard: the midpoint is 2.0
- D. It is left out until sizes are complete

#### [day3#lab-3-3] How far could it move?

Lab 3.3 · 25 min

Bound the estimate under best-case and worst-case assumptions about the households with no size, narrow it to a plausible range by shifting the imputed sizes, see which districts change side of the standard, and recommend an estimate.

[D3_3_bound_estimate_under.ipynb](https://sdaiaacademy.github.io/ds-202/labs/D3_3_bound_estimate_under.ipynb)

- [ ] The logical bounds (7 min)
- [ ] A plausible range: shift the imputed sizes (8 min)
- [ ] Which districts change side of the standard (5 min)
- [ ] Recommend an estimate, with its reason (5 min)
- [ ] ✱ Stretch: The tipping point of one district

### Session 4: Measurement error and proxies

#### [day3#s4] Measurement error and proxies

*Session 4*

- Measure reporting error against an audit
- Simulate random and one-directional error
- Say what a proxy measures and what it does not
- Link a series across a changed question, or report the break

#### [day3#recorded-and-wrong] A value can be present, valid, and wrong

*The other half of data quality*

- Household size is **reported by the household** at registration and is not verified
- It passes every rule, an integer between 1 and 20, and no rule can see that 7 should have been 5
- Only a second measurement can: here, 289 audited households with a recorded size

- **Two kinds of error.** **Random:** up as often as down, for anybody.
  **Systematic:** in one direction, or for one kind of household.

#### [day3#audit-error] 92% of recorded sizes are exact, and the mean error is almost zero

*Measured in Lab 3.4*

| Recorded − verified | Households |
| --- | --- |
| −1 | 18 |
| 0 | 266 |
| +1 | 2 |
| +2 | 3 |

- Mean error −0.035 members: a reviewer would call the column reliable
- 18 households under-report by one: a birth or a returning member not yet registered
- 5 over-report. Look at **who** they are before looking at how many

#### [day3#error-at-threshold] All five over-reporters are just above the eligibility line

*Where the error sits*

| Reported | Verified | Income, SAR | Per verified member |
| --- | --- | --- | --- |
| 7 | 5 | 5,250 | 1,050 |
| 9 | 8 | 8,150 | 1,019 |
| 4 | 3 | 3,100 | 1,033 |
| 4 | 2 | 2,450 | 1,225 |
| 9 | 7 | 8,400 | 1,200 |

With the verified size none is eligible; with the reported size all five are. A small error, placed exactly where the rule decides.

#### [day3#two-simulations] Random error in 8% of sizes moves the headline less than over-reporting in 2.6%

*Lab 3.4, steps 2 and 3*

| Item | Value |
| --- | --- |
| random ±1, 8.0% of households | −0.006 |
| over-report, 1.4% | −0.028 |
| over-report, 2.6% | −0.055 |
| over-report, 5.2% | −0.107 |

Shift of the headline from 2.060, averaged over 200 simulated registers. Over-reporters enter the denominator as eligible and collect almost nothing: the desk hands out by the family card.

#### [day3#measurement-reveal] The recorded sizes already contain the error: the headline is about 0.07 too low

*What only synthetic data can show*

**2.062 → 2.131** the estimate with every size as reported, and with every size as it truly is

- The direction was predictable from the audit; the size needed the simulation
- Missing sizes cost up to 0.077; mis-reported sizes cost 0.069
- Only the first had a column of blanks to warn you

#### [day3#proxies] A proxy measures what it measures, not what you wish it measured

*Proxies*

- Parcels per handout are set by the desk from the family card: a proxy for the verified size band
- It disagrees with the recorded size for 1.5% of households that collected: a list for review
- It is silent about households that never collected: 323 eligible by the register, none in nine months

> **What goes wrong.** Defining "eligible" as "collected regularly". Every eligible household that was not served leaves the denominator, and every district looks well served.

#### [day3#instrument-change] Ask the old and the new question side by side for a while, and link the series with the ratio

*When the question itself changes*

| Month | Old: last month | New: last 7 days | Ratio |
| --- | --- | --- | --- |
| 2026-01 | 31.5% | 24.8% | 0.787 |
| 2026-02 | 32.1% | 24.8% | 0.773 |
| 2026-03 | 32.7% | 25.1% | 0.768 |

- Share of households at the desk who say someone skipped a meal for lack of food; the wording changed in January 2026
- Three months of overlap, half the households asked each version
- Linking factor 0.776: October 2025 at 32.9% on the old question reads 25.5% on the new basis

#### [day3#comparability-break] If the ratio is not stable across months or groups, the series breaks: report two

*When not to link*

| A partner network's overlap | Old | New | Ratio |
| --- | --- | --- | --- |
| at the desk, on a card | 33.4% | 30.1% | 0.90 |
| by phone, read aloud | 29.6% | 16.8% | 0.57 |

- One factor would move desk and phone households by different amounts
- Break the series when the ratio drifts, differs by group, the reference period or definition changes, or there is no overlap
- Then: two series with a marked break, and no trend drawn across it

#### [day3#check-direction] Which way does the headline move?

*Checkpoint*

**Question:** A few households just above the income line report one or two members more than they have, and so count as eligible. Branch desks hand out parcels by the family card. What happens to "parcels per eligible household"?

- A. Nothing measurable: the errors are too few
- B. It rises: larger households receive more parcels
- C. It falls: they enter the denominator and collect almost nothing
- D. It cannot be said without verifying every household

#### [day3#lab-3-4] When the answer itself is wrong

Lab 3.4 · 25 min

Measure the reporting error of household size in the audit, simulate random error and over-reporting near the eligibility line, and measure the shift of the headline under each.

[D3_4_simulate_self_report.ipynb](https://sdaiaacademy.github.io/ds-202/labs/D3_4_simulate_self_report.ipynb)

- [ ] Measure the reporting error in the audit (6 min)
- [ ] Simulate random error (7 min)
- [ ] Simulate over-reporting near the line (7 min)
- [ ] The shift table and a proxy (5 min)
- [ ] ✱ Stretch: How large an audit to see a 2% error rate?

#### [day3#wrap-up] Three things to keep

*Day 3 · wrap-up*

- **Why, before what.** The reason for a blank comes from the source note and from outside data, and it decides which remedy is honest.
- **An estimate, a range, a reason.** 2.06, between 2.02 and 2.07; seven districts below under every assumption, three undecided.
- **A range covers what you varied.** Not the nine days of B12, and not sizes that were recorded wrong.

#### [day3#next] Validate and protect, then choose your capstone question

*Next · Day 4*

- Rules that run on every rebuild, and a batch that breaks them
- ID numbers replaced by a keyed hash, and an attempt to link them back
- The quality report, written from the outputs of one command
- Three capstone questions on a second extract with other faults

## Day 4: Validate and protect

Rules that run on every rebuild, identifiers that hold, and a report that says what the dataset is good for

#### [day4#title] Validate and protect

*SDAIA Academy · Data Acquisition, Preparation and Quality*

Day 4: Rules that run on every rebuild, identifiers that hold, and a report that says what the dataset is good for

Data Science Track · 4 teaching days + capstone day · 4 sessions · 4 labs · DS-202

#### [day4#review-day-3] One number, or a number with a range

*Review of Day 3*

**Question:** Complete cases give 1.985 parcels per eligible household per month; imputing within groups gives 2.060; the scenarios about the missing sizes run from 2.02 to 2.07. The standard is 2. What goes to Sumayyah?

- A. 1.985: it uses only values that were recorded
- B. 2.060: it is the best estimate, so it is the answer
- C. 2.06, between 2.02 and 2.07, with the reason and the districts that stay below
- D. 2.02: the mean of the two methods, to be fair to both

#### [day4#agenda] Validate and protect

*Today*

- **Session 1 · Quality dimensions as rules**: Completeness, validity, uniqueness and type, written from the data dictionary
- **Session 2 · Cross-field and cross-source checks**: Faults that show only between two fields or two sources, reported so a branch can act
- **Session 3 · Minimise and pseudonymise**: A plain hash falls to a list; a keyed hash holds; quasi-identifiers still single people out
- **Session 4 · A data-quality report**: Row counts, rule results, what is missing, how far the estimate moves, what may leave

### Session 1: Quality dimensions as rules

#### [day4#s1] Quality dimensions as rules

*Session 1*

- Translate a data dictionary into column rules
- Name the quality dimension of each rule
- Run the suite on a build and read its failures

#### [day4#repair-and-rule] A repair fixes this file. A rule protects every file after it

*Two different things*

- Day 2 repaired what was found: encodings, keys, date layouts, units
- The next extract arrives in three months, from the same 14 branches, with faults nobody has seen yet
- A **rule** states what must hold. A program checks it on every rebuild and says which rows break it

- **The evidence of LO4.** A rule suite that passes on the clean build and fails, readably, on a corrupted batch.

#### [day4#dimensions] Each dimension becomes a kind of rule

*Quality dimensions*

| Dimension | The question | A rule for the joined table |
| --- | --- | --- |
| **Type** | Is it the kind of value the column holds? | `handout_date` is written YYYY-MM-DD |
| **Completeness** | Is a required value there? | `household_key` is never blank |
| **Validity** | Is it a value the dictionary allows? | `parcels` between 1 and 3 |
| **Uniqueness** | Does a key identify one row? | `log_id` never repeats |
| **Consistency** | Do fields and sources agree? | weight is 9 to 15 kg per parcel |

Frameworks name and count the dimensions differently. The names matter less than this: every rule in your suite says which one it tests.

#### [day4#dictionary-to-rules] The data dictionary, written so that a program can check it

*Lab 4.1, steps 1 to 3*

```python
# file: Lab 4.1 · Pandera
schema = pa.DataFrameSchema({
  "log_id": pa.Column(str, unique=True),
  "parcels": pa.Column(
      int, pa.Check.in_range(1, 3)),
  "weight_kg": pa.Column(
      float, pa.Check.in_range(5, 50),
      nullable=True),
  "handout_date": pa.Column(
      str, pa.Check.str_matches(ISO)),
}, strict=True)
schema.validate(df, lazy=True)
```

- "Required: yes" in the dictionary is `nullable=False`, the default: the completeness rule
- `strict=True`: a missing or an extra column fails
- `lazy=True`: every rule runs, and all failures come back together
- Dates stay text with a pattern: a date in another layout fails; it is not guessed

#### [day4#readable-failure] A failure that reads like a sentence

*Lab 4.1, step 4*

| Rule | Column | Rows | Examples |
| --- | --- | --- | --- |
| uniqueness: no value repeats | log_id | 2 | B01-0007639 |
| completeness: no value is missing | household_key | 3 |  |
| validity: parcels between 1 and 3 | parcels | 4 | 9 |
| validity: district_id is one of the 30 districts | district_id | 2 | D99 |
| type: handout_date is a date written YYYY-MM-DD | handout_date | 5 | 03/07/2026 |

The first 2,000 rows of the clean build, broken on purpose in five places. The same table, without the suite, raises no error anywhere.

#### [day4#never-failed] A suite that has never failed has never been tested

*Testing the test*

- The suite passes on all 73,264 rows of the clean build. That proves little
- A typing mistake in a pattern, or a range that is too wide, passes every build for ever
- Break a copy on purpose, one fault per rule, and watch each rule fail
- Decide in advance, per rule: does a failure **stop** the build, or **warn**?

> **What goes wrong.** A suite is written after the cleaning, from the cleaned data, so that it passes. It then describes this file and protects nothing.

#### [day4#valid-not-true] Valid is not the same as true

*The limit of a rule*

**0** rows of the clean build fail "household_size between 1 and 20"

- Lab 3.4: the audit found recorded sizes that differ from the verified size, more often above than below
- Every one of those sizes is a whole number between 1 and 20
- A rule tests what a value **may be**. Whether it **is** so needs a second measurement

#### [day4#check-dimension] Which rule, and which dimension?

*Checkpoint*

**Question:** In the joined table, one row is one handout, and a household has many handouts. A week of one branch is uploaded twice. Which rule catches it?

- A. Uniqueness of `household_key`
- B. Uniqueness of `log_id`
- C. Completeness of `log_id`
- D. Validity of `handout_date`

#### [day4#lab-4-1] Rules for the joined table

Lab 4.1 · 25 min

Write type, range, uniqueness and completeness rules for the joined table from its data dictionary, run them on the clean build, and watch each fail on a copy you break.

[D4_1_write_type_range.ipynb](https://sdaiaacademy.github.io/ds-202/labs/D4_1_write_type_range.ipynb)

- [ ] Types and completeness from the dictionary (7 min)
- [ ] Range and validity rules (6 min)
- [ ] Uniqueness (4 min)
- [ ] Run on the clean build and on a broken copy (8 min)
- [ ] ✱ Stretch: Which rules stop the build and which only warn?

### Session 2: Cross-field and cross-source checks

#### [day4#s2] Cross-field and cross-source checks

*Session 2*

- Write rules across two fields
- Write a rule across two sources
- Produce a failure report a data owner can act on

#### [day4#october-batch] A new batch arrives, and seven column rules fail

*Lab 4.2, step 1*

| Rule that fails | Rows |
| --- | --- |
| validity: weight_kg between 5 and 50 | 278 |
| completeness: household_key | 60 |
| uniqueness: log_id | 50 |
| validity: parcels between 1 and 3 | 40 |
| validity: district_id | 20 |
| type: handout_date | 15 |
| validity: household_size | 12 |

- The first week of October: 4,180 rows, built as the quarter was
- Each line names what somebody can fix
- Look again at the first line: 278 handouts above 50 kg. Is that all that is wrong with those rows?

#### [day4#pounds-inside-range] B05 sent pounds. Most of its rows pass the range rule

*What a column rule cannot see*

**278 · 377** rows of B05 caught by "5 to 50 kg", and rows of B05 that are wrong

- A parcel weighs about 12 kg: about 26 in pounds
- One parcel in pounds: 26, **inside** 5 to 50. Passes
- Two or three parcels in pounds: 53 or 79. Fails
- The value is fine on its own. It is wrong **for its number of parcels**

#### [day4#cross-field] Two rules across fields

*Lab 4.2, step 2*

```python
# file: Lab 4.2
def not_per_parcel(df):
    ok = df.parcels.between(1, 3)
    per = df.weight_kg / df.parcels.where(ok)
    return df[per.notna()
              & ~per.between(9, 15)]

def before_registration(df):
    return df[date(df.handout_date)
              < date(df.registered_on)]
```

- 9 to 15 kg per parcel: all **377** rows of B05, and no row of any other branch
- Handout on or after registration: **30** rows in 12 branches. A household cannot collect before it exists: a wrong key or a wrong date
- Each rule skips rows that another rule already reports, so one fault gives one line

#### [day4#cross-source] A branch cannot hand out more food than it received

*Lab 4.2, step 3*

| Item | Value |
| --- | --- |
| B05 · received in the week | 9,574 kg |
| B05 · handed out, as recorded | 20,005 kg |

- The logs say what went out; the donations source says what came in. No single table holds both
- To compare them: the same unit, the same week, one row per branch. A small pipeline of its own
- It catches a whole class of faults that leave every row plausible

#### [day4#failure-report] A failure report says whose rows, and what to look at

*Lab 4.2, step 4*

| Rule | Rows | Whose | What to look at |
| --- | --- | --- | --- |
| consistency: 9 to 15 kg per parcel | 377 | B05: 377 | median 26.4 per parcel: pounds entered as kilograms? |
| consistency: handout on or after registration | 30 | 12 branches | the household id or the date of these handouts |
| consistency across sources: handed out no more than received | 1 | B05 | handed 20,005 kg, received 9,574 kg |

> **Ten lines in all.** Seven from the column rules, three from the rules you add. "Validation failed" helps nobody; a line that names the branch gets fixed.

#### [day4#reject-or-quarantine] Reject the file, or set the rows aside?

*Recap of FN-104, as a rule of the build*

- **Reject the file.** The fault is in how the file was made: a wrong unit, a wrong layout, a missing column. Every row of B05 is suspect. Send it back.
- **Quarantine the rows.** The fault is in single rows: a blank key, a date before registration. Load the rest; set these aside with a reason and count them in the log.

Either way the decision is made per rule, in advance, and the log shows it: rows in equal rows loaded plus rows set aside.

#### [day4#check-cross-field] Which rule finds it?

*Checkpoint*

**Question:** From 7 to 9 August a branch writes dates as month/day/year; the build reads that branch as day/month/year. Every date parses, and every one falls inside the quarter. Which rule is most likely to show the fault?

- A. Type: the date matches the pattern of the file
- B. Completeness: no date is missing
- C. Validity: the date is inside the quarter
- D. Consistency: rows per branch per day against that branch's usual pattern

#### [day4#lab-4-2] Three rules across fields and sources

Lab 4.2 · 25 min

Run the column rules on a corrupted October batch, add two cross-field rules and one cross-source rule that catch what they miss, and write a failure report that says which branch must fix what.

[D4_2_add_three_consistency.ipynb](https://sdaiaacademy.github.io/ds-202/labs/D4_2_add_three_consistency.ipynb)

- [ ] Run the column rules on the corrupted batch (5 min)
- [ ] Two rules across fields (8 min)
- [ ] One rule across sources (7 min)
- [ ] A failure report a branch can act on (5 min)
- [ ] ✱ Stretch: Reject the batch or quarantine the rows?

### Session 3: Minimise and pseudonymise

#### [day4#s3] Minimise and pseudonymise

*Session 3*

- Re-link a plain hash with a list and by enumeration
- Replace identifiers with a keyed hash
- Measure uniqueness on quasi-identifiers and reduce it by generalising

#### [day4#minimise-first] The safest field is the one that never entered the dataset

*Before any technique*

- Lab 1.1 listed the fields the question needs. A name, a phone number and an ID number are not among them
- They were needed for **one step**: matching the 300 walk-in records of Day 2
- After that step they are dropped, and the dataset keeps a key that says "the same household" and nothing else

- **Minimise, then pseudonymise.** First ask whether the field is needed at all. Only for what remains: how to replace the identifier so that tables still join.

#### [day4#pseudonymised-or-anonymised] Pseudonymised data is still personal data

*Recap of FN-106*

- **Pseudonymised.** Identifiers are replaced by codes. Linking back needs additional information, which is kept separately under its own controls. Somebody can still link back, so the data stays personal.
- **Anonymised.** Nobody can link the data to a person any more, with any reasonable means. A much higher bar, and rarely reached by a table with one row per household.

The national guideline names generalisation and aggregation among the techniques: age bands in place of ages, a year in place of a date. Lab 4.3 uses both.

#### [day4#plain-hash-falls] "A hash cannot be reversed." Nobody needs to reverse it

*Lab 4.3, steps 1 and 2*

**5,000 of 5,000** people on a known list re-identified in a table of plain SHA-256 hashes

- The same input gives the same hash, for everyone
- **List attack**: hash the ID numbers you hold; join
- **Enumeration**: an ID number has ten digits. Hash every possible one
- The 2,000,000 numbers of the course range take seconds on a laptop; all ten-digit numbers take hours

#### [day4#keyed-hash] A keyed hash: without the key, neither attack starts

*Lab 4.3, step 3*

```python
# file: Lab 4.3 · HMAC
import hmac, hashlib, os

key = os.environ["GHILAL_KEY"].encode()

def pseudonym(s: str) -> str:
    return hmac.new(key, s.encode(),
        hashlib.sha256).hexdigest()[:16]
```

- Stable and unique: the same household has the same pseudonym in every table, so joins still work
- The key is the "additional information": kept separately, never committed, never sent
- A list attack without the key: 0 of 5,000
- A new key gives new pseudonyms: two recipients cannot join their tables to each other

#### [day4#quasi-identifiers] The key holds, and ordinary fields still single households out

*Lab 4.3, step 4*

| Item | Value |
| --- | --- |
| district, exact date, exact size | 92.8% |
| district, year, size band | 0.0% |

Share of the 37,333 households whose combination of fields occurs exactly once.

- "They live in D09, registered on 14 March 2024, seven of them": a neighbour needs no key
- A combination of ordinary fields that singles a person out is a **quasi-identifier**
- Generalised, the smallest group has 4 households; the partner can still count shared households

#### [day4#what-travels] The classification of the source decides the conditions of sharing

*Who may receive what*

- **Stays inside.** Raw sources. Rows with identifiers as typed. The key.
- **Under an agreement.** Household-level tables, pseudonymised and generalised: to named people, for one purpose, for a stated time.
- **May be published.** Aggregates by district that single nobody out, the code, the rules, the report.

The provenance records of Day 1 classified the register and the logs as Restricted. A table derived from them does not become Public by losing a column.

#### [day4#check-pseudonym] What must change before the table is sent?

*Checkpoint*

**Question:** A table for a partner holds, per household: a keyed-hash pseudonym, the district, the exact registration date and the household size. The key is stored safely. What is the remaining risk, and the remedy?

- A. The pseudonym can be enumerated; use a longer hash
- B. Date, district and size single households out; send the year and a size band
- C. None: without names and ID numbers the table is anonymous
- D. The pseudonym links tables; remove it and keep the other fields

#### [day4#lab-4-3] A pseudonym that holds

Lab 4.3 · 25 min

Hash national ID numbers plainly and re-link them with a list and by enumeration, replace them with a keyed hash, then attempt re-linkage through district, size and registration date and reduce it by generalising.

[D4_3_replace_national_id.ipynb](https://sdaiaacademy.github.io/ds-202/labs/D4_3_replace_national_id.ipynb)

- [ ] A plain hash and a list attack (6 min)
- [ ] Enumerate the id space (5 min)
- [ ] A keyed hash (6 min)
- [ ] Re-link through quasi-identifiers, then generalise (8 min)
- [ ] ✱ Stretch: Change the key: what breaks, and what should

### Session 4: A data-quality report

#### [day4#s4] A data-quality report

*Session 4*

- Rebuild a dataset from raw sources with one command
- Draft a data-quality report from the build outputs
- Classify outputs and choose a capstone question

#### [day4#one-command] One command: raw files in, the dataset and its evidence out

*Rebuildable*

1. **1 · Read** the raw sources, exactly as they arrived
2. **2 · Clean and join** each step counts its rows; rows without a household are set aside
3. **3 · Check** every rule runs on the result
4. **4 · Write** tables with pseudonyms, the join log, the rule results, the report

- `uv run python build_dataset.py`: under a minute on a laptop for 40,000 registrations and 210,000 log rows
- Nothing is edited by hand between the raw files and the outputs, so anybody can run it again
- A rebuild is compared with the last one: the same rows, the same content

#### [day4#report-parts] The quality report: six parts, read before any number is used

*One page*

| Part | Says | Comes from |
| --- | --- | --- |
| 1 · Headline | the estimate, its range, the standard | Day 3 |
| 2 · Question and population | who is counted, for which period | Lab 1.1 |
| 3 · Sources | owner, refresh date, classification | the provenance records |
| 4 · Row counts per step | what went in, what was set aside and why | the join log |
| 5 · Rules | how many ran, which failed | the rule results |
| 6 · Limits | what the dataset cannot support | you |

#### [day4#no-typed-number] No number in the report is typed by hand

*Lab 4.4, step 2*

```python
# file: Lab 4.4
def headline(facts):
    lo, hi = facts["range"]
    return (f"an estimated "
            f"{facts['recommended']} parcels "
            f"per eligible household per month "
            f"(plausible range {lo} to {hi}; "
            f"standard {facts['standard']})")
```

- The next rebuild changes the numbers. A typed number stays, and the report then describes a dataset that no longer exists
- The lab checks it: every number in your headline must occur in the facts the build wrote
- An AI-assistant may improve the wording after your draft exists. The numbers still come from the build

#### [day4#limits] Limits: what this dataset cannot support

*Part 6*

- Household size is missing for **18.1%** of the 35,665 households, and more often for large ones
- For D09, D17 and D24 the verdict against the standard depends on the assumption: **undecided**
- B12 sent no rows for 10 to 18 August: its districts look less served than they were
- 811 log rows could not be tied to a household; they are set aside, not counted
- D29 and D30 have no row in the open table of 2022: coverage of need cannot be stated there
- Sizes are reported by households and not verified

#### [day4#what-may-leave] Before a file is committed or attached, a program looks at it

*Lab 4.4, step 3*

| Build output | Grain | Decision |
| --- | --- | --- |
| join_log.csv, rule_results.csv, the report | aggregate | may leave |
| households.csv, handouts_q3.csv | household, pseudonymised | only under an agreement, generalised |
| set_aside.csv | log row, keys as typed | stays inside |

- The set-aside rows keep each key exactly as the desk typed it, because somebody must repair it. That makes the file useful to the branch and unfit to travel
- A scan for identifier patterns in every output is one more rule of the build

#### [day4#capstone-questions] A second city, the same four kinds of source, other faults

*The capstone*

- **Question A.** Parcels per eligible household per month, by district, in the second quarter of 2026.
- **Question B.** Kilograms handed out per household member, by branch, against kilograms received.
- **Question C.** Share of eligible households that received no parcel in the quarter, by registration channel.

- You deliver a public repository that rebuilds with one command, and defend it in eight minutes
- During the defence the assessor corrupts one input file; you show which rule fails and why
- No raw personal field is committed, synthetic or not

#### [day4#check-report] Which sentence belongs in the report?

*Checkpoint*

**Question:** The build ran, every rule passed, and the estimate is 2.06 with a range of 2.02 to 2.07. Which sentence should open the limits section?

- A. All rules passed, so the data is correct
- B. The data has some quality issues that should be kept in mind
- C. Size is missing for 18.1% of households; three districts are undecided
- D. The network delivers 2.060 parcels, above the standard

#### [day4#lab-4-4] The quality report

Lab 4.4 · 25 min

Run the reference build with one command, draft the quality report from its outputs and from the findings of the four days, decide which outputs may leave the analysis environment, and choose your capstone question.

[D4_4_draft_quality_report.ipynb](https://sdaiaacademy.github.io/ds-202/labs/D4_4_draft_quality_report.ipynb)

- [ ] Rebuild from the raw sources with one command (5 min)
- [ ] Draft the report from the build outputs (10 min)
- [ ] What may leave the analysis environment (5 min)
- [ ] Choose your capstone question (5 min)
- [ ] ✱ Stretch: Corrupt one input file and rebuild

#### [day4#wrap-up] Three things to keep

*Day 4 · wrap-up*

- **Rules run every time.** Written from the dictionary, named by dimension, tested on a broken copy. Some faults show only between two fields or two sources.
- **A key, then generalise.** A plain hash falls to a list. A keyed hash holds; exact dates and sizes still single households out.
- **The report is built, the limits are written.** Numbers from the build. Limits from you: the fault, its size, what it does to the decision.

#### [day4#next] Your repository, rebuilt live

*Next · Capstone*

- Choose question A, B or C and build from the raw files of the second city
- One command; a provenance file; a rule suite; a README with row counts, rule results and the range of your estimate
- Eight minutes of defence, four of questions, and one input file corrupted by the assessor
- Keep every raw personal field out of the repository

## Capstone: Capstone project presentations

Each participant rebuilds a dataset from raw files, live, and defends it: eight minutes, then four minutes of questions

#### [capstone#title] Capstone project presentations

*SDAIA Academy · Data Acquisition, Preparation and Quality*

Capstone: Each participant rebuilds a dataset from raw files, live, and defends it: eight minutes, then four minutes of questions

Data Science Track · 4 teaching days + capstone day · 8 min talk and demo · 4 min Q&A · DS-202

#### [capstone#agenda] How the presentations run

*Capstone*

- **Expectations and final prep**: the rubric, a rebuild from a fresh clone, then the first defences
- **Defences**: eight minutes each with a live rebuild and one corrupted input, then four minutes of questions
- **Exit check, review and closing**: the supervised check, the trainer's review, the follow-up task

#### [capstone#rubric] The rubric

*How presentations are scored*

| Item | Value |
| --- | --- |
| Provenance | 15% |
| Joins and reconciliation | 25% |
| Cleaning and validation | 25% |
| Missing data and sensitivity | 20% |
| Personal data and reproducibility | 15% |

> **Every claim has a count.** Rows in, rows out, rows set aside; rules run, rules failed; an estimate with its range.

#### [capstone#format] Eight minutes of defence, then four minutes of questions

*Format*

- **1 · The question.** Which question, which population, which sources. One minute, no slides needed.
- **2 · The rebuild.** One command on the raw files. Then the assessor corrupts one input file: rebuild, and show which rule fails and why.
- **3 · The answer and its limits.** The estimate with its range, and the one limit that matters most to the person who asked.

> **Peer feedback.** After each defence, everyone writes one strength, one question and one suggestion.

#### [capstone#running-order] Who presents when

*Running order*

| # | Presenter | Question |
| --- | --- | --- |
| 1 |  |  |
| 2 |  |  |
| 3 |  |  |
| 4 |  |  |
| 5 |  |  |
| 6 |  |  |
| 7 |  |  |
| 8 |  |  |

#### [capstone#final-prep] Final prep · 20 minutes

*Before the first presentation*

Clone your repository into a new folder, run your one command there, and search the clone for a raw personal field.

#### [capstone#now-presenting] Defence and rebuild

*Now presenting*

##### Questions

#### [capstone#review] What the presentations showed

*Trainer review*

- **Strongest patterns.** What several projects got right.
- **Common gaps.** What most projects would fix next.
- **One surprise.** Something nobody expected.

#### [capstone#what-next] Keep going

*After the course*

- **The follow-up task:** a provenance file and a rule suite for one dataset from your work, or one open dataset. The brief is `labs/follow_up.md`
- **Your repository stays yours:** keep it rebuildable, and add the rule for the fault the assessor found today
- **Next in the Data Science stream:** the other DS-200 courses prepare for the same DS Assistant badge; your trainer has the current schedule

#### [capstone#thanks] Thank you

*SDAIA Academy*

Data Acquisition, Preparation and Quality
