"""Data exploration engine — profiling, chart recommendations, and Plotly helpers.

Public entry points (new):
    profile_dataframe(df) -> dict   # rich per-column profiles + correlation
    recommend_charts(profile) -> list[dict]   # ranked chart recommendations

Legacy (kept for Streamlit compat):
    get_basic_info / get_column_overview / get_numeric_summary / get_profile
    plot_histogram, plot_boxplot, plot_correlation_heatmap, plot_missing_heatmap,
    plot_value_counts, plot_timeseries
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
)

logger = logging.getLogger(__name__)

CHART_THEME: dict = {
    "template": "plotly_dark",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(15,23,42,0.8)",
    "font": {"family": "Arial, sans-serif", "color": "#E2E8F0"},
    "margin": {"t": 40, "b": 40, "l": 40, "r": 20},
}


# ---------------------------------------------------------------------------
# V3.5 — Rich profiling + chart recommendations
# ---------------------------------------------------------------------------

_HIST_BINS = 20
_TOP_VALUES = 10


def _classify_kind(series: pd.Series) -> str:
    if is_bool_dtype(series):
        return "boolean"
    if is_datetime64_any_dtype(series):
        return "datetime"
    if is_numeric_dtype(series):
        return "numeric"
    # Object-like: id vs categorical vs text
    n = max(len(series), 1)
    nunique = series.nunique(dropna=True)
    if nunique == n and n > 0:
        return "id"
    if nunique <= 50 or nunique / n < 0.1:
        return "categorical"
    return "text"


def _top_values(series: pd.Series, k: int = _TOP_VALUES) -> list[dict]:
    vc = series.dropna().value_counts().head(k)
    return [{"value": str(idx), "count": int(cnt)} for idx, cnt in vc.items()]


def _numeric_histogram(series: pd.Series, bins: int = _HIST_BINS) -> list[dict]:
    arr = series.dropna().to_numpy()
    if arr.size == 0:
        return []
    counts, edges = np.histogram(arr, bins=bins)
    out = []
    for i, c in enumerate(counts):
        lo = edges[i]
        hi = edges[i + 1]
        out.append(
            {
                "bin": f"{lo:.2f}–{hi:.2f}",
                "lo": float(lo),
                "hi": float(hi),
                "count": int(c),
            }
        )
    return out


def _profile_column(series: pd.Series) -> dict[str, Any]:
    n = len(series)
    n_missing = int(series.isna().sum())
    missing_pct = round((n_missing / n * 100), 2) if n else 0.0
    n_unique = int(series.nunique(dropna=True))
    kind = _classify_kind(series)

    profile: dict[str, Any] = {
        "name": str(series.name),
        "dtype": str(series.dtype),
        "kind": kind,
        "n_missing": n_missing,
        "missing_pct": missing_pct,
        "n_unique": n_unique,
        "top_values": _top_values(series),
    }

    if kind == "numeric" or (kind == "boolean" and is_numeric_dtype(series)):
        non_null = series.dropna()
        if len(non_null) > 0:
            try:
                profile["mean"] = float(non_null.mean())
                profile["median"] = float(non_null.median())
                profile["std"] = float(non_null.std()) if len(non_null) > 1 else 0.0
                profile["min"] = float(non_null.min())
                profile["max"] = float(non_null.max())
                profile["p25"] = float(non_null.quantile(0.25))
                profile["p75"] = float(non_null.quantile(0.75))
                profile["skewness"] = (
                    float(non_null.skew()) if len(non_null) > 2 else 0.0
                )
                profile["kurtosis"] = (
                    float(non_null.kurtosis()) if len(non_null) > 3 else 0.0
                )
                profile["histogram"] = _numeric_histogram(non_null)
            except Exception as exc:
                logger.warning("Numeric stats failed for %s: %s", series.name, exc)

    elif kind == "datetime":
        non_null = series.dropna()
        if len(non_null) > 0:
            try:
                dmin = pd.Timestamp(non_null.min())
                dmax = pd.Timestamp(non_null.max())
                profile["date_min"] = dmin.isoformat()
                profile["date_max"] = dmax.isoformat()
                profile["date_range_days"] = int((dmax - dmin).days)
            except Exception as exc:
                logger.warning("Datetime stats failed for %s: %s", series.name, exc)

    return profile


def profile_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    """Produce a JSON-serializable rich profile in a single pass.

    Returns per-column profiles, correlation matrix + top pairs,
    and convenience lists (numeric/categorical/datetime cols).
    """
    profiles: list[dict[str, Any]] = []
    for col in df.columns:
        try:
            profiles.append(_profile_column(df[col]))
        except Exception as exc:
            logger.warning("Could not profile column %s: %s", col, exc)
            profiles.append(
                {
                    "name": str(col),
                    "dtype": str(df[col].dtype),
                    "kind": "unknown",
                    "n_missing": int(df[col].isna().sum()),
                    "missing_pct": 0.0,
                    "n_unique": 0,
                    "top_values": [],
                    "error": str(exc),
                }
            )

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    datetime_cols = df.select_dtypes(include="datetime").columns.tolist()

    correlation: dict[str, Any] | None = None
    if len(numeric_cols) >= 2:
        try:
            corr = df[numeric_cols].corr().round(4)
            pairs: list[dict[str, Any]] = []
            cols = corr.columns.tolist()
            for i in range(len(cols)):
                for j in range(i + 1, len(cols)):
                    r = corr.iloc[i, j]
                    if pd.isna(r):
                        continue
                    pairs.append(
                        {
                            "col_a": str(cols[i]),
                            "col_b": str(cols[j]),
                            "r": float(round(r, 4)),
                        }
                    )
            pairs.sort(key=lambda x: abs(x["r"]), reverse=True)
            # corr.to_dict(orient="split") → {"index":..., "columns":..., "data":[[...]]}
            correlation = {
                "columns": [str(c) for c in cols],
                "matrix": corr.to_dict(orient="split"),
                "top_pairs": pairs[:10],
            }
        except Exception as exc:
            logger.warning("Correlation failed: %s", exc)

    missing_by_col = [
        {
            "column": str(col),
            "missing": int(df[col].isnull().sum()),
            "pct": round(float(df[col].isnull().mean() * 100), 2),
        }
        for col in df.columns
    ]

    return {
        "n_rows": int(df.shape[0]),
        "n_cols": int(df.shape[1]),
        "memory_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 3),
        "missing_total": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "columns": profiles,
        "correlation": correlation,
        "numeric_cols": [str(c) for c in numeric_cols],
        "categorical_cols": [str(c) for c in categorical_cols],
        "datetime_cols": [str(c) for c in datetime_cols],
        "missing_by_col": missing_by_col,
    }


_MAX_POINTS = 500


def _sample_points(df_sub: pd.DataFrame, limit: int = _MAX_POINTS) -> pd.DataFrame:
    if len(df_sub) <= limit:
        return df_sub
    return df_sub.sample(n=limit, random_state=42).sort_index()


def recommend_charts(
    df: pd.DataFrame,
    profile: dict[str, Any],
) -> list[dict[str, Any]]:
    """Rank charts by usefulness and embed the data needed to render them."""
    numeric = profile.get("numeric_cols", [])
    categorical = profile.get("categorical_cols", [])
    datetime_cols = profile.get("datetime_cols", [])
    correlation = profile.get("correlation") or {}
    top_pairs = correlation.get("top_pairs", [])

    recs: list[dict[str, Any]] = []

    # Time series — datetime vs top numerics
    if datetime_cols and numeric:
        x_col = datetime_cols[0]
        y_cols = numeric[:3]
        sub = df[[x_col, *y_cols]].dropna(subset=[x_col]).sort_values(x_col)
        sub = _sample_points(sub)
        points = []
        for _, row in sub.iterrows():
            entry: dict[str, Any] = {"x": pd.Timestamp(row[x_col]).isoformat()}
            for yc in y_cols:
                v = row[yc]
                entry[yc] = float(v) if pd.notna(v) else None
            points.append(entry)
        recs.append(
            {
                "type": "timeseries",
                "x": x_col,
                "y": y_cols,
                "points": points,
                "rationale": f"Temporal trend: {x_col} vs {', '.join(y_cols)}",
                "priority": 10,
            }
        )

    # Strong-correlation scatter plots
    for pair in top_pairs[:3]:
        if abs(pair["r"]) > 0.5:
            sub = df[[pair["col_a"], pair["col_b"]]].dropna()
            sub = _sample_points(sub)
            points = [
                {"x": float(a), "y": float(b)} for a, b in sub.itertuples(index=False)
            ]
            recs.append(
                {
                    "type": "scatter",
                    "x": pair["col_a"],
                    "y": pair["col_b"],
                    "r": pair["r"],
                    "points": points,
                    "rationale": f"Strong correlation r={pair['r']:.2f}",
                    "priority": 9,
                }
            )

    # Primary numeric histogram
    if numeric:
        recs.append(
            {
                "type": "histogram",
                "column": numeric[0],
                "rationale": "Primary numeric distribution",
                "priority": 8,
            }
        )

    # Categorical breakdown — top-20 mean of y by x
    if categorical and numeric:
        x_col = categorical[0]
        y_col = numeric[0]
        try:
            agg = df.groupby(x_col, observed=True)[y_col].mean().dropna()
            agg = agg.sort_values(ascending=False).head(20)
            bars = [
                {"label": str(idx), "value": float(round(val, 4))}
                for idx, val in agg.items()
            ]
        except Exception:
            bars = []
        recs.append(
            {
                "type": "bar_grouped",
                "x": x_col,
                "y": y_col,
                "bars": bars,
                "rationale": f"Mean {y_col} by {x_col}",
                "priority": 7,
            }
        )

    # Correlation heatmap if 4+ numeric columns
    if len(numeric) >= 4:
        recs.append(
            {
                "type": "heatmap_corr",
                "columns": numeric,
                "rationale": f"Correlation matrix: {len(numeric)} numeric columns",
                "priority": 6,
            }
        )

    # Secondary numeric histogram
    if len(numeric) >= 2:
        recs.append(
            {
                "type": "histogram",
                "column": numeric[1],
                "rationale": "Secondary numeric distribution",
                "priority": 5,
            }
        )

    return sorted(recs, key=lambda x: x["priority"], reverse=True)


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


def get_profile(df: pd.DataFrame) -> dict:
    """Return a complete data profile combining basic info, column overview, numeric summary, and missing-value stats."""
    basic = get_basic_info(df)
    cols_df = get_column_overview(df)
    numeric_df = get_numeric_summary(df)
    missing_counts = int(df.isnull().sum().sum())
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(exclude="number").columns.tolist()
    return {
        "basic_info": basic,
        "column_overview": cols_df.to_dict("records"),
        "numeric_summary": numeric_df.to_dict("records"),
        "missing_total": missing_counts,
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
    }


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


def plot_value_counts(df: pd.DataFrame, column: str, top_n: int = 20) -> go.Figure:
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


def plot_timeseries(df: pd.DataFrame, date_col: str, value_col: str) -> go.Figure:
    """Return a line chart of *value_col* over *date_col*."""
    fig = px.line(
        df.sort_values(date_col),
        x=date_col,
        y=value_col,
        title=f"{value_col} over time",
    )
    return _themed(fig)
