"""Data exploration engine — profiling and Plotly chart helpers."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pandas.api.types import is_numeric_dtype

CHART_THEME: dict = {
    "template": "plotly_dark",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(15,23,42,0.8)",
    "font": {"family": "Inter, system-ui, sans-serif", "color": "#94A3B8"},
    "margin": {"t": 40, "b": 40, "l": 40, "r": 20},
}


# ---------------------------------------------------------------------------
# Profiling helpers
# ---------------------------------------------------------------------------


def get_basic_info(df: pd.DataFrame) -> dict:
    """Return basic metadata about *df*."""
    mem_mb = round(df.memory_usage(deep=True).sum() / 1024 / 1024, 3)
    dtype_counts: dict[str, int] = {}
    for dtype in df.dtypes:
        key = str(dtype)
        dtype_counts[key] = dtype_counts.get(key, 0) + 1
    return {
        "n_rows": int(df.shape[0]),
        "n_cols": int(df.shape[1]),
        "columns": list(df.columns),
        "memory_mb": mem_mb,
        "dtype_counts": dtype_counts,
    }


def get_column_overview(df: pd.DataFrame) -> pd.DataFrame:
    """Return per-column statistics: dtype, missing %, unique count, numeric stats."""
    overview = []
    for col in df.columns:
        series = df[col]
        missing = int(series.isna().sum())
        missing_pct = float(missing / len(series) * 100) if len(series) else 0.0
        info: dict = {
            "column": col,
            "dtype": str(series.dtype),
            "missing": missing,
            "missing_%": round(missing_pct, 2),
            "unique": int(series.nunique(dropna=True)),
        }
        if is_numeric_dtype(series):
            info["min"] = float(series.min())
            info["max"] = float(series.max())
            info["mean"] = round(float(series.mean()), 4)
        overview.append(info)
    return pd.DataFrame(overview)


def get_numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return describe().T for numeric columns plus missing counts."""
    num_df = df.select_dtypes(include="number")
    if num_df.empty:
        return pd.DataFrame()
    summary = num_df.describe().T
    summary["missing"] = num_df.isna().sum()
    return summary.reset_index().rename(columns={"index": "column"})


# ---------------------------------------------------------------------------
# Plotly chart helpers
# ---------------------------------------------------------------------------


def _themed(fig: go.Figure) -> go.Figure:
    """Apply the AURA dark theme to *fig* and return it."""
    fig.update_layout(**CHART_THEME)
    return fig


def plot_histogram(df: pd.DataFrame, column: str, bins: int = 30) -> go.Figure:
    """Return a histogram for *column*."""
    fig = px.histogram(df, x=column, nbins=bins, title=f"Distribution — {column}")
    return _themed(fig)


def plot_boxplot(df: pd.DataFrame, column: str) -> go.Figure:
    """Return a box plot for *column*."""
    fig = px.box(df, y=column, title=f"Box plot — {column}")
    return _themed(fig)


def plot_correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    """Return a correlation heatmap for all numeric columns."""
    num_df = df.select_dtypes(include="number")
    corr = num_df.corr()
    fig = px.imshow(
        corr,
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="Correlation matrix",
    )
    return _themed(fig)


def plot_missing_heatmap(df: pd.DataFrame) -> go.Figure:
    """Return a heatmap showing the missing-value pattern."""
    missing = df.isnull().astype(int)
    fig = px.imshow(
        missing,
        color_continuous_scale=["#0F172A", "#7C3AED"],
        title="Missing value pattern (purple = missing)",
        aspect="auto",
    )
    return _themed(fig)


def plot_value_counts(
    df: pd.DataFrame, column: str, top_n: int = 20
) -> go.Figure:
    """Return a horizontal bar chart of the top N value counts for *column*."""
    counts = df[column].value_counts().head(top_n).reset_index()
    counts.columns = [column, "count"]
    fig = px.bar(
        counts,
        x="count",
        y=column,
        orientation="h",
        title=f"Top {top_n} values — {column}",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return _themed(fig)


def plot_timeseries(
    df: pd.DataFrame, date_col: str, value_col: str
) -> go.Figure:
    """Return a line chart of *value_col* over *date_col*."""
    fig = px.line(
        df.sort_values(date_col),
        x=date_col,
        y=value_col,
        title=f"{value_col} over time",
    )
    return _themed(fig)
