"""
Pure unit-test for **ingenious.dataprep.crawl.crawler.Crawler**

This file exercises the public API (`scrape`, `batch`) without touching the
network:

* We _do_ instantiate the real `Crawler` (so its logic is covered).
* We _replace_ the module-level helper `fetch_pages` with an in-process fake
  so no HTTP or API-key lookup occurs.
"""

from ingenious.dataprep.crawl import Crawler


# ---------------------------------------------------------------------------
# scrape()  – should delegate to fetch_pages with *one* URL
# ---------------------------------------------------------------------------
def test_scrape_calls_fetch_pages(monkeypatch):
    captured: dict[str, object] = {}  # records args for later assertions

    def _fake_fetch_pages(urls, **cfg):
        """
        Stand-in replacement for the real HTTP helper.

        * Saves the incoming parameters so the test can inspect them.
        * Returns a synthetic page payload so the caller can proceed.
        """
        captured["urls"] = urls
        captured["cfg"] = cfg
        return [{"url": urls[0], "content": "fake content"}]

    # Monkey-patch **exactly** the symbol the wrapper imports.
    monkeypatch.setattr(
        "ingenious.dataprep.crawl.crawler.fetch_pages",  # dotted path
        _fake_fetch_pages,
    )

    crawler = Crawler(foo="bar")  # any kwargs should be forwarded
    result = crawler.scrape("http://example.com")

    # ── Expectations -------------------------------------------------------
    assert result == {"url": "http://example.com", "content": "fake content"}
    assert captured["urls"] == ["http://example.com"]  # 1-element list
    assert captured["cfg"] == {"foo": "bar"}  # cfg forwarded


# ---------------------------------------------------------------------------
# batch()  – should call fetch_pages once with the *full* URL list
# ---------------------------------------------------------------------------
def test_batch_calls_fetch_pages(monkeypatch):
    call_count = {"n": 0}

    def _fake_fetch_pages(urls, **_):
        """
        A lighter stub: we only care that it gets called once with the right
        list; return value can be anything consistent.
        """
        call_count["n"] += 1
        return [{"url": u, "content": "batch"} for u in urls]

    monkeypatch.setattr(
        "ingenious.dataprep.crawl.crawler.fetch_pages",
        _fake_fetch_pages,
    )

    urls = ["http://a.com", "http://b.com"]
    crawler = Crawler()
    pages = crawler.batch(urls)

    # ── Expectations -------------------------------------------------------
    assert call_count["n"] == 1  # exactly one call
    assert [p["url"] for p in pages] == urls  # order preserved
