# %% [markdown]
# # Lab 1.4 · Who is not in the register
#
# Day 1 · Session 4 (Coverage and sampling frames) · 25 min.
#
# The register lists the households that registered. The question is about households in need. You compare the
# register, district by district, with the survey estimate of low-income households in the open table, and flag
# the districts where the register reaches less than half of them: a district can look well served only because
# the households nobody serves are in no file.
#
# **AI-off** for the first attempt.
#
# **Reference state.** `G.registry()`: the tables `registrations` and `districts_open` in an in-memory database.
#
# **Tasks**
# - [ ] 1 · Registered households per district, in SQL (5')
# - [ ] 2 · Join to the open table and find what does not match (7')
# - [ ] 3 · Coverage ratios and flags (8')
# - [ ] 4 · The coverage note (5')
# - [ ] ✱ Stretch · A second frame: all households

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

con = G.registry()
print(con.execute("SELECT * FROM districts_open LIMIT 3").df().to_string(index=False))

# %% [markdown]
# ## 1 · Registered households per district, in SQL (5')
#
# ✏️ **Exercise** · Write `registered()`: one row per district with `district_id` and `registered`, the number of
# distinct `household_id` whose status is active. (Distinct, because 180 ids are in the register twice.)

# %%
def registered() -> pd.DataFrame:
    # BEGIN SOLUTION
    return con.execute("""
        SELECT district_id, count(DISTINCT household_id) AS registered
        FROM registrations WHERE status = 'active'
        GROUP BY district_id ORDER BY district_id""").df()
    # END SOLUTION


# %%
# Check, with a safety net: the cells below still run when the exercise is not done yet
try:
    reg = registered()
except NotImplementedError:
    reg = pd.DataFrame(G.reference("d1_4_registered"))
G.keep("d1_4_registered", reg.to_dict("records"))
rt = G.registry_text()
n_active = rt[rt.status == "active"].household_id.nunique()
print(reg.head(4).to_string(index=False), "...")
G.check(len(reg) == 30 and int(reg.registered.sum()) == n_active,
        f"30 districts, {int(reg.registered.sum()):,} active registered households")

# %% [markdown]
# ## 2 · Join to the open table and find what does not match (7')
#
# A join between a list you hold and a frame from outside has three outcomes per row: in both, only in yours, only
# in theirs. An inner join shows you the first and silently drops the other two.
#
# ✏️ **Exercise** · Write `coverage_table(reg)`: a **full outer** join of `reg` with the open table on
# `district_id`, keeping `district_name_en`, `low_income_households_est` and a column `side` with the values
# `both`, `register only` or `frame only`.

# %%
frame = G.population()


def coverage_table(reg: pd.DataFrame) -> pd.DataFrame:
    # BEGIN SOLUTION
    t = reg.merge(frame[["district_id", "district_name_en", "low_income_households_est"]], on="district_id",
                  how="outer", validate="one_to_one", indicator="side")
    t["side"] = t["side"].map({"both": "both", "left_only": "register only", "right_only": "frame only"})
    return t.sort_values("district_id").reset_index(drop=True)
    # END SOLUTION


# %%
try:
    cov = coverage_table(reg)
except NotImplementedError:
    cov = reg.merge(frame[["district_id", "district_name_en", "low_income_households_est"]], on="district_id",
                    how="outer", indicator="side")
    cov["side"] = cov["side"].map({"both": "both", "left_only": "register only", "right_only": "frame only"})
print(cov.side.value_counts().to_string())
only = cov[cov.side == "register only"]
print(only[["district_id", "registered"]].to_string(index=False))
G.check(sorted(only.district_id) == ["D29", "D30"] and len(cov) == 30,
        f"D29 and D30 have {int(only.registered.sum()):,} registered households and no row in the frame")

# %% [markdown]
# ## 3 · Coverage ratios and flags (8')
#
# Coverage = registered households ÷ estimated low-income households. Flag a district `under-covered` below 0.50,
# `over 100%` above 1.00, `no frame` when the frame has no row, otherwise `ok`.
#
# ✏️ **Exercise** · Write `flag(cov)`: the table with the columns `coverage` (rounded to 2 decimals) and `flag`.

# %%
def flag(cov: pd.DataFrame) -> pd.DataFrame:
    # BEGIN SOLUTION
    t = cov.copy()
    t["coverage"] = (t["registered"] / t["low_income_households_est"]).round(2)
    t["flag"] = "ok"
    t.loc[t["coverage"] < 0.50, "flag"] = "under-covered"
    t.loc[t["coverage"] > 1.00, "flag"] = "over 100%"
    t.loc[t["low_income_households_est"].isna(), "flag"] = "no frame"
    return t
    # END SOLUTION


# %%
try:
    flagged = flag(cov)
except NotImplementedError:
    flagged = pd.DataFrame(G.reference("d1_4_flagged"))
G.keep("d1_4_flagged", flagged[["district_id", "district_name_en", "registered", "low_income_households_est",
                                "coverage", "flag"]].to_dict("records"))
show = flagged[flagged.flag != "ok"][["district_id", "district_name_en", "registered", "low_income_households_est",
                                      "coverage", "flag"]]
print(show.to_string(index=False))
print("coverage of the other districts:", flagged[flagged.flag == "ok"].coverage.min(), "to",
      flagged[flagged.flag == "ok"].coverage.max())
under = sorted(flagged[flagged.flag == "under-covered"].district_id)
G.check(under == ["D07", "D15", "D22", "D26"] and sorted(flagged[flagged.flag == "over 100%"].district_id) == ["D03"],
        "four districts under-covered, one above 100%, two without a frame")
flagged.to_csv(G.lab_dir("D1_4") / "coverage_by_district.csv", index=False)

# %% [markdown]
# 🔍 D03 is above 100%: more registered households than the frame says exist. Nothing in the register is wrong.
# The frame describes 2022, and the district has grown. A frame is an estimate with its own date and its own error.

# %% [markdown]
# ## 4 · The coverage note (5')
#
# The headline will be "parcels per **eligible registered** household". Which sentences belong under it?
#
# ✏️ **Exercise** · Return the numbers of the statements that are true and that a reader needs.

# %%
NOTES = ["The figure describes registered households only; in D07, D15, D22 and D26 fewer than half of the "
         "estimated low-income households are registered.",
         "Districts with low coverage are districts with low need.",
         "For D29 and D30 the share of households in need that are registered is unknown: the frame has no row.",
         "Coverage above 100% in D03 shows that the register contains fabricated households.",
         "The frame is a 2022 survey estimate; coverage ratios are approximate."]


def coverage_note() -> set:
    # BEGIN SOLUTION
    return {0, 2, 4}
    # END SOLUTION


# %%
try:
    chosen = set(coverage_note())
except NotImplementedError:
    chosen = {0, 2, 4}
for i in sorted(chosen):
    print("-", NOTES[i])
G.check(chosen == {0, 2, 4}, "three sentences go under the headline; two would mislead")

# %% [markdown]
# ## ✱ Stretch · A second frame: all households
#
# Registered households as a share of **all** households of the district. Which districts change rank, and why is
# this frame worse for this question?

# %%
def share_of_all() -> pd.DataFrame:
    # BEGIN SOLUTION
    t = reg.merge(frame[["district_id", "households"]], on="district_id")
    t["share_of_all"] = (t["registered"] / t["households"]).round(3)
    return t.sort_values("share_of_all").head(5)
    # END SOLUTION


try:
    print(share_of_all().to_string(index=False))
except NotImplementedError:
    print("✱ Stretch not attempted")

# %% [markdown]
# ## Checkpoint
#
# 1. Why a full outer join here, when Day 2 will insist on a join that loses nothing?
#    <details><summary>Answer</summary>Same principle: every row is accounted for. Here the rows that do not match
#    are the finding: two districts the frame does not know.</details>
# 2. A district has high parcels per registered household and coverage of 0.35. Is it well served?
#    <details><summary>Answer</summary>Its registered households are. Two thirds of its estimated low-income
#    households are outside the register and receive nothing that any file records.</details>
# 3. What kind of error is under-coverage, in the terms of Day 3?
#    <details><summary>Answer</summary>Missing units: whole households absent, and not at random. No imputation of a
#    field repairs it; it is reported beside the figure.</details>
#
# **Carry forward.** `artifacts/D1_4/coverage_by_district.csv`: a section of the quality report (Lab 4.4).
