# ingenious/dataprep/cli.py
"""
Dataprep-specific sub-commands for the **Insight Ingenious** CLI.

At the moment we expose a single `crawl` command that:
1. Pulls the page through our high-level `Crawler` wrapper (Scrapfly SDK under
   the hood, but hidden from the user).
2. Prints a small JSON object to *stdout* so the result can be piped into
   jq / redirected into a file / consumed by another shell script.

Keeping this in a **separate Typer sub-app** means:
• Core CLI (`ingen`) stays clean ─ dataprep tools can evolve independently.
• New dataprep commands (chunk-text, embed, upload-vs etc.) just add another
  `@dataprep.command` down the road.
"""

from __future__ import annotations

import json
from typing import Annotated

import typer
from rich import print as rprint  # colourises JSON if the terminal supports it

from ingenious.dataprep.crawl import Crawler  # single import point for crawling

# ──────────────────────────────────────────────────────────────────────────────
# Typer sub-application
# ──────────────────────────────────────────────────────────────────────────────
dataprep = typer.Typer(
    no_args_is_help=True,  # “ingen dataprep” → show help instead of nothing
    help="Data-preparation utilities",
)


# ──────────────────────────────────────────────────────────────────────────────
# Command: `ingen dataprep crawl <url>`
# ──────────────────────────────────────────────────────────────────────────────
@dataprep.command("crawl")
def crawl_cmd(
    url: Annotated[
        str,
        typer.Argument(
            help="The URL to scrape with Scrapfly (must be absolute, incl. scheme)"
        ),
    ],
    pretty: Annotated[
        bool,
        typer.Option(
            "--pretty/--raw",
            help="Pretty-print JSON output (default: pretty)",
            rich_help_panel="Output options",
        ),
    ] = True,
):
    """
    Fetch **one** URL and dump a minimal JSON envelope to stdout::

        {"url": "<canonical_url>", "content": "<markdown|text>"}

    The command:

    * **Never** writes to disk – leaving that choice to the caller.
    * Returns *0* on success so it can be chained with `&&`.
    * Returns *1* and prints a red error message on any exception
      (non-network issues bubble up from `Crawler`).

    Examples
    --------
    Pretty-printed (default)::

        ingen dataprep crawl https://example.com

    Raw (compact) JSON – easier to pipe into `jq -r .content`::

        ingen dataprep crawl https://example.com --raw
    """
    try:
        # ── Actual work is one line thanks to the wrapper ─────────────────────
        result = Crawler().scrape(url)

        # Serialise; indent only if the user asked for pretty output
        payload = json.dumps(
            result,
            indent=4 if pretty else None,
            ensure_ascii=False,  # keep Unicode glyphs readable
        )

        # Rich’s print preserves colour when stdout is a TTY, falls back to
        # plain text when redirected to a file/pipe – zero extra logic needed.
        rprint(payload)

    except Exception as exc:
        # Surface the exception in red and exit with *non-zero* for scripts
        typer.secho(f"Error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
