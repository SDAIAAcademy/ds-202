# Capstone brief: a rebuildable dataset for one question

You work alone. You build, from raw files, the analysis dataset for **one** question of the Ghilal Food Bank Network, in a repository of your own that rebuilds with one command, and you defend it live.

## The data

The network's branches in a second city, Madinat Al-Rimal: 14 branches, 28 districts, the first half of 2026. All of it is synthetic. Branch and district codes look like those of the course; the households, the volumes and the faults are different, and no note tells you which branch has which fault.

Make the extract on your own machine (it is not committed, and you do not commit it either):

```bash
cd labs
uv run python prepare_data.py --capstone     # writes labs/capstone/raw/, about one minute
```

| Source | File | Rows |
|---|---|---|
| Register extract | `capstone/raw/registry/registrations_extract.csv.gz` | 12,000 |
| Audit re-survey | `capstone/raw/registry/audit_resurvey.csv` | 150 |
| Branch logs | `capstone/raw/branch_logs/B01.csv.gz` to `B14.csv.gz` | 42,000 |
| Donations | `capstone/raw/donations/donations.jsonl.gz` (a file this time, not an API) | about 3,500 |
| Open district table | `capstone/raw/open/district_population_2022.csv` | 28 |

The source notes of the course (`labs/data/docs/`) describe the fields. Expect the same **kinds** of fault as in the course, in other places: mixed encodings, names decoded twice, Arabic-Indic digits, repeated registrations, three date layouts, pounds and grams, a week uploaded twice, days without rows, keys typed by hand, household sizes that are missing for a reason.

## Choose one question

| | Question | You will need |
|---|---|---|
| **A** | Parcels per eligible household per month, by district, in the second quarter of 2026 (1 April to 30 June), against the standard of 2 | register, logs |
| **B** | Kilograms handed out per household member, by branch, in the second quarter, against the kilograms each branch received | register, logs, donations |
| **C** | Share of eligible households that received no parcel in the second quarter, by registration channel | register, logs |

Eligible, as in the course: active, registered before the quarter, monthly income per household member at or below 1,000 SAR.

## What you submit

A link to a **public GitHub repository** that holds:

1. **One command** that rebuilds the analysis dataset from `capstone/raw/` (state it at the top of your README). You may start from `labs/build_dataset.py`; what is assessed is what you understand, change and add.
2. **A provenance file**: one record per source you use, with origin, owner, coverage, sharing basis, refresh date, limits and classification.
3. **A rule suite** that runs on every rebuild: types, ranges, uniqueness, completeness, and at least one rule across fields or sources.
4. **The set-aside rows** with their reason, as log id, branch and reason only.
5. **A README** that reports: row counts per step, rule results, your estimate with its sensitivity to the missing household sizes, and the limits of the dataset.

**No raw personal field is committed, synthetic or not**: no name, phone number, ID number, or household id as typed. No raw source file. No key of a pseudonym. Add `capstone/raw/` and your key to `.gitignore` before the first commit, and scan your outputs as in Lab 4.4.

## The defence: 8 minutes, then 4 minutes of questions

1. The question and the population, in one minute.
2. A **live rebuild** from the raw files.
3. The assessor **corrupts one input file** (for example: a week of one branch in another unit, a repeated block of rows, a column in another date layout). You rebuild and show which rule fails, what it says, and why.
4. Your estimate, its range, and the one limit that matters most to the person who asked.

## How it is scored

| Criterion | Weight | Full marks look like |
|---|---|---|
| Provenance | 15% | every source used has a complete record; limits are specific to this extract, found by looking |
| Joins and reconciliation | 25% | every join has a key check and a cardinality test; rows in equal rows out plus rows set aside, with reasons |
| Cleaning and validation | 25% | each repair is a rule with a count; the suite passes on your build and fails readably on the corrupted file |
| Missing data and sensitivity | 20% | the mechanism is argued from evidence; complete cases, an imputation and a range are compared; a recommended figure with its reason |
| Personal data and reproducibility | 15% | no raw personal field in the repository; a keyed pseudonym with the key outside it; a fresh clone rebuilds with one command |

## Rules on AI assistance

AI assistance is allowed in full in the capstone, with one limit: **no personal data, synthetic or real, goes to an external assistant**. Describe a column to an assistant; do not paste rows of the register or the logs. Say in your README what you used an assistant for. Every rule is defended live: in the defence you explain any line the assessor points at.

## Before you submit

- Clone your repository into a new folder and run your one command there.
- Search the repository for a ten-digit number, a mobile number and `H` followed by six digits.
- Read your limits as the programmes director would: does each one carry a number and a consequence?
