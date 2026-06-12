"""PDF report renderer — Jinja2 → HTML → Playwright PDF."""

from __future__ import annotations

import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)

_TEMPLATE_DIR = Path(__file__).parent.parent / "templates"
_ENV = Environment(
    loader=FileSystemLoader(str(_TEMPLATE_DIR)),
    autoescape=select_autoescape(["html"]),
)


async def render_pdf(context: dict) -> bytes:
    """Render the report template with *context* and return PDF bytes via Playwright."""
    html = _ENV.get_template("report.html.j2").render(**context)
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise RuntimeError(
            "playwright is not installed. Run: pip install playwright==1.45.0 && playwright install chromium"
        ) from exc

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html, wait_until="networkidle")
        pdf_bytes = await page.pdf(
            format="A4",
            print_background=True,
            margin={"top": "20mm", "bottom": "20mm", "left": "16mm", "right": "16mm"},
        )
        await browser.close()

    logger.info("PDF rendered — %d bytes", len(pdf_bytes))
    return pdf_bytes


def _get_df(session: dict):
    """Safely fetch the working DataFrame (cleaned preferred), avoiding
    the `df or df` truth-value trap on DataFrames."""
    df = session.get("cleaned_df")
    if df is None:
        df = session.get("raw_df")
    return df


def build_report_context(session: dict, profile: dict) -> dict:
    """Assemble the Data Intelligence Report context: expert analysis + an
    LLM executive summary + chart-ready data + column appendix."""
    from datetime import datetime, timezone

    meta = session.get("meta", {})
    cleaning_log = session.get("cleaning_log", [])
    dataset_name = meta.get("name") or session.get("file_name", "dataset")

    # ── Expert analysis (defensive) ─────────────────────────────
    analysis: dict = {}
    exec_summary: dict = {}
    charts: list[dict] = []
    semantics: dict = session.get("semantics") or {}
    df = _get_df(session)
    if df is not None:
        try:
            from engines.analysis import analyze

            analysis = analyze(
                df, profile, meta_name=dataset_name, semantics=semantics or None
            )
            semantics = analysis.get("semantics") or semantics
        except Exception as exc:
            logger.warning("Analysis failed during report build: %s", exc)
        try:
            from engines.ai_insights import executive_summary

            if analysis.get("llm_payload"):
                exec_summary = executive_summary(analysis["llm_payload"])
        except Exception as exc:
            logger.warning("Exec summary failed: %s", exc)
        # ── Bespoke charts → inline SVG (always renders) ─────────
        try:
            from engines.exploration import recommend_charts
            from services.svg_charts import FULL_WIDTH, chart_to_svg

            for rec in recommend_charts(df, profile, semantics or None):
                svg = chart_to_svg(rec, profile)
                if svg:
                    charts.append(
                        {
                            "title": rec.get("title") or rec.get("rationale"),
                            "rationale": rec.get("rationale"),
                            "svg": svg,
                            "full": rec.get("type") in FULL_WIDTH,
                        }
                    )
        except Exception as exc:
            logger.warning("Chart SVG build failed: %s", exc)

    quality = analysis.get("quality", {})
    quality_score = quality.get("score")

    # ── Column appendix (map profile → template-friendly shape) ──
    columns = []
    for c in profile.get("columns", []):
        top_vals = c.get("top_values") or []
        columns.append(
            {
                "name": c.get("name"),
                "dtype": c.get("dtype"),
                "kind": c.get("kind"),
                "missing_count": c.get("n_missing", 0),
                "missing_pct": c.get("missing_pct", 0),
                "n_unique": c.get("n_unique"),
                "mean": c.get("mean"),
                "top_value": top_vals[0]["value"] if top_vals else None,
            }
        )

    # ── Chart data (rendered as CSS bars in the template) ───────
    # Primary numeric histogram
    histogram = None
    for c in profile.get("columns", []):
        if c.get("kind") == "numeric" and c.get("histogram"):
            histogram = {"column": c["name"], "bins": c["histogram"]}
            break

    # ── Dataset DNA — semantic role breakdown for the cover/overview ──
    role_summary = [
        {
            "label": "Measures",
            "cols": semantics.get("measure_cols", []),
            "color": "#8b5cf6",
        },
        {
            "label": "Dimensions",
            "cols": semantics.get("dimension_cols", []),
            "color": "#3b82f6",
        },
        {
            "label": "Temporal",
            "cols": semantics.get("temporal_cols", []),
            "color": "#00e5ff",
        },
        {
            "label": "Geographic",
            "cols": semantics.get("geo_cols", []),
            "color": "#00ffb2",
        },
        {
            "label": "Identifiers",
            "cols": semantics.get("id_cols", []),
            "color": "#ec4899",
        },
    ]
    role_summary = [r for r in role_summary if r["cols"]]

    return {
        "dataset_name": dataset_name,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "n_rows": profile.get("n_rows", meta.get("n_rows", "—")),
        "n_cols": profile.get("n_cols", meta.get("n_cols", "—")),
        "missing_total": profile.get("missing_total", "—"),
        "memory_mb": round(profile.get("memory_mb", 0), 2),
        "quality_score": quality_score,
        "quality": quality,
        "exec_summary": exec_summary,
        "insights": analysis.get("insights", []),
        "correlations": analysis.get("correlations", []),
        "segments": analysis.get("segments"),
        "trends": analysis.get("trends"),
        "histogram": histogram,
        "charts": charts,
        "columns": columns,
        "archetype": semantics.get("archetype_label"),
        "archetype_blurb": semantics.get("archetype_blurb"),
        "domain": semantics.get("domain"),
        "role_summary": role_summary,
        "top_pairs": (profile.get("correlation") or {}).get("top_pairs", [])[:6],
        "cleaning_log": cleaning_log,
    }
