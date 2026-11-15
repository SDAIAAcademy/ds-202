# Data Acquisition, Preparation and Quality: labs

## Quick start

- Google Colab: open a notebook from the course page; its first cell clones this repository.
- Locally: clone the repository, then open the notebooks in `labs/` with Jupyter.

| Unit | Session | Notebook |
|---|---|---|
| Day 1 | Session 1 · Start from the question, not the files | [`D1_1_list_variables_question.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-202/blob/main/labs/D1_1_list_variables_question.ipynb) |
| Day 1 | Session 2 · Files, APIs and databases | [`D1_2_load_logs_page.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-202/blob/main/labs/D1_2_load_logs_page.ipynb) |
| Day 1 | Session 3 · Provenance and sharing basis | [`D1_3_write_provenance_records.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-202/blob/main/labs/D1_3_write_provenance_records.ipynb) |
| Day 1 | Session 4 · Coverage and sampling frames | [`D1_4_compare_registrations_open.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-202/blob/main/labs/D1_4_compare_registrations_open.ipynb) |
| Day 2 | Session 1 · Encodings and Arabic text | [`D2_1_repair_mixed_encodings.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-202/blob/main/labs/D2_1_repair_mixed_encodings.ipynb) |
| Day 2 | Session 2 · Keys and cardinality | [`D2_2_join_logs_registrations.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-202/blob/main/labs/D2_2_join_logs_registrations.ipynb) |
| Day 2 | Session 3 · Matching without a clean key | [`D2_3_match_300_records.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-202/blob/main/labs/D2_3_match_300_records.ipynb) |
| Day 2 | Session 4 · Types, units and dates | [`D2_4_standardise_three_date.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-202/blob/main/labs/D2_4_standardise_three_date.ipynb) |
| Day 3 | Session 1 · Why data go missing | [`D3_1_classify_six_missingness.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-202/blob/main/labs/D3_1_classify_six_missingness.ipynb) |
| Day 3 | Session 2 · Imputation and its cost | [`D3_2_estimate_parcels_per.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-202/blob/main/labs/D3_2_estimate_parcels_per.ipynb) |
| Day 3 | Session 3 · Sensitivity ranges | [`D3_3_bound_estimate_under.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-202/blob/main/labs/D3_3_bound_estimate_under.ipynb) |
| Day 3 | Session 4 · Measurement error and proxies | [`D3_4_simulate_self_report.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-202/blob/main/labs/D3_4_simulate_self_report.ipynb) |
| Day 4 | Session 1 · Quality dimensions as rules | [`D4_1_write_type_range.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-202/blob/main/labs/D4_1_write_type_range.ipynb) |
| Day 4 | Session 2 · Cross-field and cross-source checks | [`D4_2_add_three_consistency.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-202/blob/main/labs/D4_2_add_three_consistency.ipynb) |
| Day 4 | Session 3 · Minimise and pseudonymise | [`D4_3_replace_national_id.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-202/blob/main/labs/D4_3_replace_national_id.ipynb) |
| Day 4 | Session 4 · A data-quality report | [`D4_4_draft_quality_report.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-202/blob/main/labs/D4_4_draft_quality_report.ipynb) |

The notebooks are generated from the percent-format sources in `labs/_src/` by `labs/_tools/py2nb.py` (`uv run python _tools/py2nb.py` from `labs/`), which also writes the solutions to `labs/solutions/`. Edit the sources, not the notebooks.
