# %% [markdown]
# # Lab 3.3 · How far could it move?
#
# Day 3 · Session 3 (Sensitivity ranges) · 25 min.
#
# Lab 3.2 gave three estimates. Which one is right cannot be read from the data: it depends on households whose
# size nobody recorded. So you answer a different question, which **can** be answered: how far could the
# headline move? First the logical bounds, which assume nothing. Then a narrower range under assumptions you can
# defend. Then which districts change side of the standard inside that range, and a recommendation.
#
# **AI-off** for the first attempt.
#
# **Reference state.** `G.households_q3()` and `G.impute_within_groups(h)`, the reference imputation of Lab 3.2.
#
# **Tasks**
# - [ ] 1 · The logical bounds (7')
# - [ ] 2 · A plausible range: shift the imputed sizes (8')
# - [ ] 3 · Which districts change side of the standard (5')
# - [ ] 4 · Recommend an estimate, with its reason (5')
# - [ ] ✱ Stretch · The tipping point of one district

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

import numpy as np
import pandas as pd
import ghilal as G

h = G.households_q3()
known = h.household_size.notna()
base = G.impute_within_groups(h)
cc, central = G.estimate(h, h.household_size), G.estimate(h, base)
print(f"complete case: {cc} | imputed within groups: {central} | standard: {G.STANDARD}")

# %% [markdown]
# ## 1 · The logical bounds (7')
#
# Each of the 6,461 households without a size is either eligible or not; you do not know which. The estimate is
# an average over eligible households. It is **lowest** if exactly the blank households that received few parcels
# are eligible, and **highest** if exactly those that received many are. No assumption about sizes can take the
# estimate outside these two values.
#
# The recipe for the lowest value: start from the complete cases (their parcels `S` and their count `N`). Sort
# the blank households by `parcels_q3`, fewest first. Add them one by one; after adding `k` the estimate is
# `(S + sum of their parcels) / (N + k) / 3`. Keep the minimum. For the highest value sort the other way and keep
# the maximum.
#
# ✏️ **Exercise** · Write `logical_bounds(h)`: return `(lowest, highest)`, each rounded to 3 decimals.

# %%
def logical_bounds(h: pd.DataFrame) -> tuple:
    # BEGIN SOLUTION
    k = h.household_size.notna()
    e = h[k][(h[k].monthly_income_sar / h[k].household_size.astype(float)) <= G.THRESHOLD_SAR]
    S, N = e.parcels_q3.sum(), len(e)
    p = np.sort(h[~k].parcels_q3.to_numpy())
    n = np.arange(1, len(p) + 1)
    low = min(S / N, ((S + np.cumsum(p)) / (N + n)).min()) / 3
    high = max(S / N, ((S + np.cumsum(p[::-1])) / (N + n)).max()) / 3
    return round(float(low), 3), round(float(high), 3)
    # END SOLUTION


# %%
# Check, with a safety net: the cells below still run when the exercise is not done yet
try:
    low, high = logical_bounds(h)
except NotImplementedError:
    low, high = G.reference("d3_3_bounds")
G.keep("d3_3_bounds", [low, high])
print(f"logical bounds: {low} to {high} (width {high - low:.3f})")
G.check(low < cc < central < high and [low, high] == G.reference("d3_3_bounds"),
        f"whatever the blank households are, the estimate lies between {low} and {high}")

# %% [markdown]
# 🔍 The bounds are honest and wide: they straddle the standard of 2.0. They treat "every blank household that
# collected nothing is eligible" as seriously as anything else. You know more than that.
#
# ## 2 · A plausible range: shift the imputed sizes (8')
#
# What you know, from the source note and the audit: blanks on the phone and online channels are households of 7
# or more; the audit found blank households about two members larger than recorded ones. The imputation within
# groups may still be too small or too large. So shift it: add `delta` members to every **imputed** size, for
# `delta` in −1, 0, +1, +2, and recompute. And one more scenario: `floor7`, in which every blank on the phone or
# online channel is at least 7.
#
# ✏️ **Exercise** · Write `scenario_sizes(h, base)`: a dictionary from scenario name to a size column. Recorded
# sizes never change; a size never goes below 1.

# %%
def scenario_sizes(h: pd.DataFrame, base: pd.Series) -> dict:
    # BEGIN SOLUTION
    blank = h.household_size.isna()
    out = {}
    for delta in (-1, 0, 1, 2):
        out[f"delta {delta:+d}"] = base.where(~blank, (base + delta).clip(lower=1))
    remote = blank & h.channel.isin(["phone", "online"])
    out["floor7"] = base.where(~remote, base.clip(lower=7))
    return out
    # END SOLUTION


# %%
def _scenarios(h, base):
    blank = h.household_size.isna()
    out = {f"delta {d:+d}": base.where(~blank, (base + d).clip(lower=1)) for d in (-1, 0, 1, 2)}
    out["floor7"] = base.where(~(blank & h.channel.isin(["phone", "online"])), base.clip(lower=7))
    return out


try:
    sizes = scenario_sizes(h, base)
except NotImplementedError:
    sizes = _scenarios(h, base)
overall = pd.Series({name: G.estimate(h, s) for name, s in sizes.items()}, name="estimate")
print(overall.to_string())
plaus = (float(overall.min()), float(overall.max()))
G.keep("d3_3_range", {"scenarios": overall.to_dict(), "plausible": list(plaus)})
G.check(all((s[known] == h.household_size[known]).all() for s in sizes.values()) and overall["delta +0"] == central,
        f"plausible range {plaus[0]} to {plaus[1]}: recorded sizes untouched, delta 0 is the imputation itself")

# %% [markdown]
# ## 3 · Which districts change side of the standard (5')
#
# ✏️ **Exercise** · Write `district_range(sizes)`: a table indexed by district with the columns `low` and `high`
# (the lowest and highest estimate across the scenarios) and `verdict`: `"below"` when `high` is under the
# standard, `"at or above"` when `low` is at or above it, `"depends on the assumption"` otherwise.

# %%
def district_range(sizes: dict) -> pd.DataFrame:
    # BEGIN SOLUTION
    d = pd.DataFrame({name: G.estimate(h, s, "district_id") for name, s in sizes.items()})
    t = pd.DataFrame({"low": d.min(axis=1), "high": d.max(axis=1)})
    t["verdict"] = "depends on the assumption"
    t.loc[t.high < G.STANDARD, "verdict"] = "below"
    t.loc[t.low >= G.STANDARD, "verdict"] = "at or above"
    return t
    # END SOLUTION


# %%
try:
    dr = district_range(sizes)
except NotImplementedError:
    dr = pd.DataFrame(G.reference("d3_3_districts")).set_index("district_id")
G.keep("d3_3_districts", dr.reset_index().to_dict("records"))
print(dr.verdict.value_counts().to_string(), "\n")
print(dr[dr.verdict != "at or above"].sort_values("high").to_string())
below = sorted(dr[dr.verdict == "below"].index)
G.check({"D07", "D15", "D22", "D26"} <= set(below), f"below the standard under every scenario: {', '.join(below)}")

# %% [markdown]
# ## 4 · Recommend an estimate, with its reason (5')
#
# ✏️ **Exercise** · Return the number of the paragraph you would send to the director.

# %%
OPTIONS = [
    f"Parcels per eligible household per month were {cc}. The network is below its standard of 2.",
    f"Parcels per eligible household per month were about {central} (between {plaus[0]} and {plaus[1]} under "
    f"different assumptions about the 18% of households with no recorded size). {len(below)} districts are below the "
    f"standard under every assumption; for {int((dr.verdict == 'depends on the assumption').sum())} the answer depends "
    f"on the assumption. We recommend the estimate that fills blank sizes from similar households, because blank sizes "
    f"are mostly large households and that method uses what the branches recorded about them.",
    f"The figure lies between {low} and {high}. Nothing more can be said until every household size is recorded.",
    f"Parcels per eligible household per month were {plaus[1]}, the highest value we could justify.",
]


def recommend() -> int:
    # BEGIN SOLUTION
    return 1
    # END SOLUTION


# %%
try:
    choice = recommend()
except NotImplementedError:
    choice = 1
print(OPTIONS[choice])
(G.lab_dir("D3_3") / "recommendation.txt").write_text(OPTIONS[1], encoding="utf-8")
G.check(choice == 1, "the recommendation gives an estimate, its range, what holds under every assumption, and a reason")

# %% [markdown]
# ## ✱ Stretch · The tipping point of one district
#
# Take one district whose verdict depends on the assumption. How many members would have to be added to the
# imputed sizes for it to cross the standard? Is that a size shift the audit makes believable?

# %%
def tipping_point(district: str) -> pd.Series:
    # BEGIN SOLUTION
    blank = h.household_size.isna()
    out = {}
    for delta in range(-2, 5):
        s = base.where(~blank, (base + delta).clip(lower=1))
        out[delta] = G.estimate(h, s, "district_id")[district]
    return pd.Series(out, name=district)
    # END SOLUTION


try:
    undecided = dr[dr.verdict == "depends on the assumption"].index
    print(tipping_point(undecided[0]).to_string())
except NotImplementedError:
    print("✱ Stretch not attempted")

# %% [markdown]
# ## Verification note
#
# The last step of every lab: what this run verified, and what the lab did not verify. The cell writes
# `artifacts/D3_3/verification.md`. Read the last line and add one of your own.

# %%
note = G.verification_note("D3_3", "anything that was not varied: the nine days of B12 without rows and sizes recorded wrong are outside the range")

# %% [markdown]
# ## Checkpoint
#
# 1. The logical bounds straddle the standard. Are they useless?
#    <details><summary>Answer</summary>No: they are the only statement that needs no assumption, and they show what
#    the missing sizes could do at worst. They are too wide to act on, which is why you add assumptions, openly.</details>
# 2. Why shift only the imputed sizes?
#    <details><summary>Answer</summary>The recorded sizes are data; the imputed ones are your guess. A sensitivity
#    analysis varies the guess. (Whether recorded sizes are right is Lab 3.4.)</details>
# 3. A district is "below" under one scenario and "at or above" under another. What does the report say?
#    <details><summary>Answer</summary>That it cannot be classified with these data, with both values. Acting on one
#    of them would be acting on an artefact of the imputation.</details>
#
# **Carry forward.** `artifacts/D3_3/recommendation.txt`: with the comparison table of Lab 3.2, the evidence of LO5.
