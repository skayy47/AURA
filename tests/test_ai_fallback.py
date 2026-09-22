"""Regression tests for the AI provider fallback chain.

These cover the exact production failure of 2026-09-22: both free providers were
pinned to models their vendors had retired, so every /api/ask returned
"AI model not found". Two independent defects had to line up for that:

1. dead model pins in ``engines/ai_insights.py``;
2. ``routes/ai.py::_is_retriable`` not treating 404 as retriable, so the FIRST
   dead provider killed the whole chain instead of falling through.

Fixing only (1) would leave (2) armed for the next deprecation, so both are
tested here. The pins themselves cannot be asserted against a live API in CI
(no keys), so we assert the *known-dead* ids never come back.
"""

from __future__ import annotations

import pytest

from api.routes.ai import _is_retriable, _clean_error
from engines.ai_insights import PROVIDERS, AIProvider

# Model ids confirmed dead against the live provider APIs on 2026-09-22.
# Groq  : llama-3.3-70b-versatile -> HTTP 404 "model_not_found"
# Google: gemini-2.0-flash        -> HTTP 404 "no longer available"
RETIRED_MODEL_IDS = {
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
}


# The only kwargs chat.completions.create may ever be called with. Anything
# provider-specific travels inside extra_body, which every openai 1.x/2.x
# release merges into the JSON payload. Keeping this list fixed is what makes
# the call shape safe across SDK versions.
ALLOWED_CREATE_KWARGS = {"model", "messages", "stream", "extra_body"}


class _HttpError(Exception):
    """Stand-in for openai.APIStatusError / anthropic.APIStatusError."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code


# --------------------------------------------------------------------------
# Defect 1 — dead model pins
# --------------------------------------------------------------------------


@pytest.mark.parametrize("provider", list(PROVIDERS))
def test_no_provider_pins_a_retired_model(provider: AIProvider) -> None:
    assert PROVIDERS[provider].model not in RETIRED_MODEL_IDS, (
        f"{provider.value} is pinned to {PROVIDERS[provider].model}, which the "
        "provider has retired — it will 404 in production."
    )


def test_every_provider_has_a_model_and_env_var() -> None:
    for provider, spec in PROVIDERS.items():
        assert spec.model, f"{provider.value} has no model pinned"
        assert spec.env_var, f"{provider.value} has no env var"
        assert isinstance(spec.extra_body, dict)


def test_groq_reasoning_model_caps_hidden_reasoning() -> None:
    """gpt-oss-120b spends completion budget on hidden reasoning before it
    emits content. Without a low reasoning_effort a budget-capped caller can
    get empty content back with finish_reason='length' (the MAESTRO bug)."""
    spec = PROVIDERS[AIProvider.GROQ]
    if "gpt-oss" in spec.model:
        assert spec.extra_body.get("reasoning_effort") == "low", (
            f"{spec.model} is a reasoning model; pin reasoning_effort='low' "
            "so short answers are not starved of tokens."
        )


# --------------------------------------------------------------------------
# Defect 2 — 404 must fall through to the next provider
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "exc",
    [
        _HttpError("Error code: 404 - model_not_found", 404),
        _HttpError(
            "404 The model `llama-3.3-70b-versatile` does not exist or you do "
            "not have access to it."
        ),
        _HttpError(
            "This model models/gemini-2.0-flash is no longer available. "
            "Please update your code."
        ),
        _HttpError("NOT_FOUND", 404),
    ],
    ids=["status-404", "groq-body", "google-body", "bare-not-found"],
)
def test_model_not_found_is_retriable(exc: Exception) -> None:
    """The whole point: a dead model must NOT kill the provider chain."""
    assert _is_retriable(exc) is True


@pytest.mark.parametrize(
    "exc",
    [
        _HttpError("429 Too Many Requests", 429),
        _HttpError("RESOURCE_EXHAUSTED: quota exceeded"),
        _HttpError("401 invalid api key", 401),
        _HttpError("403 forbidden", 403),
        _HttpError("503 service unavailable", 503),
        _HttpError("upstream overloaded"),
    ],
)
def test_transient_and_auth_failures_stay_retriable(exc: Exception) -> None:
    assert _is_retriable(exc) is True


@pytest.mark.parametrize(
    "exc",
    [
        TypeError("unsupported operand type(s) for +: 'int' and 'str'"),
        AttributeError("'NoneType' object has no attribute 'shape'"),
        KeyError("cleaned_df"),
    ],
)
def test_local_bugs_are_not_retriable(exc: Exception) -> None:
    """A bug in our own code must surface, not be masked by cycling providers."""
    assert _is_retriable(exc) is False


def test_clean_error_still_maps_404_to_the_user_facing_message() -> None:
    msg = _clean_error(_HttpError("Error code: 404 - model_not_found", 404))
    assert "model not found" in msg.lower()


# --------------------------------------------------------------------------
# The two defects together — the production scenario
# --------------------------------------------------------------------------


def test_dead_first_provider_falls_through_to_the_second() -> None:
    """Simulates the /api/ask chain: provider A 404s, provider B answers.

    Mirrors the loop in routes/ai.py, including the guard that a provider is
    only swapped out BEFORE any token has reached the client.
    """
    chain = ["gemini", "groq"]
    dead = {"gemini"}
    served_by = None
    out = ""

    for attempt in chain:
        out = ""
        emitted = False
        try:
            if attempt in dead:
                raise _HttpError(
                    "Error code: 404 - {'error': {'message': 'The model does "
                    "not exist', 'code': 'model_not_found'}}",
                    404,
                )
            for chunk in ("Revenue ", "is rising ", "12%."):
                out += chunk
                emitted = True
            served_by = attempt
            break
        except Exception as exc:  # noqa: BLE001 - mirrors the route
            if not emitted and _is_retriable(exc) and attempt != chain[-1]:
                continue
            out = _clean_error(exc)
            break

    assert served_by == "groq", "chain did not fall through to the live provider"
    assert out == "Revenue is rising 12%."
    assert "not found" not in out.lower()


def test_midstream_failure_does_not_splice_two_answers() -> None:
    """Once tokens are out, a provider swap would concatenate two answers."""
    chain = ["gemini", "groq"]
    out = ""
    for attempt in chain:
        out = ""
        emitted = False
        try:
            if attempt == "gemini":
                out += "Revenue is ri"
                emitted = True
                raise _HttpError("503 connection reset", 503)
            out += "SECOND ANSWER"
            break
        except Exception as exc:  # noqa: BLE001
            if not emitted and _is_retriable(exc) and attempt != chain[-1]:
                continue
            out = _clean_error(exc)
            break

    assert "SECOND ANSWER" not in out


# --------------------------------------------------------------------------
# Defect 3 — provider-specific fields must not be passed as SDK kwargs
# --------------------------------------------------------------------------
#
# Caught before it reached users, but only just: the first cut of this fix sent
# reasoning_effort as a kwarg. That works on openai 2.x (the dev machine) and
# raises TypeError on openai==1.35.0 (requirements.txt / the Docker image),
# which has no **kwargs on chat.completions.create. A TypeError is NOT
# retriable by design, so it would have killed the provider chain in production
# while every local test stayed green. This test pins the call shape against
# whichever SDK version is actually installed.


def test_openai_compat_call_uses_only_params_the_installed_sdk_accepts() -> None:
    import inspect
    from types import SimpleNamespace

    from openai.resources.chat.completions import Completions

    import engines.ai_insights as ai

    sig = inspect.signature(Completions.create)
    accepts_var_kwargs = any(p.kind is p.VAR_KEYWORD for p in sig.parameters.values())
    captured: dict = {}

    class _FakeCompletions:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))]
            )

    class _FakeClient:
        def __init__(self, *a, **k):
            self.chat = SimpleNamespace(completions=_FakeCompletions())

    import openai

    original = openai.OpenAI
    openai.OpenAI = _FakeClient
    try:
        for provider, spec in PROVIDERS.items():
            if spec.kind != "openai_compat":
                continue
            captured.clear()
            list(ai._stream_openai_compat(spec, "sys", "usr", stream=False))

            # (a) Version-INDEPENDENT: the call may only ever use this fixed
            #     set of kwargs. This is the assertion that actually catches
            #     the bug on a dev machine whose SDK happens to be new enough
            #     to accept the kwarg, which is precisely how it slipped past
            #     a green local test run the first time.
            assert set(captured) <= ALLOWED_CREATE_KWARGS, (
                f"{provider.value} passes "
                f"{sorted(set(captured) - ALLOWED_CREATE_KWARGS)} as kwargs to "
                "chat.completions.create. Provider-specific fields must go in "
                "extra_body, or they break on older pinned SDKs."
            )

            # (b) Version-DEPENDENT: also reject anything the SDK that is
            #     actually installed would refuse.
            unknown = set(captured) - set(sig.parameters)
            assert accepts_var_kwargs or not unknown, (
                f"{provider.value} passes {sorted(unknown)} as kwargs, which "
                f"openai=={openai.__version__} rejects with TypeError. "
                "Provider-specific fields belong in extra_body."
            )

            # (c) Whatever the provider declares must actually be delivered.
            if spec.extra_body:
                assert captured.get("extra_body") == spec.extra_body, (
                    f"{provider.value}: extra_body {spec.extra_body} was not "
                    f"sent (got {captured.get('extra_body')!r})"
                )
    finally:
        openai.OpenAI = original


def test_pinned_sdk_version_still_accepts_the_call_shape() -> None:
    """Guard the assumption that ALLOWED_CREATE_KWARGS is safe on the SDK
    version requirements.txt actually pins (which is what ships in Docker),
    not merely on whatever happens to be installed here."""
    import re
    from pathlib import Path

    req = Path(__file__).resolve().parents[1] / "AURA-BACKEND" / "requirements.txt"
    pin = re.search(r"^openai==(\S+)", req.read_text(encoding="utf-8"), re.M)
    assert pin, "openai is no longer pinned in requirements.txt"

    # extra_body has existed on every openai 1.x/2.x release; a major bump
    # beyond that needs this call shape re-verified against the new SDK.
    major = int(pin.group(1).split(".")[0])
    assert major in (1, 2), (
        f"openai is pinned to {pin.group(1)}; re-verify that "
        f"{sorted(ALLOWED_CREATE_KWARGS)} is still the correct call shape."
    )


def test_reasoning_effort_value_is_valid() -> None:
    for provider, spec in PROVIDERS.items():
        effort = spec.extra_body.get("reasoning_effort")
        assert effort is None or effort in {
            "none",
            "low",
            "medium",
            "high",
        }, f"{provider.value} has an invalid reasoning_effort: {effort!r}"
