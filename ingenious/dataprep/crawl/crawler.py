"""
Thin, provider-agnostic **crawler facade** for Ingenious dataprep.

Why split the concerns?

* `Crawler` is what the CLI (`ingen dataprep crawl …`) and future
  pipelines import.
  It deliberately exposes **no Scrapfly-specific API** so that tomorrow we
  could switch to, say, Playwright or Browserless with zero surface change.

* `_scrapfly_impl.fetch_pages()` is the low-level adapter that knows how to
  talk to Scrapfly and handle the key, retry policy, etc.

This file therefore contains *only* orchestration glue and argument
normalisation.
"""

from __future__ import annotations

from typing import Dict, Iterable, List

from ._scrapfly_impl import fetch_pages


class Crawler:
    """
    High-level crawler wrapper.

    Parameters
    ----------
    **cfg :
        Arbitrary keyword arguments forwarded verbatim to the provider adapter
        (`fetch_pages`).  Example:

        ```python
        Crawler(render_js=False, country="us")
        ```
    """

    # --------------------------------------------------------------------- init
    def __init__(self, **cfg):
        # Do not touch/validate here; leave that to the provider module so that
        # the wrapper stays vendor-neutral.
        self.cfg = cfg

    # ----------------------------------------------------------------- helpers
    def scrape(self, url: str) -> Dict[str, str]:
        """
        Fetch **one** page.

        Returned mapping is exactly the first element of `fetch_pages()`
        so that call-sites don’t have to slice the list themselves.
        """
        return fetch_pages([url], **self.cfg)[0]

    def batch(self, urls: Iterable[str]) -> List[Dict[str, str]]:
        """
        Fetch **many** pages in a single provider call.

        *Why convert to list?*
        Because the underlying adapter may iterate over the sequence more than
        once (e.g. for logging) – turning a lazy generator into a list avoids
        surprises.
        """
        return fetch_pages(list(urls), **self.cfg)
