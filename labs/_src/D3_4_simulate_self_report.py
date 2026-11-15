# %% [markdown]
# # Lab 3.4 · When the answer itself is wrong
#
# Day 3 · Session 4 (Measurement error and proxies) · 25 min.
#
# Sessions 1 to 3 dealt with sizes that are blank. This lab is about sizes that are recorded, and wrong.
# Household size is reported by the household at registration and is not verified. You measure the reporting
# error against the audit, then simulate two kinds of error (random, and over-reporting by households just above
# the eligibility line) and measure how far each moves the headline.
#
# **AI-off** for the first attempt.
#
# **Reference state.** `G.households_q3()` with the reference imputation `G.impute_within_groups(h)`, and
# `G.audit()`: 600 home visits with the verified size.
#
# **Tasks**
# - [ ] 1 · Measure the reporting error in the audit (6')
# - [ ] 2 · Simulate random error (7')
# - [ ] 3 · Simulate over-reporting near the line (7')
# - [ ] 4 · The shift table and a proxy (5')
# - [ ] ✱ Stretch · How large an audit to see a 2% error rate?

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

import numpy as np
import pandas as pd
import ghilal as G

h = G.households_q3()
size = G.impute_within_groups(h)
baseline = G.estimate(h, size)
RUNS = G.pick(200, 20)
print(f"{len(h):,} households | baseline estimate (blank sizes imputed within groups): {baseline} | runs: {RUNS}")

# %% [markdown]
# ## 1 · Measure the reporting error in the audit (6')
#
# For audited households whose size **is** recorded, compare the recorded size with the verified one.
#
# ✏️ **Exercise** · Write `reporting_error()`: a Series counting the households by `recorded − verified`.

# %%
audit = G.audit().merge(h[["household_id", "household_size", "monthly_income_sar"]], on="household_id")
seen = audit[audit.household_size.notna()].copy()


def reporting_error() -> pd.Series:
    # BEGIN SOLUTION
    return (seen.household_size - seen.verified_size).astype(int).value_counts().sort_index()
    # END SOLUTION


# %%
# Check, with a safety net: the cells below still run when the exercise is not done yet
try:
    err = reporting_error()
except NotImplementedError:
    err = (seen.household_size - seen.verified_size).astype(int).value_counts().sort_index()
n = int(err.sum())
over, under = int(err[err.index > 0].sum()), int(err[err.index < 0].sum())
mean_err = float((err.index.to_numpy() * err.to_numpy()).sum() / n)
print(err.to_string())
print(f"audited with a recorded size: {n} | over-reported: {over} ({over / n:.1%}) | under-reported: {under} "
      f"({under / n:.1%}) | mean error: {mean_err:+.3f} members")
G.keep("d3_4_audit", {"n": n, "over": over, "under": under, "mean_error": round(mean_err, 3)})
G.check(err.loc[0] / n > 0.85 and over > 0 and under > 0, f"{err.loc[0] / n:.0%} of recorded sizes are exact; errors go both ways")

# %% [markdown]
# 🔍 Nine sizes in ten are exact and the mean error is close to zero. It would be easy to stop here and call the
# column reliable. Look at **who** over-reported: their income per verified member.

# %%
seen["per_member_verified"] = (seen.monthly_income_sar / seen.verified_size).round(0)
print(seen[seen.household_size > seen.verified_size][["household_size", "verified_size", "monthly_income_sar",
                                                        "per_member_verified"]].to_string(index=False))

# %% [markdown]
# Every one of them is just above 1,000 SAR per member with the verified size, and at or below it with the
# reported one. The error is small on average and it sits exactly where the eligibility rule decides.
#
# ## 2 · Simulate random error (7')
#
# First the harmless-looking kind. Suppose a share `p` of sizes is off by one, up or down with equal chance,
# for any household.
#
# ✏️ **Exercise** · Write `random_error(size, p, rng)`: a copy of `size` in which each household, with
# probability `p`, gets +1 or −1 (never below 1).

# %%
def random_error(size: pd.Series, p: float, rng) -> pd.Series:
    # BEGIN SOLUTION
    hit = rng.random(len(size)) < p
    step = rng.choice([-1, 1], size=len(size))
    return (size + hit * step).clip(lower=1)
    # END SOLUTION


# %%
def _random_error(size, p, rng):
    return (size + (rng.random(len(size)) < p) * rng.choice([-1, 1], size=len(size))).clip(lower=1)


rng = np.random.default_rng(34)
try:
    sim_random = [G.estimate(h, random_error(size, 0.08, rng)) for _ in range(RUNS)]
except NotImplementedError:
    sim_random = [G.estimate(h, _random_error(size, 0.08, rng)) for _ in range(RUNS)]
shift_random = round(float(np.mean(sim_random)) - baseline, 3)
print(f"random error in 8% of sizes: estimate {np.mean(sim_random):.3f} on average ({shift_random:+.3f}), "
      f"from {min(sim_random):.3f} to {max(sim_random):.3f} over {RUNS} runs")
G.check(abs(shift_random) < 0.03, f"random error moves the headline by {shift_random:+.3f}: little")

# %% [markdown]
# ## 3 · Simulate over-reporting near the line (7')
#
# Now the kind the audit showed. A household whose income per member is just above the line (more than 1,000 and
# at most 1,350 SAR) reports, with probability `q`, one or two members more than it has. Nobody else misreports.
#
# ✏️ **Exercise** · Write `over_report(size, q, rng)`.

# %%
def over_report(size: pd.Series, q: float, rng) -> pd.Series:
    # BEGIN SOLUTION
    per = h.monthly_income_sar / size
    near = (per > G.THRESHOLD_SAR) & (per <= 1350)
    hit = near & (rng.random(len(size)) < q)
    return size + hit * rng.choice([1, 1, 2], size=len(size))
    # END SOLUTION


# %%
def _over_report(size, q, rng):
    per = h.monthly_income_sar / size
    hit = (per > G.THRESHOLD_SAR) & (per <= 1350) & (rng.random(len(size)) < q)
    return size + hit * rng.choice([1, 1, 2], size=len(size))


rows = [("random error, 8% of households", 0.08, round(float(np.mean(sim_random)), 3), shift_random)]
for q in (0.1, 0.2, 0.4):
    try:
        sims = [G.estimate(h, over_report(size, q, rng)) for _ in range(RUNS)]
        changed = float(np.mean([(over_report(size, q, rng) != size).mean() for _ in range(5)]))
    except NotImplementedError:
        sims = [G.estimate(h, _over_report(size, q, rng)) for _ in range(RUNS)]
        changed = float(np.mean([(_over_report(size, q, rng) != size).mean() for _ in range(5)]))
    rows.append((f"over-reporting near the line, q = {q}", round(changed, 3), round(float(np.mean(sims)), 3),
                 round(float(np.mean(sims)) - baseline, 3)))
shift = pd.DataFrame(rows, columns=["error model", "share of sizes changed", "estimate", "shift"])
print(shift.to_string(index=False))
G.check(shift["shift"].iloc[2] < 3 * min(shift_random, -0.001) and shift["share of sizes changed"].iloc[2] < 0.03,
        f"over-reporting by {shift['share of sizes changed'].iloc[2]:.1%} of households moves the headline by {shift['shift'].iloc[2]:+.3f}")

# %% [markdown]
# 🔍 Fewer households misreport than in the random model, and the headline moves several times further, always
# downwards: each one enters the denominator as "eligible" and collects almost nothing, because the branch desk
# hands out by the family card and not by the register.

# %% [markdown]
# ## 4 · The shift table and a proxy (5')
#
# The recorded sizes already contain this error, so the headline computed from them is likely **too low**. The
# generator knows the true sizes; this cell is the one real work never has.

# %%
sealed = h.merge(G.sealed(), on="household_id", validate="one_to_one")
as_reported, true_size = G.estimate(sealed, sealed.size_as_reported), G.estimate(sealed, sealed.size_true)
print(f"all sizes as reported: {as_reported} | all sizes as they truly are: {true_size} | error of measurement: "
      f"{as_reported - true_size:+.3f}")
shift.to_csv(G.lab_dir("D3_4") / "shift_table.csv", index=False)
G.keep("d3_4_shift", shift.to_dict("records"))
G.keep("d3_4_truth", {"as_reported": as_reported, "true": true_size})

# %% [markdown]
# A **proxy** stands in for what you cannot measure. `usual_parcels` is set by the desk from the family card:
# 1 parcel up to 4 members, 2 for 5 to 8, 3 for 9 or more. It is a proxy for the verified size band.
#
# ✏️ **Exercise** · Write `proxy_disagreement()`: among households with a recorded size and at least one handout,
# the share whose recorded size falls in a different band from the one `usual_parcels` implies.

# %%
def proxy_disagreement() -> float:
    # BEGIN SOLUTION
    d = h[h.household_size.notna() & h.usual_parcels.notna()]
    band = pd.cut(d.household_size.astype(int), [0, 4, 8, 99], labels=[1, 2, 3]).astype(int)
    return round(float((band != d.usual_parcels.astype(int)).mean()), 3)
    # END SOLUTION


# %%
try:
    dis = proxy_disagreement()
except NotImplementedError:
    dis = G.reference("d3_4_proxy")
G.keep("d3_4_proxy", dis)
never = h[h.household_size.notna() & h.usual_parcels.isna()]
elig_never = int(((never.monthly_income_sar / never.household_size.astype(float)) <= G.THRESHOLD_SAR).sum())
print(f"recorded size and parcels per handout disagree for {dis:.1%} of households that collected")
print(f"eligible by the register and never collected in nine months: {elig_never:,} households")
G.check(0 < dis < 0.2, "the proxy flags a small share of sizes for review")

# %% [markdown]
# The proxy can only speak about households that collected. The households that are eligible by the register and
# never collected are two groups it cannot tell apart: over-reporters, and the under-served households the whole
# analysis is looking for. A proxy measures what it measures: here, "was served", not "is eligible".

# %% [markdown]
# ## ✱ Stretch · How large an audit to see a 2% error rate?
#
# If 2% of households over-report, how often does an audit of `n` recorded households contain none of them?

# %%
def chance_of_seeing_none(rate: float = 0.02) -> pd.Series:
    # BEGIN SOLUTION
    return pd.Series({n: round((1 - rate) ** n, 3) for n in (50, 100, 150, 300, 600)}, name="P(no case in the audit)")
    # END SOLUTION


try:
    print(chance_of_seeing_none().to_string())
except NotImplementedError:
    print("✱ Stretch not attempted")

# %% [markdown]
# ## Checkpoint
#
# 1. The mean reporting error is almost zero. Why does the headline still move?
#    <details><summary>Answer</summary>Eligibility is a threshold. Errors that push households across it in one
#    direction change who is counted, however small they are on average.</details>
# 2. Random error and over-reporting: which is worse for the headline, and why?
#    <details><summary>Answer</summary>Over-reporting. Random error moves households across the line both ways and
#    mostly cancels; over-reporting only moves ineligible households in.</details>
# 3. Why not define "eligible" as "collected regularly", which the desk verified?
#    <details><summary>Answer</summary>Then every eligible household that was not served leaves the denominator, and
#    every district looks well served. The proxy would answer a different question.</details>
#
# **Carry forward.** `artifacts/D3_4/shift_table.csv`: the measurement-error line of the quality report.
