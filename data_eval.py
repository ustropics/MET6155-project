# data_eval.py
import os
import glob
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import pandas as pd
import numpy as np

# ------------------------------------------------------------------
# 1. BASE PATH – CHANGE ONLY THIS
# ------------------------------------------------------------------
BASE = r"D:\school\MET6155\final_project\data"

# ------------------------------------------------------------------
# 2. SEARCH FOR FILES (CORRECT PATHS!)
# ------------------------------------------------------------------
# tas files are in: data/CMIP6/.../tas/...
tas_pattern = os.path.join(BASE, "CMIP6", "**", "tas_Amon_*.nc")

# rsds files are in: data/rsds/CMIP6/.../rsds/...
rsds_pattern = os.path.join(BASE, "rsds", "CMIP6", "**", "rsds_Amon_*.nc")

# Use recursive search
tas_files = sorted(glob.glob(tas_pattern,  recursive=True))
rsds_files = sorted(glob.glob(rsds_pattern, recursive=True))

print(f"tas  files: {len(tas_files)}")
print(f"rsds files: {len(rsds_files)}")

# Show first file of each
if tas_files:
    print("  tas example:", os.path.basename(tas_files[0]))
if rsds_files:
    print("  rsds example:", os.path.basename(rsds_files[0]))
else:
    print("  rsds NOT FOUND – check path!")

# ------------------------------------------------------------------
# 3. OPEN tas – SORT TIME MANUALLY (fixes monotonic error)
# ------------------------------------------------------------------
if not tas_files:
    raise FileNotFoundError("No tas files found")

print("\nOpening tas files... (sorting time)")
ds_tas = xr.open_mfdataset(
    tas_files,
    combine='by_coords',
    parallel=True,
    concat_dim='time',
    data_vars='minimal',
    coords='minimal',
    compat='override'
)

# CRITICAL: Sort time explicitly
ds_tas = ds_tas.sortby('time')

# ------------------------------------------------------------------
# 4. OPEN rsds – same fix
# ------------------------------------------------------------------
if rsds_files:
    print("Opening rsds files... (sorting time)")
    ds_rsds = xr.open_mfdataset(
        rsds_files,
        combine='by_coords',
        parallel=True,
        concat_dim='time',
        data_vars='minimal',
        coords='minimal',
        compat='override'
    )
    ds_rsds = ds_rsds.sortby('time')
else:
    ds_rsds = None
    print("Warning: rsds not found – skipping rsds plots")

# ------------------------------------------------------------------
# 5. Inspect
# ------------------------------------------------------------------
print(f"\ntas time:  {ds_tas.time.min().values} → {ds_tas.time.max().values}")
if ds_rsds:
    print(
        f"rsds time: {ds_rsds.time.min().values} → {ds_rsds.time.max().values}")

# ------------------------------------------------------------------
# 6. Global mean
# ------------------------------------------------------------------


def global_mean(da):
    weights = np.cos(np.deg2rad(da.lat))
    return da.weighted(weights).mean(dim=['lon', 'lat'])


tas_gm = global_mean(ds_tas.tas)

df = pd.DataFrame({'tas': tas_gm}).to_dataframe()

if ds_rsds:
    rsds_gm = global_mean(ds_rsds.rsds)
    df['rsds'] = rsds_gm

# ------------------------------------------------------------------
# 7. Plot time series
# ------------------------------------------------------------------


ax = df.plot(
    title='G6sulfur r1i1p1f2 – Global Mean (2020–2100)',
    secondary_y='rsds' if 'rsds' in df else None,
    figsize=(11, 5)
)
ax.left_axis.set_ylabel('Temperature (K)')
if 'rsds' in df:
    ax.right_axis.set_ylabel('Shortwave (W m⁻²)')
plt.axvline('2070-01-01', color='gray', linestyle='--', label='rsds gap')
plt.show()

# ------------------------------------------------------------------
# 8. Map: 2020–2029
# ------------------------------------------------------------------
dec = slice('2020-01-01', '2029-12-31')
tas_dec = ds_tas.tas.sel(time=dec).mean('time')


def plot_map(da, title, cmap, vmin, vmax):
    fig, ax = plt.subplots(figsize=(10, 5), subplot_kw={
                           'projection': ccrs.PlateCarree()})
    da.plot.contourf(ax=ax, transform=ccrs.PlateCarree(),
                     cmap=cmap, vmin=vmin, vmax=vmax,
                     cbar_kwargs={'label': da.units})
    ax.coastlines()
    ax.set_title(title)
    plt.show()


plot_map(tas_dec, 'tas 2020–2029 (K)', 'RdYlBu_r', 230, 310)

if ds_rsds:
    rsds_dec = ds_rsds.rsds.sel(time=dec).mean('time')
    plot_map(rsds_dec, 'rsds 2020–2029 (W m⁻²)', 'YlOrRd', 100, 300)
