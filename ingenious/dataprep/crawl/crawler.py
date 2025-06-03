"""
*Public façade* sitting between **Insight Ingenious** pipelines/CLI and the
*provider-specific* implementation found in `_scrapfly_impl.py`.

Why a two-layer design?
-----------------------
1. **Vendor agnosticism** – `Crawler` deliberately has **no Scrapfly imports**.
   If we decide to switch from Scrapfly to Playwright, Browserless, or an
   internal fetch-service, only the private adapter file has to change.
2. **Separation of concerns**
   * `_scrapfly_impl.fetch_pages`   → *network I/O, retries, API-keys*
   * `Crawler`                      → *orchestration & argument plumbing*
3. **Testability** – Unit tests can patch **one** symbol (`fetch_pages`) to
   avoid real HTTP calls while still covering the forwarding logic.
"""

from __future__ import annotations

from typing import Dict, Iterable, List

from ._scrapfly_impl import fetch_pages


class Crawler:
    """
    Vendor-neutral wrapper that clients instantiate.

    Any keyword argument (`**cfg`) is forwarded *verbatim* to the low-level
    `fetch_pages()` helper.  This makes the public surface stable even if we
    later expose new provider features – callers simply pass them through
    without the wrapper needing a new release.

    Examples
    --------
    Basic use with defaults::

        page = Crawler().scrape("https://example.com")

    Custom retry/JS options::

        batch = Crawler(max_attempts=3,
                        retry_on_status_code=[520],
                        extra_scrapfly_cfg={"render_js": False}
                       ).batch(urls)
    """

    # ------------------------------------------------------------------ init #
    def __init__(self, **cfg) -> None:
        """
        Store *all* supplied keyword arguments.

        We do **not** try to validate the keys – that responsibility lives in
        `_scrapfly_impl`.  Keeping the layer thin avoids duplicating rules and
        lets the adapter evolve independently.
        """
        self.cfg = cfg  # stash for later forwarding

    # -------------------------------------------------------------- .scrape #
    def scrape(self, url: str) -> Dict[str, str]:
        """
        Fetch a **single** page.

        We wrap the one-item *url* in a list because `fetch_pages` is a
        batch-oriented API.  Returning the *first* element (index 0) saves
        callers from `[0]` gymnastics.
        """
        return fetch_pages([url], **self.cfg)[0]

    # --------------------------------------------------------------- .batch #
    def batch(self, urls: Iterable[str]) -> List[Dict[str, str]]:
        """
        Fetch **multiple** URLs in one provider call.

        Parameters
        ----------
        urls
            Any iterable of absolute URLs – generator, tuple, etc.

        Design note
        -----------
        We eagerly convert *urls* to a list:

        * guarantees a real container that can be iterated multiple times
          (the provider or logging hooks might loop twice);
        * preserves **input order** so callers can rely on positional mapping
          between request and response lists.
        """
        return fetch_pages(list(urls), **self.cfg)
