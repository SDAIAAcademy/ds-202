"""The reference build of DS-202: the analysis dataset of Ghilal Food Bank Network from its raw sources.

    uv run python build_dataset.py                    # one command: raw files in, artifacts/build/ out
    uv run python build_dataset.py --write-reference  # course authors: also refresh data/reference/

It writes, into artifacts/build/: households.csv and handouts_q3.csv (the analysis dataset, with a keyed
pseudonym in place of every identifier), join_log.csv (row counts per step), set_aside.csv (rows left
out, each with its reason), rule_results.csv and quality_report.md. The labs import its steps as their
safety nets (`import build_dataset as B`); the capstone asks for a build of your own on a second extract.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import os
import re
import unicodedata
from pathlib import Path

import pandas as pd

import ghilal as G

KEY = os.environ.get("GHILAL_KEY", "ghilal-teaching-key-not-a-secret").encode()
INDIC = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
ARABIC = re.compile("[ء-ي]")
LB = 0.45359237
PER_PARCEL = (9.0, 15.0)   # kilograms in one parcel: the packing standard is 12


# ---- text ------------------------------------------------------------------------------------------------------

def norm_digits(s: str) -> str:
    return s.translate(INDIC)


def repair_text(s: str) -> str:
    """Undo text that was UTF-8, read as Windows-1256 and saved again. Unchanged when it was right."""
    try:
        fixed = s.encode("cp1256").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s
    return fixed


def norm_name(s: str) -> str:
    """A matching key for a name. The stored name is never replaced by it."""
    s = unicodedata.normalize("NFKC", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn").replace("ـ", "")
    s = re.sub("[أإآٱ]", "ا", s).replace("ى", "ي").replace("ة", "ه")
    s = re.sub(r"عبد\s+ال", "عبدال", s)
    return " ".join(s.casefold().replace("-", " ").split())


def norm_phone(s: str) -> str:
    d = re.sub(r"\D", "", norm_digits(s))
    return "0" + d[3:] if d.startswith("966") else d


def pseudonym(values: pd.Series, key: bytes = KEY) -> pd.Series:
    """A keyed hash (HMAC-SHA256, 16 hexadecimal characters). Without the key it cannot be recomputed."""
    return values.map(lambda v: hmac.new(key, str(v).encode(), hashlib.sha256).hexdigest()[:16])


# ---- the register ----------------------------------------------------------------------------------------------

def clean_registry(reg: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """Repair text and digits, type the columns and keep one row per household_id (the first registration)."""
    log = [dict(step="register rows read", rows=len(reg), note="")]
    r = reg.copy()
    fixed = r["head_name"].map(repair_text)
    n_fixed = int((fixed != r["head_name"]).sum())
    r["head_name"] = fixed
    indic = r["national_id"].str.contains("[٠-٩]", regex=True)
    r["national_id"] = r["national_id"].map(norm_digits)
    r["phone"] = r["phone"].map(norm_phone)
    r["registered_on"] = pd.to_datetime(r["registered_on"], format="%Y-%m-%d")
    r["household_size"] = pd.to_numeric(r["household_size"], errors="coerce").astype("Int64")
    r["monthly_income_sar"] = pd.to_numeric(r["monthly_income_sar"])
    log.append(dict(step="names repaired (decoded twice)", rows=len(r), note=f"{n_fixed} names"))
    log.append(dict(step="digits made Western", rows=len(r), note=f"{int(indic.sum())} national ids"))
    r = r.sort_values(["household_id", "registered_on"])
    out = r.drop_duplicates("household_id", keep="first").reset_index(drop=True)
    log.append(dict(step="one row per household_id", rows=len(out),
                    note=f"{len(r) - len(out)} later registrations of the same id set aside"))
    return out, log


# ---- the branch logs -------------------------------------------------------------------------------------------

def clean_key(k: str) -> str:
    """A household_id in its one form, H and six digits; anything else is returned as it came, stripped."""
    c = k.strip().upper().replace("-", "")
    if re.fullmatch(r"H[0-9O]{6}", c):
        c = "H" + c[1:].replace("O", "0")
    return c


def date_layouts(logs: pd.DataFrame) -> dict:
    """The date layout of each branch, decided from all its rows: a value alone cannot say."""
    out = {}
    for b, s in logs.groupby("branch_id")["handout_date"]:
        if s.str.fullmatch(r"\d{4}-\d{2}-\d{2}").all():
            out[b] = "%Y-%m-%d"
        else:
            first = s.str.slice(0, 2).astype(int).max()
            second = s.str.slice(3, 5).astype(int).max()
            assert (first > 12) != (second > 12), f"{b}: the layout cannot be decided"
            out[b] = "%d/%m/%Y" if first > 12 else "%m/%d/%Y"
    return out


def parse_dates(logs: pd.DataFrame) -> pd.Series:
    lay = date_layouts(logs)
    parts = [pd.to_datetime(s, format=lay[b]) for b, s in logs.groupby("branch_id")["handout_date"]]
    return pd.concat(parts).reindex(logs.index)


def to_kg(logs: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Weights in kilograms and, per row, the change that was made ('' when none)."""
    w = pd.to_numeric(logs["weight"], errors="coerce")
    n = pd.to_numeric(logs["parcels"])
    change = pd.Series("", index=logs.index)
    lb = logs["unit"].eq("lb")
    change[lb] = "pounds to kilograms"
    w = w.where(~lb, w * LB)
    per = w / n
    grams = per > 1000
    change[grams] = "grams to kilograms"
    w = w.where(~grams, w / 1000)
    mislabelled = (~lb) & (per > PER_PARCEL[0] * 2.2) & (per < PER_PARCEL[1] * 2.21)
    change[mislabelled] = "pounds labelled kg"
    w = w.where(~mislabelled, w * LB)
    change[w.isna()] = "weight missing, left missing"
    return w.round(2), change


def clean_logs(raw: pd.DataFrame, households: pd.DataFrame):
    """Exact copies dropped, keys repaired, dates and weights standardised, rows without a usable key set aside."""
    log = [dict(step="log rows read", rows=len(raw), note="14 branch files")]
    d = raw.drop_duplicates().copy()
    log.append(dict(step="exact copies dropped", rows=len(d), note=f"{len(raw) - len(d)} rows uploaded twice"))
    key = d["household_id"].map(clean_key)
    n_rep = int((key != d["household_id"]).sum())
    d["household_id"] = key
    log.append(dict(step="keys repaired", rows=len(d), note=f"{n_rep} keys: case, spaces, hyphen, letter O"))
    d["handout_date"] = parse_dates(d)
    d["weight_kg"], d["weight_change"] = to_kg(d)
    d["parcels"] = pd.to_numeric(d["parcels"])
    reg_on = households.set_index("household_id")["registered_on"]
    reason = pd.Series("", index=d.index)
    reason[d["household_id"].eq("")] = "blank key"
    reason[reason.eq("") & ~d["household_id"].isin(reg_on.index)] = "key not in the register"
    early = d["handout_date"] < d["household_id"].map(reg_on)
    reason[reason.eq("") & early] = "handout before registration"
    aside = d[reason.ne("")].assign(reason=reason[reason.ne("")])
    keep = d[reason.eq("")].drop(columns=["unit", "weight", "collected_by", "note"])
    for name, n in aside["reason"].value_counts().items():
        log.append(dict(step=f"set aside: {name}", rows=int(n), note="kept in set_aside.csv"))
    log.append(dict(step="log rows kept", rows=len(keep), note="every row has a household in the register"))
    return keep, aside, log


def join(logs: pd.DataFrame, households: pd.DataFrame) -> pd.DataFrame:
    """Each handout with its household. Many handouts to one household: pandas checks it."""
    cols = ["household_id", "district_id", "registered_on", "household_size", "monthly_income_sar", "status"]
    out = logs.merge(households[cols], on="household_id", how="left", validate="many_to_one", indicator=True)
    assert len(out) == len(logs) and out["_merge"].eq("both").all(), "a row was lost, added or left unmatched"
    return out.drop(columns="_merge")


def household_table(households: pd.DataFrame, joined: pd.DataFrame) -> pd.DataFrame:
    """The target population, one row each: active households registered before the quarter began."""
    q = joined[(joined["handout_date"] >= G.Q_START) & (joined["handout_date"] <= G.Q_END)]
    h = households[(households["status"] == "active") & (households["registered_on"] < G.Q_START)]
    h = h[["household_id", "district_id", "branch_id", "channel", "registered_on", "household_size",
           "monthly_income_sar"]].copy()
    h["parcels_q3"] = h["household_id"].map(q.groupby("household_id")["parcels"].sum()).fillna(0).astype(int)
    usual = joined.groupby("household_id")["parcels"].agg(lambda s: s.mode().iloc[0])
    h["usual_parcels"] = h["household_id"].map(usual).astype("Int64")
    h["registered_on"] = h["registered_on"].dt.strftime("%Y-%m-%d")
    return h.reset_index(drop=True)


def joined_table(joined: pd.DataFrame) -> pd.DataFrame:
    """Day 4's table: the quarter's handouts with their household's fields, identifiers replaced by a keyed hash."""
    q = joined[(joined["handout_date"] >= G.Q_START) & (joined["handout_date"] <= G.Q_END)].copy()
    elig = (q["monthly_income_sar"] / q["household_size"].astype("Float64") <= G.THRESHOLD_SAR).astype("Int64")
    return pd.DataFrame({
        "log_id": q["log_id"], "household_key": pseudonym(q["household_id"]), "branch_id": q["branch_id"],
        "district_id": q["district_id"], "handout_date": q["handout_date"].dt.strftime("%Y-%m-%d"),
        "registered_on": q["registered_on"].dt.strftime("%Y-%m-%d"), "parcels": q["parcels"],
        "weight_kg": q["weight_kg"], "household_size": q["household_size"], "eligible": elig}).reset_index(drop=True)


# ---- rules -----------------------------------------------------------------------------------------------------

DISTRICTS = [f"D{i:02d}" for i in range(1, 31)]
ISO = r"^\d{4}-\d{2}-\d{2}$"


def schema():
    """The column rules of the joined table: type, range, uniqueness, completeness (Lab 4.1)."""
    import pandera.pandas as pa

    def c(check, name):
        check.name, check.error = name, name
        return check

    return pa.DataFrameSchema({
        "log_id": pa.Column(str, [c(pa.Check.str_matches(r"^B\d{2}-\d{7}$"), "validity: log_id has the branch form")],
                            unique=True),
        "household_key": pa.Column(str, [c(pa.Check.str_matches(r"^[0-9a-f]{16}$"),
                                           "validity: household_key is a 16-character pseudonym")]),
        "branch_id": pa.Column(str, [c(pa.Check.isin(G.BRANCHES), "validity: branch_id is one of the 14 branches")]),
        "district_id": pa.Column(str, [c(pa.Check.isin(DISTRICTS), "validity: district_id is one of the 30 districts")]),
        "handout_date": pa.Column(str, [c(pa.Check.str_matches(ISO), "type: handout_date is a date written YYYY-MM-DD")]),
        "registered_on": pa.Column(str, [c(pa.Check.str_matches(ISO), "type: registered_on is a date written YYYY-MM-DD")]),
        "parcels": pa.Column(int, [c(pa.Check.in_range(1, 3), "validity: parcels between 1 and 3")]),
        "weight_kg": pa.Column(float, [c(pa.Check.in_range(5, 50), "validity: weight_kg between 5 and 50")],
                               nullable=True),
        "household_size": pa.Column("Int64", [c(pa.Check.in_range(1, 20), "validity: household_size between 1 and 20")],
                                    nullable=True),
        "eligible": pa.Column("Int64", [c(pa.Check.isin([0, 1]), "validity: eligible is 0 or 1")], nullable=True),
    }, strict=True, coerce=True)


def run_schema(df: pd.DataFrame, sch=None) -> pd.DataFrame:
    """Run the column rules lazily and return one line per failing rule: rule, column, rows, examples."""
    import pandera.errors as pe
    try:
        (sch or schema()).validate(df, lazy=True)
        return pd.DataFrame(columns=["rule", "column", "rows", "examples"])
    except pe.SchemaErrors as e:
        f = e.failure_cases.copy()
        f["check"] = f["check"].astype(str)
        f["check"] = f["check"].replace({"field_uniqueness": "uniqueness: no value repeats",
                                         "not_nullable": "completeness: no value is missing"})
        f.loc[f["check"].str.startswith(("dtype(", "coerce_dtype(")), "check"] = "type: value has the column's type"
        g = f.groupby(["check", "column"], dropna=False)
        out = g.agg(rows=("failure_case", "size"),
                    examples=("failure_case", lambda s: ", ".join(map(str, s.dropna().unique()[:3])))).reset_index()
        return out.rename(columns={"check": "rule"}).sort_values("rows", ascending=False).reset_index(drop=True)


def consistency(df: pd.DataFrame, donated: pd.DataFrame | None = None) -> pd.DataFrame:
    """The three consistency rules of Lab 4.2: two across fields, one across sources."""
    d = df.copy()
    hd = pd.to_datetime(d["handout_date"], errors="coerce", format="%Y-%m-%d")
    ro = pd.to_datetime(d["registered_on"], errors="coerce", format="%Y-%m-%d")
    w, n = pd.to_numeric(d["weight_kg"], errors="coerce"), pd.to_numeric(d["parcels"], errors="coerce")
    rows = []
    bad = d[hd < ro]
    rows.append(("consistency: handout on or after registration", len(bad), ", ".join(bad["log_id"].head(3))))
    per = w / n.where(n.between(1, 3))
    bad = d[per.notna() & ~per.between(*PER_PARCEL)]
    rows.append((f"consistency: {PER_PARCEL[0]:g} to {PER_PARCEL[1]:g} kg per parcel", len(bad),
                 ", ".join(f"{a} ({b:.1f} kg per parcel)" for a, b in zip(bad["log_id"].head(3), per[bad.index].head(3)))))
    if donated is not None:
        out = d.assign(w=w).groupby("branch_id")["w"].sum().rename("handed_kg").to_frame().join(
            donated.set_index("branch_id")["donated_kg"])
        over = out[out["handed_kg"] > out["donated_kg"]]
        rows.append(("consistency across sources: a branch hands out no more than it received", len(over),
                     ", ".join(f"{b}: handed {r.handed_kg:,.0f} kg, received {r.donated_kg:,.0f} kg"
                               for b, r in over.head(3).iterrows())))
    return pd.DataFrame(rows, columns=["rule", "rows", "examples"])


# ---- the one command -------------------------------------------------------------------------------------------

def build(write_reference: bool = False) -> dict:
    out = G.lab_dir("build")
    households, log = clean_registry(G.registry_text())
    logs, aside, log2 = clean_logs(G.logs_raw(), households)
    joined = join(logs, households)
    log += log2 + [dict(step="joined to the register", rows=len(joined), note="many handouts to one household")]
    hh = household_table(households, joined)
    jq = joined_table(joined)
    log.append(dict(step="handouts of the quarter", rows=len(jq), note=f"{G.Q_START} to {G.Q_END}"))
    log.append(dict(step="households of the target population", rows=len(hh),
                    note="active, registered before the quarter"))
    join_log = pd.DataFrame(log)
    rules = pd.concat([run_schema(jq).drop(columns="column"), consistency(jq)], ignore_index=True)
    missing = round(100 * hh["household_size"].isna().mean(), 1)
    est = G.estimate(hh, hh["household_size"])
    published = hh.assign(household_key=pseudonym(hh["household_id"]),
                          registered_month=hh["registered_on"].str.slice(0, 7))
    published = published[["household_key", "district_id", "branch_id", "channel", "registered_month",
                           "household_size", "monthly_income_sar", "parcels_q3"]]
    published.to_csv(out / "households.csv", index=False)
    jq.drop(columns=["registered_on"]).to_csv(out / "handouts_q3.csv", index=False)
    join_log.to_csv(out / "join_log.csv", index=False)
    aside.drop(columns=["collected_by"]).to_csv(out / "set_aside.csv", index=False)
    rules.to_csv(out / "rule_results.csv", index=False)
    report = ["# Data-quality report: parcels per eligible household, Q3 2026", "",
              "Built from the raw sources by `build_dataset.py`. Synthetic data.", "",
              "## Row counts per step", "", "| Step | Rows | Note |", "|---|---|---|"]
    report += [f"| {r.step} | {r.rows:,} | {r.note} |" for r in join_log.itertuples()]
    report += ["", "## Rules", "", f"{len(rules[rules['rows'] > 0])} of the rules report failing rows on this build.",
               "", "## Known limits", "",
               f"- household_size is missing for {missing}% of the target population; the complete-case estimate is "
               f"{est} parcels per eligible household per month and is not the recommended figure (see Day 3).",
               "- Branch B12 sent no log rows for 10 to 18 August 2026.",
               "- The open district table describes 2022 and has no row for districts D29 and D30."]
    (out / "quality_report.md").write_text("\n".join(report) + "\n", encoding="utf-8", newline="\n")
    if write_reference:
        hh.to_csv(G.REF / "household_q3.csv.gz", index=False, compression={"method": "gzip", "mtime": 0})
        jq.to_csv(G.REF / "joined_q3.csv.gz", index=False, compression={"method": "gzip", "mtime": 0})
        join_log.to_csv(G.REF / "join_log.csv", index=False, lineterminator="\n")
        don = donations_by_branch()
        don.to_csv(G.REF / "donated_kg_q3.csv", index=False, lineterminator="\n")
    return dict(join_log=join_log, rules=rules, households=hh, joined=jq, set_aside=aside, estimate=est,
                missing_pct=missing)


def donations_by_branch() -> pd.DataFrame:
    """Kilograms received per branch in the quarter, from the donations file the API serves."""
    d = pd.read_json(G.RAW / "donations" / "donations.jsonl.gz", lines=True, dtype=False, convert_dates=False).drop_duplicates("donation_id")
    d = d[(d["received_at"].str.slice(0, 10) >= G.Q_START) & (d["received_at"].str.slice(0, 10) <= G.Q_END)]
    kg = d["weight"].where(d["unit"] == "kg", d["weight"] * LB)
    return kg.groupby(d["branch_id"]).sum().round(1).rename("donated_kg").reset_index()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Build the analysis dataset from the raw sources.")
    ap.add_argument("--write-reference", action="store_true", help="also refresh data/reference/")
    r = build(ap.parse_args().write_reference)
    print(r["join_log"].to_string(index=False))
    print()
    print(r["rules"].to_string(index=False) if len(r["rules"]) else "every rule passes")
    print(f"\nhousehold_size missing: {r['missing_pct']}% | complete-case estimate: {r['estimate']}")
    print("written to", Path("artifacts/build").as_posix())
