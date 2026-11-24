# Changes

## 2027.2.0 (2026-11-24)

- Added: paging with a cursor and the four checks that prove a retrieval complete, `cursor-proof` and `paging-log` (day 1, session 2).
- Added: retrying a failed ingestion with a bounded, growing wait and raising an alert when it still fails, `retry-backoff` and `retry-alert` (day 1, session 2); a second stretch in Lab 1.2, "A retry that gives up and raises an alert", with its solution and checks.
- Added: building a master record field by field from records that disagree, with source precedence and survivorship rules, `master-record-rules` and `master-record-example` (day 2, session 3).
- Added: following up a sample of survey nonrespondents and weighting for nonresponse, `unit-nonresponse` and `nonresponse-weights` (day 3, session 2).
- Added: linking a series across a changed question with an overlap period, and when a change breaks comparability, `instrument-change` and `comparability-break` (day 3, session 4).
- Added: five practice questions, one for each of these topics.
- Added: one session outcome each to day 1 session 2, day 2 session 3, day 3 session 2 and day 3 session 4.
- Changed: shorter `paging`, `three-doors`, `text-first` and `api-total` (day 1), `no-key` and `block-score-decide` (day 2), `no-neutral-option`, `median-cost`, `recorded-and-wrong` and `proxies` (day 3); the detail moved to the speaker notes, and the retry policy to its own slide.
- The figures of the new examples are computed by `labs/_tools/practice_figures.py`.
