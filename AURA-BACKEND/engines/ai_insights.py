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

    GROQ = "groq"
    CLAUDE = "claude"
    OPENAI = "openai"


@dataclass(frozen=True)
class ProviderSpec:
    label: str
    tier: str          # "free" | "paid"
    env_var: str
    model: str
    kind: str          # "openai_compat" | "anthropic"
    base_url: str | None = None


# Single source of truth for provider config. Order = preference (free first).
PROVIDERS: dict[AIProvider, ProviderSpec] = {
    AIProvider.GROQ: ProviderSpec(
        label="Groq · Llama 3.3 70B", tier="free", env_var="GROQ_API_KEY",
        model="llama-3.3-70b-versatile", kind="openai_compat",
        base_url="https://api.groq.com/openai/v1",
    ),
    AIProvider.OPENAI: ProviderSpec(
        label="OpenAI · GPT-4o mini", tier="paid", env_var="OPENAI_API_KEY",
        model="gpt-4o-mini", kind="openai_compat",
    ),
    AIProvider.CLAUDE: ProviderSpec(
        label="Claude · Sonnet 4.6", tier="paid", env_var="ANTHROPIC_API_KEY",
        model="claude-sonnet-4-6", kind="anthropic",
    ),
}

_DEFAULT_ORDER = [AIProvider.GROQ, AIProvider.OPENAI, AIProvider.CLAUDE]


# ---------------------------------------------------------------------------
# Provider resolution
# ---------------------------------------------------------------------------

def is_configured(provider: AIProvider) -> bool:
    """True if the provider's API key is present in the environment."""
    return bool(os.getenv(PROVIDERS[provider].env_var, "").strip())


def available_providers() -> list[dict]:
    """List providers with config status — handy for the frontend / diagnostics."""
    return [
        {"id": p.value, "label": s.label, "tier": s.tier, "configured": is_configured(p)}
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
                logger.info("Provider %s not configured — falling back to %s", requested, p)
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

def _build_system_prompt(df: pd.DataFrame) -> str:
    n_rows, n_cols = df.shape
    cols = ", ".join(map(str, df.columns.tolist()))
    dtypes = ", ".join(f"{c}: {t}" for c, t in df.dtypes.items())
    return (
        f"You are AURA's AI data analyst. The user uploaded a dataset with {n_rows} rows "
        f"and {n_cols} columns. Columns: {cols}. Dtypes: {dtypes}. "
        "Answer concisely and accurately using markdown."
    )


def _truncate_df(df: pd.DataFrame, max_rows: int = 60, max_cols: int = 15) -> pd.DataFrame:
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
            model=spec.model, max_tokens=1024, system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        ) as mgr:
            for text in mgr.text_stream:
                yield text
    else:
        resp = client.messages.create(
            model=spec.model, max_tokens=1024, system=system_prompt,
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
) -> Generator[str, None, None]:
    """Ask a provider about *df* and yield streamed text chunks.

    Resolves to the best configured provider (free first) if the requested one
    has no key. Raises ValueError if none are configured.
    """
    resolved = resolve_provider(provider)
    system_prompt = _build_system_prompt(df)
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
            raw = "".join(_stream_provider(prov, _SUMMARY_SYSTEM, user, stream=False)).strip()
            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.lstrip().startswith("json"):
                    raw = raw.lstrip()[4:]
            s, e = raw.find("{"), raw.rfind("}")
            data = json.loads(raw[s:e + 1])
            return {
                "headline": str(data.get("headline", ""))[:120],
                "summary": str(data.get("summary", "")),
                "findings": [str(f) for f in (data.get("findings") or [])][:5],
                "recommendations": [str(r) for r in (data.get("recommendations") or [])][:4],
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
