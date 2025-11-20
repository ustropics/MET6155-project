import asyncio
import os
from esgpull import Esgpull, Query
from esgpull.models import File
from pathlib import Path

# ----------------------------
# Configuration
# ----------------------------
DATA_DIR = r"D:\school\MET6155\final_project\data"
os.makedirs(DATA_DIR, exist_ok=True)

# ----------------------------
# Initialize Esgpull
# ----------------------------
esg = Esgpull()
esg.config.paths.data = DATA_DIR

# ----------------------------
# Build Query - ONLY r1i1p1f2
# ----------------------------
q = Query()
q.selection.project = "CMIP6"
q.selection.activity_id = "GeoMIP"
q.selection.source_id = "CESM2-WACCM"
q.selection.experiment_id = "G6sulfur"
q.selection.variable_id = "tas"
q.selection.table_id = "Amon"
q.selection.grid_label = "gn"
q.selection.member_id = "r1i1p1f2"  # Prevents file_id collision

# ----------------------------
# Search datasets
# ----------------------------
print("Searching for datasets...")
datasets = esg.context.datasets(q)
print(f"Found {len(datasets)} dataset(s):")
for ds in datasets:
    print(f"  - {ds.dataset_id}")

if not datasets:
    print("No datasets found.")
    exit()

# ----------------------------
# Clean old DB entries
# ----------------------------
print("\nCleaning old file records from database...")
with esg.db.session as session:
    deleted = session.query(File).filter(
        File.dataset_id.contains("G6sulfur"),
        File.dataset_id.contains("r1i1p1f2")
    ).delete()
    session.commit()
print(f"Removed {deleted} old records.")

# ----------------------------
# Get files
# ----------------------------
print("\nRetrieving files...")
files = esg.context.files(q)
print(f"Found {len(files)} files to download...")

if not files:
    print("No files to download.")
    exit()

# ----------------------------
# CRITICAL FIX: Remove stale .part and .done files
# ----------------------------
print("Cleaning stale temporary files (.part, .done)...")
tmp_dir = Path.home() / ".esgpull" / "tmp"
os.makedirs(tmp_dir, exist_ok=True)

cleaned = 0
for file in files:
    if not file.sha:
        continue
    part_file = tmp_dir / f"{file.sha}.part"
    done_file = tmp_dir / f"{file.sha}.done"
    for f in (part_file, done_file):
        if f.exists():
            try:
                f.unlink()
                cleaned += 1
            except Exception as e:
                print(f"  Warning: Could not delete {f}: {e}")
if cleaned:
    print(f"Cleaned {cleaned} stale temp file(s).")

# ----------------------------
# Download
# ----------------------------
print(f"\nStarting download of {len(files)} file(s)...")
try:
    asyncio.run(esg.download(files))
    print("\nAll files downloaded successfully!")
except Exception as e:
    print(f"\nDownload failed: {e}")
    raise

# ----------------------------
# Verify
# ----------------------------
print("\nVerifying downloaded files...")
downloaded = sum(1 for f in files if os.path.exists(f.local_path))
print(f"{downloaded} / {len(files)} files are in {DATA_DIR}")

# Optional: List first few
for f in files[:3]:
    status = "Success" if os.path.exists(f.local_path) else "Failed"
    print(f"  [{status}] {f.filename}")
if len(files) > 3:
    print(f"  ... and {len(files) - 3} more")
