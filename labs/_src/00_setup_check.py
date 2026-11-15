# %% [markdown]
# # Setup check
#
# Run this notebook once before Day 1. It checks the Python version and the four packages, makes sure the
# synthetic data of the case is in place, starts and stops the local donations API, and runs one small query.
# It takes under a minute on a laptop CPU or a Colab CPU runtime. No account, no key and no model are needed
# anywhere in this course.

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

import ghilal as G

G.check(sys.version_info >= (3, 11), f"Python {sys.version.split()[0]} (3.11 or later is needed)")

# %% [markdown]
# ## The packages

# %%
import importlib

for name in ("duckdb", "pandas", "pandera", "rapidfuzz"):
    try:
        m = importlib.import_module(name)
        G.check(True, f"{name} {getattr(m, '__version__', '')}")
    except ImportError:
        G.check(False, f"{name} is missing: run `uv sync` in labs/ (or the first cell again on Colab)")

# %% [markdown]
# ## The data of the case
#
# The raw sources are committed with the repository. If the folder is missing, `G.ensure_data()` rebuilds it
# with `prepare_data.py` (about a minute); the generator uses a fixed seed, so everybody has the same files.

# %%
G.ensure_data()
files = sorted(p for p in G.RAW.rglob("*") if p.is_file())
size_mb = sum(p.stat().st_size for p in files) / 1e6
print(f"{len(files)} files, {size_mb:.1f} MB in {G.RAW.relative_to(G.LABS).as_posix()}/")
G.check(len(files) >= 20, "the four sources are in place: the register extract, 14 branch logs, donations, the open table")

# %% [markdown]
# ## One query, and the local API
#
# The register is loaded into an in-memory DuckDB database; the donations API is a small program that runs on
# your own machine (or inside the Colab runtime) and serves a file page by page. Nothing leaves the machine.

# %%
con = G.registry()
n = con.sql("select count(*) from registrations").fetchall()[0][0]
G.check(n == 40000, f"DuckDB reads the register extract: {n:,} rows")

url = G.start_api()
try:
    page = G.get_json(f"{url}/v1/donations?page=1")
    G.check(page["page"] == 1 and len(page["data"]) > 0, f"the local donations API answers at {url}")
finally:
    G.stop_api()

# %% [markdown]
# ## Arabic text
#
# The line below must show an Arabic name, readable, written right to left. If it shows question marks or
# boxes in a terminal, set `PYTHONIOENCODING=utf-8`; notebooks need nothing.

# %%
print("شبكة غِلال لبنوك الطعام · Ghilal Food Bank Network")
print("\nAll lines above start with ✅: you are ready for Day 1.")
