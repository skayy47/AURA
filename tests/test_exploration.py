"""Tests for engines/exploration.py."""
from __future__ import annotations

import pandas as pd

from engines.exploration import (
    get_basic_info,
    get_column_overview,
    get_numeric_summary,
    plot_correlation_heatmap,
    plot_histogram,
)


def _numeric_df() -> pd.DataFrame:
    return pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [10.0, 20.0, 15.0, 30.0, 25.0]})


def _string_df() -> pd.DataFrame:
    return pd.DataFrame({"name": ["Alice", "Bob", "Charlie"]})


def test_get_basic_info_shape() -> None:
    """Returns correct n_rows and n_cols."""
    df = _numeric_df()
    info = get_basic_info(df)
    assert info["n_rows"] == 5
    assert info["n_cols"] == 2


def test_get_column_overview_columns() -> None:
    """Result DataFrame has the required columns."""
    df = _numeric_df()
    overview = get_column_overview(df)
    required = {"column", "dtype", "missing_%"}
    assert required.issubset(set(overview.columns))


def test_get_numeric_summary_empty() -> None:
    """Returns an empty DataFrame for a string-only dataset."""
    df = _string_df()
    summary = get_numeric_summary(df)
    assert summary.empty


def test_plot_histogram_returns_figure() -> None:
    """plot_histogram returns a Plotly Figure."""
    import plotly.graph_objects as go
    df = _numeric_df()
    fig = plot_histogram(df, "x")
    assert isinstance(fig, go.Figure)


def test_plot_correlation_heatmap() -> None:
    """plot_correlation_heatmap returns a Plotly Figure for numeric data."""
    import plotly.graph_objects as go
    df = _numeric_df()
    fig = plot_correlation_heatmap(df)
    assert isinstance(fig, go.Figure)
