# plot_tas_anomaly_maps.py
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import glob
import os
from pathlib import Path

# ------------------------------------------------------------------
# 1. Paths
# ------------------------------------------------------------------
BASE = r"D:\school\MET6155\final_project\data"
FIGURES_DIR = Path(BASE) / ".." / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

print(f"Saving anomaly maps to: {FIGURES_DIR}\n")

# ------------------------------------------------------------------
# 2. Find all tas files
# ------------------------------------------------------------------
tas_files = sorted(glob.glob(os.path.join(
    BASE, "**", "tas_Amon_*.nc"), recursive=True))
print(f"Found {len(tas_files)} tas files")

# ------------------------------------------------------------------
# 3. Load 2020–2029 as baseline
# ------------------------------------------------------------------
baseline_file = [f for f in tas_files if "202001-202912" in f][0]
print(f"Baseline (2020–2029): {os.path.basename(baseline_file)}")

ds_base = xr.open_dataset(baseline_file)
tas_base = ds_base.tas.mean(dim='time')  # 10-year mean
ds_base.close()

# ------------------------------------------------------------------
# 4. Process each decade → anomaly → plot → save
# ------------------------------------------------------------------
for file_path in tas_files:
    filename = os.path.basename(file_path)
    try:
        start_year = int(filename.split("_")[-1].split("-")[0][:4])
        decade = f"{start_year}-{start_year + 9}"
    except:
        ds_temp = xr.open_dataset(file_path)
        start_year = pd.to_datetime(ds_temp.time.values[0]).year
        decade = f"{start_year}-{start_year + 9}"
        ds_temp.close()

    print(f"Processing {decade}...")

    # Open and compute decadal mean
    ds = xr.open_dataset(file_path)
    tas_mean = ds.tas.mean(dim='time')
    ds.close()

    # Anomaly
    tas_anom = tas_mean - tas_base

    # Plot
    fig, ax = plt.subplots(figsize=(12, 6), subplot_kw={
                           'projection': ccrs.PlateCarree()})
    levels = np.linspace(-3, 1, 31)
    im = tas_anom.plot.contourf(
        ax=ax, transform=ccrs.PlateCarree(),
        levels=levels, cmap='RdBu_r', extend='both',
        cbar_kwargs={'label': 'ΔT vs 2020–2029 (K)', 'shrink': 0.7}
    )
    ax.coastlines()
    ax.set_title(f"G6sulfur tas Anomaly – {decade}", fontsize=14)
    ax.gridlines(draw_labels=True, alpha=0.4, linestyle='--')

    # Save
    out_path = FIGURES_DIR / f"anomaly_tas_{start_year}.png"
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"   Saved: {out_path.name}")

print("\nAll anomaly maps saved!")
