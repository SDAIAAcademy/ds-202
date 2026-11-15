# %% [markdown]
# # Lab 3.1 · Six gaps, six mechanisms
#
# Day 3 · Session 1 (Why data go missing) · 25 min.
#
# Before deciding what to do about a blank, find out why it is blank. Three mechanisms:
#
# - **MCAR**, missing completely at random: the blank is unrelated to anything.
# - **MAR**, missing at random *given what is recorded*: the blank depends on fields you can see (a branch, a date).
# - **MNAR**, missing not at random: the blank depends on the missing value itself.
#
# You collect evidence for six gaps in the sources of Ghilal Food Bank Network, classify each, and say in which
# direction it pushes one named statistic. This is the evidence of outcome LO1: five of six correct.
#
# **AI-off.** The classification is a judgment from evidence; make it yourself.
#
# **Reference state.** `G.households_q3()`: the 35,665 households of the target population. The register, the
# logs, the audit of 600 home visits and the source notes in `data/docs/`.
#
# **Tasks**
# - [ ] 1 · Where household sizes are missing (7')
# - [ ] 2 · What the audit shows (5')
# - [ ] 3 · Three gaps in the logs and the API (6')
# - [ ] 4 · Classify the six and give the direction of bias (7')
# - [ ] ✱ Stretch · Why no test on the recorded data can rule out MNAR

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
import build_dataset as B   # the reference build: its steps prepare the logs for this lab

h = G.households_q3()
h["size_missing"] = h.household_size.isna()
print(f"{len(h):,} households | household_size missing: {h.size_missing.mean():.1%}")

# %% [markdown]
# ## 1 · Where household sizes are missing (7')
#
# If blanks were completely at random, the missing rate would be about the same in every group you can form.
#
# ✏️ **Exercise** · Write `missing_rate(df, by)`: the share of rows with `size_missing`, per group, rounded to 3
# decimals, as a Series.

# %%
def missing_rate(df: pd.DataFrame, by) -> pd.Series:
    # BEGIN SOLUTION
    return df.groupby(by)["size_missing"].mean().round(3)
    # END SOLUTION


# %%
# Check, with a safety net: the cells below still run when the exercise is not done yet
try:
    by_channel = missing_rate(h, "channel")
except NotImplementedError:
    missing_rate = lambda df, by: df.groupby(by)["size_missing"].mean().round(3)  # noqa: E731
    by_channel = missing_rate(h, "channel")
h["period"] = (h.registered_on < "2025-03-01").map({True: "before March 2025", False: "from March 2025"})
by_branch = missing_rate(h[h.channel == "branch"], ["branch_id", "period"]).unstack()
print(by_channel.to_string(), "\n")
print(by_branch.loc[["B01", "B03", "B07", "B11"]].to_string())
G.keep("d3_1_rates", {"channel": by_channel.to_dict(), "old_form": by_branch.loc[["B03", "B11"]].round(3).to_dict()})
G.check(by_channel["phone"] > 3 * by_channel["branch"] and by_branch.loc["B03", "before March 2025"] > 0.3,
        "sizes are missing far more often by phone and online, and at B03 and B11 before March 2025")

# %% [markdown]
# 🔍 Two different patterns in one column. Read `data/docs/register_notes.md` again: which two limits explain them?
# Now look at the sizes that **are** recorded, by channel.

# %%
big = h[~h.size_missing].assign(seven_plus=lambda d: d.household_size >= 7).groupby("channel").seven_plus.mean().round(3)
print("share of recorded sizes that are 7 or more:\n" + big.to_string())

# %% [markdown]
# ## 2 · What the audit shows (5')
#
# The register cannot tell you the size of a household whose size is blank. The audit can, for 600 households:
# the registration team visited them in September 2026 and verified the size.
#
# ✏️ **Exercise** · Write `audit_table()`: join the audit to `h` and return, for households with and without a
# recorded size, the number audited, the mean verified size and the share with 7 members or more.

# %%
audit = G.audit()


def audit_table() -> pd.DataFrame:
    # BEGIN SOLUTION
    a = audit.merge(h[["household_id", "size_missing"]], on="household_id", validate="one_to_one")
    return a.groupby("size_missing").verified_size.agg(
        audited="size", mean_size="mean", share_7_plus=lambda s: (s >= 7).mean()).round(2)
    # END SOLUTION


# %%
try:
    at = audit_table()
except NotImplementedError:
    at = pd.DataFrame(G.reference("d3_1_audit")).set_index("size_missing")
    at.index = at.index.astype(bool)
G.keep("d3_1_audit", at.reset_index().to_dict("records"))
print(at.to_string())
G.check(at.loc[True, "mean_size"] > at.loc[False, "mean_size"] + 1,
        f"households with a blank size have {at.loc[True, 'mean_size']} members on average, the others {at.loc[False, 'mean_size']}")

# %% [markdown]
# The blank sizes are, on average, larger: the value itself decides whether it is missing. No table of the
# recorded data alone could have shown that. It took data from outside.

# %% [markdown]
# ## 3 · Three gaps in the logs and the API (6')
#
# Missing data is not only blank cells of one column.

# %%
logs = G.logs_raw().drop_duplicates()
logs["date"] = B.parse_dates(logs)
blank_w = logs[logs.weight == ""]
print("blank weights:", len(blank_w), "| branches:", list(blank_w.branch_id.unique()),
      "|", blank_w.date.min().date(), "to", blank_w.date.max().date())

# %% [markdown]
# ✏️ **Exercise** · Write `empty_days(logs, branch)`: the days between 1 January and 30 September 2026 on which
# that branch has no log row at all.

# %%
def empty_days(logs: pd.DataFrame, branch: str) -> list:
    # BEGIN SOLUTION
    days = pd.date_range("2026-01-01", "2026-09-30")
    seen = set(logs.loc[logs.branch_id == branch, "date"])
    return [d for d in days if d not in seen]
    # END SOLUTION


# %%
try:
    gaps = {b: empty_days(logs, b) for b in G.BRANCHES}
except NotImplementedError:
    days = pd.date_range("2026-01-01", "2026-09-30")
    seen = {b: set(logs.loc[logs.branch_id == b, "date"]) for b in G.BRANCHES}
    gaps = {b: [d for d in days if d not in seen[b]] for b in G.BRANCHES}
gaps = {b: v for b, v in gaps.items() if v}
print({b: (str(v[0].date()), str(v[-1].date()), len(v)) for b, v in gaps.items()})
G.check(list(gaps) == ["B12"] and len(gaps["B12"]) == 9, "one branch, B12, has nine days in August with no row at all")

# %%
import gzip, json
don = pd.DataFrame(json.loads(line) for line in gzip.open(G.RAW / "donations" / "donations.jsonl.gz", "rt", encoding="utf-8"))
print("donor_type:\n" + don.donor_type.fillna("(null)").value_counts(normalize=True).round(3).to_string())
print("\nfrom the source note: donor_type is null when an individual donor asked to stay anonymous")

# %% [markdown]
# ## 4 · Classify the six and give the direction of bias (7')
#
# For each scenario: the mechanism (`"MCAR"`, `"MAR"` or `"MNAR"`) and what happens to the named statistic when
# it is computed from the recorded data as they are (`"none"`, `"too low"` or `"too high"`).
#
# | | Gap | Statistic computed from the recorded data |
# |---|---|---|
# | 1 | `phone` is blank for about 3% of registrations, evenly everywhere | mean household size of households with a phone |
# | 2 | `household_size` is blank at B03 and B11 before March 2025 (paper form without the field) | number of eligible households counted at B03 and B11 |
# | 3 | `household_size` is blank for large households on the phone and online channels | mean household size |
# | 4 | `weight` is blank at B09 from 4 to 17 May (scale away) | kilograms handed out by B09 in May |
# | 5 | B12 sent no rows for nine days of August | parcels per household in the quarter, districts served by B12 |
# | 6 | `donor_type` is null for individuals who asked to stay anonymous | share of retailers among donations with a recorded type |
#
# ✏️ **Exercise** · Return the dictionary.

# %%
def classify() -> dict:
    # BEGIN SOLUTION
    return {1: ("MCAR", "none"), 2: ("MAR", "too low"), 3: ("MNAR", "too low"),
            4: ("MAR", "too low"), 5: ("MAR", "too low"), 6: ("MNAR", "too high")}
    # END SOLUTION


# %%
KEY = {1: ("MCAR", "none"), 2: ("MAR", "too low"), 3: ("MNAR", "too low"),
       4: ("MAR", "too low"), 5: ("MAR", "too low"), 6: ("MNAR", "too high")}
try:
    mine = {int(k): tuple(v) for k, v in classify().items()}
except NotImplementedError:
    mine = {}
right = sum(mine.get(k) == v for k, v in KEY.items())
if not mine:
    print("Not answered yet: fill classify() and run this cell again.")
else:
    for k, v in KEY.items():
        print(k, "✅" if mine.get(k) == v else "❌", mine.get(k, "not answered"))
    G.check(right >= 5, f"{right} of 6 scenarios with the right mechanism and direction (LO1 asks for five)")
phone_blank = G.registry_text().assign(blank=lambda d: d.phone == "").groupby("branch_id").blank.mean()
print(f"\nscenario 1, evidence: phone blank {phone_blank.min():.1%} to {phone_blank.max():.1%} across the 14 branches")

# %% [markdown]
# 🔍 Scenarios 2, 4 and 5 are MAR because the cause is a branch and a date, both recorded: within that branch
# and period the blank does not depend on the value. Scenario 5 differs in kind: whole rows are missing, so there
# is no blank cell to fill. Scenarios 3 and 6 are MNAR, and you learned it from an audit and from a source note,
# not from the data.

# %% [markdown]
# ## ✱ Stretch · Why no test on the recorded data can rule out MNAR
#
# Build two versions of a household-size column from the audit's verified sizes: one with blanks at random, one
# with blanks only for sizes of 7 or more. Make the two missing rates equal. Can you tell them apart using only
# the rows that are **not** blank and the missing rate?

# %%
def two_worlds() -> pd.DataFrame:
    # BEGIN SOLUTION
    s = audit.verified_size
    rate = (s >= 7).mean() * 0.8
    mnar = s.where(~((s >= 7) & (pd.Series(range(len(s))) % 5 != 0)))
    mcar = s.where(pd.Series(range(len(s))) % round(1 / rate) != 0)
    return pd.DataFrame({"world": ["blank at random", "blank when 7 or more"],
                         "missing_rate": [mcar.isna().mean(), mnar.isna().mean()],
                         "mean_of_recorded": [mcar.mean(), mnar.mean()], "true_mean": [s.mean(), s.mean()]}).round(2)
    # END SOLUTION


try:
    print(two_worlds().to_string(index=False))
except NotImplementedError:
    print("✱ Stretch not attempted")

# %% [markdown]
# ## Verification note
#
# The last step of every lab: what this run verified, and what the lab did not verify. The cell writes
# `artifacts/D3_1/verification.md`. Read the last line and add one of your own.

# %%
note = G.verification_note("D3_1", "the mechanism for households outside the audit: it is argued from 600 visits and the source note")

# %% [markdown]
# ## Checkpoint
#
# 1. A missing rate that differs between branches rules out which mechanism?
#    <details><summary>Answer</summary>MCAR. It does not tell MAR from MNAR: the blank may depend on the branch only,
#    or on the value as well.</details>
# 2. What told you that the sizes blank on the phone and online channels are large ones?
#    <details><summary>Answer</summary>The source note (the list stops at 6) and the audit (blank sizes average more
#    than 7 members). Knowledge of how the data were produced, and data from outside.</details>
# 3. Why is the B12 gap not repaired by imputing a field?
#    <details><summary>Answer</summary>There is no row to hold the field. The remedy is to ask Hazem for the nine
#    days, or to report the gap beside the figures of the districts B12 serves.</details>
#
# **Carry forward.** Your six classifications; Labs 3.2 and 3.3 act on scenarios 2 and 3.
