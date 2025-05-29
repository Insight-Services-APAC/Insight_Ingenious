"""
Offline “smoke test” for the *CLI* entry-point  `ingen dataprep crawl …`.

Goals
-----
* **Prove wiring** – Does the Typer command group exist?  Does it accept a URL?
* **Run with *zero* network / API dependencies** – we monkey-patch the crawler
  with a stub so the test remains fast and CI-friendly.
* **Exercise the JSON serialisation path** (the flag `--raw` prints the record).

If this test fails the *public* interface of the CLI was broken by a refactor.
"""

from __future__ import annotations

import importlib
from typer.testing import CliRunner


# --------------------------------------------------------------------------
# 1. Tiny stub that looks like the real Crawler but never touches the wire
# --------------------------------------------------------------------------
class _StubCrawler:
    """Drop-in replacement: accepts any **cfg, returns deterministic payload."""

    def __init__(self, **_):  # cfg ignored
        ...

    def scrape(self, url: str):
        return {"url": url, "content": "cli stub"}


# --------------------------------------------------------------------------
# 2. The actual test
# --------------------------------------------------------------------------
def test_cli_crawl_stub(monkeypatch):
    # ── Patch the symbol *before* the CLI module is imported ───────────────
    # ingenious.cli does `from ingenious.dataprep.cli import dataprep …`
    # which in turn imports Crawler.  By patching early we ensure the CLI
    # command ends up using our stub instead of the real HTTP implementation.
    monkeypatch.setattr(
        "ingenious.dataprep.crawl.Crawler",  # dotted path to replace
        _StubCrawler,  # replacement object
        raising=True,  # fail if the target is missing
    )

    # ── Re-import the CLI so it picks up the patched dependency ────────────
    # (importlib.reload() would work too, but plain import is enough inside
    #  pytest’s fresh process.)
    cli = importlib.import_module("ingenious.cli")

    # ── Invoke the Typer app exactly like a user would in the shell ────────
    runner = CliRunner()
    result = runner.invoke(cli.app, ["dataprep", "crawl", "http://x", "--raw"])

    # ── Assertions: exit status + payload sanity ───────────────────────────
    assert result.exit_code == 0, result.output
    assert '"cli stub"' in result.stdout  # the stub’s marker text
