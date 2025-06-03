"""
Provider adapter for Insight Ingenious dataprep that uses the Scrapfly SDK.

This module centralizes all HTTP/fetch logic:
1. **Single responsibility** – All network‐touching code lives here.
2. **Testability** – Unit tests can stub `fetch_pages` to avoid real HTTP.
3. **Replaceability** – Swap out Scrapfly by editing only this file.

Public contract
---------------
    fetch_pages(urls, …) → List[{"url": str, "content": str}]

Raises early if:
* SCRAPFLY_API_KEY is missing
* Scrapfly returns a non‐200 status on the final attempt
* The response body is empty (often a blocked JS site or CAPTCHA)
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import List, Optional, Sequence, TypedDict

from dotenv import find_dotenv, load_dotenv
from scrapfly import ScrapflyClient, ScrapeConfig
from scrapfly.errors import ScrapflyError as ScrapflyException

log = logging.getLogger(__name__)

# =========================================================================== #
# 1. Resolve environment variables from an optional .env file (dev-only).
#    • Production injects SCRAPFLY_API_KEY via CI secrets.
#    • Local devs can keep credentials in a .env file.
# =========================================================================== #

_ENV_LOADED = load_dotenv(find_dotenv(usecwd=True), override=False)
if _ENV_LOADED:
    log.debug(".env file loaded for Scrapfly key")

# =========================================================================== #
# 2. Default per-request Scrapfly options – safe, broadly useful defaults.
#    Callers may override via `extra_scrapfly_cfg`.
# =========================================================================== #

DEFAULT_CONFIG: dict[str, object] = {
    "render_js": True,  # Use a headless browser (required for SPAs)
    "asp": True,  # Enable Scrapfly anti-scraping bypass
    "format": "markdown",  # Easier to chunk / embed than raw HTML
}

# =========================================================================== #
# 3. Retry policy – values chosen to cover **transient** failures only.
# =========================================================================== #

DEFAULT_RETRY_CODES: tuple[int, ...] = (408, 429, 500, 502, 503, 504)
DEFAULT_MAX_ATTEMPTS = 5  # 1 initial try + 4 retries (total back-off ≈ 31s)
DEFAULT_INITIAL_DELAY = 1  # seconds – first back-off step

# =========================================================================== #
# 4. Typed helper for the public payload – stricter than plain dict[str, str].
# =========================================================================== #


class Page(TypedDict):
    url: str
    content: str


# =========================================================================== #
# 5. ScrapflyClient factory – cached so tight loops reuse connections.
# =========================================================================== #


@lru_cache(maxsize=1)
def _client(api_key: str) -> ScrapflyClient:  # pragma: no cover
    """Return a singleton ScrapflyClient for the given API key."""
    return ScrapflyClient(key=api_key)


# =========================================================================== #
# 6. Main helper that callers import.
# =========================================================================== #


def fetch_pages(
    urls: List[str],
    *,
    api_key: str | None = None,
    extra_scrapfly_cfg: Optional[dict] = None,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    retry_on_status_code: Optional[Sequence[int]] = None,
    delay: int = DEFAULT_INITIAL_DELAY,
) -> List[Page]:
    """
    Fetch each URL and return their readable content.

    Parameters
    ----------
    urls
        One or many absolute URLs to scrape.
    api_key
        Explicit Scrapfly API key.  If omitted, falls back to the
        SCRAPFLY_API_KEY environment variable (or loaded from .env).
    extra_scrapfly_cfg
        Dict merged over DEFAULT_CONFIG to tweak per-request options,
        e.g. {"render_js": False, "country": "us"}.
    max_attempts
        Total tries (initial + retries) for each URL.  Passed to `tries=`.
    retry_on_status_code
        Iterable of upstream HTTP status codes (e.g., 403, 520) that warrant
        retry in addition to the DEFAULT_RETRY_CODES set.
    delay
        Initial back-off delay (in seconds).  Scrapfly doubles this on each retry:
        delay, delay*2, delay*4, …

    Returns
    -------
    List[Page]
        A list of Page dicts, in the same order as the input URLs.

    Raises
    ------
    RuntimeError
        - SCRAPFLY_API_KEY missing
        - Scrapfly returned non-200 on final attempt
        - Response body empty (often blocked or CAPTCHA page)
    ScrapflyError
        Any lower-level SDK/network error; caller may catch and retry here.
    """
    # ── 6.1 Resolve credentials – fail early if missing ────────────────────
    api_key = api_key or os.getenv("SCRAPFLY_API_KEY")
    if not api_key:
        raise RuntimeError("SCRAPFLY_API_KEY not set (env var or .env)")
    client = _client(api_key)

    # ── 6.2 Merge per-request options and derive retry codes ───────────────
    cfg = {**DEFAULT_CONFIG, **(extra_scrapfly_cfg or {})}
    retry_codes = (
        tuple(retry_on_status_code) if retry_on_status_code else DEFAULT_RETRY_CODES
    )

    # ── 6.3 Iterate and scrape each URL ───────────────────────────────────
    pages: List[Page] = []
    for url in urls:
        try:
            response = client.resilient_scrape(
                scrape_config=ScrapeConfig(url=url, **cfg),
                tries=max_attempts,
                retry_on_status_code=retry_codes,
                delay=delay,
            )
        except ScrapflyException as exc:
            # Log and re-raise so callers can decide whether to retry at a higher level
            log.debug("Scrapfly exception for %s: %s", url, exc)
            raise

        # ── 6.4 Post-flight sanity checks – catch edge cases early ──────────
        if response.status_code != 200:
            raise RuntimeError(f"Scrapfly HTTP {response.status_code} for {url}")
        if not response.content.strip():
            raise RuntimeError(f"Empty body for {url}")

        pages.append({"url": url, "content": response.content})

    return pages
