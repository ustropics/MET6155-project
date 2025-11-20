#!/usr/bin/env python3
"""
make_sargassum_figures.py

Recreates:
1. Conceptual growth vs temperature curves for Sargassum groups
2. Reconstructed forest plots (illustrative) for warming effects

Requires: numpy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    "text.usetex": False,
    "font.size": 11,
    "figure.dpi": 150,
})

# --------------------------------------------------------------------
# FIGURE 1: Conceptual Growth vs Temperature
# --------------------------------------------------------------------

temps = np.linspace(10, 35, 500)


def gaussian(x, mu, sigma):
    return np.exp(-0.5*((x-mu)/sigma)**2)


# Peaks chosen based on Carneiro et al. (2025) summaries
peaks = {
    'S. polycystum (benthic)': 24,
    'Tropical benthic Sargassum': 27,
    'Temperate benthic Sargassum': 22,
    'Pelagic S. natans/fluitans': 27
}

sigmas = {
    'S. polycystum (benthic)': 3.2,
    'Tropical benthic Sargassum': 3.5,
    'Temperate benthic Sargassum': 3.0,
    'Pelagic S. natans/fluitans': 3.8
}

plt.figure(figsize=(12, 8))
for label in peaks:
    y = gaussian(temps, peaks[label], sigmas[label])
    y /= y.max()
    plt.plot(temps, y, linewidth=2, label=label)

plt.xlabel("Temperature (°C)")
plt.ylabel("Relative Growth (normalized)")
plt.title("Conceptual Growth Response to Temperature")
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig("figure_conceptual_growth.png", dpi=300)
plt.close()

print("Saved: figure_conceptual_growth.png")

# --------------------------------------------------------------------
# FIGURE 2: Reconstructed Forest Plot (illustrative)
# --------------------------------------------------------------------

labels = [
    'Study A (SSP2)', 'Study B (SSP2)', 'Study C (SSP5)', 'Study D (SSP5)',
    'Agg. Tropical (SSP2)', 'Agg. Temperate (SSP2)',
    'Agg. Tropical (SSP5)', 'Agg. Temperate (SSP5)'
]

# synthetic effect sizes approximating direction/magnitude from Carneiro et al. (2025)
growth_effects = np.array(
    [-0.45, -0.60, -0.85, -0.70, -0.80, -0.65, -1.00, -0.75])
growth_se = np.array([0.18,  0.15,  0.20,  0.17,  0.12,  0.13,  0.14,  0.13])
growth_low = growth_effects - 1.96*growth_se
growth_high = growth_effects + 1.96*growth_se

fvfm_effects = np.array(
    [-0.30, -0.40, -0.50, -0.35, -0.55, -0.30, -0.65, -0.45])
fvfm_se = np.array([0.14,  0.12,  0.16,  0.13,  0.10,  0.11,  0.12,  0.11])
fvfm_low = fvfm_effects - 1.96*fvfm_se
fvfm_high = fvfm_effects + 1.96*fvfm_se

y = np.arange(len(labels))

fig, axes = plt.subplots(1, 2, figsize=(16, 12))

# Left: Growth rate effects
ax = axes[0]
ax.hlines(y, growth_low, growth_high, color="tab:orange", linewidth=2)
ax.plot(growth_effects, y, "s", color="tab:orange")
ax.vlines(0, -1, len(labels), linestyles='dashed', color='gray')
ax.set_yticks(y)
ax.set_yticklabels(labels)
ax.invert_yaxis()
ax.set_xlabel("Effect size (Hedges' g)")
ax.set_title("Growth Rate Effects (Illustrative)")

# Right: Fv/Fm effects
ax2 = axes[1]
ax2.hlines(y, fvfm_low, fvfm_high, color="tab:orange", linewidth=2)
ax2.plot(fvfm_effects, y, "s", color="tab:orange")
ax2.vlines(0, -1, len(labels), linestyles='dashed', color='gray')
ax2.set_yticks(y)
ax2.set_yticklabels([])
ax2.invert_yaxis()
ax2.set_xlabel("Effect size (Hedges' g)")
ax2.set_title("Fv/Fm Effects (Illustrative)")

plt.tight_layout()
plt.savefig("figure_forest_plot.png", dpi=300)
plt.close()

print("Saved: figure_forest_plot.png")

print("\nAll figures created successfully.\n")
