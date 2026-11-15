# %% [markdown]
# # Lab 2.1 · One file, three encodings
#
# Day 2 · Session 1 (Encodings and Arabic text) · 25 min.
#
# The register extract was made by appending 14 branch exports. FN-104 taught you to read a file in its code page
# and to repair a file that was decoded twice. Here the three states are mixed **inside one file**: most lines are
# UTF-8, the lines of two branches are in Windows-1256, and the names of a third branch were decoded twice and
# saved. You decide line by line, repair, normalise letters and digits into matching keys, and count every repair.
#
# **AI-tutor**, hinting only, for regular expressions. The decisions and the log are yours.
#
# **Reference state.** `G.registry_bytes()`: the extract as it arrived, one line of bytes per registration.
#
# **Tasks**
# - [ ] 1 · Decode the extract line by line and count (6')
# - [ ] 2 · Repair the names that were decoded twice (6')
# - [ ] 3 · Normalise letters and digits into keys (8')
# - [ ] 4 · The repair log, and what the digits were hiding (5')
# - [ ] ✱ Stretch · Names in Latin letters: case and hyphens

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
import re
import unicodedata
import pandas as pd
import ghilal as G
import build_dataset as B   # the reference build: its steps are the safety nets of this lab

lines = G.registry_bytes()
header, body = lines[0], lines[1:]
print(header.decode("ascii"))
print(f"{len(body):,} lines of bytes")
try:
    b"\n".join(lines).decode("utf-8")
except UnicodeDecodeError as e:
    print("the file as a whole is not UTF-8:", str(e)[:60])

# %% [markdown]
# ## 1 · Decode the extract line by line and count (6')
#
# No single encoding reads this file. Reading it all as Windows-1256 raises no error, and silently turns the
# UTF-8 lines into nonsense: the worst outcome. A line that is valid UTF-8 is, almost certainly, UTF-8; a line
# that is not is in the legacy code page.
#
# ✏️ **Exercise** · Write `decode(b)`: the text of one line and the name of the encoding that read it,
# `"utf-8"` or `"cp1256"`.

# %%
def decode(b: bytes) -> tuple[str, str]:
    # BEGIN SOLUTION
    try:
        return b.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return b.decode("cp1256"), "cp1256"
    # END SOLUTION


# %%
# Check, with a safety net: the cells below still run when the exercise is not done yet
try:
    decoded = [decode(b) for b in body]
except NotImplementedError:
    decoded = [G.decode_line(b) for b in body]
by_encoding = pd.Series([e for _, e in decoded]).value_counts()
print(by_encoding.to_string())
reg = pd.read_csv(io.StringIO(header.decode("ascii") + "\n" + "\n".join(t for t, _ in decoded)), dtype=str,
                  keep_default_na=False)
reg["line_encoding"] = [e for _, e in decoded]
print(reg.groupby("line_encoding").branch_id.unique().map(sorted).to_string())
G.check(len(reg) == 40_000 and sorted(reg[reg.line_encoding == "cp1256"].branch_id.unique()) == ["B03", "B11"],
        f"40,000 lines decoded; {by_encoding['cp1256']:,} of them, all from B03 and B11, were in Windows-1256")

# %% [markdown]
# ## 2 · Repair the names that were decoded twice (6')
#
# Every line now decodes, and one branch still looks wrong:

# %%
print(reg[reg.branch_id == "B06"].head_name.head(3).to_string(index=False))
print(reg[reg.branch_id == "B05"].head_name.head(3).to_string(index=False))

# %% [markdown]
# The names of B06 were UTF-8, were read as Windows-1256 by the branch system and saved as UTF-8 again. Undo the
# wrong step: back to Windows-1256 bytes, then decode those bytes as UTF-8. A name that was right does not survive
# that round trip, and must come back unchanged.
#
# ✏️ **Exercise** · Write `repair(s)`.

# %%
def repair(s: str) -> str:
    # BEGIN SOLUTION
    try:
        return s.encode("cp1256").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s
    # END SOLUTION


# %%
try:
    fixed = reg.head_name.map(repair)
except NotImplementedError:
    fixed = reg.head_name.map(B.repair_text)
n_repaired = int((fixed != reg.head_name).sum())
reg["head_name_raw"], reg["head_name"] = reg.head_name, fixed
odd = reg[~reg.head_name.str.fullmatch(r"[ء-ْـA-Za-z \-]+")]
print(reg[reg.branch_id == "B06"][["head_name_raw", "head_name"]].head(3).to_string(index=False))
G.check(n_repaired > 2000 and set(reg[fixed != reg.head_name_raw].branch_id) == {"B06"} and len(odd) == 0,
        f"{n_repaired:,} names repaired, all at B06; every name is now in Arabic or Latin letters")

# %% [markdown]
# ## 3 · Normalise letters and digits into keys (8')
#
# The same person is written `أحمد` and `احمد`, `عبد الله` and `عبدالله`, with or without marks and stretched
# letters. And one branch typed ID numbers and phones with Arabic-Indic digits (`١٠٩٠…`): the same number, a
# different string. A **key** is a normalised copy used for matching; the stored value is never replaced by it.
#
# | Rule | Example |
# |---|---|
# | Unicode form NFKC; drop marks (category Mn) and the stretch mark `ـ` | `مُحمّد` → `محمد`, `حـمد` → `حمد` |
# | `أ إ آ ٱ` → `ا`; `ى` → `ي`; `ة` → `ه` | `أحمد` → `احمد`, `نورة` → `نوره` |
# | join `عبد` to a following `ال` | `عبد الله` → `عبدالله` |
# | one space between words, none at the ends | `" سعد  علي "` → `سعد علي` |
# | digits `٠-٩` and `۰-۹` → `0-9` | `١٠٩٠` → `1090` |
#
# ✏️ **Exercise** · Write `name_key(s)` and `western_digits(s)`.

# %%
def name_key(s: str) -> str:
    # BEGIN SOLUTION
    s = unicodedata.normalize("NFKC", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn").replace("ـ", "")
    s = re.sub("[أإآٱ]", "ا", s).replace("ى", "ي").replace("ة", "ه")
    s = re.sub(r"عبد\s+ال", "عبدال", s)
    return " ".join(s.split())
    # END SOLUTION


def western_digits(s: str) -> str:
    # BEGIN SOLUTION
    return s.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789"))
    # END SOLUTION


# %%
tests = [("مُحمّد", "محمد"), ("حـمد", "حمد"), ("أحمد إبراهيم", "احمد ابراهيم"), ("نورة", "نوره"), ("هدى", "هدي"),
         ("عبد الله", "عبدالله"), (" سعد  علي ", "سعد علي")]
try:
    ok = all(name_key(a) == b for a, b in tests) and western_digits("١٠٩٠۱۲") == "109012"
    keys, nid = reg.head_name.map(name_key), reg.national_id.map(western_digits)
except NotImplementedError:
    ok = False
    keys, nid = reg.head_name.map(B.norm_name), reg.national_id.map(B.norm_digits)
G.check(ok, "every rule passes its example")
n_indic = int((nid != reg.national_id).sum())
reg["name_key"], reg["national_id_raw"], reg["national_id"] = keys, reg.national_id, nid
G.check(reg.national_id.str.fullmatch(r"\d{10}").all(), f"every national_id is ten Western digits; {n_indic:,} were rewritten")

# %% [markdown]
# ## 4 · The repair log, and what the digits were hiding (5')
#
# A repair that is not counted cannot be checked, repeated or reversed. One line per rule.

# %%
ar = reg.head_name.str.contains("[ء-ي]", regex=True)
log = pd.DataFrame([
    ("lines decoded as UTF-8", int(by_encoding["utf-8"])),
    ("lines decoded as Windows-1256", int(by_encoding["cp1256"])),
    ("names repaired (decoded twice)", n_repaired),
    ("national ids rewritten in Western digits", n_indic),
    ("distinct Arabic names as typed", int(reg[ar].head_name.nunique())),
    ("distinct Arabic name keys", int(reg[ar].name_key.nunique())),
    ("distinct national ids as typed", int(reg.national_id_raw.nunique())),
    ("distinct national ids after the digit rule", int(reg.national_id.nunique())),
], columns=["what", "count"])
print(log.to_string(index=False))
log.to_csv(G.lab_dir("D2_1") / "repair_log.csv", index=False)
G.keep("d2_1_log", log.to_dict("records"))
hidden = int(reg.national_id_raw.nunique() - reg.national_id.nunique())
G.check(reg.national_id.nunique() == 39_820 and hidden > 0,
        f"39,820 distinct ids after the rule; {hidden} households looked like two people while their id was typed two ways")

# %% [markdown]
# 🔍 Before the digit rule, a household registered once at the branch that types Arabic-Indic digits and once
# elsewhere had two different ID strings. A count of distinct people, or a join on that id, would have been wrong
# without any error. Look at the two name counts as well: how many "different" names were one spelling apart?

# %% [markdown]
# ## ✱ Stretch · Names in Latin letters: case and hyphens
#
# About 6% of the names are typed in Latin letters, some in capitals. Extend the key so that
# `MOHAMMED ALI AL-HARBI` and `Mohammed Ali Al-Harbi` meet.

# %%
def latin_key(s: str) -> str:
    # BEGIN SOLUTION
    return " ".join(name_key(s).casefold().replace("-", " ").split())
    # END SOLUTION


try:
    lat = reg[~ar].head_name
    print("distinct Latin names:", lat.nunique(), "→ keys:", lat.map(latin_key).nunique())
except NotImplementedError:
    print("✱ Stretch not attempted")

# %% [markdown]
# ## Checkpoint
#
# 1. Why not read the whole file as Windows-1256, which raises no error?
#    <details><summary>Answer</summary>Every byte is a letter in that code page, so nothing fails, and the 35,000
#    UTF-8 lines become nonsense. No error is not the same as correct.</details>
# 2. Why keep `head_name_raw` and `national_id_raw`?
#    <details><summary>Answer</summary>A repair is a claim. Keeping the original lets a reviewer check it, and lets
#    you reverse it when a rule turns out wrong.</details>
# 3. The name key maps `ة` to `ه`. Would you store the key as the name of the person?
#    <details><summary>Answer</summary>No. The key loses information on purpose so that variants meet; it is for
#    matching. The stored name stays as typed, repaired only for encoding.</details>
#
# **Carry forward.** `artifacts/D2_1/repair_log.csv`. Labs 2.2 to 2.4 do not need it: each starts from the raw files.
