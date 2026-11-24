---
course: "Data Acquisition, Preparation and Quality"
code: "DS-202"
version: "2027.2.0"
deck: "day1"
day: 1
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-202/slides/day1.html"
---

# Data Acquisition, Preparation and Quality

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
