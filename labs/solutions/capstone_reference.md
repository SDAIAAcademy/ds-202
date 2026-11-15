# Capstone: reference figures for the assessor

These figures come from running the cleaning, joining and rule steps of `labs/build_dataset.py` on the capstone extract (`prepare_data.py --capstone`, seed fixed), with the quarter set to 1 April to 30 June 2026. A participant's figures may differ by a few rows where a decision differs (for example which of two registrations of one household stands); ask for the decision and its count.

| Step | Rows |
|---|---|
| register rows read | 12,000 |
| names repaired (decoded twice) | 804 |
| ID numbers with Arabic-Indic digits rewritten | 819 |
| one row per household id | 11,930 (70 later registrations set aside) |
| log rows read | 42,000 |
| exact copies dropped | 28 |
| keys repaired | 539 |
| set aside: key not in the register | 84 |
| set aside: blank key | 62 |
| set aside: handout before registration | 14 |
| log rows kept | 41,812 |
| handouts of the second quarter | 22,772 |
| households of the target population | 10,650 |

- Household size is missing for 21.1% of the target population.
- Question A, complete cases: 2.089 parcels per eligible household per month. A participant who reports only this figure has not done the missing-data work; within-group imputation and a range are expected, and the recommended figure should be higher than the complete-case one, with the reason.
- Date layouts found by evidence: day first at three branches, month first at two, ISO at nine. The branches are not those of the course.
- `uv run python prepare_data.py --capstone --trainer` prints the generator's own summary (participants run it without `--trainer` and see volumes only); it knows the values that are blank in the extract. Use it to judge direction, not to mark to the third decimal.

## Corruptions to use in the defence

Pick one per participant; each takes under a minute to apply to a raw file with a short script.

| Corruption | A good suite answers with |
|---|---|
| multiply the weights of one branch by 2.2 for one week, unit left as kg | the per-parcel consistency rule, naming the branch |
| append the last 200 rows of one branch log to the same file | the uniqueness rule on the log id, or a counted drop of exact copies in the join log |
| rewrite the dates of one ISO branch as day/month/year | a type or layout failure, not silently parsed dates |
| blank the household id in 100 rows | 100 more rows set aside, with a reason, and a join log that still adds up |
| set parcels to 30 in 50 rows | the validity rule on parcels |

A build that crashes with a traceback has detected the fault but not reported it: half marks for that part. A build that completes with every rule green has missed it.
