# %% [markdown]
# # Lab 4.4 · The quality report
#
# Day 4 · Session 4 (A data-quality report) · 25 min.
#
# Sumayyah Al-Khudair will read one page before she reads any number. You rebuild the analysis dataset from the
# raw sources with one command, draft the data-quality report from what the build wrote (no number is typed by
# hand), decide which outputs may leave the analysis environment, and choose the question of your capstone.
#
# An **AI-assistant** may improve the wording of your report **after** your own draft exists; every number in it
# must still come from the build. Record what you asked and what you kept.
#
# **Reference state.** The raw sources in `data/raw/`; the reference build `build_dataset.py`; the reference
# results of Day 3 (`G.reference("d3_2_table")`, `G.reference("d3_3_range")`); `data/reference/provenance_supplied.json`.
#
# **Tasks**
# - [ ] 1 · Rebuild from the raw sources with one command (5')
# - [ ] 2 · Draft the report from the build outputs (10')
# - [ ] 3 · What may leave the analysis environment (5')
# - [ ] 4 · Choose your capstone question (5')
# - [ ] ✱ Stretch · Corrupt one input file and rebuild

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

import hashlib
import io
import json
import re
import pandas as pd
import ghilal as G
import build_dataset as B   # the reference build: one command, raw files in, artifacts/build/ out

# %% [markdown]
# ## 1 · Rebuild from the raw sources with one command (5')
#
# In a terminal the command is `uv run python build_dataset.py`. Here the same function runs in the notebook.
# It reads only `data/raw/`, and writes `artifacts/build/`: the two tables, the log of row counts per step, the
# rows set aside with their reason, the rule results and a skeleton of the report. It takes about 20 seconds.

# %%
r = B.build()
print(r["join_log"].to_string(index=False))
print()
print("files written:", ", ".join(sorted(p.name for p in G.lab_dir("build").iterdir())))

# %% [markdown]
# "It ran" is not "it rebuilt the same dataset". A rebuild is checked against the last one: same rows, same
# content.
#
# ✏️ **Exercise** · Write `fingerprint(df)`: the number of rows and the first 12 hexadecimal characters of the
# SHA-256 of the table written as CSV (without the index), as a tuple.

# %%
def fingerprint(df: pd.DataFrame) -> tuple:
    # BEGIN SOLUTION
    return len(df), hashlib.sha256(df.to_csv(index=False).encode()).hexdigest()[:12]
    # END SOLUTION


# %%
# Check, with a safety net: the cells below still run when the exercise is not done yet
try:
    fingerprint(r["join_log"])
except NotImplementedError:
    fingerprint = lambda df: (len(df), hashlib.sha256(df.to_csv(index=False).encode()).hexdigest()[:12])  # noqa: E731
def as_written(df):
    """The table as a CSV file holds it: text only, so that two builds compare value by value."""
    return pd.read_csv(io.StringIO(df.to_csv(index=False)), dtype=str, keep_default_na=False)


mine = fingerprint(as_written(r["joined"]))
ref = fingerprint(as_written(G.joined_q3()))
print("this build:", mine, "| reference build:", ref)
G.check(mine == ref, f"the rebuild is the reference build: {mine[0]:,} handouts, same content ({mine[1]})")

# %% [markdown]
# ## 2 · Draft the report from the build outputs (10')
#
# The report has six short parts. The facts for them already exist: the build wrote some, Day 3 produced others.
# The cell below collects them in one dictionary, `facts`. Your part is the two things a program cannot write:
# the **headline**, and the **limits**.

# %%
t = {row["index"]: row for row in G.reference("d3_2_table")}
rng = G.reference("d3_3_range")["plausible"]
verdicts = pd.DataFrame(G.reference("d3_3_districts"))
log = r["join_log"].set_index("step")
facts = {
    "quarter": f"{G.Q_START} to {G.Q_END}",
    "standard": G.STANDARD,
    "households": int(log.loc["households of the target population", "rows"]),
    "handouts": int(log.loc["handouts of the quarter", "rows"]),
    "set_aside": int(len(r["set_aside"])),
    "copies_dropped": 380,
    "rules_failing": int((r["rules"]["rows"] > 0).sum()),
    "rules_run": int(len(B.schema().columns)) + int(len(r["rules"])),
    "missing_pct": r["missing_pct"],
    "complete_case": t["complete case"]["estimate"],
    "recommended": t["imputed within groups"]["estimate"],
    "range": rng,
    "below_in_every_scenario": sorted(verdicts[verdicts.verdict == "below"].district_id),
    "n_below": int((verdicts.verdict == "below").sum()),
    "depends_on_assumption": sorted(verdicts[verdicts.verdict == "depends on the assumption"].district_id),
    "b12_gap": "10 to 18 August 2026",
    "no_frame": ["D29", "D30"],
}
for k, v in facts.items():
    print(f"{k:26} {v}")

# %% [markdown]
# ✏️ **Exercise** · Write `headline(facts)`: one sentence for Sumayyah with the recommended estimate, its
# plausible range, the standard, and the districts below the standard in every scenario. Every number comes from
# `facts`.
#
# ✏️ **Exercise** · Write `limits(facts)`: a list of at least five sentences. Each names one thing this dataset
# cannot support or one known fault, with its number from `facts`: the missing household sizes, the districts
# whose verdict depends on the assumption, the B12 gap, the rows set aside, the districts without a frame, the
# self-reported sizes.

# %%
def headline(facts: dict) -> str:
    # BEGIN SOLUTION
    lo, hi = facts["range"]
    return (f"In the quarter {facts['quarter']} the network handed out an estimated {facts['recommended']} parcels per "
            f"eligible household per month (plausible range {lo} to {hi}; standard {facts['standard']}); "
            f"{facts['n_below']} districts are below the standard under every assumption we tested: "
            f"{', '.join(facts['below_in_every_scenario'])}.")
    # END SOLUTION


def limits(facts: dict) -> list:
    # BEGIN SOLUTION
    return [
        f"Household size is missing for {facts['missing_pct']}% of the {facts['households']:,} households, and larger "
        f"households are missing more often; counting only complete rows gives {facts['complete_case']}, which is biased low.",
        f"For {', '.join(facts['depends_on_assumption'])} the verdict against the standard changes with the assumption "
        f"about the missing sizes: report them as undecided, not as below or above.",
        f"Branch B12 sent no log rows for {facts['b12_gap']}; the figure of its districts understates what was handed out.",
        f"{facts['set_aside']} log rows could not be tied to a household and are set aside with their reason, not counted.",
        f"Districts {' and '.join(facts['no_frame'])} have no row in the open table of 2022: coverage of the population "
        f"in need cannot be stated for them.",
        "Household size is reported by the household; the audit of Day 3 found sizes overstated more often than "
        "understated, which moves the estimate down, so the true figure is probably somewhat higher.",
        "The register holds households that registered; it says nothing about households in need that did not.",
    ]
    # END SOLUTION


# %%
def _numbers(text: str) -> set:
    return set(re.findall(r"\d+(?:[.,]\d+)*", text))


try:
    head, lim = headline(facts), limits(facts)
except NotImplementedError:
    lo, hi = facts["range"]
    head = (f"Estimated {facts['recommended']} parcels per eligible household per month (range {lo} to {hi}; standard "
            f"{facts['standard']}); below in every scenario: {', '.join(facts['below_in_every_scenario'])}.")
    lim = [f"Household size is missing for {facts['missing_pct']}% of households.",
           f"Verdict depends on the assumption for {', '.join(facts['depends_on_assumption'])}.",
           f"B12 sent no rows for {facts['b12_gap']}.", f"{facts['set_aside']} rows are set aside.",
           f"No population frame for {' and '.join(facts['no_frame'])}."]
G.check(str(facts["recommended"]) in head and str(facts["range"][0]) in head and str(facts["range"][1]) in head,
        "the headline carries the estimate and its range, not a single number")
G.check(len(lim) >= 5 and str(facts["missing_pct"]) in " ".join(lim) and "B12" in " ".join(lim),
        f"{len(lim)} limits, each one a sentence a reader can act on")

prov = {"register extract": G.reference("d1_3_register"), "open district table": G.reference("d1_3_open")}
prov |= json.loads((G.REF / "provenance_supplied.json").read_text(encoding="utf-8"))
lines = ["# Data-quality report: parcels per eligible household, Q3 2026", "",
         "Synthetic data of the Ghilal case. Every number below is read from the build outputs.", "",
         "## 1 · Headline", "", head, "",
         "## 2 · Question and population", "",
         f"Parcels per eligible household per month, by district, {facts['quarter']}. Eligible: active, registered "
         f"before the quarter, income per member at or below {G.THRESHOLD_SAR:,} SAR a month. "
         f"Target population: {facts['households']:,} households; {facts['handouts']:,} handouts.", "",
         "## 3 · Sources", "", "| Source | Owner | Refreshed | Classification |", "|---|---|---|---|"]
lines += [f"| {k.replace('_', ' ')} | {v['owner']} | {v['refresh_date']} | {v['classification']} |" for k, v in prov.items()]
lines += ["", "## 4 · Row counts per step", "", "| Step | Rows | Note |", "|---|---|---|"]
lines += [f"| {x.step} | {x.rows:,} | {x.note} |" for x in r["join_log"].itertuples()]
lines += ["", "## 5 · Rules", "",
          f"{facts['rules_run']} rules ran on the joined table (ten column rules, two across fields); "
          f"{facts['rules_failing']} report failing rows on this build.", "",
          "## 6 · Limits: what this dataset cannot support", ""] + [f"- {x}" for x in lim]
report = "\n".join(lines) + "\n"
(G.lab_dir("D4_4") / "quality_report.md").write_text(report, encoding="utf-8", newline="\n")
print(report[:1400])
typed = _numbers(head) - _numbers(json.dumps(facts)) - {"2026"}
G.check(not typed, "no number in the headline was typed by hand" if not typed else f"typed by hand: {sorted(typed)}")

# %% [markdown]
# 🔍 Read your limits as Sumayyah would. Which one changes what she does on Monday? Put that one first.

# %% [markdown]
# ## 3 · What may leave the analysis environment (5')
#
# The build wrote several files. Some are aggregates; some are household-level; one still holds what branch
# desks typed. Before anything is committed to a repository or attached to a message, a program looks.
#
# ✏️ **Exercise** · Write `leaks(df)`: the list of columns of `df` in which at least one value looks like a
# direct identifier: a household id (`H` and six digits), a ten-digit number starting with 1 (an ID number), or
# a mobile number (`05` and eight digits). Search inside the text of each value.

# %%
PATTERNS = r"H\d{6}|\b1\d{9}\b|\b05\d{8}\b"


def leaks(df: pd.DataFrame) -> list:
    # BEGIN SOLUTION
    return [c for c in df.columns if df[c].astype(str).str.contains(PATTERNS, regex=True).any()]
    # END SOLUTION


# %%
try:
    leaks(pd.DataFrame({"a": ["x"]}))
except NotImplementedError:
    leaks = lambda df: [c for c in df.columns if df[c].astype(str).str.contains(PATTERNS, regex=True).any()]  # noqa: E731
rows = []
for p in sorted(G.lab_dir("build").glob("*.csv")):
    df = pd.read_csv(p, dtype=str, keep_default_na=False)
    found = leaks(df)
    grain = "household" if "household_key" in df.columns or "household_id" in df.columns else "aggregate"
    decision = ("stays inside: direct identifiers" if found else
                "leaves only under an agreement, generalised (Lab 4.3)" if grain == "household" else "may leave")
    rows.append((p.name, len(df), grain, ", ".join(found) or "none", decision))
release = pd.DataFrame(rows, columns=["file", "rows", "grain", "columns with identifiers", "decision"])
print(release.to_string(index=False))
release.to_csv(G.lab_dir("D4_4") / "release_decisions.csv", index=False)
G.keep("d4_4_release", release.to_dict("records"))
inside = list(release[release.decision.str.startswith("stays")].file)
G.check(inside == ["set_aside.csv"] and (release.decision == "may leave").sum() == 2,
        "set_aside.csv stays inside; the two aggregate files may leave; the two household tables need an agreement")

# %% [markdown]
# 🔍 `set_aside.csv` keeps the keys exactly as they were typed, because somebody must repair them. That makes
# it the most useful file for the branch and the one that must not travel. `households.csv` has no identifier
# and still has one row per household with an exact income: pseudonymised, personal, restricted.
#
# What the repository of your capstone may hold: the code, the rules, the join log, the rule results, the
# report, and the set-aside rows as log id, branch and reason. What it may not hold: the raw sources, a
# household key as typed, the key of the pseudonyms.

# %% [markdown]
# ## 4 · Choose your capstone question (5')
#
# The capstone data is a **second city** of the network, Madinat Al-Rimal, with the same four kinds of source
# and its own faults. Three questions are open (`capstone/README.md`):
#
# - **A** · Parcels per eligible household per month, by district, Q2 2026.
# - **B** · Kilograms handed out per household member, by branch, against kilograms received.
# - **C** · Share of eligible households that received no parcel in the quarter, by registration channel.
#
# ✏️ **Exercise** · Fill `my_choice()`: the letter, the population, the sources you need, and the fault you
# expect to cost you most time. Two lines each are enough; you may change your mind on the capstone day.

# %%
def my_choice() -> dict:
    # BEGIN SOLUTION
    return {"question": "C",
            "population": "active households registered before the quarter and eligible by income per member",
            "sources": ["register extract", "branch logs"],
            "biggest_risk": "eligibility needs household size, which is missing more often for online and phone "
                            "registrations: the very groups the question compares"}
    # END SOLUTION


# %%
try:
    choice = my_choice()
except NotImplementedError:
    choice = {"question": "A", "population": "not chosen yet", "sources": [], "biggest_risk": "not chosen yet"}
(G.lab_dir("D4_4") / "capstone_choice.json").write_text(json.dumps(choice, ensure_ascii=False, indent=1) + "\n",
                                                        encoding="utf-8", newline="\n")
G.check(choice["question"] in ("A", "B", "C") and {"population", "sources", "biggest_risk"} <= set(choice),
        f"capstone question {choice['question']} recorded in artifacts/D4_4/capstone_choice.json")

# %% [markdown]
# ## ✱ Stretch · Corrupt one input file and rebuild
#
# The capstone assessor will corrupt one input file and run your build. Do it to the reference build first:
# in the last days of September, B07 typed the number of parcels ten times too large (10, 20, 30). Run the
# cleaning and the rules, and read what the build says. Then try a fault the cleaning repairs on its own
# (weights in grams) and ask yourself whether a silent repair is what you want.

# %%
def corrupt_and_rebuild() -> pd.DataFrame:
    # BEGIN SOLUTION
    raw = G.logs_raw()
    hit = (raw.branch_id == "B07") & raw.handout_date.astype(str).str.startswith("2026-09-2")
    raw.loc[hit, "parcels"] = raw.loc[hit, "parcels"].astype(str) + "0"
    households, _ = B.clean_registry(G.registry_text())
    logs, _, _ = B.clean_logs(raw, households)
    jq = B.joined_table(B.join(logs, households))
    return pd.concat([B.run_schema(jq).drop(columns="column"), B.consistency(jq)], ignore_index=True)
    # END SOLUTION


try:
    print(corrupt_and_rebuild().to_string(index=False))
except NotImplementedError:
    print("✱ Stretch not attempted")

# %% [markdown]
# ## Checkpoint
#
# 1. Why is every number of the report read from the build, and none typed?
#    <details><summary>Answer</summary>The next rebuild changes the numbers. A typed number stays, and the report
#    then describes a dataset that no longer exists.</details>
# 2. The headline gives 2.06 with a range of 2.02 to 2.07. Why not the single number?
#    <details><summary>Answer</summary>The single number hides an assumption about 18% of the households. The range
#    says how far that assumption can move the figure; the verdict of three districts depends on it.</details>
# 3. Which build output is the most useful to a branch and may not leave?
#    <details><summary>Answer</summary>The set-aside rows: they hold the keys as typed, which is what the branch
#    must repair, and which are direct identifiers.</details>
#
# **Carry forward.** `artifacts/D4_4/quality_report.md`, `release_decisions.csv` and `capstone_choice.json`:
# the report is the pattern of your capstone's second deliverable.
