"""
Deepika_K_StudentAcademicPerformance.py
---------------------------------------
Loads the student dataset, cleans the data, computes summary metrics,
and saves two chart images used by the project report.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")          # non-interactive backend — safe in all envs
import matplotlib.pyplot as plt
import seaborn as sns

# ── 0. locate dataset ────────────────────────────────────────────────────────

for candidate in ("student_data.csv", "student_dataset.csv"):
    if os.path.exists(candidate):
        DATA_FILE = candidate
        break
else:
    sys.exit("ERROR: neither student_data.csv nor student_dataset.csv found.")

print(f"Loading data from: {DATA_FILE}")

# ── 1. load ──────────────────────────────────────────────────────────────────

df = pd.read_csv(DATA_FILE)
print(f"Raw shape: {df.shape}")

# ── 2. clean ─────────────────────────────────────────────────────────────────

# Drop fully-duplicate rows
df.drop_duplicates(inplace=True)

# Coerce expected numeric columns
numeric_cols = [
    "ssc_percentage", "hsc_percentage", "degree_percentage", "cgpa",
    "entrance_exam_score", "technical_skill_score", "soft_skill_score",
    "internship_count", "live_projects", "work_experience_months",
    "certifications", "attendance_percentage", "backlogs",
    "salary_package_lpa",
]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Fill numeric NaNs with column median
df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median(numeric_only=True))

# Standardise categorical columns
if "gender" in df.columns:
    df["gender"] = df["gender"].str.strip().str.title()
if "extracurricular_activities" in df.columns:
    df["extracurricular_activities"] = (
        df["extracurricular_activities"].str.strip().str.title()
    )
if "placement_status" in df.columns:
    df["placement_status"] = pd.to_numeric(df["placement_status"], errors="coerce")

print(f"Clean shape: {df.shape}")
print(f"Missing values remaining:\n{df.isnull().sum()[df.isnull().sum() > 0]}")

# ── 3. metrics ───────────────────────────────────────────────────────────────

key_metrics = {
    "Total Students":         len(df),
    "Placement Rate (%)":     round(df["placement_status"].mean() * 100, 2)
                              if "placement_status" in df.columns else "N/A",
    "Average CGPA":           round(df["cgpa"].mean(), 3),
    "Avg Technical Score":    round(df["technical_skill_score"].mean(), 2),
    "Avg Soft-Skill Score":   round(df["soft_skill_score"].mean(), 2),
    "Avg Attendance (%)":     round(df["attendance_percentage"].mean(), 2),
    "Avg Backlogs":           round(df["backlogs"].mean(), 2),
    "Avg Internships":        round(df["internship_count"].mean(), 2),
}

print("\n-- Summary Metrics --")
for k, v in key_metrics.items():
    print(f"  {k:<28} {v}")

# ── 4. chart 1 — score distribution ─────────────────────────────────────────

dist_cols = ["cgpa", "entrance_exam_score", "technical_skill_score", "soft_skill_score"]
dist_cols = [c for c in dist_cols if c in df.columns]

fig, axes = plt.subplots(1, len(dist_cols), figsize=(5 * len(dist_cols), 5))
if len(dist_cols) == 1:
    axes = [axes]

colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52"]
for ax, col, color in zip(axes, dist_cols, colors):
    sns.histplot(df[col].dropna(), kde=True, ax=ax, color=color, bins=25, edgecolor="white")
    ax.set_title(col.replace("_", " ").title(), fontsize=13, pad=8)
    ax.set_xlabel("Score / Value", fontsize=10)
    ax.set_ylabel("Count", fontsize=10)
    mean_val = df[col].mean()
    ax.axvline(mean_val, color="black", linestyle="--", linewidth=1.2,
               label=f"Mean = {mean_val:.2f}")
    ax.legend(fontsize=9)

fig.suptitle("Score Distributions — Student Academic Performance", fontsize=15, y=1.02)
plt.tight_layout()
plt.savefig("score_distribution.png", dpi=150, bbox_inches="tight")
plt.close()
print("\n  Saved: score_distribution.png")

# ── 5. chart 2 — correlation matrix ─────────────────────────────────────────

corr_cols = [c for c in numeric_cols if c in df.columns]
corr_matrix = df[corr_cols].corr()

fig, ax = plt.subplots(figsize=(14, 10))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(
    corr_matrix, mask=mask, annot=True, fmt=".2f",
    cmap="coolwarm", center=0, linewidths=0.5,
    annot_kws={"size": 8}, ax=ax,
)
ax.set_title("Feature Correlation Matrix — Student Academic Performance",
             fontsize=14, pad=12)
plt.xticks(rotation=45, ha="right", fontsize=9)
plt.yticks(fontsize=9)
plt.tight_layout()
plt.savefig("correlation_matrix.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: correlation_matrix.png")

# ── 6. expose for import by report generator ─────────────────────────────────

METRICS = key_metrics
DATA    = df
