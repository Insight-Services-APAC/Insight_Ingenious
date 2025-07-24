"""
Network‑failure paths: the CLI should exit cleanly when the OpenAI
embedding client raises transport‑level exceptions (timeout, DNS, 5xx).
The test must cope with constructor signatures that vary between
OpenAI‑python versions.
"""
from __future__ import annotations

import importlib
import inspect
from typing import Any, Dict

from unittest.mock import patch, MagicMock
import pytest
from typer.testing import CliRunner

from ingenious.chunk.cli import cli

# ---------------------------------------------------------------------------#
# Helper – build a dummy instance even when __init__ has exotic signature   #
# ---------------------------------------------------------------------------#
def _instantiate(exc_cls: type[BaseException]) -> BaseException:  # noqa: D401
    """
    Attempt to build *some* instance of ``exc_cls`` without knowing its
    exact signature.  We progressively try:

    1. Positional "simulated"
    2. Common keyword args
    3. Signature‑introspection fall‑back (fill every required param with None)
    4. ``__new__`` bypass (last resort – rarely needed)
    """
    # 1️⃣ single positional
    try:
        return exc_cls("simulated")
    except Exception:
        pass

    # 2️⃣ common kwargs seen in OpenAI error types
    try:
        return exc_cls(message="simulated", request=None)  # type: ignore[arg-type]
    except Exception:
        pass

    # 3️⃣ introspect signature → supply None for every required param
    try:
        sig = inspect.signature(exc_cls)
        kwargs: Dict[str, Any] = {
            name: None
            for name, p in sig.parameters.items()
            if p.default is inspect._empty and p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)
        }
        return exc_cls(**kwargs)  # type: ignore[arg-type]
    except Exception:
        pass

    # 4️⃣ bypass __init__ entirely
    return exc_cls.__new__(exc_cls)  # type: ignore[call-arg]


# ---------------------------------------------------------------------------#
# Parameterisation over available OpenAI exception classes                   #
# ---------------------------------------------------------------------------#
openai_mod = importlib.import_module("openai")
EXC_NAMES = ["APITimeoutError", "APIConnectionError", "ServiceUnavailableError"]
EXC_TYPES = [getattr(openai_mod, n, RuntimeError) for n in EXC_NAMES]


@pytest.mark.parametrize("exc_type", EXC_TYPES)
@patch("ingenious.chunk.strategy.langchain_semantic.OpenAIEmbeddings")
def test_cli_network_failures(mock_embed, exc_type, sample_text, tmp_path):
    """
    Mock embedder so that `.embed_documents` raises *exc_type*; the CLI
    must exit with code 1 and print the coloured ❌ prefix.
    """
    stub = MagicMock()
    stub.embed_documents.side_effect = _instantiate(exc_type)
    mock_embed.return_value = stub

    res = CliRunner().invoke(
        cli,
        [
            "run",
            str(sample_text),
            "--strategy",
            "semantic",
            "--chunk-size",
            "64",
            "--chunk-overlap",
            "8",
            "--output",
            str(tmp_path / "out.jsonl"),
        ],
    )

    assert res.exit_code == 1
    assert "❌" in res.output
