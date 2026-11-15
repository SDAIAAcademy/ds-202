# %% [markdown]
# # Lab 2.3 · 300 records without a key
#
# Day 2 · Session 3 (Matching without a clean key) · 25 min.
#
# During Ramadan a satellite point of branches B04 and B05 handed out parcels and wrote 300 records on paper:
# a name, sometimes a phone, a district. No household id. To count those handouts you must find each person in
# the register, by name. Two errors are possible and they do not cost the same: a **missed match** leaves a
# handout uncounted; a **false match** gives one family the handout of another. Staff labelled 848 candidate
# pairs by hand; you use them to measure both errors before trusting any threshold.
#
# **AI-tutor**, hinting only. The threshold and its justification are yours.
#
# **Reference state.** `data/raw/match/walkin_300.csv`, `labelled_pairs.csv`, and the cleaned register of the
# two branches (`B.clean_registry`, the reference step of Lab 2.1).
#
# **Tasks**
# - [ ] 1 · Normalise and block (5')
# - [ ] 2 · Score the candidate pairs (6')
# - [ ] 3 · False matches at three thresholds (7')
# - [ ] 4 · Add the phone, measure again, choose (7')
# - [ ] ✱ Stretch · The review queue

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
from rapidfuzz import fuzz
import ghilal as G
import build_dataset as B   # the reference build: its steps are the safety nets of this lab

walk = pd.read_csv(G.RAW / "match" / "walkin_300.csv", dtype=str, keep_default_na=False)
labelled = pd.read_csv(G.RAW / "match" / "labelled_pairs.csv", dtype=str)
households, _ = B.clean_registry(G.registry_text())
pool = households[households.branch_id.isin(["B04", "B05"]) & (households.status == "active")]
pool = pool[["household_id", "head_name", "phone", "district_id"]].reset_index(drop=True)
print(walk.head(4).to_string(index=False))
print(f"{len(walk)} walk-in records | {len(pool):,} households of B04 and B05 | "
      f"{len(labelled)} labelled pairs, {int((labelled.is_match == '1').sum())} of them true matches")

# %% [markdown]
# ## 1 · Normalise and block (5')
#
# Comparing every walk-in with every household is 300 × 4,937 pairs. **Blocking** compares only pairs that agree
# on something reliable. Here the district was ticked on the form, not typed. The price of a block: a true pair
# that disagrees on the blocking field is never compared at all.
#
# ✏️ **Exercise** · Write `candidates(walk, pool)`: every pair of a walk-in and a household of the **same
# district**, with the name keys `key_w` and `key_r` (use `B.norm_name`) and both phones.

# %%
def candidates(walk: pd.DataFrame, pool: pd.DataFrame) -> pd.DataFrame:
    # BEGIN SOLUTION
    w = walk.assign(key_w=walk.name.map(B.norm_name)).rename(columns={"phone": "phone_w"})
    r = pool.assign(key_r=pool.head_name.map(B.norm_name)).rename(columns={"phone": "phone_r"})
    return w[["walkin_id", "district_id", "key_w", "phone_w"]].merge(
        r[["household_id", "district_id", "key_r", "phone_r"]], on="district_id")
    # END SOLUTION


# %%
# Check, with a safety net: the cells below still run when the exercise is not done yet
def _candidates(walk, pool):
    w = walk.assign(key_w=walk.name.map(B.norm_name)).rename(columns={"phone": "phone_w"})
    r = pool.assign(key_r=pool.head_name.map(B.norm_name)).rename(columns={"phone": "phone_r"})
    return w[["walkin_id", "district_id", "key_w", "phone_w"]].merge(
        r[["household_id", "district_id", "key_r", "phone_r"]], on="district_id")


try:
    cand = candidates(walk, pool)
except NotImplementedError:
    cand = _candidates(walk, pool)
true_pairs = labelled[labelled.is_match == "1"]
kept = true_pairs.merge(cand[["walkin_id", "household_id"]], on=["walkin_id", "household_id"])
print(f"{len(cand):,} candidate pairs instead of {len(walk) * len(pool):,}")
G.check(len(kept) == len(true_pairs), f"the block keeps all {len(true_pairs)} true pairs that staff labelled")

# %% [markdown]
# ## 2 · Score the candidate pairs (6')
#
# `fuzz.token_sort_ratio(a, b)` from RapidFuzz sorts the words of each name, then measures how similar the two
# strings are, from 0 to 100. It forgives a swapped letter; it does not forgive a missing father's name.
#
# ✏️ **Exercise** · Write `name_score(a, b)` and look at a few pairs.

# %%
def name_score(a: str, b: str) -> float:
    # BEGIN SOLUTION
    return fuzz.token_sort_ratio(a, b)
    # END SOLUTION


# %%
try:
    cand["score"] = [name_score(a, b) for a, b in zip(cand.key_w, cand.key_r)]
except NotImplementedError:
    cand["score"] = [fuzz.token_sort_ratio(a, b) for a, b in zip(cand.key_w, cand.key_r)]
lab = labelled.merge(cand, on=["walkin_id", "household_id"])
print(lab.sort_values("score", ascending=False).groupby("is_match").head(3)[["key_w", "key_r", "score", "is_match"]]
      .to_string(index=False))
G.check(lab[lab.is_match == "1"].score.mean() > lab[lab.is_match == "0"].score.mean(),
        f"true pairs score {lab[lab.is_match == '1'].score.mean():.0f} on average, the others {lab[lab.is_match == '0'].score.mean():.0f}")

# %% [markdown]
# ## 3 · False matches at three thresholds (7')
#
# Call a pair a match when its score reaches a threshold. On the labelled pairs you can count what that costs.
#
# - **false-match rate** = wrong pairs among the pairs you accepted
# - **missed** = true pairs you did not accept
#
# ✏️ **Exercise** · Write `evaluate(accepted)`: given a True/False column over `lab`, return
# `(accepted, false, false_rate, missed)`, the rate rounded to 3 decimals.

# %%
def evaluate(accepted: pd.Series) -> tuple:
    # BEGIN SOLUTION
    tp = int((accepted & (lab.is_match == "1")).sum())
    fp = int((accepted & (lab.is_match == "0")).sum())
    return tp + fp, fp, round(fp / max(tp + fp, 1), 3), int((lab.is_match == "1").sum()) - tp
    # END SOLUTION


# %%
def _evaluate(accepted):
    tp = int((accepted & (lab.is_match == "1")).sum())
    fp = int((accepted & (lab.is_match == "0")).sum())
    return tp + fp, fp, round(fp / max(tp + fp, 1), 3), int((lab.is_match == "1").sum()) - tp


rows = []
for t in (70, 85, 95):
    try:
        rows.append((f"name ≥ {t}", *evaluate(lab.score >= t)))
    except NotImplementedError:
        rows.append((f"name ≥ {t}", *_evaluate(lab.score >= t)))
table = pd.DataFrame(rows, columns=["rule", "accepted", "false", "false_rate", "missed"])
print(table.to_string(index=False))
G.check(table.false_rate.is_monotonic_decreasing and table.missed.is_monotonic_increasing,
        "a higher threshold: fewer false matches, more missed ones. No threshold gives both")

# %% [markdown]
# 🔍 Even at 95 some accepted pairs are the wrong family, and more than half of the true pairs are missed. Two people of the same first and family name differ only in a father's name that the walk-in form often
# left out. The name alone cannot separate them, at any threshold.

# %% [markdown]
# ## 4 · Add the phone, measure again, choose (7')
#
# A second field breaks the trade. Accept a pair when the names are roughly alike **and** the phones agree on at
# least nine of ten digits (one mistyped digit is forgiven).
#
# ✏️ **Exercise** · Write `phone_agrees(a, b)`, then choose the rule you would run automatically.

# %%
def phone_agrees(a: str, b: str) -> bool:
    # BEGIN SOLUTION
    a, b = B.norm_phone(a), B.norm_phone(b)
    return len(a) == 10 and len(b) == 10 and sum(x == y for x, y in zip(a, b)) >= 9
    # END SOLUTION


# %%
def _phone(a, b):
    a, b = B.norm_phone(a), B.norm_phone(b)
    return len(a) == 10 and len(b) == 10 and sum(x == y for x, y in zip(a, b)) >= 9


try:
    lab["phone_ok"] = [phone_agrees(a, b) for a, b in zip(lab.phone_w, lab.phone_r)]
except NotImplementedError:
    lab["phone_ok"] = [_phone(a, b) for a, b in zip(lab.phone_w, lab.phone_r)]
loose = pd.Series([fuzz.token_set_ratio(a, b) >= 70 for a, b in zip(lab.key_w, lab.key_r)], index=lab.index)
rows.append(("names alike and phone agrees", *_evaluate(loose & lab.phone_ok)))
table = pd.DataFrame(rows, columns=["rule", "accepted", "false", "false_rate", "missed"])
print(table.to_string(index=False))
table.to_csv(G.lab_dir("D2_3") / "threshold_table.csv", index=False)
G.keep("d2_3_table", table.to_dict("records"))
last = table.iloc[-1]
G.check(last.false == 0 and last.accepted > 150,
        f"with the phone: {int(last.accepted)} pairs accepted, {int(last.false)} false; {int(last.missed)} left for review by a person")

# %% [markdown]
# The rule to run automatically is the last one: no false match on the labelled pairs. The pairs it misses are
# mostly walk-ins who gave no phone. They go to a review queue for a person; they are not forced through a lower
# threshold. Zero false matches on 848 labelled pairs is not zero in general: say how it was measured.

# %% [markdown]
# ## ✱ Stretch · The review queue
#
# Apply the chosen rule to **all** candidate pairs. How many walk-ins are matched to exactly one household, how
# many to more than one, and how many to none?

# %%
def review_queue() -> pd.Series:
    # BEGIN SOLUTION
    ok = [fuzz.token_set_ratio(a, b) >= 70 and _phone(p, q)
          for a, b, p, q in zip(cand.key_w, cand.key_r, cand.phone_w, cand.phone_r)]
    n = cand[ok].groupby("walkin_id").size().reindex(walk.walkin_id, fill_value=0)
    return n.map(lambda k: "one household" if k == 1 else "none: review" if k == 0 else "several: review").value_counts()
    # END SOLUTION


try:
    print(review_queue().to_string())
except NotImplementedError:
    print("✱ Stretch not attempted")

# %% [markdown]
# ## Checkpoint
#
# 1. Why measure on labelled pairs, and not on how many matches a threshold finds?
#    <details><summary>Answer</summary>A count of matches says nothing about whether they are right. Only pairs that
#    a person judged tell you the false-match rate.</details>
# 2. Why is a false match worse than a missed one here?
#    <details><summary>Answer</summary>A missed match is visible (a record with no household) and can be reviewed. A
#    false match looks like a success and moves parcels from one family's record to another's.</details>
# 3. What did blocking on the district assume?
#    <details><summary>Answer</summary>That the district on the paper form equals the district in the register. A
#    true pair that disagrees there is never compared; the check on the labelled pairs is what told you none was lost.</details>
#
# **Carry forward.** `artifacts/D2_3/threshold_table.csv`. Larger jobs use a probabilistic linkage tool
# (Splink is one), which estimates such weights from the data; the measurement on labelled pairs stays the same.
