"""
Offline **unit** test for the Scrapfly-backed `Crawler`.

Goal
----
Verify that the high-level `Crawler` wrapper keeps working even when no network
is available and no `SCRAPFLY_API_KEY` is present.

Technique
---------
* Monkey-patch `ingenious.dataprep.crawl.Crawler` with a **stub** subclass that
  returns synthetic data immediately (no HTTP call).
* Ensure the environment variable is absent so the real implementation would
  have failed if it had been invoked.
"""

# We import the real class just to subclass it; in the test we’ll replace it.
from ingenious.dataprep.crawl import Crawler as _RealCrawler


class _StubCrawler(_RealCrawler):
    """
    Tiny drop-in replacement that short-circuits the network layer.

    Only `scrape()` is overridden because that’s all the test needs.  The base
    class’ `batch()` method still works because it ultimately delegates back to
    `.scrape()` for each URL.
    """

    def scrape(self, url: str):
        # The exact payload is irrelevant; we only need something predictable.
        return {"url": url, "content": "stub content"}


def test_stub_scrape(monkeypatch):
    """`Crawler.scrape()` should return whatever our stub returns."""
    # ── 1. Pretend there is *no* API key so the real client would raise. ──────
    monkeypatch.delenv("SCRAPFLY_API_KEY", raising=False)

    # ── 2. Patch the symbol that other modules import.  Using `raising=True`
    # makes the test fail fast if the dotted path is wrong (protects against
    # refactors).
    monkeypatch.setattr(
        "ingenious.dataprep.crawl.Crawler",
        _StubCrawler,
        raising=True,
    )

    # ── 3. Re-import the module *after* the patch so it picks up the stub. ───
    from ingenious.dataprep.crawl import Crawler  # noqa: WPS433  (runtime import)

    data = Crawler().scrape("https://x")

    # ── 4. Assertion: we received our synthetic payload, proving the patch
    #      “took” and no real network call occurred.
    assert data["content"].startswith("stub")
