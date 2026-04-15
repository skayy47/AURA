from __future__ import annotations

import os
from dotenv import load_dotenv


# Load the environment from .env file
load_dotenv()


def is_debug_mode() -> bool:
    """
    Return True if DEBUG=1 (or "true") in the .env file.
    """
    return os.getenv("DEBUG", "0").lower() in {"1", "true", "yes"}


def get_poppler_path() -> str:
    """
    Return the POPPLER_PATH value from the .env file.
    """
    return os.getenv("POPPLER_PATH", "") or ""


def get_openai_key() -> str:
    """
    Optional: return stored OpenAI API key.
    """
    return os.getenv("OPENAI_API_KEY", "") or ""
