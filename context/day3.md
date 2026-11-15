---
course: "Data Acquisition, Preparation and Quality"
code: "DS-202"
version: "2027.1.0"
deck: "day3"
day: 3
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-202/slides/day3.html"
---

# Data Acquisition, Preparation and Quality

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

#### [day3#no-neutral-option] Every way of handling a blank is an assumption about the households behind it

*There is no neutral option*

- **Complete cases.** Drop the rows. Assumes the dropped households are like the kept ones.
- **One value for all.** Fill with the median. Assumes every blank household is typical.
- **A value from similar households.** Fill from a group. Assumes that within the group, blank and recorded households are alike.

Lab 3.2 computes the headline all three ways, on the same 35,665 households.

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
- But most blank households have 7 members or more
- Income 6,000 SAR, 7 members in reality: 857 per member, eligible. With the imputed 5: 1,200, "not eligible"
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

#### [day3#recorded-and-wrong] A value can be present, valid, and wrong

*The other half of data quality*

- Household size is **reported by the household** at registration and is not verified
- It passes every rule: an integer between 1 and 20
- No validation suite can see that 7 should have been 5
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
- It is silent about households that never collected
- 323 households are eligible by the register and never collected in nine months

> **What goes wrong.** Defining "eligible" as "collected regularly". Every eligible household that was not served leaves the denominator, and every district looks well served.

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
