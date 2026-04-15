"""AURA — Page 3: Data Explorer."""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from engines.exploration import (
    get_basic_info,
    get_column_overview,
    get_numeric_summary,
    plot_boxplot,
    plot_correlation_heatmap,
    plot_histogram,
    plot_missing_heatmap,
    plot_value_counts,
)
from state.session import get_session
from utils.helpers import (
    get_logger,
    require_dataset,
    show_page_header,
    show_pipeline_progress,
    show_sidebar_status,
)

logger = get_logger(__name__)

st.set_page_config(page_title="AURA · Explore", page_icon="🔍", layout="wide")


def inject_css() -> None:
    css_path = Path("assets/css/aura.css")
    if css_path.exists():
        st.markdown(
            f"<style>{css_path.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )


inject_css()

session = get_session()
show_sidebar_status()
show_pipeline_progress(3)
show_page_header("🔍", "Data Explorer", "Visualise and understand your cleaned data")

require_dataset(cleaned=True)

df = session.cleaned_df
info = get_basic_info(df)

tab_overview, tab_charts, tab_columns, tab_numeric, tab_missing = st.tabs(
    ["📋 Overview", "📊 Charts", "📚 Columns", "📐 Numeric", "❓ Missing"]
)

# -----------------------------------------------------------------
# Overview
# -----------------------------------------------------------------
with tab_overview:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Rows", f"{info['n_rows']:,}")
    m2.metric("Columns", info["n_cols"])
    m3.metric("Memory", f"{info['memory_mb']} MB")
    m4.metric("Dtype types", len(info["dtype_counts"]))

    st.markdown("#### Dtype breakdown")
    for dtype, count in info["dtype_counts"].items():
        st.write(f"- **{dtype}**: {count} column(s)")

# -----------------------------------------------------------------
# Charts
# -----------------------------------------------------------------
with tab_charts:
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(exclude="number").columns.tolist()

    if numeric_cols:
        st.markdown("#### Numeric column")
        sel_num = st.selectbox("Select numeric column", numeric_cols, key="sel_num")
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(plot_histogram(df, sel_num), use_container_width=True)
        with c2:
            st.plotly_chart(plot_boxplot(df, sel_num), use_container_width=True)

        if len(numeric_cols) >= 2:
            st.markdown("#### Correlation heatmap")
            st.plotly_chart(plot_correlation_heatmap(df), use_container_width=True)
    else:
        st.info("No numeric columns found.")

    if cat_cols:
        st.markdown("#### Categorical column — value counts")
        sel_cat = st.selectbox("Select categorical column", cat_cols, key="sel_cat")
        st.plotly_chart(plot_value_counts(df, sel_cat), use_container_width=True)

# -----------------------------------------------------------------
# Columns
# -----------------------------------------------------------------
with tab_columns:
    col_df = get_column_overview(df)
    if col_df.empty:
        st.info("No columns to display.")
    else:
        st.dataframe(col_df, use_container_width=True)

# -----------------------------------------------------------------
# Numeric summary
# -----------------------------------------------------------------
with tab_numeric:
    num_df = get_numeric_summary(df)
    if num_df.empty:
        st.info("No numeric columns detected.")
    else:
        st.dataframe(num_df, use_container_width=True)

# -----------------------------------------------------------------
# Missing
# -----------------------------------------------------------------
with tab_missing:
    missing_counts = df.isnull().sum()
    total_missing = int(missing_counts.sum())
    st.metric("Total missing cells", total_missing)

    if total_missing > 0:
        st.plotly_chart(plot_missing_heatmap(df), use_container_width=True)
        missing_pct = (missing_counts / len(df) * 100).reset_index()
        missing_pct.columns = ["column", "missing_%"]
        missing_pct = missing_pct[missing_pct["missing_%"] > 0].sort_values(
            "missing_%", ascending=False
        )
        st.dataframe(missing_pct, use_container_width=True)
    else:
        st.success("No missing values — dataset is complete.")

# -----------------------------------------------------------------
# Next step
# -----------------------------------------------------------------
st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)
st.page_link(
    "pages/4_🤖_AI_Chat.py",
    label="Next: Ask AI about your data 🤖 →",
    use_container_width=True,
)
