---
course: "Data Acquisition, Preparation and Quality"
code: "DS-202"
version: "2027.1.0"
deck: "day4"
day: 4
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-202/slides/day4.html"
---

# Data Acquisition, Preparation and Quality

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
