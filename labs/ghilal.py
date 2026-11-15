"""Shared helpers of the DS-202 labs (case: Ghilal Food Bank Network).

    import ghilal as G
    G.registry_text()        # the register extract, decoded line by line, every column as text
    G.registry()             # the same as a table `registrations` in an in-memory DuckDB database
    G.logs_raw()             # the 14 branch log files, every column as text, 210,000 rows
    G.population()           # the open district table of 2022
    G.start_api()            # the local donations API; returns its base address. G.stop_api() ends it
    G.households_q3()        # reference state of Day 3: one row per household of the target population
    G.joined_q3()            # reference state of Day 4: one row per Q3 handout, joined to its household
    G.check(cond, "message") # prints a pass or a fail mark, never stops the notebook
    G.reference("name")      # a supplied reference result, for the safety-net cells
    G.lab_dir("D2_2")        # artifacts/<lab>/: where a lab writes its own files
"""

from __future__ import annotations

import gzip
import io
import json
import os
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

LABS = Path(__file__).resolve().parent
DATA = LABS / "data"
RAW = DATA / "raw"
DOCS = DATA / "docs"
REF = DATA / "reference"
QUICK = os.environ.get("GH_QUICK", "") not in ("", "0")
BRANCHES = [f"B{i:02d}" for i in range(1, 15)]
THRESHOLD_SAR = 1000     # eligible: monthly income per household member at or below this
STANDARD = 2.0           # the network's service standard: parcels per eligible household per month
Q_START, Q_END = "2026-07-01", "2026-09-30"
_api = {}


def pick(full, quick):
    """The small value in quick mode (GH_QUICK=1), the full one otherwise."""
    return quick if QUICK else full


def ensure_data():
    """Write data/raw/ with the generator if it is missing (a clone has it; this is a fallback)."""
    if not (RAW / "registry" / "registrations_extract.csv.gz").exists():
        import prepare_data
        prepare_data.build()


_checks: list = []


def check(ok, message: str) -> bool:
    _checks.append((bool(ok), message))
    print(("✅ " if ok else "❌ ") + message)
    return bool(ok)


def verification_note(lab: str, not_verified: str) -> str:
    """The last step of every lab: what this run verified (its check lines) and what the lab did not verify.
    Written to artifacts/<lab>/verification.md and printed."""
    lines = [f"# Verification note · Lab {lab[1]}.{lab[3]}", "", "Verified in this run:"]
    lines += [f"- [{'x' if ok else ' '}] {m}" for ok, m in _checks] or ["- nothing was checked"]
    lines += ["", f"Not verified by this lab: {not_verified}."]
    text = "\n".join(lines) + "\n"
    (lab_dir(lab) / "verification.md").write_text(text, encoding="utf-8", newline="\n")
    print(text)
    return text


def reference(name: str):
    """A reference result from data/reference/ (JSON, or a table as CSV)."""
    p = REF / f"{name}.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    for ext in (".csv.gz", ".csv"):
        if (REF / f"{name}{ext}").exists():
            import pandas as pd
            return pd.read_csv(REF / f"{name}{ext}", dtype=str, keep_default_na=False)
    raise FileNotFoundError(f"no reference named {name} in data/reference/")


def keep(name: str, value):
    """Used by the course authors: with GH_WRITE_REF=1 a solution run stores its result as a reference."""
    if os.environ.get("GH_WRITE_REF", "") in ("", "0"):
        return value
    REF.mkdir(parents=True, exist_ok=True)
    (REF / f"{name}.json").write_text(json.dumps(value, ensure_ascii=False, indent=1, default=str) + "\n",
                                      encoding="utf-8", newline="\n")
    return value


def lab_dir(name: str) -> Path:
    p = LABS / "artifacts" / name
    p.mkdir(parents=True, exist_ok=True)
    return p


# ---- the four sources ------------------------------------------------------------------------------------------

def registry_bytes() -> list[bytes]:
    """The register extract as it arrived: a header line, then one line of bytes per registration."""
    ensure_data()
    with gzip.open(RAW / "registry" / "registrations_extract.csv.gz", "rb") as f:
        return f.read().split(b"\n")[:-1]


def decode_line(b: bytes) -> tuple[str, str]:
    """A line as text and the encoding that read it: UTF-8 when it is valid UTF-8, else Windows-1256."""
    try:
        return b.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return b.decode("cp1256"), "cp1256"


def registry_text():
    """The register extract as a table of text columns. Lines are decoded one by one (Lab 2.1 opens this up)."""
    import pandas as pd
    text = "\n".join(decode_line(b)[0] for b in registry_bytes())
    return pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)


def registry():
    """An in-memory DuckDB database with the table `registrations` (text columns) and `districts_open`."""
    import duckdb
    reg, pop = registry_text(), population()  # noqa: F841 (DuckDB reads the two frames by name)
    con = duckdb.connect()
    con.execute("CREATE TABLE registrations AS SELECT * FROM reg")
    con.execute("CREATE TABLE districts_open AS SELECT * FROM pop")
    return con


def log_bytes(branch: str) -> bytes:
    ensure_data()
    return gzip.decompress((RAW / "branch_logs" / f"{branch}.csv.gz").read_bytes())


def read_log(branch: str):
    """One branch's log as text columns, in the encoding the file is really in."""
    import pandas as pd
    raw = log_bytes(branch)
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1256")
    df = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    df.insert(1, "branch_id", branch)
    return df


def logs_raw(branches=None):
    """All branch logs appended, every column as text: 210,000 rows from 14 files."""
    import pandas as pd
    return pd.concat([read_log(b) for b in (branches or BRANCHES)], ignore_index=True)


def population():
    import pandas as pd
    ensure_data()
    return pd.read_csv(RAW / "open" / "district_population_2022.csv", dtype={"district_id": str})


def audit():
    import pandas as pd
    return pd.read_csv(RAW / "registry" / "audit_resurvey.csv", dtype={"household_id": str})


def households_q3():
    """Day 3's reference state: the target population (active, registered before 1 July 2026), one row each."""
    import pandas as pd
    df = pd.read_csv(REF / "household_q3.csv.gz", dtype={"household_id": str})
    df["household_size"] = df["household_size"].astype("Int64")
    df["usual_parcels"] = df["usual_parcels"].astype("Int64")
    return df


def sealed():
    """What only the generator knows: the size each household would have reported, and its true size.
    Used in the last cell of a lab to show how far each method landed from the value it was after."""
    import pandas as pd
    return pd.read_csv(REF / "sealed_sizes.csv.gz", dtype={"household_id": str})


def joined_q3():
    """Day 4's reference state: one row per Q3 handout joined to its household, keys pseudonymised."""
    import pandas as pd
    return pd.read_csv(REF / "joined_q3.csv.gz", dtype={"household_key": str, "household_size": "Int64", "eligible": "Int64"})


def estimate(df, size, by=None):
    """Parcels per eligible household per month in the quarter. `size` is a column of household sizes;
    a household with no size is left out. With by="district_id", one value per district."""
    import pandas as pd
    size = pd.to_numeric(size, errors="coerce")
    d = df.assign(_e=(df["monthly_income_sar"] / size) <= THRESHOLD_SAR)[size.notna().to_numpy()]
    d = d[d["_e"]]
    if by:
        return (d.groupby(by)["parcels_q3"].sum() / d.groupby(by).size() / 3).round(3)
    return round(float(d["parcels_q3"].sum() / len(d) / 3), 3) if len(d) else float("nan")


# ---- the local donations API -----------------------------------------------------------------------------------

def start_api() -> str:
    """Start the donations API on this computer, on a free port, and return its base address."""
    if "server" not in _api:
        import donations_api
        ensure_data()
        _api["server"] = donations_api.make_server(RAW / "donations" / "donations.jsonl.gz")
        threading.Thread(target=_api["server"].serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{_api['server'].server_address[1]}"


def stop_api():
    s = _api.pop("server", None)
    if s:
        s.shutdown()
        s.server_close()


def get_json(url: str, retries: int = 3, wait: float = 0.2):
    """GET a JSON document, trying again after a failure that the server calls temporary (503)."""
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=10) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code != 503 or attempt == retries:
                raise
            time.sleep(wait * (attempt + 1))


# ---- provenance ------------------------------------------------------------------------------------------------

LEVELS = ["Top Secret", "Secret", "Restricted", "Public"]
PROVENANCE_FIELDS = ["origin", "owner", "coverage", "sharing_basis", "refresh_date", "limits", "classification"]


def review_provenance(rec: dict) -> list[str]:
    """The reviewer checklist for one provenance record. An empty list means the record passes."""
    import datetime as dt
    import re
    bad = [f"{k}: missing" for k in PROVENANCE_FIELDS if k not in rec]
    if bad:
        return bad
    for k in ("origin", "owner", "coverage", "sharing_basis"):
        if not isinstance(rec[k], str) or len(rec[k].strip()) < 12:
            bad.append(f"{k}: say it in a full phrase a stranger could act on")
    if not re.search(r"(19|20)\d\d", str(rec["coverage"])):
        bad.append("coverage: name the period the data cover, with its years")
    try:
        dt.date.fromisoformat(str(rec["refresh_date"]))
    except ValueError:
        bad.append("refresh_date: one date, written YYYY-MM-DD")
    if not isinstance(rec["limits"], list) or len(rec["limits"]) < 2 or any(len(str(x)) < 12 for x in rec["limits"]):
        bad.append("limits: at least two, each a full phrase")
    if rec["classification"] not in LEVELS:
        bad.append("classification: one of " + ", ".join(LEVELS))
    elif rec["classification"] != "Public" and not re.search("approval|agreement|consent", str(rec["sharing_basis"]), re.I):
        bad.append("sharing_basis: data that are not public need the approval, agreement or consent that lets you use them")
    return bad


# ---- Day 3 ------------------------------------------------------------------------------------------------------

def impute_within_groups(h):
    """Household sizes with each blank replaced by the median recorded size of households that usually receive
    the same number of parcels per handout (0 when a household has no handout at all). The reference step of
    Lab 3.2; Labs 3.3 and 3.4 start from it."""
    group = h["usual_parcels"].fillna(0).astype(int)
    med = h["household_size"].groupby(group).median().round().astype(int)
    return h["household_size"].fillna(group.map(med)).astype(int)
