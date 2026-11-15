# %% [markdown]
# # Lab 3.2 · Three estimates of one number
#
# Day 3 · Session 2 (Imputation and its cost) · 25 min.
#
# The headline: parcels per eligible household per month in the third quarter of 2026. A household is eligible
# when its monthly income per member is at most 1,000 SAR, and household size is blank for 18% of the population.
# You compute the headline three ways (complete cases, the median size, the median size of similar households)
# and see that each way is an assumption about the households you cannot classify.
#
# **AI-off** for the first attempt at each estimate.
#
# **Reference state.** `G.households_q3()`: one row per household of the target population, with
# `household_size` (blank for 18%), `monthly_income_sar`, `parcels_q3` and `usual_parcels`, the number of
# parcels the household usually receives per handout.
#
# **Tasks**
# - [ ] 1 · The complete-case estimate (5')
# - [ ] 2 · Impute the median (5')
# - [ ] 3 · Impute within groups (8')
# - [ ] 4 · The comparison table, overall and by district (7')
# - [ ] ✱ Stretch · Draw a donor at random, twenty times

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
print(h.head(4).to_string(index=False))
print(f"{len(h):,} households | size missing: {h.household_size.isna().sum():,} ({h.household_size.isna().mean():.1%})"
      f" | standard: {G.STANDARD} parcels per eligible household per month")

# %% [markdown]
# ## 1 · The complete-case estimate (5')
#
# ✏️ **Exercise** · Write `estimate(df, size)`: among the households of `df` whose `size` is known and whose
# income per member is at most 1,000 SAR, the sum of `parcels_q3` divided by the number of those households,
# divided by 3 months. Round to 3 decimals. `size` is a column aligned with `df`.

# %%
def estimate(df: pd.DataFrame, size: pd.Series) -> float:
    # BEGIN SOLUTION
    eligible = (df.monthly_income_sar / size.astype("Float64")) <= G.THRESHOLD_SAR
    e = df[eligible.fillna(False).to_numpy()]
    return round(float(e.parcels_q3.sum() / len(e) / 3), 3)
    # END SOLUTION


# %%
# Check, with a safety net: the cells below still run when the exercise is not done yet
try:
    cc = estimate(h, h.household_size)
except NotImplementedError:
    estimate = G.estimate
    cc = estimate(h, h.household_size)
known = h.household_size.notna()
print(f"complete cases: {cc} parcels per eligible household per month, from {int(known.sum()):,} households;"
      f" {int((~known).sum()):,} households take no part in it")
G.check(cc == G.estimate(h, h.household_size), f"complete-case estimate {cc}: below the standard of {G.STANDARD}")

# %% [markdown]
# Complete-case analysis is not "no assumption". It assumes the 6,461 households it drops are like the ones it
# keeps. Lab 3.1 showed they are not: they are larger.
#
# ## 2 · Impute the median (5')
#
# ✏️ **Exercise** · Write `impute_median(h)`: the size column with every blank replaced by the median of the
# recorded sizes.

# %%
def impute_median(h: pd.DataFrame) -> pd.Series:
    # BEGIN SOLUTION
    return h.household_size.fillna(int(h.household_size.median())).astype(int)
    # END SOLUTION


# %%
try:
    size_med = impute_median(h)
except NotImplementedError:
    size_med = h.household_size.fillna(int(h.household_size.median())).astype(int)
med = estimate(h, size_med)
print(f"median size: {int(h.household_size.median())} | estimate with the median imputed: {med}")
G.check(size_med.notna().all() and med == G.estimate(h, size_med), f"median imputation: {med}")

# %% [markdown]
# Every household is now classified, and the households whose size was blank all have 5 members. Those with an
# income between 5,000 and 7,000 SAR and seven members in reality are now "not eligible".
#
# ## 3 · Impute within groups (8')
#
# A better guess uses something recorded that is related to the missing value. The branch desk hands out 1, 2
# or 3 parcels per visit according to the family card: `usual_parcels` carries information about the size.

# %%
print(h.groupby(h.usual_parcels.fillna(0).astype(int)).household_size.agg(["count", "median", "min", "max"]).to_string())

# %% [markdown]
# ✏️ **Exercise** · Write `impute_within_groups(h)`: each blank replaced by the median recorded size of the
# households with the same `usual_parcels` (treat a household with no handout at all as group 0).

# %%
def impute_within_groups(h: pd.DataFrame) -> pd.Series:
    # BEGIN SOLUTION
    group = h.usual_parcels.fillna(0).astype(int)
    med = h.household_size.groupby(group).median().round().astype(int)
    return h.household_size.fillna(group.map(med)).astype(int)
    # END SOLUTION


# %%
try:
    size_grp = impute_within_groups(h)
except NotImplementedError:
    size_grp = G.impute_within_groups(h)
grp = estimate(h, size_grp)
print("imputed sizes of the blank households:\n" + size_grp[~known].value_counts().sort_index().to_string())
G.check(grp == G.estimate(h, G.impute_within_groups(h)) and grp > cc, f"imputation within groups: {grp}")

# %% [markdown]
# ## 4 · The comparison table, overall and by district (7')
#
# The director will act on districts, not on the network average.
#
# ✏️ **Exercise** · Write `by_district(size)`: the estimate per district as a Series (reuse the logic of
# `estimate` with a group-by), rounded to 3 decimals.

# %%
def by_district(size: pd.Series) -> pd.Series:
    # BEGIN SOLUTION
    eligible = ((h.monthly_income_sar / size.astype("Float64")) <= G.THRESHOLD_SAR).fillna(False).to_numpy()
    e = h[eligible]
    return (e.groupby("district_id").parcels_q3.sum() / e.groupby("district_id").size() / 3).round(3)
    # END SOLUTION


# %%
try:
    d = pd.DataFrame({"complete_case": by_district(h.household_size), "median": by_district(size_med),
                      "within_groups": by_district(size_grp)})
except NotImplementedError:
    d = pd.DataFrame({"complete_case": G.estimate(h, h.household_size, "district_id"),
                      "median": G.estimate(h, size_med, "district_id"),
                      "within_groups": G.estimate(h, size_grp, "district_id")})
table = pd.DataFrame({"estimate": [cc, med, grp], "districts_below_standard": (d < G.STANDARD).sum().to_list()},
                     index=["complete case", "median imputed", "imputed within groups"])
print(table.to_string(), "\n")
flip = d[(d < G.STANDARD).any(axis=1) & (d >= G.STANDARD).any(axis=1)]
print("districts whose side of the standard depends on the method:\n" + flip.to_string())
table.to_csv(G.lab_dir("D3_2") / "comparison.csv")
G.keep("d3_2_table", table.reset_index().to_dict("records"))
G.keep("d3_2_flip", flip.reset_index().to_dict("records"))
G.check(len(flip) >= 3, f"{len(flip)} districts are above or below the standard depending on the method")

# %% [markdown]
# 🔍 The data is synthetic, so one thing can be shown here that real work never shows. The generator knows the size
# every household **would have reported** had the form let it. Compare the three estimates with the value that
# complete data would have given.

# %%
sealed = h.merge(G.sealed(), on="household_id", validate="one_to_one")
full = G.estimate(sealed, sealed.size_as_reported)
reveal = table.assign(distance_from_complete_data=(table.estimate - full).round(3))
print(f"with no size missing, the estimate would be {full}")
print(reveal[["estimate", "distance_from_complete_data"]].to_string())
G.keep("d3_2_full", full)

# %% [markdown]
# Imputation within groups lands closest, because it used a recorded field that carries information about the
# missing one. In real work you do not get this cell. You get Lab 3.3: a range.

# %% [markdown]
# ## ✱ Stretch · Draw a donor at random, twenty times
#
# A median puts every blank household of a group at one size. A **hot deck** gives each blank the size of a
# randomly drawn recorded household of the same group. Do it twenty times: how much does the estimate vary?

# %%
def hot_deck(runs: int = 20) -> tuple:
    # BEGIN SOLUTION
    rng = np.random.default_rng(7)
    group = h.usual_parcels.fillna(0).astype(int)
    out = []
    for _ in range(runs):
        s = h.household_size.astype("Float64").copy()
        for g, idx in h[~known].groupby(group[~known]).groups.items():
            donors = h.household_size[known & (group == g)].to_numpy()
            s.loc[idx] = rng.choice(donors, size=len(idx))
        out.append(estimate(h, s))
    return round(float(np.mean(out)), 3), round(float(np.min(out)), 3), round(float(np.max(out)), 3)
    # END SOLUTION


try:
    print("hot deck: mean, lowest and highest of the runs:", hot_deck(G.pick(20, 5)))
except NotImplementedError:
    print("✱ Stretch not attempted")

# %% [markdown]
# ## Verification note
#
# The last step of every lab: what this run verified, and what the lab did not verify. The cell writes
# `artifacts/D3_2/verification.md`. Read the last line and add one of your own.

# %%
note = G.verification_note("D3_2", "which method is closest in real work: here the generator could tell; a real register cannot")

# %% [markdown]
# ## Checkpoint
#
# 1. Complete-case analysis changes no value. Why is it still an assumption?
#    <details><summary>Answer</summary>It assumes the dropped households resemble the kept ones. Here they are larger,
#    more often eligible and receive more parcels, so the estimate is too low.</details>
# 2. Why does the median do little better than dropping the rows?
#    <details><summary>Answer</summary>It gives every blank household a size of 5, while most are 7 or more. Many of
#    them stay classified as not eligible.</details>
# 3. Imputing from `usual_parcels` uses the outcome to fill a predictor. Is that a mistake?
#    <details><summary>Answer</summary>No. An imputation should use everything related to the missing value, the
#    outcome included; leaving it out weakens the very relation you want to estimate.</details>
#
# **Carry forward.** `artifacts/D3_2/comparison.csv`: the comparison table of LO5. Lab 3.3 adds the range.
