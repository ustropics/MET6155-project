import asyncio
import os
from esgpull import Esgpull, Query
from esgpull.models import File
from pathlib import Path

# ----------------------------
# Configuration - SET PATH FIRST
# ----------------------------
DATA_DIR = r"D:\school\MET6155\final_project\data"
os.makedirs(DATA_DIR, exist_ok=True)

# ----------------------------
# Initialize Esgpull - PATH FIRST
# ----------------------------
esg = Esgpull()
esg.config.paths.data = DATA_DIR   # ← MUST BE BEFORE ANY QUERY

# ----------------------------
# Build Query
# ----------------------------
q = Query()
q.selection.project = "CMIP6"
q.selection.activity_id = "GeoMIP"
q.selection.source_id = "CESM2-WACCM"
q.selection.experiment_id = "G6sulfur"
q.selection.variable_id = "tos"
q.selection.table_id = "Omon"
q.selection.grid_label = "gn"
q.selection.member_id = "r1i1p1f2"

# ----------------------------
# Search
# ----------------------------
print("Searching for tos datasets...")
datasets = esg.context.datasets(q)
print(f"Found {len(datasets)} dataset(s)")

# ----------------------------
# Clean DB
# ----------------------------
print("\nCleaning old G6sulfur r1i1p1f2 records...")
with esg.db.session as session:
    deleted = session.query(File).filter(
        File.dataset_id.contains("G6sulfur"),
        File.dataset_id.contains("r1i1p1f2")
    ).delete()
    session.commit()
print(f"Removed {deleted} old record(s)")

# ----------------------------
# Get files
# ----------------------------
files = esg.context.files(q)
print(f"Found {len(files)} tos files")

if not files:
    print("No files to download.")
    exit()

# ----------------------------
# Clean stale temp files
# ----------------------------
tmp_dir = Path.home() / ".esgpull" / "tmp"
os.makedirs(tmp_dir, exist_ok=True)
for file in files:
    if file.sha:
        for ext in (".part", ".done"):
            f = tmp_dir / f"{file.sha}{ext}"
            if f.exists():
                f.unlink()

# ----------------------------
# DOWNLOAD
# ----------------------------
print(f"\nDownloading {len(files)} tos files to:\n  {DATA_DIR}")
try:
    asyncio.run(esg.download(files))
    print("\nDownload complete!")
except Exception as e:
    print(f"Download failed: {e}")
    raise

# ----------------------------
# FINAL VERIFICATION
# ----------------------------
print("\nVerifying files in target folder...")
downloaded = 0
for f in files:
    local_path = Path(f.local_path)
    if local_path.exists():
        downloaded += 1
        print(f"  [Success] {local_path.name}")
    else:
        print(f"  [Failed] {f.filename} → expected at {local_path}")

print(f"\n{downloaded} / {len(files)} files in {DATA_DIR}")
