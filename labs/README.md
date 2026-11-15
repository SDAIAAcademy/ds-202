# Data Acquisition, Preparation and Quality: labs

Hands-on notebooks for the SDAIA Academy course **DS-202 Data Acquisition, Preparation and Quality**. Every lab works on the data of **Ghilal Food Bank Network (شبكة غِلال لبنوك الطعام)**, a fictional charity with 14 branches in 30 districts, and on one question of its programmes director: how many parcels does an eligible household receive per month, by district, against a standard of two? Each lab starts from a supplied reference state, so none depends on an earlier one.

All data is **synthetic**: every name, phone number and ID number was drawn at random by `prepare_data.py` and belongs to nobody. Treat it as personal data all the same; that is the point of the course.

**No lab calls a model.** There is no key, no account and nothing to download beyond the Python packages. A laptop CPU or a Colab CPU runtime is enough; the longest cell of the course, the reference build, runs for under a minute.

## Quick start

**Google Colab**
1. Open a notebook from the course page, or directly: `https://colab.research.google.com/github/SDAIAAcademy/ds-202/blob/main/labs/<notebook>.ipynb`.
2. Run the first cell. It clones this repository and installs `requirements-colab.txt`.

**Local**
```bash
git clone https://github.com/SDAIAAcademy/ds-202
cd ds-202/labs
uv sync                        # creates .venv from pyproject.toml (uv.lock pins every version)
uv run jupyter lab
```
Run `00_setup_check.ipynb` once, then work through `00_prework.ipynb` (about two hours) before Day 1.

## What is in this folder

| Path | What it is |
|---|---|
| `data/raw/` | the four sources as they arrived: the register extract, 14 branch logs, the donations file behind the API, the open district table; and the batches of Day 4 |
| `data/docs/` | the source notes, the field catalogue and the data dictionary |
| `data/reference/` | reference states and reference results: each lab can start from here |
| `ghilal.py` | the helper every notebook imports as `G`: paths, loaders, the check function, the local API |
| `donations_api.py` | the donations API, served on your own machine by `G.start_api()` |
| `build_dataset.py` | the reference build: `uv run python build_dataset.py` turns `data/raw/` into `artifacts/build/` |
| `prepare_data.py` | the generator of the synthetic data (fixed seed); `--capstone` writes the capstone extract |
| `capstone/README.md` | the capstone brief |
| `solutions/` | the solved notebooks, and reference figures for the capstone assessor |
| `artifacts/` | what your runs write; not committed |

## Settings

| Environment variable | Default | Effect |
|---|---|---|
| `GH_QUICK` | unset | `1` shrinks the long cells (simulations, the enumeration of Lab 4.3) for a fast run |
| `GHILAL_KEY` | a teaching key, plainly not a secret | the key of the pseudonyms in `build_dataset.py`; set your own in the capstone |

## Notebooks

| Unit | Session | Notebook |
|---|---|---|
| Before Day 1 | Setup check | [`00_setup_check.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-202/blob/main/labs/00_setup_check.ipynb) |
| Before Day 1 | Pre-work · joins and dataframes, about two hours | [`00_prework.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-202/blob/main/labs/00_prework.ipynb) |
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
| Capstone | The brief | [`capstone/README.md`](capstone/README.md) |
| After the course | The follow-up task | [`follow_up.md`](follow_up.md) |

## How a lab is built

Each notebook states its reference state and its tasks with minutes, marks every exercise with ✏️, follows each exercise with a check cell, and ends with a verification note: what the run verified and what the lab did not. If an exercise is not done, the check cell falls back to the reference result, so the rest of the notebook still runs. The solved notebooks are in `solutions/`.

The notebooks are generated from the percent-format sources in `labs/_src/` by `labs/_tools/py2nb.py` (`uv run python _tools/py2nb.py` from `labs/`), which also writes the solutions to `labs/solutions/`. Edit the sources, not the notebooks.

## AI assistance in the labs

Each lab says which mode applies. **AI-off**: the first attempt is your own. **AI-tutor**: an assistant may explain syntax or an error and gives hints only. **AI-assistant**: allowed for a named part (the wording of the report in Lab 4.4), after your own draft. The entry quiz and the exit check are supervised and AI-off. In the capstone, assistance is allowed in full. In every mode: no personal data, synthetic or real, goes to an external assistant.
