"""AI insights engine — supports Claude (Anthropic) and GPT-4o-mini (OpenAI)."""
from __future__ import annotations

import os
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


class AIProvider(Enum):
    """Supported AI providers."""

    CLAUDE = "claude"
    OPENAI = "openai"


def _build_system_prompt(df: pd.DataFrame) -> str:
    """Build a rich system prompt describing the dataset."""
    n_rows, n_cols = df.shape
    cols = ", ".join(df.columns.tolist())
    dtypes = ", ".join(f"{c}: {t}" for c, t in df.dtypes.items())
    return (
        f"You are AURA's AI analyst. The user uploaded a dataset with {n_rows} rows "
        f"and {n_cols} columns. Column names: {cols}. Dtypes: {dtypes}. "
        "Answer concisely. Use markdown formatting."
    )


def _truncate_df(df: pd.DataFrame, max_rows: int = 60, max_cols: int = 15) -> pd.DataFrame:
    """Limit df to max_rows × max_cols to stay within token budgets."""
    return df.iloc[:max_rows, :max_cols]


def ask_ai(
    df: pd.DataFrame,
    question: str,
    provider: AIProvider,
    stream: bool = True,
) -> Generator[str, None, None]:
    """
    Ask an AI provider about *df* and yield streamed text chunks.

    Raises:
        ValueError: if the required API key is not set.
    """
    system_prompt = _build_system_prompt(df)
    sample = _truncate_df(df).to_string()
    user_message = f"Dataset sample:\n\n{sample}\n\nQuestion: {question}"

    if provider == AIProvider.CLAUDE:
        yield from _ask_claude(system_prompt, user_message, stream)
    elif provider == AIProvider.OPENAI:
        yield from _ask_openai(system_prompt, user_message, stream)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def executive_summary(payload: dict, provider: AIProvider = AIProvider.CLAUDE) -> dict:
    """Generate a structured executive summary from a compact stats *payload*.

    Sends ONLY aggregated stats (never raw rows) → cheap, safe, fast.
    Returns {headline, summary, findings[], recommendations[]}.
    Falls back to a deterministic summary if no API key or on any failure.
    """
    import json

    system = (
        "You are a senior data analyst writing the executive summary of a Data "
        "Intelligence Report. You receive aggregated statistics about a dataset "
        "(never raw rows). Write for a business decision-maker: precise, confident, "
        "no fluff. Respond ONLY with minified JSON, no markdown, in this exact shape: "
        '{"headline": "<=10 words", "summary": "2-3 sentences", '
        '"findings": ["3-5 short bullet strings"], '
        '"recommendations": ["2-4 short action bullets"]}'
    )
    user = f"Dataset statistics:\n{json.dumps(payload, default=str)}"

    # Try providers in order (preferred first), self-healing if one is out of
    # credit / unconfigured. Only fall back to deterministic if ALL fail.
    order: list[AIProvider] = (
        [AIProvider.OPENAI, AIProvider.CLAUDE]
        if provider == AIProvider.OPENAI
        else [AIProvider.CLAUDE, AIProvider.OPENAI]
    )
    last_exc: Exception | None = None
    for prov in order:
        if prov == AIProvider.CLAUDE and not os.getenv("ANTHROPIC_API_KEY"):
            continue
        if prov == AIProvider.OPENAI and not os.getenv("OPENAI_API_KEY"):
            continue
        try:
            if prov == AIProvider.CLAUDE:
                raw = "".join(_ask_claude(system, user, stream=False))
            else:
                raw = "".join(_ask_openai(system, user, stream=False))
            raw = raw.strip()
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
                "by_ai": True,
            }
        except Exception as exc:
            last_exc = exc
            logger.warning("Exec summary via %s failed: %s", prov.value, exc)

    logger.warning("Executive summary fell back to deterministic (last: %s)", last_exc)
    return _deterministic_summary(payload)


def _deterministic_summary(payload: dict) -> dict:
    """Build a respectable summary from the payload without an LLM."""
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
        "by_ai": False,
    }


def _ask_claude(
    system_prompt: str, user_message: str, stream: bool
) -> Generator[str, None, None]:
    """Stream a response from Claude Sonnet 4.6."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY is not set.\n"
            "Add it to your .env file:\n  ANTHROPIC_API_KEY=sk-ant-..."
        )

    import anthropic

    client = anthropic.Anthropic(api_key=api_key)

    if stream:
        with client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        ) as stream_mgr:
            for text in stream_mgr.text_stream:
                yield text
    else:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        yield response.content[0].text  # type: ignore[index]


def _ask_openai(
    system_prompt: str, user_message: str, stream: bool
) -> Generator[str, None, None]:
    """Stream a response from GPT-4o-mini."""
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not set.\n"
            "Add it to your .env file:\n  OPENAI_API_KEY=sk-..."
        )

    from openai import OpenAI

    client = OpenAI(api_key=api_key)

    if stream:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            stream=True,
        )
        for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    else:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        yield response.choices[0].message.content or ""


# ---------------------------------------------------------------------------
# Legacy shim — kept so old callers don't break
# ---------------------------------------------------------------------------


def ask_gpt_about_dataframe(
    df: pd.DataFrame,
    question: str,
    api_key: str,
) -> str:
    """Legacy wrapper — prefer ask_ai() for new code."""
    os.environ.setdefault("OPENAI_API_KEY", api_key)
    try:
        return "".join(ask_ai(df, question, AIProvider.OPENAI, stream=False))
    except Exception as exc:
        logger.exception("AI insights error: %s", exc)
        return f"Error: {exc}"
