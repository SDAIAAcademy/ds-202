# %% [markdown]
# # Lab 2.4 · One calendar, one unit
#
# Day 2 · Session 4 (Types, units and dates) · 25 min.
#
# The 14 branch files write the handout date in three layouts and the weight in two units, and no file says
# which. `03/07/2026` is the third of July at one branch and the seventh of March at another. You decide the
# layout **per branch, from evidence**, parse every date with it, bring every weight to kilograms, and log each
# change with a count.
#
# **AI-tutor**, hinting only, for date format codes and regular expressions.
#
# **Reference state.** `G.logs_raw()`: the 210,000 log rows, every column as text.
#
# **Tasks**
# - [ ] 1 · Find the date layout of each branch (7')
# - [ ] 2 · Parse every date with the layout of its branch (5')
# - [ ] 3 · Bring every weight to kilograms (8')
# - [ ] 4 · The change log (5')
# - [ ] ✱ Stretch · What guessing value by value would have done

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
import build_dataset as B   # the reference build: its steps are the safety nets of this lab

logs = G.logs_raw().drop_duplicates().reset_index(drop=True)
print(logs.groupby("branch_id").handout_date.agg(["first", "last"]).to_string())

# %% [markdown]
# ## 1 · Find the date layout of each branch (7')
#
# Three layouts: `2026-07-03`, and two with slashes. In a slash date the day and the month cannot be told apart
# when both are 12 or less. But a branch uses **one** layout, and over nine months some of its dates have a part
# above 12: if the first part ever exceeds 12 it is the day; if the second part does, the first is the month.
#
# ✏️ **Exercise** · Write `layout_of(dates)` for the dates of one branch: return `"%Y-%m-%d"`, `"%d/%m/%Y"` or
# `"%m/%d/%Y"`. Raise a `ValueError` when the evidence does not decide.

# %%
def layout_of(dates: pd.Series) -> str:
    # BEGIN SOLUTION
    if dates.str.fullmatch(r"\d{4}-\d{2}-\d{2}").all():
        return "%Y-%m-%d"
    first = dates.str.slice(0, 2).astype(int).max()
    second = dates.str.slice(3, 5).astype(int).max()
    if (first > 12) == (second > 12):
        raise ValueError("the layout cannot be decided from these dates")
    return "%d/%m/%Y" if first > 12 else "%m/%d/%Y"
    # END SOLUTION


# %%
# Check, with a safety net: the cells below still run when the exercise is not done yet
try:
    layouts = {b: layout_of(s) for b, s in logs.groupby("branch_id").handout_date}
except NotImplementedError:
    layouts = B.date_layouts(logs)
by_layout = pd.Series(layouts).reset_index().groupby(0)["index"].apply(list)
print(by_layout.to_string())
G.keep("d2_4_layouts", layouts)
G.check(sorted(by_layout["%m/%d/%Y"]) == ["B05", "B13"] and len(by_layout["%d/%m/%Y"]) == 4
        and len(by_layout["%Y-%m-%d"]) == 8, "8 branches write ISO dates, 4 day first, 2 month first")
ambiguous = logs[logs.handout_date.str.contains("/")]
both_small = (ambiguous.handout_date.str.slice(0, 2).astype(int) <= 12) & (ambiguous.handout_date.str.slice(3, 5).astype(int) <= 12)
print(f"slash dates that cannot be read alone: {int(both_small.sum()):,} of {len(ambiguous):,}")

# %% [markdown]
# ## 2 · Parse every date with the layout of its branch (5')
#
# ✏️ **Exercise** · Write `parse(logs, layouts)`: a column of dates in the order of `logs`, each branch parsed with
# its own layout. Use `pd.to_datetime(..., format=...)` so that a value that does not fit raises an error.

# %%
def parse(logs: pd.DataFrame, layouts: dict) -> pd.Series:
    # BEGIN SOLUTION
    parts = [pd.to_datetime(s, format=layouts[b]) for b, s in logs.groupby("branch_id").handout_date]
    return pd.concat(parts).reindex(logs.index)
    # END SOLUTION


# %%
try:
    dates = parse(logs, layouts)
except NotImplementedError:
    dates = B.parse_dates(logs)
logs["date"] = dates
per_month = logs.groupby([logs.branch_id, logs.date.dt.month]).size().unstack(fill_value=0)
print(per_month.loc[["B01", "B05", "B12"]].to_string())
G.check(dates.notna().all() and dates.min() == pd.Timestamp("2026-01-01") and dates.max() == pd.Timestamp("2026-09-30"),
        "every date parsed; all between 1 January and 30 September 2026")
G.check(per_month.min().min() > 300, "every branch has handouts in every month: no branch was read with the wrong layout")

# %% [markdown]
# 🔍 The second check is the one that would catch a wrong layout: read month first as day first, and a branch's
# handouts pile into the first twelve days of each month and the rest fail to parse.

# %% [markdown]
# ## 3 · Bring every weight to kilograms (8')
#
# A parcel is packed to a standard of 12 kg. Look at the weight per parcel, by branch and unit.

# %%
logs["w"] = pd.to_numeric(logs.weight, errors="coerce")
logs["n"] = pd.to_numeric(logs.parcels)
per = (logs.w / logs.n).rename("per_parcel")
print(per.groupby([logs.branch_id, logs.unit]).describe()[["count", "min", "50%", "max"]].round(1)
      .loc[["B01", "B05", "B09", "B13"]].to_string())
print("weights missing:", int(logs.w.isna().sum()), "| all at", list(logs[logs.w.isna()].branch_id.unique()),
      logs[logs.w.isna()].date.min().date(), "to", logs[logs.w.isna()].date.max().date())

# %% [markdown]
# Four situations: pounds labelled `lb` (two branches); values a thousand times too large, grams typed into a
# kilogram field; values labelled `kg` that sit where pounds sit, around 26 per parcel; and blanks. One pound is
# 0.45359237 kg.
#
# ✏️ **Exercise** · Write `to_kg(logs)`: return the weight in kilograms and, for each row, the change made:
# `""`, `"pounds to kilograms"`, `"grams to kilograms"`, `"pounds labelled kg"` or `"weight missing, left missing"`.
# Use the per-parcel weight as evidence: above 1,000 is grams; labelled kg and between 19.8 and 33.2 is pounds.

# %%
def to_kg(logs: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    # BEGIN SOLUTION
    w = pd.to_numeric(logs.weight, errors="coerce")
    n = pd.to_numeric(logs.parcels)
    change = pd.Series("", index=logs.index)
    lb = logs.unit.eq("lb")
    change[lb] = "pounds to kilograms"
    w = w.where(~lb, w * 0.45359237)
    per = w / n
    grams = per > 1000
    change[grams] = "grams to kilograms"
    w = w.where(~grams, w / 1000)
    mislabelled = (~lb) & per.between(19.8, 33.2)
    change[mislabelled] = "pounds labelled kg"
    w = w.where(~mislabelled, w * 0.45359237)
    change[w.isna()] = "weight missing, left missing"
    return w.round(2), change
    # END SOLUTION


# %%
try:
    kg, change = to_kg(logs)
except NotImplementedError:
    kg, change = B.to_kg(logs)
logs["weight_kg"], logs["weight_change"] = kg, change
after = (logs.weight_kg / logs.n).dropna()
print(change.value_counts().to_string())
G.check(after.between(9, 15).all(), f"every recorded weight is now {after.min():.1f} to {after.max():.1f} kg per parcel")
G.check(set(logs[change == "pounds labelled kg"].branch_id) == {"B13"} and
        logs[change == "pounds labelled kg"].date.min() >= pd.Timestamp("2026-09-14"),
        "the mislabelled pounds are all at B13, from 14 September")

# %% [markdown]
# The blank weights stay blank. A missing weight is not zero and is not 12: what to do with it is a question
# for Day 3.

# %% [markdown]
# ## 4 · The change log (5')

# %%
rows = [(f"dates read as {lay}", int(logs.branch_id.map(layouts).eq(lay).sum()), ", ".join(sorted(bs)))
        for lay, bs in by_layout.items()]
rows += [(f"weight: {name}", int(n), ", ".join(sorted(logs[change == name].branch_id.unique())))
         for name, n in change[change != ""].value_counts().items()]
rows.append(("weight: unchanged", int((change == "").sum()), "kilograms as recorded"))
change_log = pd.DataFrame(rows, columns=["change", "rows", "branches"])
print(change_log.to_string(index=False))
change_log.to_csv(G.lab_dir("D2_4") / "change_log.csv", index=False)
G.keep("d2_4_change_log", change_log.to_dict("records"))
G.check(change_log[change_log.change.str.startswith("dates")].rows.sum() == len(logs)
        and change_log[change_log.change.str.startswith("weight")].rows.sum() == len(logs),
        f"the date lines add up to {len(logs):,} rows, and so do the weight lines")

# %% [markdown]
# ## ✱ Stretch · What guessing value by value would have done
#
# Parse the dates of B05 (month first) the way a hurried loader would: day first, value by value, turning what
# does not fit into "no date". How many dates come out wrong, how many are lost, and does anything warn you?

# %%
def guessed() -> dict:
    # BEGIN SOLUTION
    b05 = logs[logs.branch_id == "B05"]
    g = pd.to_datetime(b05.handout_date, format="%d/%m/%Y", errors="coerce")
    return {"rows": len(b05), "lost": int(g.isna().sum()), "wrong, silently": int((g.notna() & (g != b05.date)).sum()),
            "right by luck": int((g == b05.date).sum())}
    # END SOLUTION


try:
    print(guessed())
except NotImplementedError:
    print("✱ Stretch not attempted")

# %% [markdown]
# ## Checkpoint
#
# 1. Why decide the layout per branch and not per value?
#    <details><summary>Answer</summary>A value such as 03/07/2026 carries no evidence. The file it sits in does: one
#    date with a part above 12 settles every date of that branch.</details>
# 2. The rule "labelled kg and 19.8 to 33.2 per parcel is pounds" changed several hundred rows. What makes it defensible?
#    <details><summary>Answer</summary>The packing standard (12 kg), the empty gap between the two clouds of values,
#    and that all the rows are one branch after one date. And it is in the change log, so the owner can confirm it.</details>
# 3. Why are the blank weights not filled with 12 kg per parcel?
#    <details><summary>Answer</summary>Filling is a decision about missing data with consequences for every average of
#    weight. It is taken on purpose, on Day 3, not by a cleaning step.</details>
#
# **Carry forward.** `artifacts/D2_4/change_log.csv`: a section of the quality report (Lab 4.4).
