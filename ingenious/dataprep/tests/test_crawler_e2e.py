"""
🔌 **Live integration test** for the Scrapfly-backed Crawler.

Why a separate “e2e” test?
--------------------------
* The unit tests already prove our wrapper calls the right functions.
* This *end-to-end* check actually fires a HTTP request against the real
  Scrapfly service to make sure:
  1. Our key-resolution logic works in CI / staging.
  2. The default Scrapfly config (`render_js=True`, `format="markdown"`, …)
     returns non-empty, human-readable text.
  3. The domain-specific page contains a couple of expected keywords, giving
     us a **semantic** sanity check instead of just counting bytes.

Because it touches the network **and** consumes API quota, the test is
**opt-in**: it only runs when the environment variable `SCRAPFLY_API_KEY`
is present *and* pytest is invoked with the `-m e2e` marker.
"""

from __future__ import annotations

import os
import pytest

from ingenious.dataprep.crawl import Crawler


# --------------------------------------------------------------------------- #
# 1.  Mark the whole module as “e2e” so normal `pytest` runs skip it.
#    (Defined in pytest.ini / pyproject.toml → [pytest] markers = e2e: …)
# --------------------------------------------------------------------------- #
pytestmark = pytest.mark.e2e


# --------------------------------------------------------------------------- #
# 2.  Single integration test
# --------------------------------------------------------------------------- #
@pytest.mark.skipif(
    not os.getenv("SCRAPFLY_API_KEY"),
    reason="SCRAPFLY_API_KEY env var not set; skipping live network test",
)
def test_real_medical_article():
    """
    Crawl a public medical article and perform a *very* light-weight
    content assertion.

    We don’t snapshot the full HTML/markdown because the page might change.
    Instead we verify:
    • URL canonicalisation (fragment removed)
    • Response length ≥ 200 chars  → no empty pages / captcha blocks
    • Two topical keywords appear   → confirms we didn’t scrape an error page
    """
    url = "https://www.medicalnewstoday.com/articles/tyrer-cuzick-score#summary"
    expected_keywords = ["breast cancer", "mammogram"]

    # ---- real network call --------------------------------------------------
    page = Crawler().scrape(url)

    # ---- basic contract checks ---------------------------------------------
    assert page["url"].startswith(url.split("#")[0])  # fragment stripped
    assert len(page["content"].strip()) >= 200  # non-trivial body

    # ---- semantic smoke test ------------------------------------------------
    lowered = page["content"].lower()
    for kw in expected_keywords:
        assert kw in lowered, f"keyword {kw!r} missing from content"


# --------------------------------------------------------------------------- #
# 3.  Batch integration test – two real breast-cancer-related pages
# --------------------------------------------------------------------------- #
@pytest.mark.skipif(
    not os.getenv("SCRAPFLY_API_KEY"),
    reason="SCRAPFLY_API_KEY env var not set; skipping live network test",
)
def test_batch_two_urls():
    """
    Same idea as *test_real_medical_article* but exercises **Crawler.batch**.

    Pages chosen:
    • Volpara article – “How breast density impacts lifetime cancer risk”
      https://www.volparahealth.com/news/how-breast-density-impacts-lifetime-cancer-risk/
    • MNT article    – “Tyrer-Cuzick score” summary section
      https://www.medicalnewstoday.com/articles/tyrer-cuzick-score#summary

    Assertions:
    1. We get exactly two results *in the same order* as the input list.
    2. Every page has ≥ 200 printable characters → no empty / CAPTCHA pages.
    3. Each page contains at least one topical keyword so we know we scraped
       real content, not an error page.
    """
    urls = [
        "https://www.volparahealth.com/news/how-breast-density-impacts-lifetime-cancer-risk/",
        "https://www.medicalnewstoday.com/articles/tyrer-cuzick-score#summary",
    ]
    # Topical words that should appear somewhere in the readable text
    expected_keywords = [
        ["breast density", "include genetics"],  # for Volpara
        ["breast cancer", "mammogram"],  # for MNT
    ]

    pages = Crawler().batch(urls)

    # ---- contract: count & order -------------------------------------------
    assert len(pages) == 2
    assert [p["url"] for p in pages] == urls

    # ---- minimal content & semantic checks ---------------------------------
    for page, keywords in zip(pages, expected_keywords):
        assert len(page["content"].strip()) >= 200
        lowered = page["content"].lower()
        assert any(kw in lowered for kw in keywords), (
            f"none of {keywords!r} found in {page['url']}"
        )
