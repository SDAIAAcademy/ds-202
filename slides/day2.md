---
course: "Data Acquisition, Preparation and Quality"
code: "DS-202"
version: "2027.2.0"
deck: "day2"
day: 2
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-202/slides/day2.html"
---

# Data Acquisition, Preparation and Quality

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
