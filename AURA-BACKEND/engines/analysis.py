"""Expert auto-analysis engine — turns a profiled DataFrame into ranked,
decision-useful insights, segment drivers, trends, and a compact stats payload
for an LLM executive summary.

Pure pandas/numpy — no LLM, no raw rows leave this module. Every section is
defensive and degrades independently.

Public entry point:
    analyze(df, profile) -> dict
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd
from pandas.api.types import is_numeric_dtype

from engines.semantics import infer_semantics

logger = logging.getLogger(__name__)

# Insight severity: 3 = critical, 2 = notable, 1 = minor
_TOP_INSIGHTS = 8


# ---------------------------------------------------------------------------
# Data quality
# ---------------------------------------------------------------------------


def _quality(df: pd.DataFrame, profile: dict) -> dict[str, Any]:
    n_rows = int(df.shape[0])
    n_cols = int(df.shape[1])
    cells = max(n_rows * n_cols, 1)

    missing_total = int(profile.get("missing_total", df.isnull().sum().sum()))
    missing_pct = round(missing_total / cells * 100, 2)
    dup_rows = int(profile.get("duplicate_rows", df.duplicated().sum()))
    dup_pct = round(dup_rows / max(n_rows, 1) * 100, 2)

    constant_cols = [str(c) for c in df.columns if df[c].nunique(dropna=False) <= 1]
    high_card = [
        str(c)
        for c in df.columns
        if df[c].nunique(dropna=True) > 0.9 * n_rows
        and n_rows > 20
        and not is_numeric_dtype(df[c])
    ]

    missing_hotspots = sorted(
        (
            {"column": str(c), "pct": round(float(df[c].isnull().mean() * 100), 1)}
            for c in df.columns
            if df[c].isnull().any()
        ),
        key=lambda x: x["pct"],
        reverse=True,
    )[:5]

    # Composite quality score (0-100): penalise missing, dupes, constant cols
    score = 100.0
    score -= min(missing_pct * 1.5, 40)
    score -= min(dup_pct * 1.0, 25)
    score -= min(len(constant_cols) * 4, 15)
    score = int(max(0, round(score)))

    return {
        "score": score,
        "missing_total": missing_total,
        "missing_pct": missing_pct,
        "duplicate_rows": dup_rows,
        "duplicate_pct": dup_pct,
        "constant_cols": constant_cols,
        "high_cardinality_cols": high_card,
        "missing_hotspots": missing_hotspots,
    }


# ---------------------------------------------------------------------------
# Outliers (IQR)
# ---------------------------------------------------------------------------


def _outliers(df: pd.DataFrame, measure_cols: list[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for col in measure_cols:
        try:
            s = df[col].dropna()
            if len(s) < 8:
                continue
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1
            if iqr <= 0:
                continue
            lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            n_out = int(((s < lo) | (s > hi)).sum())
            if n_out > 0:
                out.append(
                    {
                        "column": str(col),
                        "count": n_out,
                        "pct": round(n_out / len(s) * 100, 1),
                    }
                )
        except Exception as exc:
            logger.warning("Outlier calc failed for %s: %s", col, exc)
    return sorted(out, key=lambda x: x["pct"], reverse=True)[:5]


# ---------------------------------------------------------------------------
# Categorical dominance
# ---------------------------------------------------------------------------


def _dominance(df: pd.DataFrame, profile: dict) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    n = max(int(df.shape[0]), 1)
    for col in profile.get("categorical_cols", []):
        try:
            vc = df[col].dropna().value_counts()
            if vc.empty:
                continue
            top_label, top_count = str(vc.index[0]), int(vc.iloc[0])
            share = round(top_count / n * 100, 1)
            if share >= 60 and df[col].nunique() > 1:
                out.append(
                    {
                        "column": str(col),
                        "value": top_label,
                        "share": share,
                    }
                )
        except Exception as exc:
            logger.warning("Dominance calc failed for %s: %s", col, exc)
    return sorted(out, key=lambda x: x["share"], reverse=True)[:3]


# ---------------------------------------------------------------------------
# Segment driver — best categorical × primary numeric
# ---------------------------------------------------------------------------


def _segments(df: pd.DataFrame, sem: dict) -> dict[str, Any] | None:
    measures = sem.get("primary_measures") or []
    segmentable = sem.get("segmentable_cols") or []
    if not measures or not segmentable:
        return None

    y = measures[0]
    # Prefer a slice column with 2..12 groups; fall back to the best available.
    best_cat = next(
        (c for c in segmentable if 2 <= df[c].nunique(dropna=True) <= 12),
        segmentable[0],
    )

    try:
        grp = (
            df.groupby(best_cat, observed=True)[y]
            .mean()
            .dropna()
            .sort_values(ascending=False)
        )
        if grp.empty:
            return None
        bars = [{"label": str(i), "value": float(round(v, 3))} for i, v in grp.items()][
            :8
        ]
        top_label, top_val = str(grp.index[0]), float(grp.iloc[0])
        bot_label, bot_val = str(grp.index[-1]), float(grp.iloc[-1])
        spread = round((top_val - bot_val) / abs(bot_val) * 100, 1) if bot_val else None
        return {
            "dimension": str(best_cat),
            "measure": str(y),
            "bars": bars,
            "top": {"label": top_label, "value": round(top_val, 3)},
            "bottom": {"label": bot_label, "value": round(bot_val, 3)},
            "spread_pct": spread,
        }
    except Exception as exc:
        logger.warning("Segment calc failed: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Trend — datetime × primary numeric
# ---------------------------------------------------------------------------


def _trends(df: pd.DataFrame, sem: dict) -> dict[str, Any] | None:
    x = sem.get("primary_temporal")
    measures = sem.get("primary_measures") or []
    if not x or not measures:
        return None
    y = measures[0]
    try:
        sub = df[[x, y]].dropna().sort_values(x)
        if len(sub) < 6:
            return None
        sub = sub.set_index(x)
        span_days = (sub.index.max() - sub.index.min()).days
        rule = "D" if span_days <= 90 else ("W" if span_days <= 730 else "ME")
        series = sub[y].resample(rule).mean().dropna()
        if len(series) < 3:
            return None
        first, last = float(series.iloc[0]), float(series.iloc[-1])
        change = round((last - first) / abs(first) * 100, 1) if first else None
        direction = (
            "rising" if last > first else ("falling" if last < first else "flat")
        )
        points = [
            {"x": str(idx.date()), "value": float(round(v, 3))}
            for idx, v in series.items()
        ][:40]
        return {
            "date_col": str(x),
            "measure": str(y),
            "direction": direction,
            "change_pct": change,
            "points": points,
        }
    except Exception as exc:
        logger.warning("Trend calc failed: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Insight ranking
# ---------------------------------------------------------------------------


def _build_insights(
    quality: dict,
    outliers: list,
    correlations: list,
    dominance: list,
    segments: dict | None,
    trends: dict | None,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []

    if (
        trends
        and trends.get("change_pct") is not None
        and abs(trends["change_pct"]) >= 10
    ):
        sev = 3 if abs(trends["change_pct"]) >= 40 else 2
        items.append(
            {
                "kind": "trend",
                "severity": sev,
                "icon": "trend",
                "title": f"{trends['measure']} is {trends['direction']} over time",
                "detail": f"{trends['measure']} changed {trends['change_pct']:+.0f}% across the "
                f"{trends['date_col']} timeline.",
            }
        )

    for c in correlations[:3]:
        strength = abs(c["r"])
        sev = 3 if strength >= 0.7 else 2
        rel = "positively" if c["r"] >= 0 else "negatively"
        items.append(
            {
                "kind": "correlation",
                "severity": sev,
                "icon": "link",
                "title": f"{c['col_a']} and {c['col_b']} move together",
                "detail": f"{c['col_a']} is {rel} correlated with {c['col_b']} (r = {c['r']:+.2f}). "
                f"{'Strong' if strength >= 0.7 else 'Moderate'} relationship worth modeling.",
            }
        )

    if (
        segments
        and segments.get("spread_pct") is not None
        and abs(segments["spread_pct"]) >= 25
    ):
        items.append(
            {
                "kind": "segment",
                "severity": 2,
                "icon": "segment",
                "title": f"{segments['dimension']} drives {segments['measure']}",
                "detail": f"'{segments['top']['label']}' averages {segments['top']['value']:.2f} vs "
                f"'{segments['bottom']['label']}' at {segments['bottom']['value']:.2f} — a "
                f"{abs(segments['spread_pct']):.0f}% gap across {segments['dimension']}.",
            }
        )

    if quality["missing_hotspots"]:
        h = quality["missing_hotspots"][0]
        if h["pct"] >= 5:
            sev = 3 if h["pct"] >= 30 else 2
            items.append(
                {
                    "kind": "missing",
                    "severity": sev,
                    "icon": "missing",
                    "title": f"'{h['column']}' has {h['pct']:.0f}% missing values",
                    "detail": "Imputed during cleaning, but high missingness can bias analysis — "
                    "verify the source.",
                }
            )

    for o in outliers[:2]:
        if o["pct"] >= 1:
            items.append(
                {
                    "kind": "outliers",
                    "severity": 2 if o["pct"] >= 5 else 1,
                    "icon": "outlier",
                    "title": f"'{o['column']}' contains {o['count']} outliers",
                    "detail": f"{o['pct']:.0f}% of values fall outside 1.5×IQR — possible data errors "
                    "or genuine extremes.",
                }
            )

    for d in dominance[:1]:
        items.append(
            {
                "kind": "dominant",
                "severity": 1,
                "icon": "dominant",
                "title": f"'{d['column']}' is dominated by one value",
                "detail": f"'{d['value']}' accounts for {d['share']:.0f}% of rows — limited variance "
                "in this dimension.",
            }
        )

    if quality["duplicate_rows"] > 0:
        items.append(
            {
                "kind": "duplicates",
                "severity": 1,
                "icon": "duplicate",
                "title": f"{quality['duplicate_rows']} duplicate rows removed",
                "detail": f"{quality['duplicate_pct']:.0f}% of rows were exact duplicates.",
            }
        )

    items.sort(key=lambda x: x["severity"], reverse=True)
    return items[:_TOP_INSIGHTS]


# ---------------------------------------------------------------------------
# LLM payload (compact, no raw rows)
# ---------------------------------------------------------------------------


def _llm_payload(
    meta_name: str,
    n_rows: int,
    n_cols: int,
    quality: dict,
    insights: list,
    correlations: list,
    segments: dict | None,
    trends: dict | None,
) -> dict[str, Any]:
    return {
        "dataset": meta_name,
        "rows": n_rows,
        "columns": n_cols,
        "quality_score": quality["score"],
        "missing_pct": quality["missing_pct"],
        "duplicate_rows": quality["duplicate_rows"],
        "top_insights": [
            {"title": i["title"], "detail": i["detail"]} for i in insights
        ],
        "correlations": [
            {"a": c["col_a"], "b": c["col_b"], "r": c["r"]} for c in correlations[:5]
        ],
        "segment": (
            {
                "dimension": segments["dimension"],
                "measure": segments["measure"],
                "top": segments["top"],
                "bottom": segments["bottom"],
            }
            if segments
            else None
        ),
        "trend": (
            {
                "measure": trends["measure"],
                "direction": trends["direction"],
                "change_pct": trends["change_pct"],
            }
            if trends
            else None
        ),
    }


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def analyze(
    df: pd.DataFrame,
    profile: dict,
    meta_name: str = "dataset",
    semantics: dict | None = None,
) -> dict[str, Any]:
    """Run the full expert analysis over a profiled DataFrame.

    Driven by semantic roles so trends/segments/outliers/correlations use real
    *measures* (sales, profit) — never identifiers like ``row_id``.
    """
    sem = semantics or infer_semantics(df, profile)
    measures = set(sem.get("measure_cols", []))

    quality = _quality(df, profile)
    outliers = _outliers(df, sem.get("measure_cols", []))
    # Only correlations between genuine measures — drop id/geo noise.
    correlations = [
        p
        for p in (profile.get("correlation") or {}).get("top_pairs", [])
        if abs(p.get("r", 0)) >= 0.3
        and p.get("col_a") in measures
        and p.get("col_b") in measures
    ]
    dominance = _dominance(df, profile)
    segments = _segments(df, sem)
    trends = _trends(df, sem)

    insights = _build_insights(
        quality, outliers, correlations, dominance, segments, trends
    )
    payload = _llm_payload(
        meta_name,
        int(df.shape[0]),
        int(df.shape[1]),
        quality,
        insights,
        correlations,
        segments,
        trends,
    )
    payload["archetype"] = sem.get("archetype_label")
    payload["domain"] = sem.get("domain")

    return {
        "quality": quality,
        "outliers": outliers,
        "correlations": correlations,
        "dominance": dominance,
        "segments": segments,
        "trends": trends,
        "insights": insights,
        "semantics": sem,
        "llm_payload": payload,
    }
