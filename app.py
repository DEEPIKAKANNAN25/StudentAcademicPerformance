"""
app.py  –  Student Academic Performance Dashboard
Run with:  streamlit run app.py
"""

import os
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# ── page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Student Academic Performance",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── load & clean data ─────────────────────────────────────────────────────────

@st.cache_data
def load_data():
    for candidate in ("student_data.csv", "student_dataset.csv"):
        if os.path.exists(candidate):
            df = pd.read_csv(candidate)
            break
    else:
        st.error("Dataset not found. Place student_data.csv in the app directory.")
        st.stop()

    df.drop_duplicates(inplace=True)

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
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median(numeric_only=True))

    if "gender" in df.columns:
        df["gender"] = df["gender"].str.strip().str.title()
    if "extracurricular_activities" in df.columns:
        df["extracurricular_activities"] = df["extracurricular_activities"].str.strip().str.title()
    if "placement_status" in df.columns:
        df["placement_status"] = pd.to_numeric(df["placement_status"], errors="coerce")

    return df, numeric_cols


df_raw, NUMERIC_COLS = load_data()

# ── sidebar filters ───────────────────────────────────────────────────────────

st.sidebar.header("Filters")

# Gender
genders = sorted(df_raw["gender"].dropna().unique().tolist())
sel_gender = st.sidebar.multiselect("Gender", genders, default=genders)

# Placement status
placement_options = {"All": None, "Placed": 1, "Not Placed": 0}
sel_placement_label = st.sidebar.radio("Placement Status", list(placement_options.keys()))
sel_placement = placement_options[sel_placement_label]

# Extracurricular
extra_opts = sorted(df_raw["extracurricular_activities"].dropna().unique().tolist())
sel_extra = st.sidebar.multiselect("Extracurricular Activities", extra_opts, default=extra_opts)

# CGPA range
cgpa_min = float(df_raw["cgpa"].min())
cgpa_max = float(df_raw["cgpa"].max())
sel_cgpa = st.sidebar.slider(
    "CGPA Range", min_value=cgpa_min, max_value=cgpa_max,
    value=(cgpa_min, cgpa_max), step=0.1,
)

# Attendance range
att_min = float(df_raw["attendance_percentage"].min())
att_max = float(df_raw["attendance_percentage"].max())
sel_att = st.sidebar.slider(
    "Attendance % Range", min_value=att_min, max_value=att_max,
    value=(att_min, att_max), step=1.0,
)

# Backlogs
bl_max_val = int(df_raw["backlogs"].max())
sel_backlogs = st.sidebar.slider("Max Backlogs", 0, bl_max_val, bl_max_val)

# ── apply filters ─────────────────────────────────────────────────────────────

df = df_raw.copy()
if sel_gender:
    df = df[df["gender"].isin(sel_gender)]
if sel_placement is not None:
    df = df[df["placement_status"] == sel_placement]
if sel_extra:
    df = df[df["extracurricular_activities"].isin(sel_extra)]
df = df[df["cgpa"].between(*sel_cgpa)]
df = df[df["attendance_percentage"].between(*sel_att)]
df = df[df["backlogs"] <= sel_backlogs]

# ── title ─────────────────────────────────────────────────────────────────────

st.title("🎓 Student Academic Performance Dashboard")
st.markdown(
    f"Showing **{len(df):,}** of **{len(df_raw):,}** students after filters."
)

if df.empty:
    st.warning("No students match the selected filters. Adjust the sidebar.")
    st.stop()

# ── KPI row ───────────────────────────────────────────────────────────────────

st.markdown("---")
k1, k2, k3, k4, k5, k6 = st.columns(6)

placement_rate = df["placement_status"].mean() * 100 if "placement_status" in df else 0

k1.metric("Total Students",      f"{len(df):,}")
k2.metric("Placement Rate",      f"{placement_rate:.1f}%")
k3.metric("Avg CGPA",            f"{df['cgpa'].mean():.2f}")
k4.metric("Avg Technical Score", f"{df['technical_skill_score'].mean():.1f}")
k5.metric("Avg Attendance %",    f"{df['attendance_percentage'].mean():.1f}%")
k6.metric("Avg Backlogs",        f"{df['backlogs'].mean():.2f}")

st.markdown("---")

# ── tabs ──────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Score Distributions",
    "🔥 Correlation Matrix",
    "📈 Interactive Analysis",
    "📋 Raw Data",
])

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — Score Distributions
# ═════════════════════════════════════════════════════════════════════════════

with tab1:
    st.subheader("Score Distributions")
    st.markdown(
        "Histograms with KDE curves for the four key continuous scores. "
        "Dashed lines mark the filtered mean."
    )

    dist_cols = [
        ("cgpa",                  "#4C72B0", "CGPA"),
        ("entrance_exam_score",   "#DD8452", "Entrance Exam Score"),
        ("technical_skill_score", "#55A868", "Technical Skill Score"),
        ("soft_skill_score",      "#C44E52", "Soft-Skill Score"),
    ]

    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    for ax, (col, color, label) in zip(axes, dist_cols):
        data = df[col].dropna()
        sns.histplot(data, kde=True, ax=ax, color=color, bins=25, edgecolor="white")
        mean_val = data.mean()
        ax.axvline(mean_val, color="black", linestyle="--", linewidth=1.3,
                   label=f"Mean = {mean_val:.2f}")
        ax.set_title(label, fontsize=13, pad=8)
        ax.set_xlabel("Value", fontsize=10)
        ax.set_ylabel("Count", fontsize=10)
        ax.legend(fontsize=9)
    fig.suptitle("Score Distributions — Filtered Students", fontsize=15, y=1.02)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # Show static pre-generated PNG if it exists as a comparison
    if os.path.exists("score_distribution.png"):
        with st.expander("Show pre-generated chart (full dataset)"):
            st.image("score_distribution.png", use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — Correlation Matrix
# ═════════════════════════════════════════════════════════════════════════════

with tab2:
    st.subheader("Feature Correlation Matrix")
    st.markdown(
        "Pearson correlations across all numeric features for filtered students. "
        "Warm = positive, Cool = negative."
    )

    corr_df = df[[c for c in NUMERIC_COLS if c in df.columns]]
    corr_matrix = corr_df.corr()

    fig2, ax2 = plt.subplots(figsize=(14, 10))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(
        corr_matrix, mask=mask, annot=True, fmt=".2f",
        cmap="coolwarm", center=0, linewidths=0.5,
        annot_kws={"size": 8}, ax=ax2,
    )
    ax2.set_title("Correlation Matrix — Filtered Students", fontsize=14, pad=12)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.yticks(fontsize=9)
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

    if os.path.exists("correlation_matrix.png"):
        with st.expander("Show pre-generated chart (full dataset)"):
            st.image("correlation_matrix.png", use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 — Interactive Analysis
# ═════════════════════════════════════════════════════════════════════════════

with tab3:
    st.subheader("Interactive Analysis")

    col_left, col_right = st.columns(2)

    # ── placement breakdown ──
    with col_left:
        st.markdown("**Placement Rate by Gender**")
        if "placement_status" in df.columns and "gender" in df.columns:
            gender_place = (
                df.groupby("gender")["placement_status"]
                .agg(["mean", "count"])
                .reset_index()
                .rename(columns={"mean": "placement_rate", "count": "n"})
            )
            gender_place["placement_rate"] = (gender_place["placement_rate"] * 100).round(1)

            fig3, ax3 = plt.subplots(figsize=(5, 4))
            bars = ax3.bar(
                gender_place["gender"], gender_place["placement_rate"],
                color=["#4C72B0", "#DD8452", "#55A868"][:len(gender_place)],
                edgecolor="white", width=0.5,
            )
            for bar, rate in zip(bars, gender_place["placement_rate"]):
                ax3.text(bar.get_x() + bar.get_width() / 2,
                         bar.get_height() + 0.5,
                         f"{rate}%", ha="center", va="bottom", fontsize=10)
            ax3.set_ylabel("Placement Rate (%)")
            ax3.set_ylim(0, gender_place["placement_rate"].max() * 1.25 + 1)
            ax3.set_title("Placement Rate by Gender")
            plt.tight_layout()
            st.pyplot(fig3)
            plt.close()

    # ── CGPA vs Technical Score scatter ──
    with col_right:
        st.markdown("**CGPA vs Technical Skill Score**")
        fig4, ax4 = plt.subplots(figsize=(5, 4))
        colors_map = {"Male": "#4C72B0", "Female": "#DD8452"}
        for gender, grp in df.groupby("gender"):
            ax4.scatter(
                grp["cgpa"], grp["technical_skill_score"],
                alpha=0.35, s=18,
                color=colors_map.get(gender, "#888888"),
                label=gender,
            )
        ax4.set_xlabel("CGPA")
        ax4.set_ylabel("Technical Skill Score")
        ax4.set_title("CGPA vs Technical Skill Score")
        ax4.legend(fontsize=9)
        plt.tight_layout()
        st.pyplot(fig4)
        plt.close()

    st.markdown("---")
    col_b1, col_b2 = st.columns(2)

    # ── Attendance vs CGPA ──
    with col_b1:
        st.markdown("**Attendance % vs CGPA**")
        fig5, ax5 = plt.subplots(figsize=(5, 4))
        ax5.scatter(
            df["attendance_percentage"], df["cgpa"],
            alpha=0.3, s=15, color="#55A868",
        )
        # trend line
        z = np.polyfit(
            df["attendance_percentage"].dropna(),
            df.loc[df["attendance_percentage"].notna(), "cgpa"],
            1,
        )
        p = np.poly1d(z)
        x_line = np.linspace(df["attendance_percentage"].min(),
                              df["attendance_percentage"].max(), 200)
        ax5.plot(x_line, p(x_line), "r--", linewidth=1.5, label="Trend")
        ax5.set_xlabel("Attendance (%)")
        ax5.set_ylabel("CGPA")
        ax5.set_title("Attendance % vs CGPA")
        ax5.legend(fontsize=9)
        plt.tight_layout()
        st.pyplot(fig5)
        plt.close()

    # ── Backlogs distribution ──
    with col_b2:
        st.markdown("**Backlogs Distribution**")
        fig6, ax6 = plt.subplots(figsize=(5, 4))
        backlog_counts = df["backlogs"].value_counts().sort_index()
        ax6.bar(
            backlog_counts.index.astype(str),
            backlog_counts.values,
            color="#7c5cd8", edgecolor="white",
        )
        ax6.set_xlabel("Number of Backlogs")
        ax6.set_ylabel("Student Count")
        ax6.set_title("Backlog Distribution")
        plt.tight_layout()
        st.pyplot(fig6)
        plt.close()

    st.markdown("---")

    # ── Internships vs Placement ──
    st.markdown("**Internship Count vs Placement Rate**")
    if "placement_status" in df.columns:
        intern_place = (
            df.groupby("internship_count")["placement_status"]
            .agg(["mean", "count"])
            .reset_index()
            .rename(columns={"mean": "placement_rate", "count": "n"})
        )
        intern_place["placement_rate"] = (intern_place["placement_rate"] * 100).round(1)

        fig7, ax7 = plt.subplots(figsize=(10, 4))
        ax7.bar(
            intern_place["internship_count"].astype(str),
            intern_place["placement_rate"],
            color="#3b82d4", edgecolor="white",
        )
        for _, row in intern_place.iterrows():
            ax7.text(
                str(int(row["internship_count"])),
                row["placement_rate"] + 0.4,
                f"{row['placement_rate']}%\n(n={int(row['n'])})",
                ha="center", va="bottom", fontsize=8,
            )
        ax7.set_xlabel("Number of Internships")
        ax7.set_ylabel("Placement Rate (%)")
        ax7.set_title("Placement Rate by Internship Count")
        ax7.set_ylim(0, intern_place["placement_rate"].max() * 1.3 + 1)
        plt.tight_layout()
        st.pyplot(fig7)
        plt.close()

# ═════════════════════════════════════════════════════════════════════════════
# TAB 4 — Raw Data
# ═════════════════════════════════════════════════════════════════════════════

with tab4:
    st.subheader("Filtered Dataset")

    search_col = st.selectbox("Sort by", NUMERIC_COLS, index=NUMERIC_COLS.index("cgpa"))
    ascending = st.radio("Order", ["Descending", "Ascending"], horizontal=True) == "Ascending"

    display_df = df.sort_values(search_col, ascending=ascending).reset_index(drop=True)
    st.dataframe(display_df, use_container_width=True, height=450)

    csv_bytes = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download filtered data as CSV",
        data=csv_bytes,
        file_name="filtered_students.csv",
        mime="text/csv",
    )

# ── footer ────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#57606a;font-size:12px;'>"
    "Student Academic Performance Dashboard &nbsp;|&nbsp; "
    "Data: Kaggle Student Dataset"
    "</div>",
    unsafe_allow_html=True,
)
