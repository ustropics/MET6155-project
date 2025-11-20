# plt_tos_anomaly_maps.py
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
DATA_DIR = r"D:\school\MET6155\final_project\data"
FIGURES_DIR = Path(DATA_DIR).parent / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

print(f"Figures will be saved to: {FIGURES_DIR}\n")

# ------------------------------------------------------------------
# 2. Find tos files
# ------------------------------------------------------------------
tos_files = sorted(glob.glob(os.path.join(
    DATA_DIR, "**", "tos_Omon_*.nc"), recursive=True))
print(f"Found {len(tos_files)} tos files:")
for f in tos_files:
    print(f"  → {os.path.basename(f)}")

if not tos_files:
    raise FileNotFoundError("No tos files found!")

# ------------------------------------------------------------------
# 3. Open with CORRECT combine='nested' + concat_dim='time'
# ------------------------------------------------------------------
print("\nOpening all tos files with xarray...")
ds = xr.open_mfdataset(
    tos_files,
    combine='nested',          # ← FIX: was 'by_coords'
    concat_dim='time',         # ← Explicitly concatenate along time
    compat='override',
    coords='minimal',
    data_vars='minimal'
)

# Ensure time is sorted
ds = ds.sortby('time')

# Decode time properly (cftime → pandas)
ds = xr.decode_cf(ds)

print(f"Time range: {ds.time.min().values} → {ds.time.max().values}")

# ------------------------------------------------------------------
# 4. Define decades
# ------------------------------------------------------------------
decades = [
    ("2020", "2029"),
    ("2030", "2039"),
    ("2040", "2049"),
    ("2050", "2059"),
    ("2060", "2069"),
    ("2070", "2079"),
    ("2080", "2089"),
    ("2090", "2099"),
]

# ------------------------------------------------------------------
# 5. Baseline: 2020–2029
# ------------------------------------------------------------------
print("\nComputing baseline (2020–2029)...")
baseline = ds.tos.sel(time=slice("2020-01-01", "2029-12-31")).mean(dim='time')
print(f"Global mean baseline SST: {baseline.mean().values:.2f} K")

# ------------------------------------------------------------------
# 6. Process each decade
# ------------------------------------------------------------------
for start, end in decades:
    print(f"\nProcessing {start}–{end}...")
    decade_slice = ds.tos.sel(time=slice(f"{start}-01-01", f"{end}-12-31"))

    if decade_slice.size == 0:
        print(f"  → No data for {start}–{end}, skipping.")
        continue

    tos_mean = decade_slice.mean(dim='time')
    tos_anom = tos_mean - baseline

    # Plot
    fig, ax = plt.subplots(figsize=(12, 6), subplot_kw={
                           'projection': ccrs.PlateCarree()})
    levels = np.linspace(-2.5, 0.5, 21)
    im = tos_anom.plot.contourf(
        ax=ax,
        transform=ccrs.PlateCarree(),
        levels=levels,
        cmap='RdBu_r',
        extend='both',
        cbar_kwargs={'label': 'ΔSST vs 2020–2029 (K)', 'shrink': 0.7}
    )
    ax.coastlines()
    ax.set_title(f"G6sulfur SST Anomaly – {start}–{end}", fontsize=14)
    ax.gridlines(draw_labels=True, alpha=0.4, linestyle='--')

    # Save
    out_path = FIGURES_DIR / f"tos_anomaly_{start}.png"
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"   Saved: {out_path.name}")

# ------------------------------------------------------------------
# 7. Global mean trend
# ------------------------------------------------------------------
print("\nComputing global SST trend...")


def global_mean(da):
    weights = np.cos(np.deg2rad(da.lat))
    return da.weighted(weights).mean(['lat', 'lon'])


# Annual → decadal means
annual = ds.tos.resample(time='YS').mean()
decadal = annual.resample(time='10YS').mean()
anoms = global_mean(decadal - baseline)

# Plot
plt.figure(figsize=(10, 4))
anoms.plot(marker='o', color='teal')
plt.axhline(0, color='k', linewidth=0.8)
plt.title('G6sulfur Global-Mean SST Anomaly (vs 2020–2029)')
plt.ylabel('ΔSST (K)')
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "tos_global_trend.png", dpi=150)
plt.show()

print(f"\nAll done! Figures saved in: {FIGURES_DIR}")
