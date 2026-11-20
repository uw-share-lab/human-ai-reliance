#!/usr/bin/env python3
"""
Engagement descriptives figure (CHI 2027 revision; paper Figure fig:engagement).

Four panels over all 254 logged conversational sessions: chat duration, AI
words per session (grey band = static rationale length, 47-100 words),
participant words per session, and hand-coded engagement depth (0-4).
Static print figure: one sequential hue, medians in ink, no legend.

Usage (from post-study-analysis/):
    python scripts/engagement_descriptives_figure.py [OUTDIR]
Default OUTDIR: outputs/figures/  (gitignored). Writes engagement_descriptives.{pdf,png}.
"""
import os, sys, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join("outputs", "figures")
os.makedirs(out, exist_ok=True)
e = pd.read_csv("data-derived/conversation_engagement_metrics.csv")
dep = pd.read_csv("data-derived/engagement_depth_resolved.csv")[["conversation_id", "depth"]]
e = e.merge(dep, on="conversation_id", how="left")
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
BLUE = "#2a78d6"            # sequential default hue (step 450)
REF = "#52514e"             # reference lines wear secondary ink, not a series colour
plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.linewidth": 0.6, "font.family": "sans-serif"})
fig, axs = plt.subplots(1, 4, figsize=(7.0, 1.95), facecolor=SURF, gridspec_kw={"width_ratios": [1, 1, 1, 0.8]})
def style(ax, xlabel):
    ax.set_facecolor(SURF); ax.set_xlabel(xlabel)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.yaxis.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
def hist(ax, x, bins, xlabel, unit, median=True):
    ax.hist(x, bins=bins, color=BLUE, edgecolor=SURF, linewidth=1.0)   # surface gap between bars
    if median:
        med = np.median(x); ax.axvline(med, color=INK, lw=1.0)
        ax.text(med, ax.get_ylim()[1] * 0.97, f" median {med:g}{unit}", color=INK, va="top", ha="left", fontsize=7)
    style(ax, xlabel)
d = e.duration_seconds
hist(axs[0], d, np.arange(0, 290, 15), "Chat duration (s)", " s", median=False)
n_lim = int(e.exceeded_3_minutes.sum())
axs[0].annotate(f"{n_lim} of {len(e)}\nran to the\n3-min limit\n(median {d.median():.0f} s)", xy=(178, n_lim * 0.9), xytext=(-5, n_lim * 0.45), color=INK, fontsize=7, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6))
axs[0].set_ylabel("Sessions")
hist(axs[1], e.total_ai_words, np.arange(0, 1000, 50), "AI words per session", "")
axs[1].axvspan(47, 100, color=INK2, alpha=0.18, lw=0)
# grey band = static rationale length (47–100 words); explained in the caption
hist(axs[2], e.total_user_words, np.arange(0, 520, 25), "Participant words per session", "")
c = e.depth.value_counts().reindex(range(5), fill_value=0)
axs[3].bar(c.index, c.values, color=BLUE, width=0.82, edgecolor=SURF, linewidth=1.0)
for k, v in c.items(): axs[3].text(k, v + 2, str(v), ha="center", va="bottom", fontsize=7, color=INK)
axs[3].set_xticks(range(5)); style(axs[3], "Engagement depth")
axs[3].set_ylim(0, c.max() * 1.18)
fig.tight_layout(pad=0.4, w_pad=1.2)
for ext in ("pdf", "png"): fig.savefig(f"{out}/engagement_descriptives.{ext}", dpi=300, facecolor=SURF)
print("n sessions", len(e), "| depth missing", e.depth.isna().sum(), "| median dur", d.median(), "| >=180s", (e.exceeded_3_minutes).sum())
