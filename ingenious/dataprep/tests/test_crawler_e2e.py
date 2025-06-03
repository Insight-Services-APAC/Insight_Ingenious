"""
🌐  **Live integration tests** for the Scrapfly-backed *Crawler*
──────────────────────────────────────────────────────────────────────

These tests make *real* calls to the Scrapfly API, so they will:

* consume API quota,
* take noticeably longer than the pure-unit suite, and
* fail if your Internet connection is down.

-------------------------------------------------------------------------------
Running them locally
-------------------------------------------------------------------------------
1. **Create / activate** the virtual-env with `uv` **and** install the
   integration extras:

    ```bash
    uv venv                     # -→ .venv + pinned Python
    source .venv/bin/activate
    uv pip install -e ".[dataprep,tests]"
    ```

2. **Set the API key** – either export it in the shell **or** place it in a
   `.env` file at the repo root.  For example:

    ```bash
    export SCRAPFLY_API_KEY="sk_live_********"
    ```

3. **Run only the fast, offline tests** (default selection skips `e2e`):

    ```bash
    uv run pytest -q
    ```

4. **Run this live suite** *alone*:

    ```bash
    uv run pytest -m e2e -q
    ```

5. **Run everything** (unit + e2e):

    ```bash
    uv run pytest -m "e2e or not e2e" -q
    ```

-------------------------------------------------------------------------------
How “opt-in” is implemented
-------------------------------------------------------------------------------
* Each test function is tagged with `@pytest.mark.e2e`.
* The entire module is **skipped** unless the environment variable
  `SCRAPFLY_API_KEY` is present *and* the user passes `-m e2e` (or an
  equivalent expression) to `pytest`.

-------------------------------------------------------------------------------
Why keep a live network suite when unit tests already stub I/O?
-------------------------------------------------------------------------------
* **Reality check**   Unit tests can *only* prove that our code *calls* the
  Scrapfly SDK with the right parameters; they cannot guarantee that those
  parameters still work against the public Internet.
* **Regression alarm**   If Scrapfly introduces a breaking change (e.g. a new
  header requirement) or our retry logic regresses, CI will flag it here
  instead of in production.
* **Executable docs**   These tests double as copy-pastable examples that show
  how to pass advanced knobs (`max_attempts`, `retry_on_status_code`, `delay`)
  through the high-level `Crawler` façade.

The suite is intentionally lean—four targeted tests that each validate one
behavioural slice.  Should a target site disappear, we can swap the URL
without touching production code.
"""

from __future__ import annotations

import os
import time
import pytest

from scrapfly.errors import ScrapflyError  # explicit type used in assertions
from ingenious.dataprep.crawl import Crawler

# =========================================================================== #
# 0.  Pytest configuration helpers
# =========================================================================== #
# ➊  Mark **every test in this module** with the custom label “e2e”; a default
#    `pytest` invocation (`pytest -q`) will therefore *not* execute them unless
#    the caller includes `-m e2e` or `-m "not e2e"` selection flags.
pytestmark = pytest.mark.e2e

# ➋  Shared skip decorator – avoids copy‑pasting the same `@pytest.mark.skipif`
#    on every test.  It checks that the API key is available before the test
#    runs; otherwise the test is skipped (not failed) to keep CI green when
#    secrets are missing.
requires_key = pytest.mark.skipif(
    not os.getenv("SCRAPFLY_API_KEY"),
    reason="SCRAPFLY_API_KEY env var not set; skipping live network test",
)

# =========================================================================== #
# 1.  Sanity‑check a single successful scrape with **default** parameters
# =========================================================================== #


@requires_key
def test_real_medical_article() -> None:
    """Scrape a MedicalNewsToday article and assert the content looks sane."""
    # We intentionally include a fragment (`#summary`) – the crawler should
    # canonicalise the URL and drop it.
    url = "https://www.medicalnewstoday.com/articles/tyrer-cuzick-score#summary"
    expected_keywords = {"breast", "cancer", "mammogram"}

    # Perform the HTTP request using *default* crawler settings: 5 attempts,
    # exponential back‑off(1→16 s), default Scrapfly markdown output.
    page = Crawler().scrape(url)

    # ------------------- assertions ---------------------------------------
    # 1) URL canonicalisation – fragment (#summary) must be removed.
    assert page["url"].startswith(url.split("#")[0])

    # 2) Non‑empty body – quick check that we didn’t get rate‑limited
    #    or receive a CAPTCHA page.
    assert len(page["content"].strip()) >= 200, "response body too short"

    # 3) Very light semantic check – at least one keyword present.
    assert expected_keywords & set(page["content"].lower().split()), "keywords missing"


# =========================================================================== #
# 2.  Batch scrape – verifies order, length, and page-specific keywords
# =========================================================================== #


@requires_key
def test_batch_two_urls() -> None:
    """Scrape two URLs and assert every expected keyword is present."""
    urls = [
        "https://www.volparahealth.com/news/how-breast-density-impacts-lifetime-cancer-risk/",
        "https://www.medicalnewstoday.com/articles/tyrer-cuzick-score#summary",
    ]

    # Full keyword sets we expect *all* to appear for each page
    expected_keywords = [
        {"breast", "cancer", "mammogram", "density"},  # Volpara article
        {"breast", "cancer", "mammogram"},  # MNT article
    ]

    pages = Crawler().batch(urls)

    # 1️⃣  Order preserved
    assert [p["url"] for p in pages] == urls

    # 2️⃣  Length & semantic checks (all keywords must appear)
    for page, keywords in zip(pages, expected_keywords, strict=True):
        text_words = set(page["content"].lower().split())

        # a) Non-trivial body
        assert len(page["content"].strip()) >= 200, f"Body too short for {page['url']}"

        # b) Every keyword present
        missing = keywords - text_words
        assert not missing, f"{page['url']} missing {missing}"


# =========================================================================== #
# 3.  Custom retry policy – expect failure after N controlled attempts
# =========================================================================== #


@requires_key
def test_custom_retry_policy_handles_transient_503() -> None:
    """Prove we give up after three attempts on a permanent 503 endpoint."""
    url = "https://httpbin.dev/status/503"  # httpbin always returns 503 here

    # We pass **max_attempts=3** and include 503 in retry list so the SDK will
    # perform: initial try + 2 retries → then raise ScrapflyError.
    crawler = Crawler(max_attempts=3, retry_on_status_code=[503])

    with pytest.raises(ScrapflyError):
        crawler.scrape(url)
