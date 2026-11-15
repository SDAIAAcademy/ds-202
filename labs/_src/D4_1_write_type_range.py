# %% [markdown]
# # Lab 4.1 · Rules for the joined table
#
# Day 4 · Session 1 (Quality dimensions as rules) · 25 min.
#
# The joined table of the quarter has one row per handout with the fields of its household. Its data dictionary
# says what each column may hold. You turn the dictionary into rules that a program checks on **every** rebuild:
# type, completeness, range and validity, uniqueness. The suite must pass on the clean build and fail, readably,
# on a copy you break.
#
# **AI-off** for the first attempt at each rule; an **AI-tutor**, hinting only, may explain rule syntax.
#
# **Reference state.** `G.joined_q3()`: 73,264 handouts of the quarter, identifiers already replaced by a keyed
# pseudonym. `data/docs/data_dictionary.csv`.
#
# **Tasks**
# - [ ] 1 · Types and completeness from the dictionary (7')
# - [ ] 2 · Range and validity rules (6')
# - [ ] 3 · Uniqueness (4')
# - [ ] 4 · Run on the clean build and on a broken copy (8')
# - [ ] ✱ Stretch · Which rules stop the build and which only warn?

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
import pandera.pandas as pa
import ghilal as G
import build_dataset as B   # the reference build: its rule suite is the safety net of this lab

j = G.joined_q3()
dictionary = pd.read_csv(G.DOCS / "data_dictionary.csv")
print(dictionary.to_string(index=False))
print(f"\n{len(j):,} rows")
ISO = r"^\d{4}-\d{2}-\d{2}$"
DISTRICTS = [f"D{i:02d}" for i in range(1, 31)]


def rule(check, name: str):
    """Give a check a name a person can read: the quality dimension, then what must hold."""
    check.name, check.error = name, name
    return check

# %% [markdown]
# ## 1 · Types and completeness from the dictionary (7')
#
# A Pandera column states a type and whether blanks are allowed: `pa.Column(str)`,
# `pa.Column(float, nullable=True)`. A column that is "required: yes" in the dictionary is not nullable; that is
# its **completeness** rule. Use `"Int64"` for an integer column that may be blank. Dates stay text here, with a
# pattern, so that a date in another layout fails instead of being guessed.
#
# ✏️ **Exercise** · Write `typed_columns()`: a dictionary from column name to `pa.Column`, for all ten columns.
# No value rules yet, except the pattern `ISO` for the two dates (name it with `rule`).

# %%
def typed_columns() -> dict:
    # BEGIN SOLUTION
    return {
        "log_id": pa.Column(str), "household_key": pa.Column(str), "branch_id": pa.Column(str),
        "district_id": pa.Column(str),
        "handout_date": pa.Column(str, [rule(pa.Check.str_matches(ISO), "type: handout_date is a date written YYYY-MM-DD")]),
        "registered_on": pa.Column(str, [rule(pa.Check.str_matches(ISO), "type: registered_on is a date written YYYY-MM-DD")]),
        "parcels": pa.Column(int), "weight_kg": pa.Column(float, nullable=True),
        "household_size": pa.Column("Int64", nullable=True), "eligible": pa.Column("Int64", nullable=True),
    }
    # END SOLUTION


# %%
# Check, with a safety net: the cells below still run when the exercise is not done yet
try:
    cols = typed_columns()
except NotImplementedError:
    cols = {k: pa.Column(c.dtype, list(c.checks)[:1] if "date" in k or k == "registered_on" else None,
                         nullable=c.nullable) for k, c in B.schema().columns.items()}
nullable = sorted(k for k, c in cols.items() if c.nullable)
G.check(len(cols) == 10 and nullable == ["eligible", "household_size", "weight_kg"],
        f"ten typed columns; blanks allowed only in {', '.join(nullable)}")

# %% [markdown]
# ## 2 · Range and validity rules (6')
#
# **Validity**: a value is one the dictionary allows. Three kinds of check cover this table:
# `pa.Check.in_range(1, 3)`, `pa.Check.isin([...])` and `pa.Check.str_matches(pattern)`.
#
# ✏️ **Exercise** · Write `value_rules()`: a dictionary from column name to a list of named checks, for
# `log_id` (pattern `^B\d{2}-\d{7}$`), `household_key` (16 hexadecimal characters), `branch_id`, `district_id`,
# `parcels`, `weight_kg` (5 to 50), `household_size` (1 to 20) and `eligible` (0 or 1). Begin each name with
# `"validity: "`.

# %%
def value_rules() -> dict:
    # BEGIN SOLUTION
    return {
        "log_id": [rule(pa.Check.str_matches(r"^B\d{2}-\d{7}$"), "validity: log_id has the branch form")],
        "household_key": [rule(pa.Check.str_matches(r"^[0-9a-f]{16}$"), "validity: household_key is a 16-character pseudonym")],
        "branch_id": [rule(pa.Check.isin(G.BRANCHES), "validity: branch_id is one of the 14 branches")],
        "district_id": [rule(pa.Check.isin(DISTRICTS), "validity: district_id is one of the 30 districts")],
        "parcels": [rule(pa.Check.in_range(1, 3), "validity: parcels between 1 and 3")],
        "weight_kg": [rule(pa.Check.in_range(5, 50), "validity: weight_kg between 5 and 50")],
        "household_size": [rule(pa.Check.in_range(1, 20), "validity: household_size between 1 and 20")],
        "eligible": [rule(pa.Check.isin([0, 1]), "validity: eligible is 0 or 1")],
    }
    # END SOLUTION


# %%
try:
    rules = value_rules()
except NotImplementedError:
    rules = {k: [c for c in col.checks if str(c.name).startswith("validity")] for k, col in B.schema().columns.items()}
    rules = {k: v for k, v in rules.items() if v}
names = [c.name for v in rules.values() for c in v]
G.check(len(rules) == 8 and all(str(n).startswith("validity: ") for n in names), f"{len(names)} validity rules, each with a readable name")

# %% [markdown]
# ## 3 · Uniqueness (4')
#
# **Uniqueness**: a key identifies one row. Which columns of this table must never repeat? Think of the grain:
# one row per handout; one household has many handouts.
#
# ✏️ **Exercise** · Write `unique_columns()`: the list of columns that must be unique.

# %%
def unique_columns() -> list:
    # BEGIN SOLUTION
    return ["log_id"]
    # END SOLUTION


# %%
try:
    uniq = unique_columns()
except NotImplementedError:
    uniq = ["log_id"]
G.check(uniq == ["log_id"], "log_id must be unique; household_key must not be: a household has many handouts")


def suite(cols: dict, rules: dict, uniq: list) -> pa.DataFrameSchema:
    """The rule suite: typed columns, their value rules, the unique keys. No column may be missing or extra."""
    out = {}
    for k, c in cols.items():
        out[k] = pa.Column(c.dtype, list(c.checks) + rules.get(k, []), nullable=c.nullable, unique=k in uniq)
    return pa.DataFrameSchema(out, strict=True, coerce=True)


schema = suite(cols, rules, uniq)

# %% [markdown]
# ## 4 · Run on the clean build and on a broken copy (8')
#
# `B.run_schema(df, schema)` runs every rule (lazily: it does not stop at the first failure) and returns one line
# per failing rule: the rule, the column, the number of rows, some examples. A suite that has never failed has
# never been tested, so you break a copy on purpose.

# %%
clean = B.run_schema(j, schema)
print("clean build:", "every rule passes" if clean.empty else clean.to_string(index=False))
G.check(clean.empty, f"the suite passes on the clean build of {len(j):,} rows")

# %% [markdown]
# ✏️ **Exercise** · Write `break_it(j)`: a copy of the first 2,000 rows with at least five different faults, each
# in a few rows: a repeated `log_id`, a blank `household_key`, `parcels` of 9, a `district_id` that does not
# exist, a `handout_date` written `03/07/2026`.

# %%
def break_it(j: pd.DataFrame) -> pd.DataFrame:
    # BEGIN SOLUTION
    b = j.head(2000).copy()
    b.loc[b.index[1], "log_id"] = b.loc[b.index[0], "log_id"]
    b.loc[b.index[10:13], "household_key"] = None
    b.loc[b.index[20:24], "parcels"] = 9
    b.loc[b.index[30:32], "district_id"] = "D99"
    b.loc[b.index[40:45], "handout_date"] = "03/07/2026"
    return b
    # END SOLUTION


# %%
def _break(j):
    b = j.head(2000).copy()
    b.loc[b.index[1], "log_id"] = b.loc[b.index[0], "log_id"]
    b.loc[b.index[10:13], "household_key"] = None
    b.loc[b.index[20:24], "parcels"] = 9
    b.loc[b.index[30:32], "district_id"] = "D99"
    b.loc[b.index[40:45], "handout_date"] = "03/07/2026"
    return b


try:
    broken = break_it(j)
except NotImplementedError:
    broken = _break(j)
report = B.run_schema(broken, schema)
print(report.to_string(index=False))
report.to_csv(G.lab_dir("D4_1") / "broken_copy_report.csv", index=False)
G.keep("d4_1_report", report.to_dict("records"))
dims = sorted({r.split(":")[0] for r in report.rule})
G.check(len(report) >= 5 and {"completeness", "type", "uniqueness", "validity"} <= set(dims),
        f"{len(report)} rules fail on the broken copy, in four dimensions: {', '.join(dims)}")

# %% [markdown]
# 🔍 Read the report as the owner of the data would. Does each line say what is wrong, where, and in how many
# rows? Compare with what Python says for the same table without the suite: nothing at all.

# %% [markdown]
# ## ✱ Stretch · Which rules stop the build and which only warn?
#
# Not every failure deserves to stop a rebuild. Sort the rule names of your suite into two lists and give the
# reason for one rule of each list.

# %%
def severity() -> dict:
    # BEGIN SOLUTION
    stop = ["uniqueness: no value repeats", "completeness: no value is missing",
            "type: handout_date is a date written YYYY-MM-DD", "validity: district_id is one of the 30 districts"]
    warn = ["validity: weight_kg between 5 and 50", "validity: household_size between 1 and 20"]
    return {"stop": stop, "warn": warn,
            "why": "a repeated key or an unknown district corrupts every count; an odd weight leaves the parcel count intact"}
    # END SOLUTION


try:
    print(severity())
except NotImplementedError:
    print("✱ Stretch not attempted")

# %% [markdown]
# ## Verification note
#
# The last step of every lab: what this run verified, and what the lab did not verify. The cell writes
# `artifacts/D4_1/verification.md`. Read the last line and add one of your own.

# %%
note = G.verification_note("D4_1", "whether valid values are true, and anything that needs two fields or two sources (Lab 4.2)")

# %% [markdown]
# ## Checkpoint
#
# 1. Why keep the dates as text with a pattern, and not let the suite convert them?
#    <details><summary>Answer</summary>A converter guesses: 03/07/2026 would become a date, in one of two months. A
#    pattern refuses it, and the failure names the layout problem.</details>
# 2. `household_size` passes "between 1 and 20" for every row. Is the column right?
#    <details><summary>Answer</summary>It is valid. Lab 3.4 showed it can be valid and wrong: rules test what a
#    value may be, not whether it is true.</details>
# 3. Why must the suite fail on a broken copy before you trust it?
#    <details><summary>Answer</summary>A rule that cannot fail protects nothing. A typing mistake in a pattern or a
#    range that is too wide passes every clean build for ever.</details>
#
# **Carry forward.** Your `suite`. Lab 4.2 starts from the reference suite `B.schema()`, which is the same rules.
