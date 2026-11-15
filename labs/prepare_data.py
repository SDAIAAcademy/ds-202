"""The data generator of DS-202 (case: Ghilal Food Bank Network). Standard library only.

    uv run python prepare_data.py             # rewrites data/raw/ and the generator's reference files
    uv run python prepare_data.py --capstone  # writes capstone/raw/: a second extract, other faults

Everything is synthetic and deterministic: the same seed gives the same bytes on every run.
No row describes a real person, and no national ID number here is a real one.
The planted problems are listed in solutions/answer_key.md, with the lab that finds each.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import io
import json
import math
import random
from collections import defaultdict
from pathlib import Path

LABS = Path(__file__).resolve().parent
THRESHOLD_SAR = 1000          # eligible: monthly income per household member at or below this
Q_START, Q_END = dt.date(2026, 7, 1), dt.date(2026, 9, 30)

FIRST = [("محمد", "Mohammed"), ("أحمد", "Ahmed"), ("عبدالله", "Abdullah"), ("عبدالرحمن", "Abdulrahman"),
         ("إبراهيم", "Ibrahim"), ("علي", "Ali"), ("عمر", "Omar"), ("خالد", "Khalid"), ("سعد", "Saad"),
         ("فهد", "Fahad"), ("سلمان", "Salman"), ("ناصر", "Nasser"), ("يوسف", "Yousef"), ("حسن", "Hassan"),
         ("صالح", "Saleh"), ("ماجد", "Majed"), ("تركي", "Turki"), ("بندر", "Bandar"), ("مشعل", "Mishal"),
         ("عبدالعزيز", "Abdulaziz"), ("سلطان", "Sultan"), ("نايف", "Naif"), ("حمد", "Hamad"), ("زياد", "Ziyad")]
FIRST_F = [("فاطمة", "Fatimah"), ("نورة", "Noura"), ("عائشة", "Aisha"), ("مريم", "Mariam"), ("سارة", "Sara"),
           ("هدى", "Huda"), ("منى", "Mona"), ("أمل", "Amal"), ("ليلى", "Layla"), ("حصة", "Hessa"),
           ("جميلة", "Jamila"), ("خديجة", "Khadijah")]
FAMILY = [("الحربي", "Al-Harbi"), ("العتيبي", "Al-Otaibi"), ("القحطاني", "Al-Qahtani"), ("الغامدي", "Al-Ghamdi"),
          ("الزهراني", "Al-Zahrani"), ("الشهري", "Al-Shehri"), ("الدوسري", "Al-Dosari"), ("المطيري", "Al-Mutairi"),
          ("الشمري", "Al-Shammari"), ("العنزي", "Al-Anazi"), ("المالكي", "Al-Maliki"), ("الأحمدي", "Al-Ahmadi"),
          ("السبيعي", "Al-Subaie"), ("البلوي", "Al-Balawi"), ("الجهني", "Al-Juhani"), ("العمري", "Al-Amri"),
          ("الرشيدي", "Al-Rashidi"), ("اليامي", "Al-Yami"), ("الخالدي", "Al-Khaldi"), ("التميمي", "Al-Tamimi"),
          ("الحازمي", "Al-Hazmi"), ("الفيفي", "Al-Faifi"), ("السلمي", "Al-Sulami"), ("الثبيتي", "Al-Thubaiti"),
          ("الأسمري", "Al-Asmari"), ("النجار", "Al-Najjar"), ("الصالح", "Al-Saleh"), ("إدريس", "Idris"),
          ("باوزير", "Bawazir"), ("هوساوي", "Hawsawi"), ("فلاتة", "Fallatah"), ("بخاري", "Bukhari"),
          ("الحداد", "Al-Haddad"), ("القرشي", "Al-Qurashi"), ("العوفي", "Al-Awfi"), ("الرويلي", "Al-Ruwaili")]
DISTRICTS = [("Al-Nuzha", "النزهة"), ("Al-Rawda", "الروضة"), ("Al-Waha", "الواحة"), ("Al-Salam", "السلام"),
             ("Al-Faisaliyah", "الفيصلية"), ("Al-Khalidiyah", "الخالدية"), ("Al-Mahjar", "المحجر"),
             ("Al-Rabwa", "الربوة"), ("Al-Safa", "الصفا"), ("Al-Marwa", "المروة"), ("Al-Naseem", "النسيم"),
             ("Al-Aziziyah", "العزيزية"), ("Al-Badiyah", "البادية"), ("Al-Shifa", "الشفا"), ("Al-Sahil", "الساحل"),
             ("Al-Yarmouk", "اليرموك"), ("Al-Andalus", "الأندلس"), ("Al-Zahra", "الزهراء"), ("Al-Mansoura", "المنصورة"),
             ("Al-Wurud", "الورود"), ("Al-Basateen", "البساتين"), ("Al-Jabal", "الجبل"), ("Al-Fayha", "الفيحاء"),
             ("Al-Sinaiyah", "الصناعية"), ("Al-Hamra", "الحمراء"), ("Wadi Al-Sidr", "وادي السدر"),
             ("Al-Murooj", "المروج"), ("Al-Qadisiyah", "القادسية"), ("Al-Dahiya Al-Jadida", "الضاحية الجديدة"),
             ("Al-Matar", "المطار")]
NOTES = ["", "", "", "", "", "", "", "استلم الجار", "بدون بطاقة العائلة", "طرد إضافي للأيتام", "تأخر الاستلام",
         "collected by neighbour", "family card not shown"]
CATEGORIES = ["dry goods", "rice", "dates", "canned food", "oil", "fresh produce", "infant food"]
SIZE_P = [.04, .07, .10, .14, .16, .15, .12, .08, .05, .04, .02, .015, .01, .005]
INDIC = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")


def cfg(capstone: bool, rng: random.Random) -> dict:
    """Which branch has which fault. Fixed for the course; drawn again for the capstone extract."""
    b = [f"B{i:02d}" for i in range(1, 15)]
    if not capstone:
        return dict(n_reg=40000, n_dup=180, n_logs=210000, months=list(range(1, 10)), cp1256=["B03", "B11"],
                    bom=["B08"], mojibake="B06", indic="B09", dmy=["B03", "B08", "B10", "B11"], mdy=["B05", "B13"],
                    lb=["B05", "B13"], lb_as_kg="B13", grams="B09", no_weight="B09", gap="B12", double="B02",
                    hyphen="B10", old_form=["B03", "B07", "B11"], low=["D07", "D15", "D22", "D26"], over="D03",
                    size_missing=0.18, topup=0.27)
    s = b[:]
    rng.shuffle(s)
    d = [f"D{i:02d}" for i in range(1, 29)]
    rng.shuffle(d)
    return dict(n_reg=12000, n_dup=70, n_logs=42000, months=list(range(1, 7)), cp1256=s[0:2], bom=[s[2]],
                mojibake=s[3], indic=s[4], dmy=s[0:1] + s[5:7], mdy=s[7:9], lb=s[7:9], lb_as_kg=s[8], grams=s[9],
                no_weight=s[10], gap=s[11], double=s[12], hyphen=s[13], old_form=[s[1], s[5], s[11]], low=d[:4],
                over=d[4], size_missing=0.21, topup=0.30)


def gz_write(path: Path, data: bytes) -> None:
    """A gzip file with no timestamp inside, so the bytes are the same on every run."""
    path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, filename="") as f:
        f.write(data)
    path.write_bytes(buf.getvalue())


def name_variant(rng: random.Random, ar: str) -> str:
    """The spelling a clerk typed: letter variants, a stray mark, a stretched letter, extra spaces."""
    r = rng.random()
    if r < .22:
        ar = ar.replace("أ", "ا").replace("إ", "ا")
    if rng.random() < .15:
        ar = ar.replace("ة", "ه")
    if rng.random() < .10:
        ar = ar.replace("ى", "ي")
    if rng.random() < .12:
        ar = ar.replace("عبدال", "عبد ال")
    if rng.random() < .02:
        ar = ar.replace("محمد", "مُحمّد").replace("علي", "عَلي")
    if rng.random() < .015:
        i = rng.randrange(1, max(2, len(ar) - 1))
        if ar[i] != " " and ar[i - 1] != " ":
            ar = ar[:i] + "ـ" + ar[i:]
    if rng.random() < .03:
        ar = ar.replace(" ", "  ", 1) + " "
    return ar


def phone_variant(rng: random.Random, p: str) -> str:
    r = rng.random()
    if r < .15:
        return "+966" + p[1:]
    if r < .22:
        return "966" + p[1:]
    if r < .28:
        return p[:3] + " " + p[3:6] + " " + p[6:]
    return p


def typo(rng: random.Random, s: str) -> str:
    i = rng.randrange(1, len(s) - 1)
    if s[i] == " " or s[i + 1 if i + 1 < len(s) else i] == " ":
        return s
    return s[:i] + s[i + 1:] if rng.random() < .5 else s[:i] + s[i + 1] + s[i] + s[i + 2:]


def fmt_date(d: dt.date, style: str) -> str:
    return {"iso": d.isoformat(), "dmy": d.strftime("%d/%m/%Y"), "mdy": d.strftime("%m/%d/%Y")}[style]


def build(capstone: bool = False) -> dict:
    rng = random.Random(20270202 if not capstone else 20270611)
    C = cfg(capstone, rng)
    out = LABS / ("capstone/raw" if capstone else "data/raw")
    year = 2026
    months = C["months"]
    last_day = dt.date(year, months[-1] + 1, 1) - dt.timedelta(days=1)
    q_start = Q_START if not capstone else dt.date(2026, 4, 1)
    q_end = Q_END if not capstone else dt.date(2026, 6, 30)
    branches = [f"B{i:02d}" for i in range(1, 15)]
    dids = [f"D{i:02d}" for i in range(1, 31)]
    primary = {d: branches[i // 2] if i < 28 else branches[12 + (i - 28)] for i, d in enumerate(dids)}

    # ---- districts: registrations share, coverage of the low-income frame, access to a branch
    share = {d: rng.uniform(0.7, 1.6) for d in dids}
    for d in C["low"]:
        share[d] *= 0.55
    cover = {d: rng.uniform(0.74, 0.97) for d in dids}
    access = {d: rng.uniform(0.86, 1.0) for d in dids}
    for d in C["low"]:
        cover[d] = rng.uniform(0.31, 0.44)
        access[d] = rng.uniform(0.50, 0.60)
    cover[C["over"]] = 1.27
    if not capstone:
        access["D11"], access["D19"] = 0.725, 0.70      # two districts close to the service standard

    # ---- households
    n_h = C["n_reg"] - C["n_dup"]
    ids = rng.sample(range(100000, 1000000), n_h + 2000)
    hid, spare = [f"H{i}" for i in ids[:n_h]], [f"H{i}" for i in ids[n_h:]]
    nids = rng.sample(range(1_090_000_000, 1_092_000_000), n_h)
    start = dt.date(2021, 1, 3)
    span = (dt.date(year, months[-1], 28) - start).days
    old_cut = dt.date(2025, 3, 1)
    H = []
    for k in range(n_h):
        d = rng.choices(dids, weights=[share[x] for x in dids])[0]
        br = primary[d] if rng.random() < .85 else rng.choice(branches)
        reg = start + dt.timedelta(days=rng.randrange(span + 1))
        ch = rng.choices(["branch", "phone", "online"], weights=[60, 25, 15 if reg.year >= 2023 else 0])[0]
        size = rng.choices(range(1, 15), weights=SIZE_P)[0]
        income = int(round(math.exp(rng.gauss(math.log(4200) + 0.035 * (size - 5), 0.55)) / 50) * 50)
        rep = size                                     # the size the household reported at registration
        if abs(income / size - THRESHOLD_SAR) < 350 and income / size > THRESHOLD_SAR and rng.random() < .45:
            rep = size + rng.choice([1, 1, 2])         # just above the line: some report a larger household
        elif rng.random() < .04 and size > 1:
            rep = size - 1                             # a birth or a returning member not yet reported
        female = rng.random() < .22
        f, fa, fam = rng.choice(FIRST_F if female else FIRST), rng.choice(FIRST), rng.choice(FAMILY)
        latin = rng.random() < .06
        ar_name = f"{f[0]} {fa[0]} {fam[0]}"
        name = f"{f[1]} {fa[1]} {fam[1]}" if latin else name_variant(rng, ar_name)
        if latin and rng.random() < .3:
            name = name.upper()
        phone = "05" + "".join(rng.choice("0123456789") for _ in range(8))
        closed = None
        if rng.random() < .08:
            closed = reg + dt.timedelta(days=rng.randrange(60, 900))
            if closed > last_day:
                closed = None
        H.append(dict(id=hid[k], nid=str(nids[k]), name=name, ar=ar_name, en=f"{f[1]} {fa[1]} {fam[1]}", phone=phone,
                      phone_raw="" if rng.random() < .03 else phone_variant(rng, phone), d=d, b=br, ch=ch, reg=reg,
                      size=size, rep=rep, income=income, closed=closed,
                      elig=income / size <= THRESHOLD_SAR, miss=False))

    # ---- which household sizes are blank in the register: three mechanisms, an exact share in total
    for h in H:
        if h["b"] in C["old_form"] and h["reg"] < old_cut and rng.random() < .70:
            h["miss"] = "old_form"                     # the old paper form had no field for it
        elif h["ch"] == "online" and h["rep"] >= 8 and rng.random() < .85:
            h["miss"] = "dropdown"                     # the online form's list stopped at 7
    target = round(C["size_missing"] * n_h)
    rest = [h for h in H if not h["miss"]]
    for h in rng.sample(rest, target - sum(1 for h in H if h["miss"])):
        h["miss"] = "random"

    # ---- handouts: what really happened at the branches
    T = []
    for h in H:
        per = 1 if h["size"] <= 4 else 2 if h["size"] <= 8 else 3
        for m in months:
            first = dt.date(year, m, 1)
            nxt = dt.date(year + (m == 12), m % 12 + 1, 1)
            if h["reg"] >= nxt or (h["closed"] and h["closed"] < first):
                continue
            visits = (rng.random() < .90 * access[h["d"]]) + (rng.random() < C["topup"]) if h["elig"] \
                else (rng.random() < .08)
            for _ in range(visits):
                day = first + dt.timedelta(days=rng.randrange((nxt - first).days))
                if day < h["reg"] or (h["closed"] and day > h["closed"]):
                    continue
                br = h["b"] if rng.random() < .95 else primary[h["d"]]
                T.append(dict(h=h, date=day, b=br, parcels=per, kg=round(per * rng.gauss(12, 0.6), 1)))
    true_q = defaultdict(int)
    for t in T:
        if q_start <= t["date"] <= q_end:
            true_q[t["h"]["id"]] += t["parcels"]
    kg_true = defaultdict(float)
    for t in T:
        kg_true[(t["b"], t["date"].month)] += t["kg"]

    # ---- what reached the log files: a gap, a week uploaded twice, and exactly n_logs rows
    gm = months[-2]
    gap = (dt.date(year, gm, 10), dt.date(year, gm, 18))
    dbl = (dt.date(year, 3, 8), dt.date(year, 3, 14 if not capstone else 10))
    logs = [t for t in T if not (t["b"] == C["gap"] and gap[0] <= t["date"] <= gap[1])]
    n_gap = len(T) - len(logs)
    in_dbl = [t for t in logs if t["b"] == C["double"] and dbl[0] <= t["date"] <= dbl[1]]
    surplus = len(logs) + len(in_dbl) - C["n_logs"]
    assert surplus >= 0, f"too few handouts generated: {surplus}"
    free = [i for i, t in enumerate(logs) if not (t["b"] == C["double"] and dbl[0] <= t["date"] <= dbl[1])
            and not (q_start <= t["date"] <= q_end)]
    drop = set(rng.sample(free, surplus))
    logs = [t for i, t in enumerate(logs) if i not in drop]
    logs.sort(key=lambda t: (t["b"], t["date"], t["h"]["id"]))
    seq = defaultdict(int)
    rows = []
    for t in logs:
        seq[t["b"]] += 1
        h = t["h"]
        who = h["ar"].split()[0] + " " + h["ar"].split()[-1] if rng.random() < .8 else \
            rng.choice(FIRST)[0] + " " + h["ar"].split()[-1]
        rows.append(dict(log_id=f"{t['b']}-{seq[t['b']]:07d}", b=t["b"], hid=h["id"], date=t["date"],
                         parcels=t["parcels"], w=t["kg"], unit="kg", who=who, note=rng.choice(NOTES), fault=""))
    idx = list(range(len(rows)))
    rng.shuffle(idx)
    scale = len(rows) / 208950
    cut = [int(round(x * scale)) for x in (420, 310, 240, 1200, 700, 90)]
    pos = 0
    late = [h for h in H if h["reg"] >= q_start]
    for kind, n in zip(("unknown", "blank", "letter_o", "lower", "spaces", "before_reg"), cut):
        for i in idx[pos:pos + n]:
            r = rows[i]
            if kind == "unknown":
                r["hid"] = rng.choice(spare)
            elif kind == "blank":
                r["hid"] = ""
            elif kind == "letter_o":
                if "0" not in r["hid"]:
                    continue
                j = rng.choice([p for p, c in enumerate(r["hid"]) if c == "0"])
                r["hid"] = r["hid"][:j] + "O" + r["hid"][j + 1:]
            elif kind == "lower":
                r["hid"] = r["hid"].lower()
            elif kind == "spaces":
                r["hid"] = " " + r["hid"] + "  "
            elif kind == "before_reg":
                cand = rng.choice(late)
                if cand["reg"] <= r["date"]:
                    continue
                r["hid"] = cand["id"]
            r["fault"] = kind
        pos += n
    for r in rows:
        if r["b"] == C["hyphen"] and not r["fault"] and rng.random() < .04:
            r["hid"], r["fault"] = r["hid"][0] + "-" + r["hid"][1:], "hyphen"
        if r["b"] in C["lb"]:
            r["w"], r["unit"] = round(r["w"] * 2.20462, 1), "lb"
        if r["b"] == C["lb_as_kg"] and r["date"] >= dt.date(year, months[-1], 14):
            r["unit"] = "kg"                                        # pounds labelled as kilograms
        if r["b"] == C["no_weight"] and dt.date(year, 5, 4) <= r["date"] <= dt.date(year, 5, 17):
            r["w"] = None                                           # the scale was away for repair
    grams = [r for r in rows if r["b"] == C["grams"] and r["w"] is not None]
    for r in rng.sample(grams, 150 if not capstone else 60):
        r["w"] = int(round(r["w"] * 1000))                          # grams typed into a kilogram field
    final = []
    for r in rows:
        final.append(r)
        if r["b"] == C["double"] and dbl[0] <= r["date"] <= dbl[1]:
            final.append(r)                                         # the week that was uploaded twice
    assert len(final) == C["n_logs"], len(final)
    by_b = defaultdict(list)
    for r in final:
        by_b[r["b"]].append(r)
    for b in branches:
        style = "dmy" if b in C["dmy"] else "mdy" if b in C["mdy"] else "iso"
        lines = ["log_id,household_id,handout_date,parcels,weight,unit,collected_by,note"]
        for r in by_b[b]:
            w = "" if r["w"] is None else str(r["w"])
            lines.append(f"{r['log_id']},{r['hid']},{fmt_date(r['date'], style)},{r['parcels']},{w},{r['unit']},"
                         f"{r['who']},{r['note']}")
        text = "\n".join(lines) + "\n"
        enc = "cp1256" if b in C["cp1256"] else "utf-8-sig" if b in C["bom"] else "utf-8"
        gz_write(out / "branch_logs" / f"{b}.csv.gz", text.encode(enc))

    # ---- the register extract: 14 branch exports appended, in three states of encoding
    dups = rng.sample(H, C["n_dup"])
    recs = [(h, h["b"], h["reg"], h["rep"], h["phone_raw"]) for h in H]
    for h in dups:
        b2 = rng.choice([b for b in branches if b != h["b"]])
        reg2 = min(h["reg"] + dt.timedelta(days=rng.randrange(30, 400)), dt.date(year, months[-1], 28))
        recs.append((h, b2, reg2, h["rep"] + (rng.random() < .3), phone_variant(rng, h["phone"])))
    recs.sort(key=lambda x: (x[1], x[2], x[0]["id"]))
    blob = [b"household_id,national_id,head_name,phone,district_id,branch_id,channel,registered_on,"
            b"household_size,monthly_income_sar,status\n"]
    for h, b, reg, rep, ph in recs:
        nid, name = h["nid"], h["name"]
        if b == C["indic"]:
            nid, ph = nid.translate(INDIC), ph.translate(INDIC)
        size = "" if h["miss"] else str(rep)
        status = "closed" if h["closed"] else "active"
        if b == C["mojibake"]:
            name = name.encode("utf-8").decode("cp1256")
            assert name.encode("cp1256").decode("utf-8") == h["name"]
        line = f"{h['id']},{nid},{name},{ph},{h['d']},{b},{h['ch']},{reg.isoformat()},{size},{h['income']},{status}\n"
        blob.append(line.encode("cp1256" if b in C["cp1256"] else "utf-8"))
    gz_write(out / "registry" / "registrations_extract.csv.gz", b"".join(blob))

    # ---- the audit: home visits in which the true household size was verified
    miss, seen = [h for h in H if h["miss"] and not h["closed"]], [h for h in H if not h["miss"] and not h["closed"]]
    n_a = 300 if not capstone else 150
    audit = rng.sample(miss, n_a) + rng.sample(seen, n_a)
    audit.sort(key=lambda h: h["id"])
    (out / "registry").mkdir(parents=True, exist_ok=True)
    (out / "registry" / "audit_resurvey.csv").write_text(
        "household_id,verified_size,visit_month\n" + "".join(f"{h['id']},{h['size']},{year}-09\n" for h in audit),
        encoding="utf-8", newline="\n")

    # ---- donations, as the API serves them
    dons, n = [], 0
    for b in branches:
        for m in months:
            total = kg_true[(b, m)] * rng.uniform(1.05, 1.15)
            k = rng.randrange(35, 49)
            parts = [rng.random() + .2 for _ in range(k)]
            for p in parts:
                kg = total * p / sum(parts)
                dtype = rng.choices(["individual", "retailer", "farm", "corporate"], weights=[45, 30, 10, 15])[0]
                day = rng.randrange(1, 29)
                lb = dtype == "retailer" and b in C["lb"] + [C["double"]] and rng.random() < .3
                dons.append(dict(received_at=f"{year}-{m:02d}-{day:02d}T{rng.randrange(8, 20):02d}:"
                                             f"{rng.randrange(60):02d}:00+03:00", branch_id=b,
                                 donor_type=None if dtype == "individual" and rng.random() < .45 else dtype,
                                 category=rng.choice(CATEGORIES), weight=round(kg * (2.20462 if lb else 1), 1),
                                 unit="lb" if lb else "kg", est_value_sar=int(round(kg * rng.uniform(6, 14)))))
    dons.sort(key=lambda x: (x["received_at"], x["branch_id"], x["weight"]))
    for x in dons:
        n += 1
        x["donation_id"] = f"DN-{year}-{n:06d}"
    gz_write(out / "donations" / "donations.jsonl.gz",
             "".join(json.dumps({"donation_id": x.pop("donation_id"), **x}, ensure_ascii=False) + "\n"
                     for x in dons).encode("utf-8"))

    # ---- the open population table (reference year 2022; the two newest districts are not in it)
    reg_d = defaultdict(int)
    for h in H:
        reg_d[h["d"]] += 1
    lines = ["district_id,district_name_en,district_name_ar,population,households,low_income_households_est,"
             "reference_year"]
    for i, d in enumerate(dids[:28]):
        low = int(round(reg_d[d] / cover[d], -1))
        hh = int(round(low / rng.uniform(0.09, 0.21), -1))
        lines.append(f"{d},{DISTRICTS[i][0]},{DISTRICTS[i][1]},{int(round(hh * rng.uniform(4.9, 5.9), -1))},{hh},"
                     f"{low},2022")
    (out / "open").mkdir(parents=True, exist_ok=True)
    (out / "open" / "district_population_2022.csv").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    truth_pop = [h for h in H if not h["closed"] and h["reg"] < q_start and h["elig"]]
    by_d = defaultdict(lambda: [0, 0])
    for h in truth_pop:
        by_d[h["d"]][0] += true_q[h["id"]]
        by_d[h["d"]][1] += 1
    truth = dict(
        note="What the generator knows and the sources do not: the true household sizes and the handouts that "
             "never reached a log file.",
        households=n_h, register_rows=len(recs), log_rows=len(final), true_handouts=len(T), gap_rows=n_gap,
        double_upload_rows=len(final) - len(rows), size_missing=sum(1 for h in H if h["miss"]),
        size_missing_by_cause={k: sum(1 for h in H if h["miss"] == k) for k in ("old_form", "dropdown", "random")},
        eligible_households=len(truth_pop),
        parcels_per_eligible_household_per_month=round(sum(v[0] for v in by_d.values()) / len(truth_pop) / 3, 4),
        by_district={d: round(v[0] / v[1] / 3, 4) for d, v in sorted(by_d.items())},
        donations=len(dons), config={k: v for k, v in C.items()})

    if capstone:
        return truth

    ref = LABS / "data" / "reference"
    ref.mkdir(parents=True, exist_ok=True)
    (ref / "truth_summary.json").write_text(json.dumps(truth, indent=1, ensure_ascii=False) + "\n", encoding="utf-8",
                                            newline="\n")

    # ---- Lab 2.3: 300 walk-in records without a key, and pairs that staff labelled
    pool = [h for h in H if h["b"] in ("B04", "B05") and not h["closed"]]
    matched = rng.sample(pool, 255)
    walk, pairs = [], []
    by_fam = defaultdict(list)
    for h in pool:
        by_fam[h["ar"].split()[-1]].append(h)
    for k in range(300):
        wid = f"W{k + 1:03d}"
        if k < 255:
            h = matched[k]
            parts = h["ar"].split()
            nm = name_variant(rng, " ".join(parts if rng.random() < .55 else [parts[0], parts[-1]]))
            if rng.random() < .25:
                nm = typo(rng, nm)
            ph = "" if rng.random() < .30 else h["phone"]
            if ph and rng.random() < .15:
                j = rng.randrange(2, 10)
                ph = ph[:j] + rng.choice("0123456789") + ph[j + 1:]
            walk.append((wid, nm, ph, h["d"], h["rep"]))
            pairs.append((wid, h["id"], 1))
            ar = h["ar"]
        else:
            f, fa, fam = rng.choice(FIRST), rng.choice(FIRST), rng.choice(FAMILY[:12])
            ar = f"{f[0]} {fa[0]} {fam[0]}"
            walk.append((wid, name_variant(rng, ar), "05" + "".join(rng.choice("0123456789") for _ in range(8)),
                         rng.choice(["D07", "D08", "D09", "D10"]), rng.randrange(2, 9)))
            h = None
        near = [c for c in by_fam[ar.split()[-1]] if c is not h and c["ar"].split()[0] == ar.split()[0]]
        rng.shuffle(near)
        for c in near[:2 if h else 3]:
            pairs.append((wid, c["id"], 0))
    order = list(range(300))
    rng.shuffle(order)
    walk = [walk[i] for i in order]
    (out / "match").mkdir(parents=True, exist_ok=True)
    (out / "match" / "walkin_300.csv").write_text(
        "walkin_id,name,phone,district_id,household_size_stated\n" + "".join(",".join(map(str, w)) + "\n" for w in walk),
        encoding="utf-8", newline="\n")
    pairs.sort()
    (out / "match" / "labelled_pairs.csv").write_text(
        "walkin_id,household_id,is_match\n" + "".join(",".join(map(str, p)) + "\n" for p in pairs),
        encoding="utf-8", newline="\n")

    # ---- Day 4: the first week of October as a joined batch, clean and corrupted, and the donated weight
    import hashlib
    import hmac
    key = b"ghilal-teaching-key-not-a-secret"
    w0, w1 = dt.date(2026, 10, 1), dt.date(2026, 10, 7)
    batch, kg_b = [], defaultdict(float)
    for h in H:
        if h["closed"] or not h["elig"] or rng.random() > .21 * access[h["d"]]:
            continue
        per = 1 if h["size"] <= 4 else 2 if h["size"] <= 8 else 3
        day = w0 + dt.timedelta(days=rng.randrange(7))
        kg = round(per * rng.gauss(12, 0.6), 1)
        kg_b[h["b"]] += kg
        batch.append([f"{h['b']}-9{len(batch):06d}", hmac.new(key, h["id"].encode(), hashlib.sha256).hexdigest()[:16],
                      h["b"], h["d"], day.isoformat(), h["reg"].isoformat(), per, kg,
                      "" if h["miss"] else h["rep"], "" if h["miss"] else int(h["income"] / h["rep"] <= THRESHOLD_SAR)])
    head = "log_id,household_key,branch_id,district_id,handout_date,registered_on,parcels,weight_kg,household_size,eligible\n"
    (out / "batches").mkdir(parents=True, exist_ok=True)
    (out / "batches" / "joined_2026-10-w1.csv").write_text(
        head + "".join(",".join(map(str, r)) + "\n" for r in batch), encoding="utf-8", newline="\n")
    bad = [r[:] for r in batch]
    pick = list(range(len(bad)))
    rng.shuffle(pick)
    planted = {}
    for name_, n_, fn in [
        ("parcels out of range", 40, lambda r: r.__setitem__(6, rng.choice([0, -1, 30]))),
        ("handout before registration", 30, lambda r: r.__setitem__(5, "2026-10-20")),
        ("household_key blank", 60, lambda r: r.__setitem__(1, "")),
        ("handout_date not ISO", 15, lambda r: r.__setitem__(4, dt.date.fromisoformat(r[4]).strftime("%d/%m/%Y"))),
        ("district not in the list", 20, lambda r: r.__setitem__(3, rng.choice(["D31", "D00"]))),
        ("household_size out of range", 12, lambda r: r.__setitem__(8, rng.choice([0, 45])))]:
        take = [i for i in pick if bad[i][2] != "B05"][:n_]
        pick = [i for i in pick if i not in set(take)]
        for i in take:
            fn(bad[i])
        planted[name_] = n_
    b05 = [r for r in bad if r[2] == "B05"]
    for r in b05:
        r[7] = round(r[7] * 2.20462, 1)                              # pounds written into weight_kg
    planted["weight in pounds at B05"] = len(b05)
    clones = [bad[i][:] for i in pick[:25]]
    bad += clones
    planted["log_id repeated"] = 25
    (out / "batches" / "joined_2026-10-w1_corrupted.csv").write_text(
        head + "".join(",".join(map(str, r)) + "\n" for r in bad), encoding="utf-8", newline="\n")
    (out / "batches" / "donated_kg_2026-10-w1.csv").write_text(
        "branch_id,donated_kg\n" + "".join(f"{b},{round(kg_b[b] * rng.uniform(1.05, 1.15), 1)}\n" for b in branches),
        encoding="utf-8", newline="\n")
    truth["batch_rows"], truth["batch_planted"] = len(batch), planted
    (ref / "truth_summary.json").write_text(json.dumps(truth, indent=1, ensure_ascii=False) + "\n", encoding="utf-8",
                                            newline="\n")
    return truth


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--capstone", action="store_true", help="write capstone/raw/: the second extract")
    a = ap.parse_args()
    t = build(a.capstone)
    for k in ("households", "register_rows", "log_rows", "true_handouts", "gap_rows", "double_upload_rows",
              "size_missing", "size_missing_by_cause", "eligible_households",
              "parcels_per_eligible_household_per_month", "donations"):
        print(f"{k:42s} {t[k]}")
