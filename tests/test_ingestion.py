"""Tests for engines/ingestion.py."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from engines.ingestion import load_file


def _make_file(name: str, content: bytes) -> MagicMock:
    """Build a minimal mock that mimics a Streamlit UploadedFile."""
    mock = MagicMock()
    mock.name = name
    mock.read.return_value = content
    return mock


def test_load_csv_basic() -> None:
    """A simple CSV loads correctly and returns expected shape + meta."""
    csv_content = b"name,age,city\nAlice,30,NY\nBob,25,LA\n"
    f = _make_file("data.csv", csv_content)
    df, meta = load_file(f)
    assert df.shape == (2, 3)
    assert meta["n_rows"] == 2
    assert meta["n_cols"] == 3
    assert meta["format"] == "CSV"
    assert meta["name"] == "data.csv"


def test_load_json_basic() -> None:
    """A simple JSON loads correctly."""
    import json

    records = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    json_bytes = json.dumps(records).encode()
    f = _make_file("data.json", json_bytes)
    df, meta = load_file(f)
    assert df.shape == (2, 2)
    assert meta["format"] == "JSON"


def test_load_unsupported_format() -> None:
    """Unsupported format raises ValueError."""
    f = _make_file("notes.txt", b"hello world")
    with pytest.raises(ValueError, match="not supported"):
        load_file(f)


def test_load_oversized_file() -> None:
    """File larger than 200 MB raises ValueError."""
    big_content = b"x" * (201 * 1024 * 1024)
    f = _make_file("huge.csv", big_content)
    with pytest.raises(ValueError, match="200 MB"):
        load_file(f)


def test_encoding_detection() -> None:
    """CSV encoded in latin-1 (with non-UTF-8 chars) loads without error."""
    # é is 0xe9 in latin-1, not valid UTF-8 alone
    csv_content = "name,city\nAndr\xe9,Paris\nSoph\xefie,Lyon\n".encode("latin-1")
    f = _make_file("latin.csv", csv_content)
    df, meta = load_file(f)
    assert df.shape[0] == 2
    assert meta["format"] == "CSV"
