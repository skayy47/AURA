"""AURA — Page 3: Data Explorer."""
from __future__ import annotations

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
    load_css,
    page_header,
    require_dataset,
    show_pipeline_progress,
    show_sidebar_status,
)

logger = get_logger(__name__)

st.set_page_config(page_title="AURA — Explore", page_icon="🔍", layout="wide")
load_css()
show_pipeline_progress(3)

with st.sidebar:
    show_sidebar_status()

require_dataset(cleaned=True)

page_header("🔍", "Data Explorer", "Visualise patterns, distributions, and correlations")

sess = get_session()
df = sess.cleaned_df
info = get_basic_info(df)

tab_overview, tab_charts, tab_columns, tab_numeric, tab_missing = st.tabs(
    ["📋 Overview", "📊 Charts", "📚 Columns", "📐 Numeric", "❓ Missing"]
)

CHART_THEME = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(10,16,34,0.6)",
    font=dict(color="#94A3B8", size=12),
    colorway=["#6C3FE5", "#3B82F6", "#22D3EE", "#10B981", "#F59E0B"],
    margin=dict(l=40, r=20, t=40, b=40),
)

# ── Overview ──────────────────────────────────────────────────────────────────
with tab_overview:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Rows",        f"{info['n_rows']:,}")
    m2.metric("Columns",     info["n_cols"])
    m3.metric("Memory",      f"{info['memory_mb']} MB")
    m4.metric("Dtype types", len(info["dtype_counts"]))

    st.markdown(
        '<p style="font-size:0.82rem;font-weight:700;color:#94A3B8;'
        'text-transform:uppercase;letter-spacing:0.08em;margin:1.4rem 0 0.5rem;">'
        "Dtype breakdown</p>",
        unsafe_allow_html=True,
    )
    for dtype, count in info["dtype_counts"].items():
        st.markdown(
            f'<div style="font-family:monospace;font-size:0.83rem;'
            f'color:#94A3B8;padding:2px 0;">'
            f'<span style="color:#8B5CF6;">{dtype}</span>'
            f' &nbsp;—&nbsp; {count} column(s)</div>',
            unsafe_allow_html=True,
        )

# ── Charts ────────────────────────────────────────────────────────────────────
with tab_charts:
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols     = df.select_dtypes(exclude="number").columns.tolist()

    if numeric_cols:
        st.markdown(
            '<p style="font-size:0.82rem;font-weight:700;color:#94A3B8;'
            'text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem;">'
            "Numeric column</p>",
            unsafe_allow_html=True,
        )
        sel_num = st.selectbox("Select numeric column", numeric_cols, key="sel_num")
        fig_h = plot_histogram(df, sel_num)
        fig_b = plot_boxplot(df, sel_num)
        fig_h.update_layout(**CHART_THEME)
        fig_b.update_layout(**CHART_THEME)
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(fig_h, use_container_width=True)
        with c2:
            st.plotly_chart(fig_b, use_container_width=True)

        if len(numeric_cols) >= 2:
            st.markdown(
                '<p style="font-size:0.82rem;font-weight:700;color:#94A3B8;'
                'text-transform:uppercase;letter-spacing:0.08em;margin:1rem 0 0.5rem;">'
                "Correlation heatmap</p>",
                unsafe_allow_html=True,
            )
            fig_c = plot_correlation_heatmap(df)
            fig_c.update_layout(**CHART_THEME)
            st.plotly_chart(fig_c, use_container_width=True)
    else:
        st.info("No numeric columns found.")

    if cat_cols:
        st.markdown(
            '<p style="font-size:0.82rem;font-weight:700;color:#94A3B8;'
            'text-transform:uppercase;letter-spacing:0.08em;margin:1rem 0 0.5rem;">'
            "Categorical column — value counts</p>",
            unsafe_allow_html=True,
        )
        sel_cat = st.selectbox("Select categorical column", cat_cols, key="sel_cat")
        fig_v = plot_value_counts(df, sel_cat)
        fig_v.update_layout(**CHART_THEME)
        st.plotly_chart(fig_v, use_container_width=True)

# ── Columns ───────────────────────────────────────────────────────────────────
with tab_columns:
    col_df = get_column_overview(df)
    if col_df.empty:
        st.info("No columns to display.")
    else:
        st.dataframe(col_df, use_container_width=True)

# ── Numeric summary ───────────────────────────────────────────────────────────
with tab_numeric:
    num_df = get_numeric_summary(df)
    if num_df.empty:
        st.info("No numeric columns detected.")
    else:
        st.dataframe(num_df, use_container_width=True)

# ── Missing ───────────────────────────────────────────────────────────────────
with tab_missing:
    missing_counts = df.isnull().sum()
    total_missing  = int(missing_counts.sum())
    st.metric("Total missing cells", total_missing)

    if total_missing > 0:
        fig_m = plot_missing_heatmap(df)
        fig_m.update_layout(**CHART_THEME)
        st.plotly_chart(fig_m, use_container_width=True)
        missing_pct = (missing_counts / len(df) * 100).reset_index()
        missing_pct.columns = ["column", "missing_%"]
        missing_pct = missing_pct[missing_pct["missing_%"] > 0].sort_values(
            "missing_%", ascending=False
        )
        st.dataframe(missing_pct, use_container_width=True)
    else:
        st.success("No missing values — dataset is complete.")

# ── CTA ───────────────────────────────────────────────────────────────────────
st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)
st.page_link("pages/4_🤖_AI_Chat.py", label="Next: AI Insights →", use_container_width=True)
