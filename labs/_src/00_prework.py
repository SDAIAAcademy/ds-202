# %% [markdown]
# # Pre-work · Joins and dataframes
#
# Guided self-study before Day 1 · about two hours.
#
# The course assumes that you write joins and group-by queries without help. This notebook is the practice: eight
# short exercises on two small tables, in pandas and in SQL, each with a check. Work **without an assistant**:
# the entry quiz at the start of Day 1 is supervised and AI-off, and it asks what these exercises ask.
#
# The tables are made in the notebook (a few hundred rows, no personal data). They are not the data of the course.
#
# **Exercises**
# - [ ] 1 · Filter and select (10')
# - [ ] 2 · Group and aggregate (15')
# - [ ] 3 · The same question in SQL (15')
# - [ ] 4 · An inner join, counted (15')
# - [ ] 5 · A left join and the rows without a match (15')
# - [ ] 6 · A join that multiplies rows (20')
# - [ ] 7 · Dates with an explicit format (15')
# - [ ] 8 · A reconciliation in one function (15')

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

import random
import duckdb
import pandas as pd
import ghilal as G

rng = random.Random(202)
depots = pd.DataFrame({
    "depot_id": [f"P{i:02d}" for i in range(1, 13)],
    "city": [rng.choice(["North", "South", "East", "West"]) for _ in range(12)],
    "opened_year": [rng.randint(2015, 2024) for _ in range(12)],
})
rows = []
for i in range(1, 601):
    d = rng.choice(list(depots.depot_id) + ["P13", "P14"]) if rng.random() < 0.97 else ""
    day = rng.randint(1, 28)
    month = rng.randint(1, 6)
    rows.append((f"V{i:04d}", d, f"{day:02d}/{month:02d}/2026", rng.choice(["rice", "dates", "oil", "flour"]),
                 round(rng.uniform(40, 900), 1)))
deliveries = pd.DataFrame(rows, columns=["delivery_id", "depot_id", "delivered_on", "item", "kg"])
print(depots.head(3).to_string(index=False))
print(deliveries.head(3).to_string(index=False))
print(f"\n{len(depots)} depots, {len(deliveries)} deliveries")

# %% [markdown]
# ## 1 · Filter and select (10')
#
# ✏️ **Exercise** · Write `heavy_rice(deliveries)`: the deliveries of rice above 500 kg, columns `delivery_id`
# and `kg` only, heaviest first.

# %%
def heavy_rice(deliveries: pd.DataFrame) -> pd.DataFrame:
    # BEGIN SOLUTION
    d = deliveries[(deliveries.item == "rice") & (deliveries.kg > 500)]
    return d[["delivery_id", "kg"]].sort_values("kg", ascending=False)
    # END SOLUTION


# %%
# Check, with a safety net: the cells below still run when the exercise is not done yet
try:
    r1 = heavy_rice(deliveries)
except NotImplementedError:
    r1 = deliveries[(deliveries.item == "rice") & (deliveries.kg > 500)][["delivery_id", "kg"]].sort_values("kg", ascending=False)
G.check(list(r1.columns) == ["delivery_id", "kg"] and r1.kg.is_monotonic_decreasing and r1.kg.min() > 500,
        f"{len(r1)} deliveries of rice above 500 kg, heaviest first")

# %% [markdown]
# ## 2 · Group and aggregate (15')
#
# ✏️ **Exercise** · Write `per_item(deliveries)`: one row per item with the number of deliveries (`n`) and the
# total kilograms (`kg`, rounded to 1 decimal), sorted by item.

# %%
def per_item(deliveries: pd.DataFrame) -> pd.DataFrame:
    # BEGIN SOLUTION
    return (deliveries.groupby("item").agg(n=("delivery_id", "size"), kg=("kg", "sum"))
            .round({"kg": 1}).reset_index().sort_values("item"))
    # END SOLUTION


# %%
try:
    r2 = per_item(deliveries)
except NotImplementedError:
    r2 = deliveries.groupby("item").agg(n=("delivery_id", "size"), kg=("kg", "sum")).round({"kg": 1}).reset_index()
print(r2.to_string(index=False))
G.check(int(r2.n.sum()) == len(deliveries) and abs(r2.kg.sum() - deliveries.kg.sum()) < 1,
        "the groups add up to the table: every delivery is in exactly one group")

# %% [markdown]
# The check is the habit of this course: after a group-by, the parts must add up to the whole.

# %% [markdown]
# ## 3 · The same question in SQL (15')
#
# DuckDB runs SQL on a data frame by its variable name.
#
# ✏️ **Exercise** · Write `per_item_sql()`: a SQL query, as text, that gives the same table as exercise 2
# (columns `item`, `n`, `kg`; sorted by item).

# %%
def per_item_sql() -> str:
    # BEGIN SOLUTION
    return """
        select item, count(*) as n, round(sum(kg), 1) as kg
        from deliveries
        group by item
        order by item
    """
    # END SOLUTION


# %%
try:
    q3 = per_item_sql()
except NotImplementedError:
    q3 = "select item, count(*) as n, round(sum(kg), 1) as kg from deliveries group by item order by item"
r3 = duckdb.sql(q3).df()
G.check(list(r3.item) == list(r2.item) and list(r3.n) == list(r2.n), "SQL and pandas give the same counts per item")

# %% [markdown]
# ## 4 · An inner join, counted (15')
#
# ✏️ **Exercise** · Write `with_city(deliveries, depots)`: the deliveries with the `city` of their depot, by an
# **inner** join on `depot_id`.

# %%
def with_city(deliveries: pd.DataFrame, depots: pd.DataFrame) -> pd.DataFrame:
    # BEGIN SOLUTION
    return deliveries.merge(depots[["depot_id", "city"]], on="depot_id", how="inner")
    # END SOLUTION


# %%
try:
    r4 = with_city(deliveries, depots)
except NotImplementedError:
    r4 = deliveries.merge(depots[["depot_id", "city"]], on="depot_id", how="inner")
lost = len(deliveries) - len(r4)
print(f"rows in: {len(deliveries)} | rows out: {len(r4)} | lost: {lost}")
G.check("city" in r4.columns and lost > 0, f"the inner join lost {lost} deliveries and said nothing")

# %% [markdown]
# 🔍 The join ran without an error and some deliveries are gone. Which ones? An inner join never tells you.

# %% [markdown]
# ## 5 · A left join and the rows without a match (15')
#
# ✏️ **Exercise** · Write `unmatched(deliveries, depots)`: the deliveries whose `depot_id` has no row in
# `depots` (a left join with `indicator=True`, or an anti-join). Keep the columns of `deliveries`.

# %%
def unmatched(deliveries: pd.DataFrame, depots: pd.DataFrame) -> pd.DataFrame:
    # BEGIN SOLUTION
    m = deliveries.merge(depots[["depot_id"]], on="depot_id", how="left", indicator=True)
    return m[m["_merge"] == "left_only"].drop(columns="_merge")
    # END SOLUTION


# %%
try:
    r5 = unmatched(deliveries, depots)
except NotImplementedError:
    r5 = deliveries[~deliveries.depot_id.isin(depots.depot_id)]
print(r5.depot_id.replace("", "(blank)").value_counts().to_string())
G.check(len(r5) == lost, f"the {lost} lost deliveries are found: a blank key, or a depot that is not in the table")

# %% [markdown]
# ## 6 · A join that multiplies rows (20')
#
# Somebody appends a second row for depot `P03` to the depots table: the depot moved to another city.

# %%
depots2 = pd.concat([depots, pd.DataFrame([{"depot_id": "P03", "city": "East", "opened_year": 2025}])], ignore_index=True)
joined2 = deliveries.merge(depots2[["depot_id", "city"]], on="depot_id", how="left")
print(f"rows in: {len(deliveries)} | rows out of a LEFT join: {len(joined2)}")

# %% [markdown]
# A left join never loses a left row. It can **add** rows.
#
# ✏️ **Exercise** · Write `repeated_keys(table, key)`: the values of `key` that occur more than once in `table`,
# as a sorted list. Then explain to yourself how many rows the join added, and why exactly that many.

# %%
def repeated_keys(table: pd.DataFrame, key: str) -> list:
    # BEGIN SOLUTION
    n = table[key].value_counts()
    return sorted(n[n > 1].index)
    # END SOLUTION


# %%
try:
    r6 = repeated_keys(depots2, "depot_id")
except NotImplementedError:
    r6 = ["P03"]
added = len(joined2) - len(deliveries)
G.check(r6 == ["P03"] and added == int((deliveries.depot_id == "P03").sum()),
        f"P03 is in the depots table twice, so each of its {added} deliveries came out twice")
try:
    deliveries.merge(depots2[["depot_id", "city"]], on="depot_id", how="left", validate="many_to_one")
except pd.errors.MergeError as e:
    print("with validate='many_to_one' the join stops:", e)

# %% [markdown]
# ## 7 · Dates with an explicit format (15')
#
# `delivered_on` is text, written day/month/year.
#
# ✏️ **Exercise** · Write `per_month(deliveries)`: the number of deliveries per month (1 to 6), as a Series
# indexed by month. Parse the dates with an explicit `format=`; do not let pandas guess.

# %%
def per_month(deliveries: pd.DataFrame) -> pd.Series:
    # BEGIN SOLUTION
    d = pd.to_datetime(deliveries.delivered_on, format="%d/%m/%Y")
    return d.dt.month.value_counts().sort_index()
    # END SOLUTION


# %%
try:
    r7 = per_month(deliveries)
except NotImplementedError:
    r7 = pd.to_datetime(deliveries.delivered_on, format="%d/%m/%Y").dt.month.value_counts().sort_index()
print(r7.to_string())
G.check(list(r7.index) == [1, 2, 3, 4, 5, 6] and int(r7.sum()) == len(deliveries),
        "six months, and every delivery is in one of them")

# %% [markdown]
# 🔍 Read the same column as month/day/year: `pd.to_datetime(deliveries.delivered_on, format="%m/%d/%Y", errors="coerce")`.
# How many dates fail, and how many parse to a **wrong** day without any error? Day 2 returns to this.

# %% [markdown]
# ## 8 · A reconciliation in one function (15')
#
# ✏️ **Exercise** · Write `reconcile(deliveries, depots)`: a dictionary with `rows_in`, `matched`, `blank_key`,
# `unknown_key`, in which `matched + blank_key + unknown_key == rows_in`.

# %%
def reconcile(deliveries: pd.DataFrame, depots: pd.DataFrame) -> dict:
    # BEGIN SOLUTION
    blank = deliveries.depot_id.eq("")
    known = deliveries.depot_id.isin(depots.depot_id)
    return {"rows_in": len(deliveries), "matched": int(known.sum()), "blank_key": int(blank.sum()),
            "unknown_key": int((~known & ~blank).sum())}
    # END SOLUTION


# %%
try:
    r8 = reconcile(deliveries, depots)
except NotImplementedError:
    blank, known = deliveries.depot_id.eq(""), deliveries.depot_id.isin(depots.depot_id)
    r8 = {"rows_in": len(deliveries), "matched": int(known.sum()), "blank_key": int(blank.sum()),
          "unknown_key": int((~known & ~blank).sum())}
print(r8)
G.check(r8["matched"] + r8["blank_key"] + r8["unknown_key"] == r8["rows_in"] and r8["blank_key"] > 0,
        "rows in equal rows matched plus rows not matched, each with its reason")

# %% [markdown]
# ## Check yourself before the entry quiz
#
# 1. A left join of 600 rows to a lookup table returns 640 rows. What happened?
#    <details><summary>Answer</summary>Some keys occur more than once in the lookup table; every left row with
#    such a key came out once per match.</details>
# 2. An inner join of 600 rows returns 570. Name two different reasons a row can be lost.
#    <details><summary>Answer</summary>A blank key; a key that is not in the other table (unknown, or written
#    differently: a space, another letter case).</details>
# 3. After a group-by, which one check tells you no row was dropped or counted twice?
#    <details><summary>Answer</summary>The group counts add up to the number of rows of the table.</details>
# 4. `03/04/2026`: which date is it?
#    <details><summary>Answer</summary>It cannot be said from the value. The layout belongs to the source; state
#    it in the code with an explicit format.</details>
#
# If an exercise took you much longer than its minutes, repeat it with a table of your own before Day 1.
