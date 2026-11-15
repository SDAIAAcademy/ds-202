# %% [markdown]
# # Lab 4.3 · A pseudonym that holds
#
# Day 4 · Session 3 (Minimise and pseudonymise) · 25 min.
#
# A partner charity asks for a household-level table so that the two organisations can count households they
# both serve. A linking key is needed; the national ID number must not travel. A colleague proposes to send the
# SHA-256 hash of each ID number, "because a hash cannot be reversed". You attack that table twice, replace the
# hash by a keyed one, and then attempt re-linkage a third way, through the ordinary fields that travel with it.
#
# **AI-off** for the first attempt. Every ID number here is synthetic: drawn at random, belonging to nobody.
#
# **Reference state.** The cleaned register (`B.clean_registry`, the reference step of Lab 2.1): 39,820 households, 37,333 of them active.
#
# **Tasks**
# - [ ] 1 · A plain hash and a list attack (6')
# - [ ] 2 · Enumerate the id space (5')
# - [ ] 3 · A keyed hash (6')
# - [ ] 4 · Re-link through quasi-identifiers, then generalise (8')
# - [ ] ✱ Stretch · Change the key: what breaks, and what should

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
import hmac
import secrets
import time
import pandas as pd
import ghilal as G
import build_dataset as B   # the reference build: its cleaned register is the starting point of this lab

reg, _ = B.clean_registry(G.registry_text())
reg = reg[reg.status == "active"].reset_index(drop=True)
print(f"{len(reg):,} active households | example id (synthetic): {reg.national_id.iloc[0]}")

# %% [markdown]
# ## 1 · A plain hash and a list attack (6')
#
# ✏️ **Exercise** · Write `plain_hash(s)`: the SHA-256 of the text `s`, as 64 hexadecimal characters.

# %%
def plain_hash(s: str) -> str:
    # BEGIN SOLUTION
    return hashlib.sha256(s.encode()).hexdigest()
    # END SOLUTION


# %%
# Check, with a safety net: the cells below still run when the exercise is not done yet
try:
    plain_hash("x")
except NotImplementedError:
    plain_hash = lambda s: hashlib.sha256(s.encode()).hexdigest()  # noqa: E731
G.check(plain_hash("1090000001") == hashlib.sha256(b"1090000001").hexdigest() and len(plain_hash("1")) == 64,
        "the same input always gives the same 64 characters, for everyone")
shared = pd.DataFrame({"id_hash": reg.national_id.map(plain_hash), "district_id": reg.district_id,
                       "registered_on": reg.registered_on.dt.strftime("%Y-%m-%d"), "household_size": reg.household_size})
print(shared.head(3).to_string(index=False))

# %% [markdown]
# The table that would be sent: no name, no number. Now be the other side. Somebody holds a list of 5,000 people
# with their ID numbers: an old contact list, a leaked file. (Here: 5,000 rows of the register, names included.)
#
# ✏️ **Exercise** · Write `list_attack(shared, known)`: hash the ID numbers of `known` and join them to `shared`.
# Return the joined table: each row is a person re-identified, with name, district and household size.

# %%
known = reg.sample(5000, random_state=4)[["national_id", "head_name"]]


def list_attack(shared: pd.DataFrame, known: pd.DataFrame) -> pd.DataFrame:
    # BEGIN SOLUTION
    k = known.assign(id_hash=known.national_id.map(plain_hash))
    return k.merge(shared, on="id_hash", how="inner")
    # END SOLUTION


# %%
try:
    hit = list_attack(shared, known)
except NotImplementedError:
    hit = known.assign(id_hash=known.national_id.map(plain_hash)).merge(shared, on="id_hash")
print(f"re-identified: {len(hit):,} of {len(known):,} people on the list")
G.check(len(hit) == len(known), "a plain hash is re-linked by anyone who holds the identifiers: 100% of the list")

# %% [markdown]
# ## 2 · Enumerate the id space (5')
#
# Without any list: an ID number is ten digits. The attacker hashes **every possible number** and looks each
# hash up. The synthetic numbers of this course were drawn from a range of two million
# (1,090,000,000 to 1,091,999,999) so that the whole attack runs in seconds; measure the rate, then compute
# what a full ten-digit space would take at that rate.
#
# ✏️ **Exercise** · Write `enumerate_ids(shared, start, stop)`: hash every number from `start` up to `stop`
# (exclusive) and return the dictionary `{id_hash: national_id}` for the hashes found in `shared`.

# %%
def enumerate_ids(shared: pd.DataFrame, start: int, stop: int) -> dict:
    # BEGIN SOLUTION
    wanted = set(shared.id_hash)
    found = {}
    for n in range(start, stop):
        hx = hashlib.sha256(str(n).encode()).hexdigest()
        if hx in wanted:
            found[hx] = str(n)
    return found
    # END SOLUTION


# %%
START, STOP = 1_090_000_000, G.pick(1_092_000_000, 1_090_200_000)
t0 = time.perf_counter()
try:
    found = enumerate_ids(shared, START, STOP)
except NotImplementedError:
    wanted = set(shared.id_hash)
    found = {hx: str(n) for n in range(START, STOP) if (hx := hashlib.sha256(str(n).encode()).hexdigest()) in wanted}
secs = time.perf_counter() - t0
rate = (STOP - START) / secs
in_range = int(reg.national_id.astype("int64").between(START, STOP - 1).sum())
print(f"{STOP - START:,} candidates hashed in {secs:.1f} s ({rate:,.0f} per second): {len(found):,} households recovered")
print(f"at this rate the full ten-digit space (10,000,000,000 numbers) takes about {1e10 / rate / 3600:.1f} hours "
      f"on this one processor core")
G.check(len(found) == in_range, f"every household whose number lies in the range was recovered: {len(found):,} of {in_range:,}")

# %% [markdown]
# 🔍 The space of possible identifiers is small enough to try them all. Hashing does not hide a value that can
# be guessed; adding the same fixed text to every number before hashing changes nothing, once that text is known.

# %% [markdown]
# ## 3 · A keyed hash (6')
#
# A keyed hash (HMAC) mixes a **secret key** into the hash. Without the key nobody can compute the pseudonym of
# a candidate number, so neither attack starts. The key is the "additional information" that the guideline on
# pseudonymisation requires to be kept separately, under its own controls. It is never committed and never sent.
#
# ✏️ **Exercise** · Write `pseudonym(s, key)`: HMAC-SHA256 of `s` under `key` (bytes), first 16 hexadecimal
# characters.

# %%
key = secrets.token_bytes(32)                      # made here, kept in memory; in a project: an environment
(G.lab_dir("D4_3") / "README.txt").write_text(     # variable or a secrets store, outside the repository
    "The key of this lab lives in memory only. Nothing in this folder may hold it.\n", encoding="utf-8")


def pseudonym(s: str, key: bytes) -> str:
    # BEGIN SOLUTION
    return hmac.new(key, s.encode(), hashlib.sha256).hexdigest()[:16]
    # END SOLUTION


# %%
try:
    pseudonym("x", key)
except NotImplementedError:
    pseudonym = lambda s, key: hmac.new(key, s.encode(), hashlib.sha256).hexdigest()[:16]  # noqa: E731
shared2 = shared.assign(id_hash=reg.national_id.map(lambda s: pseudonym(s, key))).rename(columns={"id_hash": "household_key"})
attack = known.assign(household_key=known.national_id.map(plain_hash).str.slice(0, 16)).merge(shared2, on="household_key")
guess = known.assign(household_key=known.national_id.map(lambda s: pseudonym(s, b"a guessed key"))).merge(shared2, on="household_key")
print(f"list attack without the key: {len(attack)} re-identified | with a guessed key: {len(guess)}")
G.check(len(attack) == 0 and len(guess) == 0 and shared2.household_key.is_unique
        and pseudonym("1090000001", key) == pseudonym("1090000001", key),
        "without the key nothing links; with it, the pseudonym is stable and unique, so tables still join")

# %% [markdown]
# ## 4 · Re-link through quasi-identifiers, then generalise (8')
#
# The key holds. The table still carries the district, the exact registration date and the household size.
# Someone who knows a neighbour ("they live in D09, registered on 14 March 2024, seven of them") needs no key.
# A combination of ordinary fields that singles a household out is a **quasi-identifier**.
#
# ✏️ **Exercise** · Write `unique_share(df, cols)`: the share of rows whose combination of `cols` occurs exactly
# once, rounded to 3 decimals.

# %%
def unique_share(df: pd.DataFrame, cols: list) -> float:
    # BEGIN SOLUTION
    n = df.groupby(cols, dropna=False)[cols[0]].transform("size")
    return round(float((n == 1).mean()), 3)
    # END SOLUTION


# %%
def _us(df, cols):
    return round(float((df.groupby(cols, dropna=False)[cols[0]].transform("size") == 1).mean()), 3)


try:
    u_exact = unique_share(shared2, ["district_id", "registered_on", "household_size"])
except NotImplementedError:
    unique_share = _us
    u_exact = _us(shared2, ["district_id", "registered_on", "household_size"])
general = shared2.assign(
    registered_year=shared2.registered_on.str.slice(0, 4),
    size_band=pd.cut(shared2.household_size.astype("Float64"), [0, 4, 8, 99], labels=["1 to 4", "5 to 8", "9 or more"])
    .astype(str).replace("nan", "not recorded")).drop(columns=["registered_on", "household_size"])
u_general = unique_share(general, ["district_id", "registered_year", "size_band"])
smallest = int(general.groupby(["district_id", "registered_year", "size_band"]).size().min())
table = pd.DataFrame([("district, exact date, exact size", u_exact),
                      ("district, year, size band", u_general)], columns=["fields that travel", "share of households singled out"])
print(table.to_string(index=False))
print(f"smallest group after generalising: {smallest} households")
table.to_csv(G.lab_dir("D4_3") / "uniqueness.csv", index=False)
G.keep("d4_3_uniqueness", {"exact": u_exact, "generalised": u_general, "smallest_group": smallest})
G.check(u_exact > 0.5 and u_general < 0.01, f"singled out: {u_exact:.1%} with exact fields, {u_general:.1%} after generalising")

# %% [markdown]
# 🔍 Generalising cost the partner nothing it needs to count shared households, and it removed almost every
# household that could be singled out. The table is still personal data: pseudonymised data can be linked back
# by whoever holds the key. It travels under an agreement, to named people, for one purpose.

# %% [markdown]
# ## ✱ Stretch · Change the key: what breaks, and what should
#
# Compute the pseudonyms again with a new key. Do the two tables still join? When is that a problem, and when
# is it exactly what you want?

# %%
def rotate() -> dict:
    # BEGIN SOLUTION
    k2 = secrets.token_bytes(32)
    new = reg.national_id.map(lambda s: pseudonym(s, k2))
    return {"pseudonyms shared by old and new table": int(new.isin(shared2.household_key).sum()),
            "still unique": bool(new.is_unique),
            "meaning": "a table made with the old key no longer links to a new one: wanted between two recipients, "
                       "a problem between two builds of the same dataset"}
    # END SOLUTION


try:
    print(rotate())
except NotImplementedError:
    print("✱ Stretch not attempted")

# %% [markdown]
# ## Verification note
#
# The last step of every lab: what this run verified, and what the lab did not verify. The cell writes
# `artifacts/D4_3/verification.md`. Read the last line and add one of your own.

# %%
note = G.verification_note("D4_3", "re-linkage by somebody who holds other data about the households: uniqueness on three fields is a first measure, not a guarantee")

# %% [markdown]
# ## Checkpoint
#
# 1. "A hash cannot be reversed." True, and beside the point. Why?
#    <details><summary>Answer</summary>Nobody reverses it. They hash candidate identifiers and compare: a known list,
#    or every possible number. The same input gives the same hash for everyone.</details>
# 2. Where does the key live in a project that rebuilds with one command?
#    <details><summary>Answer</summary>Outside the repository: an environment variable or a secrets store read at
#    build time. Whoever can read the repository must not be able to recompute a pseudonym.</details>
# 3. The pseudonymised table has no name and no number. Is it anonymous?
#    <details><summary>Answer</summary>No. It is pseudonymised: the key links it back, and exact dates and sizes
#    single households out. Generalise what travels, and treat the table as personal data.</details>
#
# **Carry forward.** `artifacts/D4_3/uniqueness.csv`. The reference build uses the same keyed hash for
# `household_key`, with a key read from the environment variable `GHILAL_KEY`.
