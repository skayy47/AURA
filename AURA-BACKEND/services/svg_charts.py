"""Server-side SVG chart renderer for the Data Intelligence Report.

Converts the chart recommendations from ``engines.exploration.recommend_charts``
into self-contained ``<svg>`` strings. Pure Python — no browser, no JS chart
lib — so the report's visuals always render (even where Chromium's canvas is
restricted) and are bespoke to each dataset.

Public entry point:
    chart_to_svg(rec, profile) -> str | None
"""

from __future__ import annotations

import html
import logging
import math
from typing import Any

logger = logging.getLogger(__name__)

# Palette matches the report template.
_VIOLET = "#8b5cf6"
_CYAN = "#00e5ff"
_BLUE = "#3b82f6"
_MINT = "#00ffb2"
_RED = "#fb7185"
_GRID = "rgba(255,255,255,0.08)"
_TEXT_M = "#94a3b8"
_TEXT_D = "#4a5878"
_SERIES = [_VIOLET, _CYAN, _BLUE, _MINT, "#f59e0b"]


def _esc(s: Any) -> str:
    return html.escape(str(s), quote=True)


def _fmt(v: float) -> str:
    """Compact number formatting: 1.2K, 3.4M, -0.45."""
    try:
        v = float(v)
    except (TypeError, ValueError):
        return str(v)
    a = abs(v)
    if a >= 1_000_000_000:
        return f"{v / 1_000_000_000:.1f}B"
    if a >= 1_000_000:
        return f"{v / 1_000_000:.1f}M"
    if a >= 1_000:
        return f"{v / 1_000:.1f}K"
    if a >= 10:
        return f"{v:.0f}"
    if a == 0:
        return "0"
    return f"{v:.2f}"


def _truncate(s: str, n: int) -> str:
    s = str(s)
    return s if len(s) <= n else s[: n - 1] + "…"


def _svg(inner: str, w: int, h: int) -> str:
    return (
        f'<svg viewBox="0 0 {w} {h}" width="100%" '
        f'preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="-apple-system, Segoe UI, sans-serif">{inner}</svg>'
    )


# ---------------------------------------------------------------------------
# Horizontal bar
# ---------------------------------------------------------------------------


def bar_svg(bars: list[dict], w: int = 500) -> str:
    bars = bars[:10]
    if not bars:
        return ""
    row_h, pad_t, pad_b = 26, 6, 6
    h = pad_t + pad_b + row_h * len(bars)
    label_w, val_w = 132, 52
    x0, x1 = label_w, w - val_w
    span = x1 - x0
    maxv = max((abs(b["value"]) for b in bars), default=1) or 1
    parts = [
        '<defs><linearGradient id="bargrad" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0%" stop-color="{_VIOLET}" stop-opacity="0.5"/>'
        f'<stop offset="100%" stop-color="{_CYAN}"/></linearGradient></defs>'
    ]
    for i, b in enumerate(bars):
        y = pad_t + i * row_h
        cy = y + row_h / 2
        bw = abs(b["value"]) / maxv * span
        fill = _RED if b["value"] < 0 else "url(#bargrad)"
        parts.append(
            f'<text x="{label_w - 10}" y="{cy + 3}" text-anchor="end" '
            f'font-size="11" fill="{_TEXT_M}">{_esc(_truncate(b["label"], 16))}</text>'
        )
        parts.append(
            f'<rect x="{x0}" y="{y + 5}" width="{bw:.1f}" height="{row_h - 12}" '
            f'rx="3" fill="{fill}"/>'
        )
        parts.append(
            f'<text x="{x0 + bw + 6:.1f}" y="{cy + 3}" font-size="10" '
            f'fill="{_TEXT_M}" font-family="monospace">{_esc(_fmt(b["value"]))}</text>'
        )
    return _svg("".join(parts), w, int(h))


# ---------------------------------------------------------------------------
# Vertical histogram
# ---------------------------------------------------------------------------


def histogram_svg(bins: list[dict], w: int = 500, h: int = 180) -> str:
    if not bins:
        return ""
    pad_l, pad_r, pad_t, pad_b = 8, 8, 10, 22
    plot_w, plot_h = w - pad_l - pad_r, h - pad_t - pad_b
    n = len(bins)
    gap = 2
    bw = (plot_w / n) - gap
    maxc = max((b["count"] for b in bins), default=1) or 1
    parts = [
        '<defs><linearGradient id="histgrad" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{_CYAN}"/>'
        f'<stop offset="100%" stop-color="{_BLUE}" stop-opacity="0.35"/></linearGradient></defs>'
    ]
    base = pad_t + plot_h
    for i, b in enumerate(bins):
        bh = b["count"] / maxc * plot_h
        x = pad_l + i * (bw + gap)
        parts.append(
            f'<rect x="{x:.1f}" y="{base - bh:.1f}" width="{bw:.1f}" '
            f'height="{bh:.1f}" rx="2" fill="url(#histgrad)"/>'
        )
    parts.append(
        f'<line x1="{pad_l}" y1="{base}" x2="{w - pad_r}" y2="{base}" stroke="{_GRID}"/>'
    )
    lo = bins[0].get("bin", "").split("–")[0][:8]
    hi = bins[-1].get("bin", "").split("–")[-1][:8]
    parts.append(
        f'<text x="{pad_l}" y="{h - 6}" font-size="9" fill="{_TEXT_D}" font-family="monospace">{_esc(lo)}</text>'
    )
    parts.append(
        f'<text x="{w - pad_r}" y="{h - 6}" text-anchor="end" font-size="9" fill="{_TEXT_D}" font-family="monospace">{_esc(hi)}</text>'
    )
    return _svg("".join(parts), w, h)


# ---------------------------------------------------------------------------
# Line chart (single or multi-series)
# ---------------------------------------------------------------------------


def _line_paths(series: list[dict], w: int, h: int) -> str:
    pad_l, pad_r, pad_t, pad_b = 40, 10, 12, 22
    plot_w, plot_h = w - pad_l - pad_r, h - pad_t - pad_b

    all_vals = [p["value"] for s in series for p in s["points"]]
    if not all_vals:
        return ""
    vmin, vmax = min(all_vals), max(all_vals)
    if vmin == vmax:
        vmin, vmax = vmin - 1, vmax + 1
    # Union of x labels in order of appearance.
    xseen: list[str] = []
    for s in series:
        for p in s["points"]:
            if p["x"] not in xseen:
                xseen.append(p["x"])
    xidx = {x: i for i, x in enumerate(xseen)}
    nx = max(len(xseen) - 1, 1)

    def X(x: str) -> float:
        return pad_l + xidx[x] / nx * plot_w

    def Y(v: float) -> float:
        return pad_t + (1 - (v - vmin) / (vmax - vmin)) * plot_h

    parts = [
        '<defs><linearGradient id="linearea" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{_VIOLET}" stop-opacity="0.35"/>'
        f'<stop offset="100%" stop-color="{_VIOLET}" stop-opacity="0"/></linearGradient></defs>'
    ]
    base = pad_t + plot_h
    # gridlines + y labels (min / mid / max)
    for frac, val in ((0.0, vmax), (0.5, (vmin + vmax) / 2), (1.0, vmin)):
        gy = pad_t + frac * plot_h
        parts.append(
            f'<line x1="{pad_l}" y1="{gy:.1f}" x2="{w - pad_r}" y2="{gy:.1f}" stroke="{_GRID}"/>'
        )
        parts.append(
            f'<text x="{pad_l - 6}" y="{gy + 3:.1f}" text-anchor="end" font-size="9" fill="{_TEXT_D}" font-family="monospace">{_esc(_fmt(val))}</text>'
        )

    single = len(series) == 1
    for si, s in enumerate(series):
        pts = s["points"]
        if not pts:
            continue
        color = _SERIES[si % len(_SERIES)]
        coords = " ".join(f"{X(p['x']):.1f},{Y(p['value']):.1f}" for p in pts)
        if single:
            area = (
                f"{X(pts[0]['x']):.1f},{base:.1f} "
                + coords
                + f" {X(pts[-1]['x']):.1f},{base:.1f}"
            )
            parts.append(f'<polygon points="{area}" fill="url(#linearea)"/>')
        parts.append(
            f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="2.2" stroke-linejoin="round"/>'
        )

    # x labels: first and last
    if xseen:
        parts.append(
            f'<text x="{pad_l}" y="{h - 6}" font-size="9" fill="{_TEXT_D}" font-family="monospace">{_esc(xseen[0])}</text>'
        )
        parts.append(
            f'<text x="{w - pad_r}" y="{h - 6}" text-anchor="end" font-size="9" fill="{_TEXT_D}" font-family="monospace">{_esc(xseen[-1])}</text>'
        )
    return "".join(parts)


def line_svg(rec: dict, w: int = 1000, h: int = 280) -> str:
    series = rec.get("series") or []
    if not series and rec.get("points"):
        series = [{"name": rec.get("y", "value"), "points": rec["points"]}]
    series = [s for s in series if s.get("points")]
    if not series:
        return ""
    inner = _line_paths(series, w, h)
    # Legend for multi-series
    if len(series) > 1:
        lx = 44
        items = []
        for si, s in enumerate(series):
            color = _SERIES[si % len(_SERIES)]
            items.append(
                f'<rect x="{lx}" y="2" width="9" height="9" rx="2" fill="{color}"/>'
                f'<text x="{lx + 13}" y="10" font-size="10" fill="{_TEXT_M}">{_esc(_truncate(s["name"], 18))}</text>'
            )
            lx += 22 + len(_truncate(str(s["name"]), 18)) * 6
        inner = (
            f'<g>{"".join(items)}</g>' + f'<g transform="translate(0,12)">{inner}</g>'
        )
        h += 12
    return _svg(inner, w, h)


# ---------------------------------------------------------------------------
# Donut
# ---------------------------------------------------------------------------


def donut_svg(segments: list[dict], w: int = 500, h: int = 220) -> str:
    segments = segments[:8]
    total = sum(s["value"] for s in segments) or 1
    cx, cy, r, sw = 90, h / 2, 64, 26
    circ = 2 * math.pi * r
    parts = [
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#0b1426" stroke-width="{sw}"/>'
    ]
    offset = 0.0
    for i, s in enumerate(segments):
        frac = s["value"] / total
        seg_len = frac * circ
        color = _SERIES[i % len(_SERIES)]
        parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-dasharray="{seg_len:.2f} {circ - seg_len:.2f}" '
            f'stroke-dashoffset="{-offset:.2f}" transform="rotate(-90 {cx} {cy})"/>'
        )
        offset += seg_len
    parts.append(
        f'<text x="{cx}" y="{cy - 2}" text-anchor="middle" font-size="18" font-weight="700" fill="#f8fafc" font-family="monospace">{_esc(_fmt(total))}</text>'
    )
    parts.append(
        f'<text x="{cx}" y="{cy + 13}" text-anchor="middle" font-size="8" fill="{_TEXT_D}">TOTAL</text>'
    )
    # Legend
    ly = (h - len(segments) * 20) / 2 + 6
    for i, s in enumerate(segments):
        color = _SERIES[i % len(_SERIES)]
        y = ly + i * 20
        parts.append(
            f'<rect x="180" y="{y - 9}" width="10" height="10" rx="2" fill="{color}"/>'
        )
        parts.append(
            f'<text x="197" y="{y}" font-size="11" fill="{_TEXT_M}">{_esc(_truncate(s["label"], 22))}</text>'
        )
        parts.append(
            f'<text x="{w - 8}" y="{y}" text-anchor="end" font-size="11" fill="#f8fafc" font-family="monospace">{s.get("pct", 0)}%</text>'
        )
    return _svg("".join(parts), w, h)


# ---------------------------------------------------------------------------
# Scatter
# ---------------------------------------------------------------------------


def scatter_svg(rec: dict, w: int = 500, h: int = 220) -> str:
    points = rec.get("points") or []
    if len(points) < 2:
        return ""
    points = points[:300]
    pad_l, pad_r, pad_t, pad_b = 40, 10, 12, 22
    plot_w, plot_h = w - pad_l - pad_r, h - pad_t - pad_b
    xs = [p["x"] for p in points]
    ys = [p["y"] for p in points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    if xmin == xmax:
        xmin, xmax = xmin - 1, xmax + 1
    if ymin == ymax:
        ymin, ymax = ymin - 1, ymax + 1

    def X(v):
        return pad_l + (v - xmin) / (xmax - xmin) * plot_w

    def Y(v):
        return pad_t + (1 - (v - ymin) / (ymax - ymin)) * plot_h

    parts = []
    base = pad_t + plot_h
    parts.append(
        f'<line x1="{pad_l}" y1="{base}" x2="{w - pad_r}" y2="{base}" stroke="{_GRID}"/>'
    )
    parts.append(
        f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{base}" stroke="{_GRID}"/>'
    )
    for p in points:
        parts.append(
            f'<circle cx="{X(p["x"]):.1f}" cy="{Y(p["y"]):.1f}" r="2.4" fill="{_VIOLET}" fill-opacity="0.5"/>'
        )
    # Least-squares regression line
    n = len(points)
    sx, sy = sum(xs), sum(ys)
    mx, my = sx / n, sy / n
    num = sum((px - mx) * (py - my) for px, py in zip(xs, ys))
    den = sum((px - mx) ** 2 for px in xs)
    if den:
        slope = num / den
        intercept = my - slope * mx
        parts.append(
            f'<line x1="{X(xmin):.1f}" y1="{Y(slope * xmin + intercept):.1f}" '
            f'x2="{X(xmax):.1f}" y2="{Y(slope * xmax + intercept):.1f}" '
            f'stroke="{_CYAN}" stroke-width="2" stroke-dasharray="4 3"/>'
        )
    parts.append(
        f'<text x="{pad_l}" y="{h - 6}" font-size="9" fill="{_TEXT_D}">{_esc(rec.get("x", "x"))}</text>'
    )
    parts.append(
        f'<text x="{w - pad_r}" y="{pad_t + 4}" text-anchor="end" font-size="9" fill="{_TEXT_D}">{_esc(rec.get("y", "y"))}</text>'
    )
    return _svg("".join(parts), w, h)


# ---------------------------------------------------------------------------
# Correlation heatmap
# ---------------------------------------------------------------------------


def heatmap_svg(profile: dict, columns: list[str], w: int = 1000) -> str:
    corr = (profile.get("correlation") or {}).get("matrix")
    if not corr:
        return ""
    cols = corr["columns"]
    data = corr["data"]
    keep = [c for c in columns if c in cols][:8] or cols[:8]
    idx = [cols.index(c) for c in keep]
    n = len(keep)
    if n < 2:
        return ""
    label_w = 96
    cell = min((w - label_w - 10) / n, 70)
    h = int(label_w * 0 + cell * n + 96)
    top = 88
    parts = []
    for j, cj in enumerate(keep):
        x = label_w + j * cell + cell / 2
        parts.append(
            f'<text x="{x:.1f}" y="{top - 8}" font-size="9" fill="{_TEXT_M}" '
            f'transform="rotate(-40 {x:.1f} {top - 8})" text-anchor="start">{_esc(_truncate(cj, 12))}</text>'
        )
    for i, ci in enumerate(keep):
        y = top + i * cell
        parts.append(
            f'<text x="{label_w - 8}" y="{y + cell / 2 + 3:.1f}" text-anchor="end" font-size="9" fill="{_TEXT_M}">{_esc(_truncate(ci, 13))}</text>'
        )
        for j in range(n):
            r = data[idx[i]][idx[j]]
            r = 0.0 if r is None else float(r)
            if r >= 0:
                col = f"rgba(139,92,246,{abs(r):.2f})"
            else:
                col = f"rgba(251,113,133,{abs(r):.2f})"
            x = label_w + j * cell
            parts.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell - 2:.1f}" height="{cell - 2:.1f}" rx="3" fill="{col}" stroke="{_GRID}"/>'
            )
            if cell > 34:
                tc = "#f8fafc" if abs(r) > 0.4 else _TEXT_D
                parts.append(
                    f'<text x="{x + cell / 2:.1f}" y="{y + cell / 2 + 3:.1f}" text-anchor="middle" font-size="9" fill="{tc}" font-family="monospace">{r:.2f}</text>'
                )
    return _svg("".join(parts), w, h)


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

# Charts that should span the full report width.
FULL_WIDTH = {"timeseries", "heatmap_corr"}


def chart_to_svg(rec: dict, profile: dict) -> str | None:
    """Render a single chart recommendation to an SVG string."""
    try:
        t = rec.get("type")
        if t == "timeseries":
            return line_svg(rec)
        if t == "bar_grouped":
            return bar_svg(rec.get("bars", []))
        if t == "donut":
            return donut_svg(rec.get("segments", []))
        if t == "scatter":
            return scatter_svg(rec)
        if t == "heatmap_corr":
            return heatmap_svg(profile, rec.get("columns", []))
        if t == "histogram":
            col = next(
                (
                    c
                    for c in profile.get("columns", [])
                    if c.get("name") == rec.get("column")
                ),
                None,
            )
            if col and col.get("histogram"):
                return histogram_svg(col["histogram"])
        return None
    except Exception as exc:  # noqa: BLE001 - a bad chart must never break the report
        logger.warning("SVG render failed for %s: %s", rec.get("type"), exc)
        return None
