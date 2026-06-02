#!/usr/bin/env python3
"""
Threshold analysis for identifying non-engagers in the high-interactivity condition.

Outputs:
  analysis/engagement_thresholds.txt   — exclusion counts at each threshold
  analysis/plots/                      — distribution figures
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

METRICS_PATH = os.path.join("analysis", "conversation_engagement_metrics.csv")
OUT_TXT = os.path.join("analysis", "engagement_thresholds.txt")
PLOTS_DIR = os.path.join("analysis", "plots")


# ---------------------------------------------------------------------------
# Threshold definitions
# ---------------------------------------------------------------------------
TURN_THRESHOLDS  = [1, 2, 3]          # exclude if num_user_turns  < threshold
WORD_THRESHOLDS  = [10, 20, 30, 50]   # exclude if total_user_words < threshold
AVG_WORD_THRESHOLDS = [5, 10, 15, 20] # exclude if avg_user_words_per_turn < threshold

# Combined: both conditions must be true to exclude
COMBINED = [
    (1,  10,  "turns<1  AND words<10"),
    (2,  10,  "turns<2  AND words<10"),
    (2,  20,  "turns<2  AND words<20"),
    (2,  30,  "turns<2  AND words<30"),
    (3,  20,  "turns<3  AND words<20"),
    (3,  30,  "turns<3  AND words<30"),
]


def pct(n, total):
    return f"{n:3d} / {total}  ({100*n/total:5.1f}%)"


def exclusions_by_scenario(df, mask):
    """Return a breakdown of exclusions per scenario_id."""
    return df[mask].groupby("scenario_id").size().reindex(
        sorted(df["scenario_id"].unique()), fill_value=0
    )


def main():
    os.makedirs(PLOTS_DIR, exist_ok=True)

    df = pd.read_csv(METRICS_PATH)
    N = len(df)

    lines = []
    lines.append(f"Engagement threshold analysis — {N} total high-interactivity conversations\n")
    lines.append("=" * 70)

    # -----------------------------------------------------------------------
    # Raw distribution summary
    # -----------------------------------------------------------------------
    lines.append("\n--- Raw distribution ---\n")
    for col in ["num_user_turns", "total_user_words", "avg_user_words_per_turn"]:
        s = df[col].dropna()
        lines.append(f"{col}:")
        lines.append(f"  min={s.min():.0f}  p25={s.quantile(.25):.1f}  "
                     f"median={s.median():.1f}  p75={s.quantile(.75):.1f}  "
                     f"max={s.max():.0f}  mean={s.mean():.1f}")
    lines.append(f"\n  num_user_turns == 0 : {pct((df['num_user_turns']==0).sum(), N)}")
    lines.append(f"  num_user_turns == 1 : {pct((df['num_user_turns']==1).sum(), N)}")

    # -----------------------------------------------------------------------
    # Turn-based thresholds
    # -----------------------------------------------------------------------
    lines.append("\n\n--- Turns-based exclusions (exclude if num_user_turns < threshold) ---\n")
    lines.append(f"  {'Threshold':<30} {'Excluded':>10}   per-scenario breakdown")
    for t in TURN_THRESHOLDS:
        mask = df["num_user_turns"] < t
        bysc = exclusions_by_scenario(df, mask)
        lines.append(f"  turns < {t:<23} {pct(mask.sum(), N)}   {dict(bysc)}")

    # -----------------------------------------------------------------------
    # Word-based thresholds
    # -----------------------------------------------------------------------
    lines.append("\n\n--- Word-based exclusions (exclude if total_user_words < threshold) ---\n")
    for t in WORD_THRESHOLDS:
        mask = df["total_user_words"] < t
        bysc = exclusions_by_scenario(df, mask)
        lines.append(f"  words < {t:<22} {pct(mask.sum(), N)}   {dict(bysc)}")

    # -----------------------------------------------------------------------
    # Avg-words-per-turn thresholds
    # -----------------------------------------------------------------------
    lines.append("\n\n--- Avg words/turn exclusions (exclude if avg_user_words_per_turn < threshold) ---\n")
    for t in AVG_WORD_THRESHOLDS:
        mask = df["avg_user_words_per_turn"].fillna(0) < t
        bysc = exclusions_by_scenario(df, mask)
        lines.append(f"  avg_wpt < {t:<21} {pct(mask.sum(), N)}   {dict(bysc)}")

    # -----------------------------------------------------------------------
    # Combined thresholds
    # -----------------------------------------------------------------------
    lines.append("\n\n--- Combined exclusions (turns AND words both below cutoff) ---\n")
    for (t_turn, t_word, label) in COMBINED:
        mask = (df["num_user_turns"] < t_turn) & (df["total_user_words"] < t_word)
        bysc = exclusions_by_scenario(df, mask)
        lines.append(f"  {label:<30} {pct(mask.sum(), N)}   {dict(bysc)}")

    # -----------------------------------------------------------------------
    # OR-combined (either condition triggers exclusion)
    # -----------------------------------------------------------------------
    lines.append("\n\n--- OR-combined exclusions (turns OR words below cutoff) ---\n")
    for (t_turn, t_word, _) in COMBINED:
        label = f"turns<{t_turn}  OR  words<{t_word}"
        mask = (df["num_user_turns"] < t_turn) | (df["total_user_words"] < t_word)
        bysc = exclusions_by_scenario(df, mask)
        lines.append(f"  {label:<30} {pct(mask.sum(), N)}   {dict(bysc)}")

    # -----------------------------------------------------------------------
    # Write text report
    # -----------------------------------------------------------------------
    report = "\n".join(lines)
    with open(OUT_TXT, "w") as f:
        f.write(report)
    print(report)

    # -----------------------------------------------------------------------
    # Plots
    # -----------------------------------------------------------------------
    _plot_distributions(df)
    _plot_threshold_curves(df, N)
    _plot_scatter(df)

    print(f"\nPlots written to {PLOTS_DIR}/")


def _plot_distributions(df):
    fig = plt.figure(figsize=(14, 10))
    fig.suptitle("Engagement variable distributions — high-interactivity condition", fontsize=13)
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

    # 1. num_user_turns histogram
    ax = fig.add_subplot(gs[0, 0])
    bins = range(0, df["num_user_turns"].max() + 2)
    ax.hist(df["num_user_turns"], bins=bins, align="left", color="#4c72b0", edgecolor="white", linewidth=0.6)
    ax.set_xlabel("User turns")
    ax.set_ylabel("Conversations")
    ax.set_title("User turns per conversation")
    ax.set_xticks(list(bins)[:-1])
    for t, color in [(1, "#e07b39"), (2, "#c44e52"), (3, "#8c8c8c")]:
        ax.axvline(t - 0.5, color=color, linestyle="--", linewidth=1.2, label=f"<{t}")
    ax.legend(title="Excl. thresholds", fontsize=7, title_fontsize=7)

    # 2. total_user_words histogram
    ax = fig.add_subplot(gs[0, 1])
    ax.hist(df["total_user_words"], bins=30, color="#55a868", edgecolor="white", linewidth=0.6)
    ax.set_xlabel("Total user words")
    ax.set_title("Total user words per conversation")
    for t, color in [(10, "#e07b39"), (20, "#c44e52"), (30, "#8c8c8c"), (50, "#9467bd")]:
        ax.axvline(t, color=color, linestyle="--", linewidth=1.2, label=f"<{t}")
    ax.legend(title="Excl. thresholds", fontsize=7, title_fontsize=7)

    # 3. avg_user_words_per_turn histogram
    ax = fig.add_subplot(gs[0, 2])
    ax.hist(df["avg_user_words_per_turn"].dropna(), bins=25, color="#c44e52", edgecolor="white", linewidth=0.6)
    ax.set_xlabel("Avg words / user turn")
    ax.set_title("Avg words per user turn")
    for t, color in [(5, "#e07b39"), (10, "#c44e52"), (15, "#8c8c8c"), (20, "#9467bd")]:
        ax.axvline(t, color=color, linestyle="--", linewidth=1.2, label=f"<{t}")
    ax.legend(title="Excl. thresholds", fontsize=7, title_fontsize=7)

    # 4. Cumulative user turns
    ax = fig.add_subplot(gs[1, 0])
    vals = sorted(df["num_user_turns"])
    cdf = [sum(v <= x for v in vals) / len(vals) for x in vals]
    ax.plot(vals, cdf, color="#4c72b0", linewidth=1.5)
    ax.set_xlabel("User turns")
    ax.set_ylabel("Cumulative proportion")
    ax.set_title("CDF — user turns")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    ax.grid(True, alpha=0.3)
    for t, color in [(1, "#e07b39"), (2, "#c44e52"), (3, "#8c8c8c")]:
        ax.axvline(t, color=color, linestyle="--", linewidth=1, label=f"<{t}")
    ax.legend(fontsize=7)

    # 5. Cumulative total words
    ax = fig.add_subplot(gs[1, 1])
    vals = sorted(df["total_user_words"])
    cdf = [sum(v <= x for v in vals) / len(vals) for x in vals]
    ax.plot(vals, cdf, color="#55a868", linewidth=1.5)
    ax.set_xlabel("Total user words")
    ax.set_ylabel("Cumulative proportion")
    ax.set_title("CDF — total user words")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    ax.grid(True, alpha=0.3)
    for t, color in [(10, "#e07b39"), (20, "#c44e52"), (30, "#8c8c8c"), (50, "#9467bd")]:
        ax.axvline(t, color=color, linestyle="--", linewidth=1, label=f"<{t}")
    ax.legend(fontsize=7)

    # 6. Boxplots by study_type
    ax = fig.add_subplot(gs[1, 2])
    aita   = df[df["study_type"] == "aita"]["num_user_turns"]
    sexism = df[df["study_type"] == "sexism"]["num_user_turns"]
    bp = ax.boxplot([aita, sexism], labels=["AITA", "Sexism"], patch_artist=True,
                    medianprops=dict(color="black", linewidth=1.5))
    bp["boxes"][0].set_facecolor("#4c72b0")
    bp["boxes"][1].set_facecolor("#c44e52")
    ax.set_ylabel("User turns")
    ax.set_title("User turns by study type")

    fig.savefig(os.path.join(PLOTS_DIR, "engagement_distributions.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


def _plot_threshold_curves(df, N):
    """Show % excluded as threshold sweeps — one curve per variable."""
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    fig.suptitle("% of conversations excluded at each threshold", fontsize=12)

    # Turns
    ax = axes[0]
    xs = range(0, 7)
    ys = [100 * (df["num_user_turns"] < t).sum() / N for t in xs]
    ax.plot(xs, ys, marker="o", color="#4c72b0")
    ax.set_xlabel("Threshold (exclude if turns < x)")
    ax.set_ylabel("% excluded")
    ax.set_title("By user turns")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    for i, (x, y) in enumerate(zip(xs, ys)):
        ax.annotate(f"{y:.1f}%", (x, y), textcoords="offset points", xytext=(0, 6), fontsize=7, ha="center")
    ax.grid(True, alpha=0.3)

    # Total words
    ax = axes[1]
    xs2 = list(range(0, 105, 5))
    ys2 = [100 * (df["total_user_words"] < t).sum() / N for t in xs2]
    ax.plot(xs2, ys2, marker="o", markersize=4, color="#55a868")
    ax.set_xlabel("Threshold (exclude if words < x)")
    ax.set_title("By total user words")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.grid(True, alpha=0.3)

    # Avg words/turn
    ax = axes[2]
    xs3 = list(range(0, 45, 2))
    ys3 = [100 * (df["avg_user_words_per_turn"].fillna(0) < t).sum() / N for t in xs3]
    ax.plot(xs3, ys3, marker="o", markersize=4, color="#c44e52")
    ax.set_xlabel("Threshold (exclude if avg wpt < x)")
    ax.set_title("By avg words / user turn")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS_DIR, "exclusion_curves.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


def _plot_scatter(df):
    """Scatter: total_user_words vs num_user_turns, coloured by study_type."""
    fig, ax = plt.subplots(figsize=(8, 6))

    colors = {"aita": "#4c72b0", "sexism": "#c44e52"}
    for stype, grp in df.groupby("study_type"):
        ax.scatter(grp["num_user_turns"], grp["total_user_words"],
                   label=stype.upper(), alpha=0.5, s=30, color=colors.get(stype, "grey"))

    # Reference lines for a few candidate thresholds
    ax.axvline(2, color="#555", linestyle="--", linewidth=1, label="turns=2")
    ax.axhline(20, color="#999", linestyle=":", linewidth=1, label="words=20")

    ax.set_xlabel("Number of user turns")
    ax.set_ylabel("Total user words")
    ax.set_title("User turns vs. total words — high-interactivity condition")
    ax.legend()
    ax.grid(True, alpha=0.25)

    fig.savefig(os.path.join(PLOTS_DIR, "turns_vs_words_scatter.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
