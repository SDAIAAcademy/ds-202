# %% [markdown]
# # Lab 1.2 · Three ways in
#
# Day 1 · Session 2 (Files, APIs and databases) · 25 min.
#
# The four sources arrive in three ways: files (the 14 branch logs and the open table), an API (donations) and a
# database (the register). You load each one and, before looking at a single value, count what arrived against
# what the source says it sent.
#
# **AI-off** for the first attempt at each loader.
#
# **Reference state.** `data/raw/branch_logs/B01.csv.gz` to `B14.csv.gz`; the donations API, started on this
# computer by `G.start_api()`; the register as a table in an in-memory database, `G.registry()`.
#
# **Tasks**
# - [ ] 1 · Load the 14 log files, whatever their encoding (7')
# - [ ] 2 · Page through the donations API and reconcile with its total (8')
# - [ ] 3 · Query the register in SQL (6')
# - [ ] 4 · The source inventory (4')
# - [ ] ✱ Stretch · Does a smaller page size change what arrives?

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

import io
import pandas as pd
import ghilal as G

G.ensure_data()

# %% [markdown]
# ## 1 · Load the 14 log files, whatever their encoding (7')
#
# `G.log_bytes("B01")` returns the bytes of one branch file. B01 reads as UTF-8. Try B03 the same way.

# %%
print(G.log_bytes("B01").decode("utf-8")[:160])
try:
    G.log_bytes("B03").decode("utf-8")
except UnicodeDecodeError as e:
    print("B03 as UTF-8 fails:", str(e)[:70])
print("B08 begins with:", G.log_bytes("B08")[:6])

# %% [markdown]
# B03 is in the Windows Arabic code page (`cp1256`), as in FN-104. B08 begins with three bytes, `EF BB BF`, a
# byte order mark that a spreadsheet wrote; the codec `utf-8-sig` removes it.
#
# ✏️ **Exercise** · Write `read_branch(b)`: the file of branch `b` as a table of **text** columns (`dtype=str`,
# `keep_default_na=False`), decoded as `utf-8-sig` when that works and as `cp1256` otherwise, with a column
# `branch_id` added. Read nothing as a number or a date yet: a loader that guesses types hides what Day 2 repairs.

# %%
def read_branch(b: str) -> pd.DataFrame:
    # BEGIN SOLUTION
    raw = G.log_bytes(b)
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1256")
    df = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    df.insert(1, "branch_id", b)
    return df
    # END SOLUTION


# %%
try:
    logs = pd.concat([read_branch(b) for b in G.BRANCHES], ignore_index=True)
except NotImplementedError:
    logs = G.logs_raw()
per_branch = logs.groupby("branch_id").size()
print(per_branch.to_string())
G.check(len(logs) == 210_000 and list(logs.columns)[0] == "log_id", f"{len(logs):,} log rows from 14 files, first column log_id")
G.check(logs.loc[logs.branch_id == "B03", "collected_by"].str.contains("[ء-ي]", regex=True).all(),
        "the names of B03 are in Arabic letters")

# %% [markdown]
# ## 2 · Page through the donations API and reconcile with its total (8')
#
# The source note (`data/docs/donations_api.md`) says: ask for a page, follow `next` until it is null, and expect
# a busy answer (503) now and then. `G.get_json(url)` asks once and tries again after a 503.
#
# ✏️ **Exercise** · Write `fetch_all(base)`: every record of every page, in the order served, as a list, and the
# `total` the API reports.

# %%
base = G.start_api()
first = G.get_json(base + "/v1/donations?page=1&per_page=200")
print({k: first[k] for k in ("page", "per_page", "total", "next")}, "| first record:", first["data"][0])


def fetch_all(base: str) -> tuple[list, int]:
    # BEGIN SOLUTION
    records, url, total = [], "/v1/donations?page=1&per_page=200", None
    while url:
        page = G.get_json(base + url)
        records += page["data"]
        total, url = page["total"], page["next"]
    return records, total
    # END SOLUTION


# %%
try:
    records, total = fetch_all(base)
except NotImplementedError:
    records, total = [], G.reference("d1_2_api")["total"]
    url = "/v1/donations?page=1&per_page=200"
    while url:
        page = G.get_json(base + url)
        records += page["data"]
        url = page["next"]
donations = pd.DataFrame(records)
print(f"records received: {len(donations):,} | total reported by the API: {total:,}")
repeated = donations[donations.duplicated("donation_id", keep=False)].sort_values("donation_id")
print(f"donation ids received more than once: {repeated.donation_id.nunique()}")
print(repeated.head(4)[["donation_id", "received_at", "branch_id", "weight"]].to_string(index=False))

# %% [markdown]
# More records than the total. Donations arrived while you were paging, so some pages begin with records the page
# before ended with. The count that reconciles is the number of distinct `donation_id`.

# %%
donations = donations.drop_duplicates("donation_id").reset_index(drop=True)
G.keep("d1_2_api", {"received": len(records), "total": total, "distinct": len(donations)})
G.check(len(donations) == total, f"{len(donations):,} distinct donations = the total the API reports")

# %% [markdown]
# ## 3 · Query the register in SQL (6')
#
# `G.registry()` is a DuckDB database with the table `registrations`, every column as text.
#
# ✏️ **Exercise** · Write one query that returns one row: the number of rows, the number of distinct
# `household_id`, and the earliest and latest `registered_on`.

# %%
con = G.registry()


def register_counts() -> tuple:
    # BEGIN SOLUTION
    return con.execute("""
        SELECT count(*), count(DISTINCT household_id), min(registered_on), max(registered_on)
        FROM registrations""").fetchone()
    # END SOLUTION


# %%
try:
    counts = tuple(register_counts())
except NotImplementedError:
    counts = tuple(G.reference("d1_2_register"))
G.keep("d1_2_register", list(counts))
print("rows, distinct ids, first and last registration:", counts)
G.check(counts[0] == 40_000 and counts[1] == 39_820, "40,000 rows but 39,820 households: 180 ids are there twice")
print(con.execute("""SELECT household_id, count(*) AS n, min(branch_id) AS a, max(branch_id) AS b
                     FROM registrations GROUP BY 1 HAVING count(*) > 1 ORDER BY 1 LIMIT 3""").df().to_string(index=False))

# %% [markdown]
# ## 4 · The source inventory (4')
#
# One table, one line per source: what arrived, what the source says it sent, and whether the two agree.

# %%
population = G.population()
inventory = pd.DataFrame([
    ("register", "database extract", counts[0], "40,000 registrations (source note)", counts[0] == 40_000),
    ("branch logs", "14 files", len(logs), "no count is stated anywhere", None),
    ("donations", f"API, {-(-total // 200)} pages", len(donations), f"total = {total:,}", len(donations) == total),
    ("open district table", "one file", len(population), "28 districts of 2022 (source note)", len(population) == 28),
], columns=["source", "arrives as", "rows", "the source says", "agrees"])
print(inventory.to_string(index=False))
inventory.to_csv(G.lab_dir("D1_2") / "source_inventory.csv", index=False)
G.check(inventory.agrees.isna().sum() == 1, "three sources reconcile; the logs come with nothing to reconcile against")
G.stop_api()

# %% [markdown]
# 🔍 The branch logs are the largest source and the only one that says nothing about itself. A week uploaded twice
# and a week never uploaded both pass this table. Day 2 and Day 3 find one of each.

# %% [markdown]
# ## ✱ Stretch · Does a smaller page size change what arrives?

# %%
def fetch_small(per_page: int = 50) -> int:
    # BEGIN SOLUTION
    base = G.start_api()
    n, url = 0, f"/v1/donations?page=1&per_page={per_page}"
    while url:
        page = G.get_json(base + url)
        n, url = n + len(page["data"]), page["next"]
    G.stop_api()
    return n
    # END SOLUTION


try:
    print("records with pages of 50:", fetch_small(G.pick(50, 100)))
except NotImplementedError:
    print("✱ Stretch not attempted")

# %% [markdown]
# ## Checkpoint
#
# 1. Why load every log column as text first?
#    <details><summary>Answer</summary>A loader that guesses turns an id into a number and reads 03/07/2026 as March
#    or July without telling you. As text, nothing is lost and every repair is a step you can count.</details>
# 2. The API returned 12 records more than its total. Which number goes in the inventory?
#    <details><summary>Answer</summary>The distinct donation ids, with a line that 12 repeats were dropped and why.
#    The total is the claim of the source; your count has to explain any difference from it.</details>
# 3. The register has 40,000 rows and 39,820 household ids. Is that an error?
#    <details><summary>Answer</summary>Not in the register: a household that registers again gets a second row. It
#    becomes an error when you join to it as if each id were there once (Lab 2.2).</details>
#
# **Carry forward.** `artifacts/D1_2/source_inventory.csv`.
