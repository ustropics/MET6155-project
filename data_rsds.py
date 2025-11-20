import asyncio
import os
from esgpull import Esgpull, Query
from esgpull.models import File
from pathlib import Path

# ----------------------------
# Configuration
# ----------------------------
DATA_DIR = r"D:\school\MET6155\final_project\data\rsds"  # separate folder
os.makedirs(DATA_DIR, exist_ok=True)

# ----------------------------
# Initialize Esgpull
# ----------------------------
esg = Esgpull()
esg.config.paths.data = DATA_DIR

# ----------------------------
# Build Query: G6sulfur + rsds + r1i1p1f2
# ----------------------------
q = Query()
q.selection.project = "CMIP6"
q.selection.activity_id = "GeoMIP"
q.selection.source_id = "CESM2-WACCM"
q.selection.experiment_id = "G6sulfur"
q.selection.variable_id = "rsds"        # ← Surface downwelling shortwave
q.selection.table_id = "Amon"          # Monthly mean
q.selection.grid_label = "gn"
q.selection.member_id = "r1i1p1f2"     # Same as your tas run

# ----------------------------
# Search datasets
# ----------------------------
print("Searching for rsds datasets in G6sulfur...")
datasets = esg.context.datasets(q)
print(f"Found {len(datasets)} dataset(s):")
for ds in datasets:
    print(f"  - {ds.dataset_id}")

if not datasets:
    print("No rsds data found. Try checking ESGF or model availability.")
    exit()

# ----------------------------
# Clean old DB entries
# ----------------------------
print("\nCleaning old rsds file records...")
with esg.db.session as session:
    deleted = session.query(File).filter(
        File.dataset_id.contains("G6sulfur"),
        File.dataset_id.contains("rsds"),
        File.dataset_id.contains("r1i1p1f2")
    ).delete()
    session.commit()
print(f"Removed {deleted} old records.")

# ----------------------------
# Get files
# ----------------------------
print("\nRetrieving rsds files...")
files = esg.context.files(q)
print(f"Found {len(files)} files to download...")

if not files:
    print("No files found.")
    exit()

# ----------------------------
# Clean stale .part/.done files (Windows fix)
# ----------------------------
print("Cleaning stale temp files...")
tmp_dir = Path.home() / ".esgpull" / "tmp"
os.makedirs(tmp_dir, exist_ok=True)

cleaned = 0
for file in files:
    if file.sha:
        for suffix in (".part", ".done"):
            tmp_file = tmp_dir / f"{file.sha}{suffix}"
            if tmp_file.exists():
                try:
                    tmp_file.unlink()
                    cleaned += 1
                except:
                    pass
if cleaned:
    print(f"Cleaned {cleaned} stale temp file(s).")

# ----------------------------
# Download
# ----------------------------
print(f"\nDownloading {len(files)} rsds file(s)...")
try:
    asyncio.run(esg.download(files))
    print("\nAll rsds files downloaded successfully!")
except Exception as e:
    print(f"\nDownload failed: {e}")
    raise

# ----------------------------
# Verify
# ----------------------------
print("\nVerification:")
downloaded = sum(1 for f in files if os.path.exists(f.local_path))
print(f"{downloaded}/{len(files)} files saved to {DATA_DIR}")
