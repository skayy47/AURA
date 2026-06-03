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
