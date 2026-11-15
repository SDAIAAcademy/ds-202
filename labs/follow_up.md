# Follow-up task: a provenance file and a rule suite for a dataset of your own

After the capstone you apply two things from the course to **one dataset from your work, or one open dataset**. The trainer sets the date and where to hand it in, and records that it was received and reviewed.

## Choose the dataset

- A dataset you use at work, **if** your organisation allows it to be described outside its systems. You hand in the provenance file and the rules, never the data.
- Otherwise an open dataset from a public portal. Note its address and the date you downloaded it.

Do not hand in any row of a dataset that holds personal data, and do not paste such rows into a hosted assistant.

## What to hand in

1. **A provenance file** (`provenance.json` or `provenance.md`), one record for the dataset, with the seven fields of Lab 1.3: origin, owner, coverage, sharing basis, refresh date, limits, classification. At least three limits, each found by looking at the data or by asking its owner, and each specific: a number, a period, a field.
2. **A rule suite** (Pandera, Great Expectations or SQL assertions) with at least eight rules that cover type, completeness, validity and uniqueness, and at least one rule across two fields or two sources. Every rule has a name that says its dimension and what must hold.
3. **Two outputs of the suite**: one on the dataset as it is, one on a copy you broke on purpose, with a readable failure for each rule you broke.
4. **Half a page**: which rules fail on the dataset as it is, what you would ask the owner, and what the dataset cannot support.

## How it is reviewed

| Check | Met when |
|---|---|
| The provenance record is complete | all seven fields are filled, and the reviewer's checklist of Lab 1.3 (`G.review_provenance`) raises nothing |
| The limits are specific | each names a field, a period or a count |
| The suite can fail | the broken copy fails, rule by rule, in words the owner of the data can read |
| The suite reruns | one command runs it; the command is stated |
| No personal data left its place | nothing handed in holds a row of personal data |

The task is not graded with marks. It is complete when all five checks are met.
