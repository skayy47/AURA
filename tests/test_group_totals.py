"""Grounding context carries exact per-group totals.

Regression for the compound-aggregation defect: asked "total revenue by
segment", the model only had overall mean/count and answered with
mean × row-count approximations presented as exact totals.
"""

from __future__ import annotations

import pandas as pd

from engines.ai_insights import (
    _build_system_prompt,
    _group_totals_section,
    _measure_rank,
)


def _sales() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": [f"o{i}" for i in range(8)],
            "segment": ["A", "A", "B", "B", "B", "C", "C", "C"],
            "unit_price_usd": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0],
            "revenue_usd": [100.5, 200.0, 50.25, 50.25, 50.0, 1.0, 2.0, 3.0],
        }
    )


def test_exact_group_sums_are_in_the_prompt():
    df = _sales()
    section = _group_totals_section(df, {"id_cols": ["order_id"]})
    assert "revenue_usd by segment" in section
    assert '"A": sum=300.50' in section
    assert '"B": sum=150.50' in section
    assert '"C": sum=6.00' in section
    assert "sum=" in _build_system_prompt(df, {"id_cols": ["order_id"]})


def test_identifiers_are_never_used_as_dimensions():
    section = _group_totals_section(_sales(), {"id_cols": ["order_id"]})
    assert "by order_id" not in section


def test_additive_measures_rank_before_rates_and_prices():
    assert (
        _measure_rank("revenue_usd")
        < _measure_rank("quantity")
        < _measure_rank("unit_price_usd")
    )
    assert _measure_rank("profit_usd") < _measure_rank("discount_pct")


def test_no_categorical_columns_means_no_section():
    df = pd.DataFrame({"x": [1, 2, 3], "y": [4.0, 5.0, 6.0]})
    assert _group_totals_section(df) == ""
