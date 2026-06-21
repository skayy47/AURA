"""PDF report renderer — Jinja2 → HTML → Playwright PDF."""

from __future__ import annotations

import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from services import report_i18n

logger = logging.getLogger(__name__)

_TEMPLATE_DIR = Path(__file__).parent.parent / "templates"
_ENV = Environment(
    loader=FileSystemLoader(str(_TEMPLATE_DIR)),
    autoescape=select_autoescape(["html"]),
)

# Locale-aware number filters for the template:
#   {{ value | gi(lang) }}        grouped integer  (1 234 567)
#   {{ value | gd(lang, places) }} grouped decimal (0,97)
_ENV.filters["gi"] = report_i18n.fmt_int
_ENV.filters["gd"] = report_i18n.fmt_dec


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


def build_report_context(session: dict, profile: dict, language: str = "en") -> dict:
    """Assemble the Data Intelligence Report context: expert analysis + an
    LLM executive summary + chart-ready data + column appendix.

    Fully localized to *language* ("en" / "fr"): insights, executive summary,
    role/archetype/domain labels, the date, and every static template string.
    """
    from datetime import datetime, timezone

    lang = report_i18n.normalize_lang(language)
    labels = report_i18n.labels_for(lang)

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
        # Reuse the per-language analysis the /analyze route already cached.
        cached = session.get(f"analysis_{lang}")
        if cached and cached.get("llm_payload"):
            analysis = cached
            semantics = analysis.get("semantics") or semantics
        else:
            try:
                from engines.analysis import analyze

                analysis = analyze(
                    df,
                    profile,
                    meta_name=dataset_name,
                    semantics=semantics or None,
                    language=lang,
                )
                semantics = analysis.get("semantics") or semantics
            except Exception as exc:
                logger.warning("Analysis failed during report build: %s", exc)
        try:
            from engines.ai_insights import executive_summary

            if analysis.get("llm_payload"):
                exec_summary = executive_summary(analysis["llm_payload"], language=lang)
        except Exception as exc:
            logger.warning("Exec summary failed: %s", exc)
        # ── Bespoke charts → inline SVG (always renders) ─────────
        try:
            from engines.exploration import recommend_charts
            from services.svg_charts import FULL_WIDTH, chart_to_svg

            for rec in recommend_charts(df, profile, semantics or None, language=lang):
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
    role_names = report_i18n.role_labels_for(lang)
    role_specs = [
        (semantics.get("measure_cols", []), "#8b5cf6"),
        (semantics.get("dimension_cols", []), "#3b82f6"),
        (semantics.get("temporal_cols", []), "#00e5ff"),
        (semantics.get("geo_cols", []), "#00ffb2"),
        (semantics.get("id_cols", []), "#ec4899"),
    ]
    role_summary = [
        {"label": role_names[i], "cols": cols, "color": color}
        for i, (cols, color) in enumerate(role_specs)
        if cols
    ]

    arch_label, arch_blurb = report_i18n.archetype_for(semantics.get("archetype"), lang)
    return {
        "lang": lang,
        "labels": labels,
        "dataset_name": dataset_name,
        "generated_at": report_i18n.fmt_date(datetime.now(timezone.utc), lang),
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
        "archetype": arch_label or semantics.get("archetype_label"),
        "archetype_blurb": arch_blurb or semantics.get("archetype_blurb"),
        "domain": report_i18n.domain_for(semantics.get("domain"), lang),
        "role_summary": role_summary,
        "top_pairs": (profile.get("correlation") or {}).get("top_pairs", [])[:6],
        "cleaning_log": cleaning_log,
    }
