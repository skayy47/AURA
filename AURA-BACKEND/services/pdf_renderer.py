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


def build_report_context(session: dict, profile: dict) -> dict:
    """Assemble the Jinja2 template context from a session + explore profile dict."""
    from datetime import datetime, timezone

    meta = session.get("meta", {})
    cleaning_log = session.get("cleaning_log", [])

    quality_score: int | None = None
    for entry in reversed(cleaning_log):
        if isinstance(entry, dict) and entry.get("step") == "SchemaValidator":
            detail = entry.get("detail", "")
            if "Quality score:" in detail:
                try:
                    quality_score = int(detail.split("Quality score:")[-1].strip().split("/")[0])
                except ValueError:
                    pass
            break

    top_pairs = (profile.get("correlation") or {}).get("top_pairs", [])[:5]
    columns = profile.get("columns", [])

    return {
        "dataset_name": meta.get("name") or session.get("file_name", "dataset"),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "n_rows": profile.get("n_rows", meta.get("n_rows", "—")),
        "n_cols": profile.get("n_cols", meta.get("n_cols", "—")),
        "missing_total": profile.get("missing_total", meta.get("missing_total", "—")),
        "memory_mb": round(profile.get("memory_mb", 0), 2),
        "quality_score": quality_score,
        "columns": columns,
        "top_pairs": top_pairs,
        "cleaning_log": cleaning_log,
    }
