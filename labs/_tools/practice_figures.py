"""Figures of the short worked examples on the slides and in the practice questions (version 2027.2.0).

    uv run python _tools/practice_figures.py          # from labs/; prints every figure as JSON

Every example is synthetic and set beside the main case of Ghilal Food Bank Network: a stock-movements API with
cursors, a nightly ingestion that retries, one matched household with three sources, a phone survey with a
follow-up of its nonrespondents, and a desk question that changed its wording. None of them is a lab answer.
Standard library only, fixed seeds.
"""

from __future__ import annotations

import json
import random


# ---- 1 · Paging with a cursor, and the proof that the retrieval is complete ----------------------------------

def cursor_paging(total=2_346, per=500, lost_request=4):
    """A cursor API of `total` stock movements. Request `lost_request` timed out after the service had answered;
    the client kept that answer's next cursor and dropped its records, so the request after it skips one page.
    Returns the paging log and the four proofs."""
    ids = [f"M{i:06d}" for i in range(1, total + 1)]
    pages = [ids[i:i + per] for i in range(0, total, per)]
    cursors = [None] + [f"c{k}" for k in range(1, len(pages))]          # cursor that asks for page k
    log, k, sent_after = [], 0, None
    while k < len(pages):
        sent = cursors[k]
        nxt = cursors[k + 1] if k + 1 < len(pages) else None
        log.append(dict(request=len(log) + 1, cursor_sent=sent or "none", expected=sent_after or "none",
                        records=len(pages[k]), first=pages[k][0], last=pages[k][-1], next_cursor=nxt or "null"))
        sent_after = nxt
        k += 2 if len(log) == lost_request - 1 else 1                     # the faulty retry skips one page
    received = sum(r["records"] for r in log)
    breaks = [r["request"] for r in log if r["cursor_sent"] != r["expected"]]
    return dict(per_page=per, total_reported=total, pages_expected=len(pages), log=log, received=received,
                distinct=received, missing=total - received, chain_breaks=breaks,
                last_next_null=log[-1]["next_cursor"] == "null")


# ---- 2 · Retry with bounded backoff, then an alert ------------------------------------------------------------

def backoff(base=1.0, factor=2.0, cap=8.0, attempts=5):
    waits = [min(cap, base * factor ** k) for k in range(attempts - 1)]
    return dict(base=base, cap=cap, attempts=attempts, waits=waits, total_wait=sum(waits))


def retry_log():
    """The nightly ingestion of the stock API on one night: four retryable failures, a fifth, an alert."""
    b = backoff()
    statuses = ["503", "503", "timeout", "429", "503"]
    rows = [dict(attempt=i + 1, status=s, wait_after=(b["waits"][i] if i < len(b["waits"]) else None))
            for i, s in enumerate(statuses)]
    return dict(policy=b, log=rows, outcome="gives up after attempt 5; run stops; alert raised")


# ---- 3 · Field-by-field survivorship for one master record ----------------------------------------------------

def master_record():
    """One household matched across three records. Rules: per field, the most trusted source that has a value;
    a tie between equally trusted sources goes to the most recent; every value keeps its source."""
    recs = {
        "register (B04)": dict(date="2023-05-14", phone="ending 870", district="D11", size="5", income="4,800"),
        "walk-in form": dict(date="2026-03-02", phone="ending 225", district="D12", size="7", income=""),
        "home visit": dict(date="2026-09-17", phone="", district="D12", size="6", income=""),
    }
    precedence = {
        "phone": ["walk-in form", "register (B04)"],                      # the most recent the household gave
        "district": ["home visit", "walk-in form", "register (B04)"],     # seen at the door beats ticked on a form
        "size": ["home visit", "register (B04)", "walk-in form"],         # verified beats reported
        "income": ["register (B04)"],                                     # only the register asks
    }
    master = {}
    for f, order in precedence.items():
        for src in order:
            if recs[src][f]:
                master[f] = dict(value=recs[src][f], source=src)
                break
    conflicts = {f: sorted({r[f] for r in recs.values() if r[f]}) for f in precedence}
    return dict(records=recs, precedence=precedence, master=master,
                fields_in_conflict=[f for f, v in conflicts.items() if len(v) > 1])


# ---- 4 · A follow-up of nonrespondents, and weights for nonresponse -------------------------------------------

def nonresponse(seed=2026, n=1200, subsample=4):
    """A phone survey of n registered households: "did last month's parcels last the month?". Response depends
    on distance to the branch, and also on the answer itself (households in difficulty answer less often).
    Phase 2 visits a random 1 in `subsample` of the nonrespondents at home."""
    rng = random.Random(seed)
    pop = []
    for _ in range(n):
        far = rng.random() < 0.45
        lasted = rng.random() < (0.44 if far else 0.62)
        p_resp = (0.48 if far else 0.72) * (1.0 if lasted else 0.72)
        pop.append(dict(far=far, lasted=lasted, resp=rng.random() < p_resp))
    truth = sum(h["lasted"] for h in pop) / n
    r1 = [h for h in pop if h["resp"]]
    nr = [h for h in pop if not h["resp"]]
    naive = sum(h["lasted"] for h in r1) / len(r1)
    # weighting classes: each respondent stands for the sampled households of its class
    cls = {}
    for far in (False, True):
        s = [h for h in pop if h["far"] == far]
        r = [h for h in s if h["resp"]]
        cls[far] = dict(sampled=len(s), responded=len(r), weight=len(s) / len(r),
                        lasted=sum(h["lasted"] for h in r))
    weighted = sum(c["lasted"] * c["weight"] for c in cls.values()) / n
    # two-phase follow-up
    rng2 = random.Random(seed + 1)
    sub = rng2.sample(nr, len(nr) // subsample)
    r2 = [h for h in sub if rng2.random() < 0.85]                         # a home visit reaches most of them
    w2 = len(nr) / len(r2)
    two_phase = (sum(h["lasted"] for h in r1) + w2 * sum(h["lasted"] for h in r2)) / n
    return dict(sampled=n, phase1_responded=len(r1), phase1_rate=round(len(r1) / n, 3),
                nonrespondents=len(nr), phase2_subsample=len(sub), phase2_responded=len(r2),
                phase2_still_missing=len(sub) - len(r2),
                phase2_weight=round(w2, 2),
                lasted_phase1=sum(h["lasted"] for h in r1), lasted_phase2=sum(h["lasted"] for h in r2),
                classes={("far" if k else "near"): dict(sampled=v["sampled"], responded=v["responded"],
                                                       rate=round(v["responded"] / v["sampled"], 3),
                                                       weight=round(v["weight"], 2),
                                                       lasted_share=round(v["lasted"] / v["responded"], 3))
                         for k, v in cls.items()},
                estimate_respondents=round(naive, 3), estimate_class_weighted=round(weighted, 3),
                estimate_two_phase=round(two_phase, 3), truth_known_only_here=round(truth, 3))


def nonresponse_question():
    """The parallel example of the practice question: 900 sampled, 540 respond (300 yes), 1 in 3 of the 360
    nonrespondents visited, 100 of the 120 answer (30 yes)."""
    n, r1, yes1, nr, sub, r2, yes2 = 900, 540, 300, 360, 120, 100, 30
    w2 = nr / r2
    return dict(respondents_only=round(yes1 / r1, 3), phase2_weight=w2,
                two_phase=round((yes1 + w2 * yes2) / n, 3),
                pooled_unweighted=round((yes1 + yes2) / (r1 + r2), 3),             # a wrong option
                weight_by_subsampling_rate=round((yes1 + nr / sub * yes2) / n, 3))  # a wrong option


def linking_question():
    """The practice question on linking: series A has a stable overlap ratio, series B does not."""
    a, b = [0.81, 0.80, 0.82], [0.92, 0.74, 0.61]
    return dict(mean_a=round(sum(a) / 3, 2), mean_b=round(sum(b) / 3, 2),
                spread_a=round(max(a) - min(a), 2), spread_b=round(max(b) - min(b), 2))


def paging_question(per=400, received=4_410):
    """The practice question on paging: a cursor source that states no total. 12 requests, an unbroken chain,
    the last next cursor null, every id once. The chain proves the end was reached; nothing proves the count."""
    requests = -(-received // per)
    return dict(per_page=per, requests=requests, received=received, distinct=received, total_stated=None,
                checks_passed=["chain", "end", "keys"], check_open="count from a second route")


# ---- 5 · A changed question, an overlap period, and when not to link -----------------------------------------

def instrument_change(seed=7):
    """Monthly share of households at the desk who say someone skipped a meal for lack of food. The old question
    asks about the last month; the new one about the last 7 days. From January to March 2026 both are asked (half
    of the households each), and the old series is put on the new basis with the ratio of the overlap."""
    rng = random.Random(seed)
    months = ["2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04", "2026-05"]
    level = [0.330, 0.336, 0.342, 0.318, 0.322, 0.327, 0.331, 0.329]  # what the old question would show
    ratio_true = 0.78
    old, new = {}, {}
    for m, lv in zip(months, level):
        if m <= "2026-03":
            old[m] = round(lv + rng.uniform(-0.004, 0.004), 3)
        if m >= "2026-01":
            new[m] = round(lv * ratio_true + rng.uniform(-0.004, 0.004), 3)
    overlap = [m for m in months if m in old and m in new]
    ratios = {m: round(new[m] / old[m], 3) for m in overlap}
    factor = round(sum(new[m] for m in overlap) / sum(old[m] for m in overlap), 3)
    linked = {m: (round(old[m] * factor, 3) if m not in new else new[m]) for m in months}
    # a partner network made the same change; its overlap split by channel (the phone script reads the new
    # question aloud, the desk hands a card): the case where one factor would not do
    by_channel = {"desk": dict(old=0.334, new=0.301), "phone": dict(old=0.296, new=0.168)}
    for c in by_channel.values():
        c["ratio"] = round(c["new"] / c["old"], 2)
    # what a chart without the overlap would show: the last old month, then the first new month
    apparent_drop = round(old["2025-12"] - new["2026-01"], 3)
    return dict(old=old, new=new, overlap=overlap, ratios=ratios, factor=factor, linked=linked,
                apparent_drop_dec_to_jan=apparent_drop, by_channel=by_channel)


if __name__ == "__main__":
    print(json.dumps(dict(cursor_paging=cursor_paging(), retry=retry_log(),
                          master_record=master_record(), nonresponse=nonresponse(),
                          nonresponse_question=nonresponse_question(), instrument_change=instrument_change(),
                          linking_question=linking_question(), paging_question=paging_question()),
                     indent=1, ensure_ascii=False))
