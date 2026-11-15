# %% [markdown]
# # Lab 1.3 · Two provenance records
#
# Day 1 · Session 3 (Provenance and sharing basis) · 25 min.
#
# A provenance record answers, for one source, the questions a reviewer asks a year from now: where did this come
# from, who owns it, what does it cover, on what basis may we use it, how fresh is it, and what are its limits.
# You write the records of two sources from their source notes, run the checklist of the reviewer, and assemble
# the provenance file of the project. The records of the other two sources are supplied.
#
# **AI-off.** The notes are short; read them.
#
# **Reference state.** `data/docs/register_notes.md`, `open_population.md`, and the two supplied records in
# `data/reference/provenance_supplied.json`.
#
# **Tasks**
# - [ ] 1 · The record of the register (9')
# - [ ] 2 · The record of the open district table (7')
# - [ ] 3 · Run the checklist and repair a weak record (5')
# - [ ] 4 · Assemble `provenance.json` (4')
# - [ ] ✱ Stretch · A record for the audit file

# %%
import os, sys, subprocess
from pathlib import Path

IN_COLAB = "google.colab" in sys.modules
if IN_COLAB:
    REPO_URL = "https://github.com/SDAIAAcademy/ds-202.git"
    if not Path("/content/ds-202").exists():
        subprocess.run(["git", "clone", "-q", REPO_URL, "/content/ds-202"], check=True)
    os.chdir("/content/ds-202/labs")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements-colab.txt"], check=True)
else:
    while not Path("ghilal.py").exists() and Path.cwd() != Path.cwd().parent:
        os.chdir("..")  # solutions/ notebooks run from labs/
sys.path.insert(0, os.getcwd())

import json
import ghilal as G

print((G.DOCS / "register_notes.md").read_text(encoding="utf-8"))

# %% [markdown]
# ## 1 · The record of the register (9')
#
# Seven keys. Six are the fields of the outcome (origin, owner, coverage, sharing basis, refresh date, limits);
# the seventh is the classification level, one of Top Secret, Secret, Restricted, Public, which the network
# applies as its own policy.
#
# | Key | What a reviewer needs to read there |
# |---|---|
# | `origin` | the system and how the extract was made |
# | `owner` | the person to ask, by role |
# | `coverage` | which units and which period, with years; who is **not** in it |
# | `sharing_basis` | the consent, agreement or approval that lets you use it, and for what |
# | `refresh_date` | the day your copy was taken, `YYYY-MM-DD` |
# | `limits` | a list: what the data cannot be trusted for |
# | `classification` | the level |
#
# ✏️ **Exercise** · Write the record of the register from its note.

# %%
def register_record() -> dict:
    # BEGIN SOLUTION
    return {
        "origin": "Registration system of Ghilal Food Bank Network; extract made by appending the 14 branch exports",
        "owner": "Widad Al-Ghunaim, registration supervisor; extracts approved by the data protection officer",
        "coverage": "One row per registration, 2021-01-03 to 2026-09-28; households that never registered are absent",
        "sharing_basis": "Consent at registration for delivering and planning food support; internal approval "
                         "DS-2026-041 for service coverage analysis, Q3 2026; no onward sharing of identified records",
        "refresh_date": "2026-10-04",
        "limits": ["household_size and monthly_income_sar are reported by the household, not verified",
                   "no household-size field on the paper form of B03 and B11 before 2025-03-01",
                   "the online form and the call script offer sizes 1 to 6 only",
                   "branch exports are in more than one text encoding",
                   "a household that registered twice has two rows with one household_id"],
        "classification": "Restricted",
    }
    # END SOLUTION


# %%
# Check, with a safety net: the cells below still run when the exercise is not done yet
try:
    reg = register_record()
except NotImplementedError:
    reg = G.reference("d1_3_register")
G.keep("d1_3_register", reg)
problems = G.review_provenance(reg)
print("checklist:", problems or "passes")
G.check(not problems and reg["refresh_date"] == "2026-10-04" and reg["classification"] == "Restricted",
        "the register record passes: copy of 2026-10-04, Restricted")

# %% [markdown]
# ## 2 · The record of the open district table (7')
#
# Open data still has provenance: a publisher, a licence, a reference year that is not the year you downloaded it.

# %%
print((G.DOCS / "open_population.md").read_text(encoding="utf-8"))

# %% [markdown]
# ✏️ **Exercise** · Write the record. Which date is the refresh date: the year the rows describe, the day of
# publication, or the day of download?

# %%
def open_record() -> dict:
    # BEGIN SOLUTION
    return {
        "origin": "Open Data Portal of Madinat Al-Sidr Municipality, dataset Population and households by district, 2022",
        "owner": "The statistics office of the municipality (publisher); our copy is kept by the analyst",
        "coverage": "28 districts as they were in 2022; D29 and D30, established in 2024, are absent",
        "sharing_basis": "Open licence of the portal: free reuse with attribution to the publisher",
        "refresh_date": "2026-10-02",
        "limits": ["describes 2022; the city has grown since, unevenly",
                   "low_income_households_est is a survey estimate with no published margin of error",
                   "low income in the survey is not the eligibility rule of the network"],
        "classification": "Public",
    }
    # END SOLUTION


# %%
try:
    opn = open_record()
except NotImplementedError:
    opn = G.reference("d1_3_open")
G.keep("d1_3_open", opn)
problems = G.review_provenance(opn)
print("checklist:", problems or "passes")
G.check(not problems and opn["refresh_date"] == "2026-10-02" and opn["classification"] == "Public"
        and "2022" in opn["coverage"], "the open table record passes: downloaded 2026-10-02, describes 2022, Public")

# %% [markdown]
# 🔍 The refresh date is the day your copy was taken. The reference year belongs in `coverage`, and the gap
# between the two (2022 against 2026) belongs in `limits`.

# %% [markdown]
# ## 3 · Run the checklist and repair a weak record (5')
#
# A colleague drafted the record of the branch logs in a hurry. Run the checklist on it, read each complaint, and
# repair it from `data/docs/branch_logs_notes.md`.

# %%
weak = {"origin": "files", "owner": "Hazem", "coverage": "this year", "sharing_basis": "internal",
        "refresh_date": "October", "limits": ["messy"], "classification": "Internal"}
for line in G.review_provenance(weak):
    print(" -", line)

# %% [markdown]
# ✏️ **Exercise** · Return the repaired record.

# %%
def repaired_logs_record() -> dict:
    # BEGIN SOLUTION
    return {
        "origin": "Handout logs kept by each of the 14 branches, uploaded weekly by branch supervisors",
        "owner": "Hazem Al-Sulaim, branch operations lead",
        "coverage": "One row per handout, 1 January to 30 September 2026, all 14 branches",
        "sharing_basis": "Operational records of the network, used for planning under internal approval DS-2026-041",
        "refresh_date": "2026-10-03",
        "limits": ["date layout, weight unit and text encoding differ by branch and are not stated",
                   "household_id is typed by hand at some desks",
                   "a week can be uploaded twice or be missing, and no file says so",
                   "the scale of B09 was away from 4 to 17 May 2026"],
        "classification": "Restricted",
    }
    # END SOLUTION


# %%
try:
    logs_rec = repaired_logs_record()
except NotImplementedError:
    logs_rec = G.reference("provenance_supplied")["branch_logs"]
G.check(not G.review_provenance(logs_rec) and len(G.review_provenance(weak)) >= 7,
        f"the weak draft fails {len(G.review_provenance(weak))} checks; the repaired record passes")

# %% [markdown]
# ## 4 · Assemble `provenance.json` (4')
#
# One file for the project, one record per source. It lives in the repository beside the code, and it changes in
# the same commit as the extract it describes.

# %%
supplied = G.reference("provenance_supplied")
provenance = {"register": reg, "branch_logs": logs_rec, "donations_api": supplied["donations_api"],
              "open_population": opn}
out = G.lab_dir("D1_3") / "provenance.json"
out.write_text(json.dumps(provenance, ensure_ascii=False, indent=1), encoding="utf-8")
failed = {k: G.review_provenance(v) for k, v in provenance.items() if G.review_provenance(v)}
G.check(not failed and len(provenance) == 4, "four records, every one passes the checklist")
print("classification by source:", {k: v["classification"] for k, v in provenance.items()})

# %% [markdown]
# ## ✱ Stretch · A record for the audit file

# %%
def audit_record() -> dict:
    # BEGIN SOLUTION
    return {
        "origin": "Home visits by the registration team in which the household size was verified",
        "owner": "Widad Al-Ghunaim, registration supervisor",
        "coverage": "600 active households visited in September 2026: 300 with a blank size, 300 with a recorded size",
        "sharing_basis": "Collected by the network for quality control; same internal approval DS-2026-041",
        "refresh_date": "2026-10-04",
        "limits": ["a sample of 600, not the register", "half the sample was chosen because its size was blank"],
        "classification": "Restricted",
    }
    # END SOLUTION


try:
    print("checklist:", G.review_provenance(audit_record()) or "passes")
except NotImplementedError:
    print("✱ Stretch not attempted")

# %% [markdown]
# ## Checkpoint
#
# 1. The open table is public. Why does it need a record at all?
#    <details><summary>Answer</summary>Public says who may read it, not what it is good for: its year, its method and
#    its missing districts decide what you may conclude from it.</details>
# 2. The sharing basis of the register names a purpose. What follows for a second question next year?
#    <details><summary>Answer</summary>The approval covers service coverage analysis for Q3 2026. A new purpose
#    needs a new look by the data protection officer; the extract is not yours to reuse because you hold it.</details>
# 3. Where does "sizes above 6 cannot be entered online" belong, and who will need it?
#    <details><summary>Answer</summary>In `limits`. Day 3 needs it: it is the reason household sizes are missing for
#    large households in particular.</details>
#
# **Carry forward.** `artifacts/D1_3/provenance.json`: the evidence of LO2, and a part of the capstone repository.
