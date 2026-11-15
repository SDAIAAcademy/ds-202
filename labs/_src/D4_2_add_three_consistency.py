# %% [markdown]
# # Lab 4.2 · Three rules across fields and sources
#
# Day 4 · Session 2 (Cross-field and cross-source checks) · 25 min.
#
# The first week of October arrives as a new batch for the rebuild, and it is corrupted. The column rules of
# Lab 4.1 catch part of the damage. Some faults pass every column rule, because each value is fine on its own:
# they show only when two fields, or two sources, are compared. You add two cross-field rules and one
# cross-source rule, and write a failure report that tells each branch what to fix.
#
# **AI-off** for the first attempt at each rule; an **AI-tutor**, hinting only, may explain rule syntax.
#
# **Reference state.** `data/raw/batches/joined_2026-10-w1_corrupted.csv` and its clean twin; the kilograms each
# branch received that week, `donated_kg_2026-10-w1.csv`; the reference column rules `B.schema()`.
#
# **Tasks**
# - [ ] 1 · Run the column rules on the corrupted batch (5')
# - [ ] 2 · Two rules across fields (8')
# - [ ] 3 · One rule across sources (7')
# - [ ] 4 · A failure report a branch can act on (5')
# - [ ] ✱ Stretch · Reject the batch or quarantine the rows?

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

import pandas as pd
import ghilal as G
import build_dataset as B   # the reference build: its rule suite is the starting point of this lab

BATCH = G.RAW / "batches"
bad = pd.read_csv(BATCH / "joined_2026-10-w1_corrupted.csv")
good = pd.read_csv(BATCH / "joined_2026-10-w1.csv")
donated = pd.read_csv(BATCH / "donated_kg_2026-10-w1.csv")
print(f"corrupted batch: {len(bad):,} rows | clean batch: {len(good):,} rows")

# %% [markdown]
# ## 1 · Run the column rules on the corrupted batch (5')

# %%
column_report = B.run_schema(bad)
print(column_report.to_string(index=False))
G.check(B.run_schema(good).empty and len(column_report) == 7,
        f"the clean batch passes; the corrupted one fails {len(column_report)} column rules")

# %% [markdown]
# 🔍 Seven rules fail, each with a line somebody can act on. Now look at the weight line: 278 handouts "above
# 50 kg". Is that the whole story of those rows? Look at where they come from and at the weight per parcel.

# %%
heavy = bad[bad.weight_kg > 50]
print(heavy.branch_id.value_counts().to_string())
print((bad.weight_kg / bad.parcels.where(bad.parcels.between(1, 3))).groupby(bad.branch_id).median().round(1).to_string())

# %% [markdown]
# ## 2 · Two rules across fields (8')
#
# All 278 are at B05, and B05's handouts weigh about 26 "kilograms" per parcel, not 12: B05 sent pounds. Its
# one-parcel handouts weigh about 26, **inside** the allowed range of 5 to 50, and passed. A column rule cannot
# see them; the relation between two fields can.
#
# ✏️ **Exercise** · Write two functions, each returning the **failing rows** of a table:
# - `not_per_parcel(df)`: `weight_kg / parcels` is recorded and outside 9 to 15 (rows whose parcels are not 1 to 3 are another
#   rule's business: skip them);
# - `before_registration(df)`: `handout_date` is before `registered_on` (compare as dates; rows whose date is not
#   in the ISO layout are another rule's business: skip them with `errors="coerce"`).

# %%
def not_per_parcel(df: pd.DataFrame) -> pd.DataFrame:
    # BEGIN SOLUTION
    per = df.weight_kg / df.parcels.where(df.parcels.between(1, 3))
    return df[per.notna() & ~per.between(9, 15)]
    # END SOLUTION


def before_registration(df: pd.DataFrame) -> pd.DataFrame:
    # BEGIN SOLUTION
    hd = pd.to_datetime(df.handout_date, format="%Y-%m-%d", errors="coerce")
    ro = pd.to_datetime(df.registered_on, format="%Y-%m-%d", errors="coerce")
    return df[hd < ro]
    # END SOLUTION


# %%
# Check, with a safety net: the cells below still run when the exercise is not done yet
def _npp(df):
    per = df.weight_kg / df.parcels.where(df.parcels.between(1, 3))
    return df[per.notna() & ~per.between(9, 15)]


def _br(df):
    return df[pd.to_datetime(df.handout_date, format="%Y-%m-%d", errors="coerce")
              < pd.to_datetime(df.registered_on, format="%Y-%m-%d", errors="coerce")]


try:
    f_weight, f_date = not_per_parcel(bad), before_registration(bad)
    clean_ok = not_per_parcel(good).empty and before_registration(good).empty
except NotImplementedError:
    f_weight, f_date, clean_ok = _npp(bad), _br(bad), True
print(f"outside 9 to 15 kg per parcel: {len(f_weight)} rows, branches {sorted(f_weight.branch_id.unique())}")
print(f"handout before registration: {len(f_date)} rows, in {f_date.branch_id.nunique()} branches")
G.check(clean_ok and len(f_weight) > 278 and set(f_weight.branch_id) == {"B05"} and len(f_date) == 30,
        f"the per-parcel rule finds all {len(f_weight)} handouts of B05, not only 278; {len(f_date)} handouts predate their household")

# %% [markdown]
# ## 3 · One rule across sources (7')
#
# A branch cannot hand out more food than it received. The donations source says how many kilograms each branch
# received that week. This rule compares two sources that no single table holds together.
#
# ✏️ **Exercise** · Write `over_donated(df, donated)`: one row per branch that handed out more kilograms than it
# received, with the columns `branch_id`, `handed_kg` and `donated_kg`.

# %%
def over_donated(df: pd.DataFrame, donated: pd.DataFrame) -> pd.DataFrame:
    # BEGIN SOLUTION
    handed = df.groupby("branch_id").weight_kg.sum().round(1).rename("handed_kg").reset_index()
    t = handed.merge(donated, on="branch_id", how="left", validate="one_to_one")
    return t[t.handed_kg > t.donated_kg].reset_index(drop=True)
    # END SOLUTION


# %%
def _od(df, donated):
    t = df.groupby("branch_id").weight_kg.sum().round(1).rename("handed_kg").reset_index().merge(donated, on="branch_id")
    return t[t.handed_kg > t.donated_kg].reset_index(drop=True)


try:
    f_source = over_donated(bad, donated)
    clean_ok = over_donated(good, donated).empty
except NotImplementedError:
    f_source, clean_ok = _od(bad, donated), True
print(f_source.to_string(index=False))
G.check(clean_ok and list(f_source.branch_id) == ["B05"], "one branch handed out more than it received: B05, about twice as much")

# %% [markdown]
# ## 4 · A failure report a branch can act on (5')
#
# "Validation failed" helps nobody. A failure report says, per rule: what must hold, how many rows break it,
# **whose** rows they are, and an example. The owner of the rows is the branch.
#
# ✏️ **Exercise** · Write `by_branch(rows)`: a short text such as `"B05: 395"` or `"B02: 4, B09: 3, …"` listing
# the three branches with the most failing rows, largest first.

# %%
def by_branch(rows: pd.DataFrame) -> str:
    # BEGIN SOLUTION
    return ", ".join(f"{b}: {n}" for b, n in rows.branch_id.value_counts().head(3).items())
    # END SOLUTION


# %%
try:
    by_branch(f_weight)
except NotImplementedError:
    by_branch = lambda rows: ", ".join(f"{b}: {n}" for b, n in rows.branch_id.value_counts().head(3).items())  # noqa: E731
report = pd.DataFrame([
    ("consistency: 9 to 15 kg per parcel", len(f_weight), by_branch(f_weight),
     f"median {(f_weight.weight_kg / f_weight.parcels).median():.1f} per parcel: pounds entered as kilograms?"),
    ("consistency: handout on or after registration", len(f_date), by_branch(f_date),
     "check the household id or the date of these handouts"),
    ("consistency across sources: handed out no more than received", len(f_source),
     ", ".join(f_source.branch_id), "; ".join(f"handed {r.handed_kg:,.0f} kg, received {r.donated_kg:,.0f} kg"
                                               for r in f_source.itertuples())),
], columns=["rule", "rows", "whose", "what to look at"])
full = pd.concat([column_report.assign(whose="", **{"what to look at": column_report.examples})
                  [["rule", "rows", "whose", "what to look at"]], report], ignore_index=True)
print(full.to_string(index=False))
full.to_csv(G.lab_dir("D4_2") / "failure_report.csv", index=False)
G.keep("d4_2_report", report.to_dict("records"))
G.check(len(full) == 10 and report.whose.iloc[0].startswith("B05"), "ten failing rules in one report; the three new ones name the branch")

# %% [markdown]
# Ten lines. Three of them, the ones you wrote, would have let a week of pounds into every weight total and 30
# misattributed handouts into the household counts, with every column rule green.

# %% [markdown]
# ## ✱ Stretch · Reject the batch or quarantine the rows?
#
# Two responses to a failed rule: refuse the whole batch, or load the good rows and set the bad ones aside with
# a reason. Decide per rule, and count what would be loaded.

# %%
def decide() -> dict:
    # BEGIN SOLUTION
    bad_ids = set(f_date.log_id) | set(bad[bad.duplicated("log_id", keep=False)].log_id)
    quarantined = bad[bad.log_id.isin(bad_ids)]
    return {"reject the file of": "B05 (every weight is in the wrong unit: a fault of the file, not of rows)",
            "quarantine": f"{len(quarantined)} rows of other faults, each with its reason",
            "load": f"{len(bad[(bad.branch_id != 'B05') & ~bad.log_id.isin(bad_ids)]):,} rows, after the remaining column failures are set aside too"}
    # END SOLUTION


try:
    for k, v in decide().items():
        print(f"{k}: {v}")
except NotImplementedError:
    print("✱ Stretch not attempted")

# %% [markdown]
# ## Checkpoint
#
# 1. Why did the range rule on `weight_kg` catch only part of the B05 rows?
#    <details><summary>Answer</summary>A one-parcel handout in pounds weighs about 26, inside 5 to 50. Only handouts
#    of two or three parcels went over the range. The per-parcel rule compares weight with parcels and sees all.</details>
# 2. What does the cross-source rule need that the others do not?
#    <details><summary>Answer</summary>A second source, brought to the same unit and period, and joined at the right
#    grain: one row per branch. It is a small pipeline of its own, and it is worth it.</details>
# 3. A rule fails on 30 rows of 4,000. Does the rebuild stop?
#    <details><summary>Answer</summary>That is decided per rule, in advance, and written down: a fault of structure
#    stops the build; a few bad rows are quarantined with a reason and counted in the log.</details>
#
# **Carry forward.** `artifacts/D4_2/failure_report.csv`: with the suite of Lab 4.1, the evidence of LO4.
