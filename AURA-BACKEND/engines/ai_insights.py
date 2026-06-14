"""AI insights engine — multi-provider, free-first.

Providers (see PROVIDERS registry):
    • Groq · Llama 3.3 70B   — FREE  (default; OpenAI-compatible API)
    • OpenAI · GPT-4o mini   — PAID  (OpenAI-compatible API)
    • Claude · Sonnet 4.6    — PAID  (Anthropic API)

Groq and OpenAI share one OpenAI-compatible code path (only api_key + base_url
differ). Claude uses the Anthropic SDK. Resolution is resilient: if the requested
provider has no key, we fall back to the best *configured* provider (free first),
and the executive summary degrades to a deterministic summary if none are usable.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from enum import Enum
from typing import Generator

import pandas as pd

from utils.helpers import get_logger

logger = get_logger(__name__)

QUICK_PROMPTS: list[str] = [
    "Summarise this dataset in 5 bullet points.",
    "What data quality issues do you see?",
    "Which columns are most important for ML?",
    "Find any anomalies or outliers.",
    "Suggest 3 visualisations to explore this data.",
]


class AIProvider(str, Enum):
    """Supported AI providers."""

    GEMINI = "gemini"
    GROQ = "groq"
    CLAUDE = "claude"
    OPENAI = "openai"


@dataclass(frozen=True)
class ProviderSpec:
    label: str
    tier: str  # "free" | "paid"
    env_var: str
    model: str
    kind: str  # "openai_compat" | "anthropic"
    base_url: str | None = None


# Single source of truth for provider config. Order = preference (free first).
# Gemini Flash leads: 15 RPM free tier, excellent bilingual (EN/FR) quality.
PROVIDERS: dict[AIProvider, ProviderSpec] = {
    AIProvider.GEMINI: ProviderSpec(
        label="Gemini · Flash 2.0",
        tier="free",
        env_var="GOOGLE_API_KEY",
        model="gemini-2.0-flash",
        kind="openai_compat",
        base_url="https://generativelanguage.googleapis.com/openai/",
    ),
    AIProvider.GROQ: ProviderSpec(
        label="Groq · Llama 3.3 70B",
        tier="free",
        env_var="GROQ_API_KEY",
        model="llama-3.3-70b-versatile",
        kind="openai_compat",
        base_url="https://api.groq.com/openai/v1",
    ),
    AIProvider.OPENAI: ProviderSpec(
        label="OpenAI · GPT-4o mini",
        tier="paid",
        env_var="OPENAI_API_KEY",
        model="gpt-4o-mini",
        kind="openai_compat",
    ),
    AIProvider.CLAUDE: ProviderSpec(
        label="Claude · Sonnet 4.6",
        tier="paid",
        env_var="ANTHROPIC_API_KEY",
        model="claude-sonnet-4-6",
        kind="anthropic",
    ),
}

_DEFAULT_ORDER = [AIProvider.GEMINI, AIProvider.GROQ, AIProvider.OPENAI, AIProvider.CLAUDE]


# ---------------------------------------------------------------------------
# Provider resolution
# ---------------------------------------------------------------------------


def is_configured(provider: AIProvider) -> bool:
    """True if the provider's API key is present in the environment."""
    return bool(os.getenv(PROVIDERS[provider].env_var, "").strip())


def available_providers() -> list[dict]:
    """List providers with config status — handy for the frontend / diagnostics."""
    return [
        {
            "id": p.value,
            "label": s.label,
            "tier": s.tier,
            "configured": is_configured(p),
        }
        for p, s in PROVIDERS.items()
    ]


def resolve_provider(requested: AIProvider | None) -> AIProvider:
    """Return the requested provider if configured, else the best configured one
    (free first). Raises if none are configured."""
    if requested and is_configured(requested):
        return requested
    for p in _DEFAULT_ORDER:
        if is_configured(p):
            if requested and p != requested:
                logger.info(
                    "Provider %s not configured — falling back to %s", requested, p
                )
            return p
    raise ValueError(
        "No AI provider is configured. Set a free GROQ_API_KEY "
        "(console.groq.com), or ANTHROPIC_API_KEY / OPENAI_API_KEY."
    )


def coerce_provider(value: str | AIProvider | None) -> AIProvider:
    """Map a loose string (e.g. from the frontend) to an AIProvider; default Groq."""
    if isinstance(value, AIProvider):
        return value
    try:
        return AIProvider((value or "").strip().lower())
    except ValueError:
        return AIProvider.GROQ


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------


_LANGUAGE_NAMES = {"en": "English", "fr": "French"}


def _language_directive(language: str | None) -> str:
    """A system-prompt rule forcing the model to answer in the UI language.

    Empty for English (the default). Column names, code, and numbers are kept
    verbatim so the analysis stays accurate.
    """
    code = (language or "en").strip().lower()[:2]
    name = _LANGUAGE_NAMES.get(code)
    if not name or code == "en":
        return ""
    return (
        f"\n- ALWAYS respond in {name}. Write the ENTIRE answer in {name} — "
        f"headings, bullet points, and prose. Keep column names, code, and "
        f"numeric values exactly as they appear in the data."
    )


def _build_system_prompt(
    df: pd.DataFrame, semantics: dict | None = None, language: str = "en"
) -> str:
    n_rows, n_cols = df.shape

    dtype_lines = "\n".join(f"  {c}: {t}" for c, t in df.dtypes.items())

    null_counts = df.isnull().sum()
    nulls_present = null_counts[null_counts > 0]
    if not nulls_present.empty:
        null_section = "Columns with missing values (full dataset):\n" + "\n".join(
            f"  {c}: {v:,} missing ({v / n_rows * 100:.1f}%)"
            for c, v in nulls_present.items()
        )
    else:
        null_section = "Missing values: 0 across all columns (clean dataset)."

    num_df = df.select_dtypes(include="number")
    if not num_df.empty:
        desc = num_df.describe().round(4)
        stat_lines = []
        for col in desc.columns:
            s = desc[col]
            stat_lines.append(
                f"  {col}: count={int(s['count'])}, min={s['min']:.4g}, "
                f"mean={s['mean']:.4g}, max={s['max']:.4g}, std={s['std']:.4g}"
            )
        numeric_section = (
            "Numeric column statistics (computed on full dataset):\n"
            + "\n".join(stat_lines)
        )
    else:
        numeric_section = "No numeric columns detected."

    cat_df = df.select_dtypes(include=["object", "category"])
    cat_parts: list[str] = []
    for col in list(cat_df.columns)[:5]:
        vc = cat_df[col].value_counts().head(3)
        vc_str = ", ".join(f'"{k}"({v})' for k, v in vc.items())
        cat_parts.append(f"  {col}: {vc_str}")
    cat_section = (
        ("Top values per categorical column:\n" + "\n".join(cat_parts))
        if cat_parts
        else ""
    )

    sections = [
        f"You are AURA AI — a sharp, direct data analyst. "
        f"The user uploaded a dataset: **{n_rows:,} rows × {n_cols} columns**.",
        f"Column types:\n{dtype_lines}",
        null_section,
        numeric_section,
    ]
    if cat_section:
        sections.append(cat_section)

    id_rule = ""
    if semantics:
        arch = semantics.get("archetype_label")
        domain = semantics.get("domain")
        measures = semantics.get("measure_cols") or []
        dims = semantics.get("dimension_cols") or []
        temporal = semantics.get("temporal_cols") or []
        ids = semantics.get("id_cols") or []
        geo = semantics.get("geo_cols") or []
        role_lines = [
            f"Dataset shape: {arch}" + (f" · domain: {domain}" if domain else "")
        ]
        if measures:
            role_lines.append(
                f"Measures (real quantities to analyze): {', '.join(measures)}"
            )
        if dims:
            role_lines.append(f"Dimensions (slice/compare by these): {', '.join(dims)}")
        if temporal:
            role_lines.append(f"Time columns: {', '.join(temporal)}")
        if geo:
            role_lines.append(f"Geographic columns: {', '.join(geo)}")
        if ids:
            role_lines.append(f"Identifier/key columns: {', '.join(ids)}")
        sections.append(
            "Semantic column roles (already inferred):\n"
            + "\n".join(f"  {ln}" for ln in role_lines)
        )
        if ids:
            id_rule = (
                f"\n- Columns {', '.join(ids)} are IDENTIFIERS (keys). NEVER treat them as "
                "measures — no trends, outliers, averages, or correlations on identifiers."
            )

    sections.append(
        "RULES:\n"
        "- The statistics above are computed on the FULL dataset. Answer DIRECTLY from them.\n"
        "- NEVER say 'I would need to run code' or 'without the actual data' — you HAVE it.\n"
        "- Be specific and numerical. Name actual columns and cite real values from above.\n"
        "- Format with markdown: bold key figures, use bullet lists, code blocks for any code.\n"
        "- Be concise and insight-driven. No filler, no preamble."
        + id_rule
        + _language_directive(language)
    )

    return "\n\n".join(sections)


def _truncate_df(
    df: pd.DataFrame, max_rows: int = 10, max_cols: int = 12
) -> pd.DataFrame:
    return df.iloc[:max_rows, :max_cols]


# ---------------------------------------------------------------------------
# Unified call layer
# ---------------------------------------------------------------------------


def _stream_provider(
    provider: AIProvider, system_prompt: str, user_message: str, stream: bool
) -> Generator[str, None, None]:
    """Dispatch a (streaming) chat completion to the resolved provider."""
    spec = PROVIDERS[provider]
    if spec.kind == "anthropic":
        yield from _stream_anthropic(spec, system_prompt, user_message, stream)
    else:
        yield from _stream_openai_compat(spec, system_prompt, user_message, stream)


def _stream_openai_compat(
    spec: ProviderSpec, system_prompt: str, user_message: str, stream: bool
) -> Generator[str, None, None]:
    """Groq + OpenAI — same SDK, only api_key + base_url differ."""
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv(spec.env_var, ""), base_url=spec.base_url)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    if stream:
        for chunk in client.chat.completions.create(
            model=spec.model, messages=messages, stream=True
        ):
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    else:
        resp = client.chat.completions.create(model=spec.model, messages=messages)
        yield resp.choices[0].message.content or ""


def _stream_anthropic(
    spec: ProviderSpec, system_prompt: str, user_message: str, stream: bool
) -> Generator[str, None, None]:
    import anthropic

    client = anthropic.Anthropic(api_key=os.getenv(spec.env_var, ""))
    if stream:
        with client.messages.stream(
            model=spec.model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        ) as mgr:
            for text in mgr.text_stream:
                yield text
    else:
        resp = client.messages.create(
            model=spec.model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        yield resp.content[0].text  # type: ignore[index]


# ---------------------------------------------------------------------------
# Public: dataset chat
# ---------------------------------------------------------------------------


def ask_ai(
    df: pd.DataFrame,
    question: str,
    provider: AIProvider = AIProvider.GROQ,
    stream: bool = True,
    semantics: dict | None = None,
    language: str = "en",
) -> Generator[str, None, None]:
    """Ask a provider about *df* and yield streamed text chunks.

    Resolves to the best configured provider (free first) if the requested one
    has no key. Raises ValueError if none are configured. When *semantics* is
    supplied, the system prompt is grounded in column roles so the model never
    treats an identifier like ``row_id`` as a measure.
    """
    resolved = resolve_provider(provider)
    system_prompt = _build_system_prompt(df, semantics, language)
    sample = _truncate_df(df).to_string()
    user_message = f"Dataset sample:\n\n{sample}\n\nQuestion: {question}"
    yield from _stream_provider(resolved, system_prompt, user_message, stream)


# ---------------------------------------------------------------------------
# Public: executive summary (structured, with graceful degradation)
# ---------------------------------------------------------------------------

_SUMMARY_SYSTEM = (
    "You are a senior data analyst writing the executive summary of a Data "
    "Intelligence Report. You receive aggregated statistics about a dataset "
    "(never raw rows). Write for a business decision-maker: precise, confident, "
    "no fluff. Respond ONLY with minified JSON, no markdown, in this exact shape: "
    '{"headline": "<=10 words", "summary": "2-3 sentences", '
    '"findings": ["3-5 short bullet strings"], '
    '"recommendations": ["2-4 short action bullets"]}'
)


def executive_summary(payload: dict, provider: AIProvider = AIProvider.GROQ) -> dict:
    """Structured exec summary from a compact stats *payload* (no raw rows).

    Tries the requested provider first, then every other configured provider
    (free first), then falls back to a deterministic summary. Always returns.
    """
    user = f"Dataset statistics:\n{json.dumps(payload, default=str)}"

    order: list[AIProvider] = []
    if provider:
        order.append(provider)
    order += [p for p in _DEFAULT_ORDER if p not in order]

    last_exc: Exception | None = None
    for prov in order:
        if not is_configured(prov):
            continue
        try:
            raw = "".join(
                _stream_provider(prov, _SUMMARY_SYSTEM, user, stream=False)
            ).strip()
            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.lstrip().startswith("json"):
                    raw = raw.lstrip()[4:]
            s, e = raw.find("{"), raw.rfind("}")
            data = json.loads(raw[s : e + 1])
            return {
                "headline": str(data.get("headline", ""))[:120],
                "summary": str(data.get("summary", "")),
                "findings": [str(f) for f in (data.get("findings") or [])][:5],
                "recommendations": [
                    str(r) for r in (data.get("recommendations") or [])
                ][:4],
                "provider": PROVIDERS[prov].label,
                "by_ai": True,
            }
        except Exception as exc:
            last_exc = exc
            logger.warning("Exec summary via %s failed: %s", prov.value, exc)

    logger.warning("Executive summary fell back to deterministic (last: %s)", last_exc)
    return _deterministic_summary(payload)


def _deterministic_summary(payload: dict) -> dict:
    """Respectable summary built from the payload without any LLM."""
    rows = payload.get("rows", "—")
    cols = payload.get("columns", "—")
    q = payload.get("quality_score", "—")
    insights = payload.get("top_insights", [])
    findings = [i["title"] for i in insights[:5]] or ["No major anomalies detected."]
    recs: list[str] = []
    if payload.get("missing_pct", 0) >= 5:
        recs.append("Investigate the source of missing values before modeling.")
    if payload.get("trend"):
        recs.append(f"Monitor the {payload['trend']['measure']} trend going forward.")
    if payload.get("correlations"):
        c = payload["correlations"][0]
        recs.append(f"Explore the {c['a']}–{c['b']} relationship for predictive value.")
    if not recs:
        recs.append("Dataset is clean and ready for modeling or BI.")
    return {
        "headline": f"{rows} rows × {cols} columns · quality {q}/100",
        "summary": (
            f"This dataset contains {rows} records across {cols} columns with a quality "
            f"score of {q}/100. The analysis surfaced {len(insights)} notable patterns "
            "across correlations, segments, and data-quality dimensions."
        ),
        "findings": findings,
        "recommendations": recs[:4],
        "provider": "Deterministic",
        "by_ai": False,
    }


# ---------------------------------------------------------------------------
# Public: data-specific suggested questions (deterministic, grounded)
# ---------------------------------------------------------------------------


def suggested_questions(
    analysis: dict, semantics: dict | None = None, language: str = "en"
) -> list[str]:
    """Build 4-6 questions DERIVED from the real findings for this dataset.

    Deterministic (instant, free, never hallucinated) and grounded in the
    actual trend/segment/correlation/quality results — so the chips reference
    real measures and dimensions, never an identifier like ``row_id``. Localized
    to the UI language ("en" default, "fr" supported) so the chips match locale.
    """
    is_fr = (language or "en").strip().lower().startswith("fr")
    sem = semantics or analysis.get("semantics") or {}
    trends = analysis.get("trends")
    segments = analysis.get("segments")
    correlations = analysis.get("correlations", [])
    quality = analysis.get("quality", {})
    outliers = analysis.get("outliers", [])
    dominance = analysis.get("dominance", [])
    measures = sem.get("primary_measures", [])
    domain = sem.get("domain")

    direction_fr = {"rising": "à la hausse", "falling": "à la baisse", "flat": "stable"}

    ranked: list[tuple[int, str]] = []

    if trends and trends.get("change_pct") is not None:
        pct = abs(trends["change_pct"])
        d = trends["direction"]
        ranked.append(
            (
                100,
                f"Qu'est-ce qui explique la tendance {direction_fr.get(d, d)} de "
                f"{pct:.0f} % de {trends['measure']} ?"
                if is_fr
                else f"What's driving the {pct:.0f}% {d} trend in {trends['measure']}?",
            )
        )
    if segments and segments.get("top") and segments.get("bottom"):
        ranked.append(
            (
                92,
                f"Pourquoi {segments['top']['label']} surpasse-t-il "
                f"{segments['bottom']['label']} pour {segments['measure']} ?"
                if is_fr
                else f"Why does {segments['top']['label']} outperform "
                f"{segments['bottom']['label']} in {segments['measure']}?",
            )
        )
    if correlations:
        c = correlations[0]
        ranked.append(
            (
                85,
                f"Qu'est-ce qui explique la relation entre {c['col_a']} et {c['col_b']} ?"
                if is_fr
                else f"What explains the relationship between {c['col_a']} and {c['col_b']}?",
            )
        )
    if measures:
        ranked.append(
            (
                68,
                f"Quelles colonnes sont les plus prédictives de {measures[0]} ?"
                if is_fr
                else f"Which columns are most predictive of {measures[0]}?",
            )
        )
    hotspots = quality.get("missing_hotspots", [])
    if hotspots and hotspots[0].get("pct", 0) >= 5:
        h = hotspots[0]
        ranked.append(
            (
                64,
                f"Comment gérer les {h['pct']:.0f} % de valeurs manquantes dans {h['column']} ?"
                if is_fr
                else f"How should I handle the {h['pct']:.0f}% missing values in {h['column']}?",
            )
        )
    if outliers and outliers[0].get("pct", 0) >= 2:
        ranked.append(
            (
                60,
                f"Les valeurs aberrantes de {outliers[0]['column']} sont-elles "
                f"des erreurs ou de vrais extrêmes ?"
                if is_fr
                else f"Are the outliers in {outliers[0]['column']} data errors or genuine extremes?",
            )
        )
    if quality.get("score") is not None and quality["score"] < 90:
        ranked.append(
            (
                50,
                "Que dois-je nettoyer ou corriger avant de modéliser ces données ?"
                if is_fr
                else "What should I clean or fix before modeling this data?",
            )
        )
    if dominance:
        d0 = dominance[0]
        ranked.append(
            (
                46,
                f"La domination de {d0['value']} dans {d0['column']} biaise-t-elle l'analyse ?"
                if is_fr
                else f"Does {d0['value']} dominating {d0['column']} bias the analysis?",
            )
        )

    if is_fr:
        label = f" {domain}" if domain else ""
        ranked.append(
            (40, f"Donne-moi les 3 enseignements majeurs de ce jeu de données{label}.")
        )
    else:
        label = f"{domain} " if domain else ""
        ranked.append((40, f"Give me the 3 biggest takeaways from this {label}dataset."))

    ranked.sort(key=lambda x: x[0], reverse=True)
    out: list[str] = []
    seen: set[str] = set()
    for _, q in ranked:
        if q not in seen:
            seen.add(q)
            out.append(q)
        if len(out) >= 6:
            break
    return out


# ---------------------------------------------------------------------------
# Legacy shim
# ---------------------------------------------------------------------------


def ask_gpt_about_dataframe(df: pd.DataFrame, question: str, api_key: str) -> str:
    """Legacy wrapper — prefer ask_ai()."""
    os.environ.setdefault("OPENAI_API_KEY", api_key)
    try:
        return "".join(ask_ai(df, question, AIProvider.OPENAI, stream=False))
    except Exception as exc:
        logger.exception("AI insights error: %s", exc)
        return f"Error: {exc}"
