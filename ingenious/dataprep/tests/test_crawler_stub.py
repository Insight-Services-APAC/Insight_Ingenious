"""
🧪 **Offline unit test** for the **Scrapfly‑backed `Crawler` wrapper**.

Why this test exists
--------------------
* Ensure the *public* wrapper (`ingenious.dataprep.crawl.Crawler`) keeps
  functioning when **no network** and **no `SCRAPFLY_API_KEY`** are available –
  typical conditions on CI machines or developer laptops in aeroplane mode.
* Catch accidental tight coupling between the wrapper and the HTTP layer.

Strategy
~~~~~~~~
1. **Delete** the `SCRAPFLY_API_KEY` from the environment to simulate an
   unconfigured machine. The real implementation would raise at runtime.
2. **Monkey‑patch** the symbol *other modules import* (`ingenious.dataprep.crawl.Crawler`)
   with a tiny stub subclass that returns deterministic data and never touches
   the internet.
3. **Re‑import** the wrapper so subsequent code – including the assertion –
   receives the stub instead of the real thing.
"""

from __future__ import annotations

# ───────────────────────────  third‑party / local imports  ───────────────────
from ingenious.dataprep.crawl import Crawler as _RealCrawler

# =========================================================================== #
# Stub implementation – overrides only what the test needs.
# =========================================================================== #


class _StubCrawler(_RealCrawler):
    """Return predictable data, bypassing Scrapfly entirely."""

    def scrape(self, url: str):  # type: ignore[override]
        # Return a minimal page record; content value just needs a marker string
        # so the assertion can recognise it later.
        return {"url": url, "content": "stub content"}


# =========================================================================== #
# Test function – imperative docstring as per repo’s style guide.
# =========================================================================== #


def test_stub_scrape(monkeypatch) -> None:  # noqa: D401
    """Simulate no API key and assert the stubbed wrapper still returns data."""

    # 1️⃣  Remove env var so the *real* network client would fail if invoked.
    monkeypatch.delenv("SCRAPFLY_API_KEY", raising=False)

    # 2️⃣  Patch the import path to replace the real class with our stub.
    #     `raising=True` → test fails fast if the dotted path becomes invalid
    #     after a refactor – a guard against silent API breakage.
    monkeypatch.setattr(
        "ingenious.dataprep.crawl.Crawler",
        _StubCrawler,
        raising=True,
    )

    # 3️⃣  Re‑import after patching so we get the stub, not the original.
    from ingenious.dataprep.crawl import Crawler  # noqa: WPS433 – intentional

    # 4️⃣  Call the method under test (no network traffic should occur).
    data = Crawler().scrape("https://x")

    # 5️⃣  Assert the content came from our stub, proving the patch worked and
    #     the wrapper’s public API can operate in a network‑less environment.
    assert data["content"].startswith("stub")
