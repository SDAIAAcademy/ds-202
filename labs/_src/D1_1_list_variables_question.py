# %% [markdown]
# # Lab 1.1 · The question before the files
#
# Day 1 · Session 1 (Start from the question, not the files) · 25 min.
#
# Sumayyah Al-Khudair, programmes director of Ghilal Food Bank Network, asks: *in the third quarter of 2026, how
# many parcels did an eligible household receive per month in each district, and which districts are below the
# standard of two?* You are Rimas Al-Sinani, the analyst. Before opening any file you take the question apart,
# list the variables it needs with one source field for each, and write down what you will not take.
#
# **AI-off.** This first attempt is yours; the reasoning is the outcome.
#
# **Reference state.** `data/docs/field_catalogue.csv`: every field of the four sources, with what it holds.
#
# **Tasks**
# - [ ] 1 · Take the question apart (5')
# - [ ] 2 · The fields the question needs (10')
# - [ ] 3 · The fields you will not take (5')
# - [ ] 4 · What no source provides (5')
# - [ ] ✱ Stretch · A second question, and what it adds

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
import pandas as pd
import ghilal as G

catalogue = pd.read_csv(G.DOCS / "field_catalogue.csv")
print(catalogue.groupby("source").size().to_string())
print(catalogue[catalogue.source == "register"].to_string(index=False))

# %% [markdown]
# ## 1 · Take the question apart (5')
#
# A question fixes four things before any data: the **unit** that is counted, the **population** of units, the
# **period**, and the **groups** the answer is split by. The eligibility rule of the network: a household is eligible
# when it is active and its monthly income per member is at most 1,000 SAR. To give every household the same three
# months, the population is the households registered before the quarter began.
#
# ✏️ **Exercise** · Return the four parts. `unit` is one of `"handout"`, `"household"`, `"person"`, `"district"`.

# %%
def question_parts() -> dict:
    # BEGIN SOLUTION
    return {"unit": "household",
            "population": "active households registered before 2026-07-01 whose income per member is at most 1000 SAR",
            "period": ["2026-07-01", "2026-09-30"],
            "groups": "district_id"}
    # END SOLUTION


# %%
# Check, with a safety net: the cells below still run when the exercise is not done yet
try:
    parts = question_parts()
except NotImplementedError:
    parts = G.reference("d1_1_parts")
G.keep("d1_1_parts", parts)
G.check(parts["unit"] == "household" and parts["period"] == ["2026-07-01", "2026-09-30"]
        and parts["groups"] == "district_id", "unit: household; period: the third quarter; groups: district")

# %% [markdown]
# ## 2 · The fields the question needs (10')
#
# Work backwards from the answer: *parcels per eligible household per month, by district*. Which fields make the
# numerator, which decide who is in the denominator, which link the two sources, and which place a household in a
# district?
#
# ✏️ **Exercise** · Return the list of `(source, field)` pairs you need, and nothing you cannot justify.

# %%
def needed_fields() -> list:
    # BEGIN SOLUTION
    return [("branch_logs", "household_id"), ("branch_logs", "handout_date"), ("branch_logs", "parcels"),
            ("register", "household_id"), ("register", "district_id"), ("register", "registered_on"),
            ("register", "status"), ("register", "household_size"), ("register", "monthly_income_sar"),
            ("open_population", "district_id"), ("open_population", "low_income_households_est")]
    # END SOLUTION


# %%
CORE = {("branch_logs", "household_id"), ("branch_logs", "handout_date"), ("branch_logs", "parcels"),
        ("register", "household_id"), ("register", "district_id"), ("register", "registered_on"),
        ("register", "status"), ("register", "household_size"), ("register", "monthly_income_sar")}
direct = set(map(tuple, catalogue.loc[catalogue.personal.isin(["direct identifier", "may hold personal data"]),
                                      ["source", "field"]].to_numpy()))
try:
    needed = set(map(tuple, needed_fields()))
except NotImplementedError:
    needed = set(map(tuple, G.reference("d1_1_needed")))
G.keep("d1_1_needed", sorted(needed))
print("beyond the core, to justify:", sorted(needed - CORE))
G.check(CORE <= needed, f"the nine core fields are all there (you listed {len(needed)})")
G.check(not (needed & direct), "no name, phone number, ID number or free text among them")

# %% [markdown]
# 🔍 The answer needs no name and no ID number: `household_id` links a handout to its household. A field that is
# not needed is not taken into the analysis dataset. That is the minimisation principle of the Personal Data
# Protection Law, applied at the first step, when it is cheapest.

# %% [markdown]
# ## 3 · The fields you will not take (5')
#
# ✏️ **Exercise** · Return a dictionary: each field that identifies a person directly, or may, with your reason
# for leaving it out, in a phrase.

# %%
def not_taken() -> dict:
    # BEGIN SOLUTION
    return {"national_id": "household_id already links the sources; the question needs no national identifier",
            "head_name": "no step of the answer uses a name",
            "phone": "nobody is contacted in this analysis",
            "collected_by": "who collected does not change the count of parcels",
            "note": "free text can hold anything about a person and is not used"}
    # END SOLUTION


# %%
try:
    left = not_taken()
except NotImplementedError:
    left = G.reference("d1_1_not_taken")
G.keep("d1_1_not_taken", left)
G.check({f for _, f in direct} <= set(left) and all(len(str(v)) > 10 for v in left.values()),
        f"{len(left)} fields left out, each with a reason")

# %% [markdown]
# ## 4 · What no source provides (5')
#
# Some things the question needs are in no file. Naming them now is cheaper than discovering them in the answer.
#
# ✏️ **Exercise** · Return the numbers of the statements below that are true gaps: needed, and in no source.

# %%
STATEMENTS = ["Households in need that never registered",
              "The number of parcels in a handout",
              "The verified size of every household",
              "The district of a registered household",
              "Low-income households in districts D29 and D30",
              "The date of a handout"]


def gaps() -> set:
    # BEGIN SOLUTION
    return {0, 2, 4}
    # END SOLUTION


# %%
try:
    g = set(gaps())
except NotImplementedError:
    g = set(G.reference("d1_1_gaps"))
G.keep("d1_1_gaps", sorted(g))
for i in sorted(g):
    print("gap:", STATEMENTS[i])
G.check(g == {0, 2, 4}, "three gaps: the unregistered, verified sizes, the two new districts")
out = G.lab_dir("D1_1") / "variables.json"
out.write_text(json.dumps({"question": parts, "needed": sorted(needed), "not_taken": left,
                           "gaps": [STATEMENTS[i] for i in sorted(g)]}, ensure_ascii=False, indent=1), encoding="utf-8")
print("written:", out.relative_to(G.LABS).as_posix())

# %% [markdown]
# ## ✱ Stretch · A second question
#
# Hazem Al-Sulaim asks for kilograms handed out per household member, by branch. Which fields does that add?

# %%
def second_question_adds() -> list:
    # BEGIN SOLUTION
    return [("branch_logs", "weight"), ("branch_logs", "unit"), ("register", "branch_id")]
    # END SOLUTION


try:
    print(second_question_adds())
except NotImplementedError:
    print("✱ Stretch not attempted")

# %% [markdown]
# ## Checkpoint
#
# 1. Why is the population "registered before the quarter began" and not "every active household"?
#    <details><summary>Answer</summary>A household that registered in September had one month to collect, not three.
#    Mixing exposures lowers the figure for districts with many new registrations.</details>
# 2. `household_size` is personal data. Why is it taken?
#    <details><summary>Answer</summary>Eligibility is income per member: without the size no household can be
#    classified. Minimisation removes what the purpose does not need, not what it does.</details>
# 3. The register cannot tell you about households that never registered. Which source can, partly?
#    <details><summary>Answer</summary>The open district table: its estimate of low-income households is a frame to
#    compare the register with (Lab 1.4).</details>
#
# **Carry forward.** `artifacts/D1_1/variables.json`: the variable list. Lab 4.4 comes back to it.
