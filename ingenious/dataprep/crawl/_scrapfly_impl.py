"""
Provider adapter that fetches pages with the **Scrapfly SDK**
(no LangChain dependency).

The function `fetch_pages()` is intentionally *thin*:

* handle API-key discovery (CLI arg › env var › optional .env)
* normalise Scrapfly configuration
* perform 1-to-N HTTP fetches
* raise *early* if anything is wrong (missing key, bad status, empty body)
* return a list of {"url", "content"} records – the contract expected by
  ingenious.dataprep.crawl.Crawler

Nothing else – pagination, rate-limiting, retry logic, etc. – is pushed up to
callers so the wrapper can stay provider-agnostic.
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Dict, List

from dotenv import load_dotenv, find_dotenv
from scrapfly import ScrapflyClient, ScrapeConfig
from scrapfly.errors import ScrapflyError as ScrapflyException

log = logging.getLogger(__name__)

# ────────────────────────────── one-time .env convenience ──────────────────────
# Local developers drop a `.env` next to their `config.yml`; CI will simply
# ignore this because its environment is populated by secrets.
_ENV_LOADED = load_dotenv(find_dotenv(usecwd=True), override=False)
if _ENV_LOADED:
    log.debug(".env file loaded for Scrapfly key")

# ───────────────────────────── default per-request options ─────────────────────
DEFAULT_CONFIG: Dict[str, str | bool] = {
    "render_js": True,  # use headless browser; needed for SPAs
    "asp": True,  # enable Scrapfly’s anti-scraping protection bypass
    "format": "markdown",  # cleaner to chunk/LLM-embed than raw HTML
}

# Little alias for readability in type hints
Page = Dict[str, str]


# ─────────────────────────────── client factory (cached) ───────────────────────
@lru_cache(maxsize=1)
def _client(api_key: str) -> ScrapflyClient:
    """
    ScrapflyClient is cheap, but caching avoids re-instantiation in tight loops
    and makes the function thread-safe.
    """
    return ScrapflyClient(key=api_key)


# ───────────────────────────────── public entry-point ──────────────────────────
def fetch_pages(
    urls: List[str],
    *,
    api_key: str | None = None,
    extra_scrapfly_cfg: Dict | None = None,
) -> List[Page]:
    """
    Fetch **each** URL and return a list of:

        {"url": "<url>", "content": "<markdown|text>"}

    Parameters
    ----------
    urls:
        One or many absolute URLs.

    api_key:
        Explicit Scrapfly API key – overrides env/.env.  Useful for the CLI
        flag `--api-key` or programmatic injection in tests.

    extra_scrapfly_cfg:
        Keyword arguments merged *over* DEFAULT_CONFIG, e.g.
        `{"render_js": False, "country": "us"}`.

    Raises
    ------
    RuntimeError
        * if the API key could not be resolved
        * if Scrapfly returns non-200 status
        * if the response body is empty (site blocked or JavaScript error)

    ScrapflyException
        Any lower-level SDK/network error bubbles up unchanged so callers can
        decide whether to retry.
    """
    # ── Resolve API key (CLI arg ▸ env var) ────────────────────────────────────
    api_key = api_key or os.getenv("SCRAPFLY_API_KEY")
    if not api_key:
        raise RuntimeError("SCRAPFLY_API_KEY not set (env var or .env)")

    client = _client(api_key)
    cfg = {**DEFAULT_CONFIG, **(extra_scrapfly_cfg or {})}

    pages: List[Page] = []
    for url in urls:
        try:
            resp = client.scrape(ScrapeConfig(url=url, **cfg))
        except ScrapflyException as exc:
            # Expose HTTP/network issues to caller; keep stack-trace.
            log.debug("Scrapfly exception for %s: %s", url, exc)
            raise

        # ── Basic sanity checks before we claim success ───────────────────────
        if resp.status_code != 200:
            raise RuntimeError(f"Scrapfly HTTP {resp.status_code} for {url}")
        if not resp.content.strip():
            raise RuntimeError(f"Empty body for {url}")

        pages.append({"url": url, "content": resp.content})

    return pages
