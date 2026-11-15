# %% [markdown]
# # Lab 2.2 · A join that loses nothing
#
# Day 2 · Session 2 (Keys and cardinality) · 25 min.
#
# Every handout must find its household: many log rows to one register row. Three things can go wrong without
# any error message. A key typed by hand does not match and its row drops out. A household that is in the
# register twice doubles its handouts. And nobody notices, because nobody counted. You repair the keys by rule,
# test the cardinality before joining, and write a join log in which the rows add up.
#
# **AI-off** for the first attempt at the join.
#
# **Reference state.** `G.logs_raw()`: the 210,000 log rows as text. `G.registry_text()`: the register as text.
#
# **Tasks**
# - [ ] 1 · Repair the keys and name what cannot be repaired (8')
# - [ ] 2 · Test the cardinality before joining (5')
# - [ ] 3 · Join and reconcile (7')
# - [ ] 4 · The join log and the set-aside file (5')
# - [ ] ✱ Stretch · Handouts dated before the registration

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

import re
import pandas as pd
import ghilal as G
import build_dataset as B   # the reference build: its steps are the safety nets of this lab

raw = G.logs_raw()
reg = G.registry_text()
logs = raw.drop_duplicates().copy()
steps = [("log rows read", len(raw), "14 branch files"),
         ("exact copies dropped", len(logs), f"{len(raw) - len(logs)} rows whose every field, log_id included, repeats")]
print(steps)
print(raw[raw.duplicated(keep=False)].groupby("branch_id").handout_date.agg(["min", "max", "size"]))

# %% [markdown]
# A week of one branch was uploaded twice: the same `log_id` twice, every field equal. Those are copies of a
# record, not two handouts, and dropping them is safe **because** the id repeats. That step is done for you above.
#
# ## 1 · Repair the keys and name what cannot be repaired (8')
#
# A `household_id` is the letter H and six digits. Look at the ones that are not.

# %%
form = logs.household_id.str.fullmatch(r"H\d{6}")
print(f"{int((~form).sum()):,} keys are not in the form H + six digits; some of them:")
print(logs[~form].household_id.drop_duplicates().sample(8, random_state=3).map(repr).to_string(index=False))

# %% [markdown]
# Four habits of typing change the string and not the household: lower case, spaces around, a hyphen after the H,
# and the letter O for the digit 0. A rule may repair those, because it cannot change **which** household is meant.
# A blank cannot be repaired. Nothing may be "repaired" by picking a similar id from the register.
#
# ✏️ **Exercise** · Write `clean_key(k)`: strip spaces, upper-case, remove a hyphen; then, when the result is H
# followed by six characters that are digits or the letter O, turn each O into 0. Return anything else as it is
# after stripping.

# %%
def clean_key(k: str) -> str:
    # BEGIN SOLUTION
    c = k.strip().upper().replace("-", "")
    if re.fullmatch(r"H[0-9O]{6}", c):
        c = "H" + c[1:].replace("O", "0")
    return c
    # END SOLUTION


# %%
# Check, with a safety net: the cells below still run when the exercise is not done yet
tests = [("h482913", "H482913"), (" H482913  ", "H482913"), ("H-482913", "H482913"), ("H48O913", "H480913"), ("", "")]
try:
    ok = all(clean_key(a) == b for a, b in tests)
    key = logs.household_id.map(clean_key)
except NotImplementedError:
    ok = False
    key = logs.household_id.map(B.clean_key)
G.check(ok, "the four typing habits are repaired; a blank stays blank")
n_repaired = int((key != logs.household_id).sum())
logs["household_id_raw"], logs["household_id"] = logs.household_id, key
status = pd.Series("in the right form", index=logs.index)
status[logs.household_id != logs.household_id_raw] = "repaired by rule"
status[logs.household_id == ""] = "blank"
print(status.value_counts().to_string())
steps.append(("keys repaired", len(logs), f"{n_repaired} keys: case, spaces, hyphen, letter O"))
G.check(logs.household_id.str.fullmatch(r"H\d{6}|").all(), f"{n_repaired:,} keys repaired; every key is now H + six digits, or blank")

# %% [markdown]
# ## 2 · Test the cardinality before joining (5')
#
# Many handouts to **one** household: that is an assumption about the register, and it can be tested.

# %%
naive = logs.merge(reg, on="household_id", how="left")
print(f"left join without a test: {len(logs):,} log rows in, {len(naive):,} rows out ({len(naive) - len(logs):+,})")
try:
    logs.merge(reg, on="household_id", how="left", validate="many_to_one")
except pd.errors.MergeError as e:
    print("with validate='many_to_one':", e)

# %% [markdown]
# A left join never loses a left row, and it **adds** rows when a key matches twice on the right. The register
# holds 180 household ids twice (Lab 1.2): each of their handouts came out double. `validate="many_to_one"` makes
# the join refuse.
#
# The rule of the network: the first registration stands; a later registration of the same id at another branch
# is set aside and reported to the registration supervisor.
#
# ✏️ **Exercise** · Write `one_per_household(reg)`: the register with one row per `household_id`, the earliest
# `registered_on`, and the rows that were set aside.

# %%
def one_per_household(reg: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    # BEGIN SOLUTION
    r = reg.sort_values(["household_id", "registered_on"])
    later = r.duplicated("household_id", keep="first")
    return r[~later].reset_index(drop=True), r[later].reset_index(drop=True)
    # END SOLUTION


# %%
try:
    households, later = one_per_household(reg)
except NotImplementedError:
    r = reg.sort_values(["household_id", "registered_on"])
    households, later = r[~r.duplicated("household_id")], r[r.duplicated("household_id")]
G.check(households.household_id.is_unique and len(households) == 39_820 and len(later) == 180,
        "39,820 households, one row each; 180 later registrations set aside")

# %% [markdown]
# ## 3 · Join and reconcile (7')
#
# ✏️ **Exercise** · Write `join(logs, households)`: a left join on `household_id` that takes `district_id`,
# `registered_on` and `status` from the register, validated as many-to-one, with an indicator column `_merge`.

# %%
def join(logs: pd.DataFrame, households: pd.DataFrame) -> pd.DataFrame:
    # BEGIN SOLUTION
    cols = ["household_id", "district_id", "registered_on", "status"]
    return logs.merge(households[cols], on="household_id", how="left", validate="many_to_one", indicator=True)
    # END SOLUTION


# %%
try:
    j = join(logs, households)
except NotImplementedError:
    j = logs.merge(households[["household_id", "district_id", "registered_on", "status"]], on="household_id",
                   how="left", validate="many_to_one", indicator=True)
reason = pd.Series("", index=j.index)
reason[j.household_id == ""] = "blank key"
reason[(j["_merge"] == "left_only") & (j.household_id != "")] = "key not in the register"
matched, aside = j[reason == ""], j[reason != ""].assign(reason=reason[reason != ""])
print(aside.reason.value_counts().to_string())
G.check(len(j) == len(logs), f"rows out of the join = rows in: {len(j):,}")
G.check(len(matched) + len(aside) == len(logs), f"{len(matched):,} matched + {len(aside):,} set aside = {len(logs):,}")

# %% [markdown]
# ## 4 · The join log and the set-aside file (5')
#
# The join log is the evidence of this outcome: one line per step, and the lines add up. The set-aside rows go
# to a file with their reason, so the owner of the logs can repair the source. They are not deleted.

# %%
for name, n in aside.reason.value_counts().items():
    steps.append((f"set aside: {name}", int(n), "kept in set_aside.csv with the reason"))
steps.append(("log rows joined to a household", len(matched), "many handouts to one household, tested"))
join_log = pd.DataFrame(steps, columns=["step", "rows", "note"])
print(join_log.to_string(index=False))
out = G.lab_dir("D2_2")
join_log.to_csv(out / "join_log.csv", index=False)
aside[["log_id", "branch_id", "household_id_raw", "handout_date", "parcels", "reason"]].to_csv(out / "set_aside.csv", index=False)
G.keep("d2_2_join_log", join_log.to_dict("records"))
G.check(len(raw) == (len(raw) - len(logs)) + len(aside) + len(matched),
        f"210,000 read = {len(raw) - len(logs)} copies + {len(aside)} set aside + {len(matched):,} joined")
print(aside.groupby(["branch_id", "reason"]).size().unstack(fill_value=0).head(5))

# %% [markdown]
# 🔍 An unknown key is spread over all branches; it is a typing error that happens to give a well-formed id. What
# would have happened to these rows in an inner join? And to the 180 households in a join without the test?

# %% [markdown]
# ## ✱ Stretch · Handouts dated before the registration
#
# A key can be well formed, exist in the register and still be the wrong household. One sign: the handout is
# dated before the household registered. Parse the dates with the reference step and count.

# %%
def before_registration() -> int:
    # BEGIN SOLUTION
    d = B.parse_dates(matched)
    return int((d < pd.to_datetime(matched.registered_on)).sum())
    # END SOLUTION


try:
    print("handouts dated before the registration of their household:", before_registration())
except NotImplementedError:
    print("✱ Stretch not attempted")

# %% [markdown]
# ## Checkpoint
#
# 1. Why is turning the letter O into 0 allowed, and choosing the most similar id from the register not?
#    <details><summary>Answer</summary>In an id of H and six digits, an O can only be a mistyped 0: the rule cannot
#    change which household is meant. "Most similar" picks a household, and can pick the wrong one.</details>
# 2. The naive join returned more rows than it was given. Which check would have told you without counting?
#    <details><summary>Answer</summary>`validate="many_to_one"`: pandas tests that the key is unique on the right
#    and refuses to join when it is not.</details>
# 3. Why keep the set-aside rows in a file?
#    <details><summary>Answer</summary>They are handouts that happened. With their reason, the branch can correct the
#    key and the next build takes them in; deleted, they are a silent undercount.</details>
#
# **Carry forward.** `artifacts/D2_2/join_log.csv` and `set_aside.csv`: the evidence of LO3.
