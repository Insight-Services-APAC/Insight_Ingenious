"""
Dataprep command-group for the *Insight Ingenious* CLI
=====================================================

We piggy-back on the project-wide **ingen** CLI (exposed by the entry-point
`ingen = "ingenious.cli:app"` in *pyproject.toml*).
This module registers an *additional* Typer **sub-application**
under `ingen dataprep …` that exposes two scraping helpers:

* ``ingen dataprep crawl``   → pull **one** page, print a single JSON object.
* ``ingen dataprep batch``   → pull **many** pages, stream **NDJSON**
  (newline-delimited JSON, one object per line) so callers can pipe the output
  into tools like *jq*, *xargs*, databases, etc.

Why a dedicated CLI layer instead of letting users import ``Crawler``?
----------------------------------------------------------------------
1. **Zero Python required** – data-scientists can fetch pages from Bash.
2. **Re-usability** – the same code path is used by notebooks, Airflow, ad-hoc
   shell scripts **and** our automated prompt-ingestion pipelines.
3. **Auditability** – every CLI call can be logged with full arguments, giving
   us a paper-trail of which pages were captured, when, and with what retry
   policy.

Flag→Parameter mapping
----------------------
The table below shows how shell flags are translated into keyword arguments
that end up in :pyfunc:`ingenious.dataprep.crawl._scrapfly_impl.fetch_pages`.

| CLI flag                | Kwarg on *Crawler* | Meaning inside the SDK                |
|-------------------------|--------------------|----------------------------------------|
| ``--api-key``           | ``api_key``        | override *SCRAPFLY_API_KEY* for 1 run |
| ``--max-attempts``      | ``max_attempts``   | total tries per URL                    |
| ``--retry-code``        | ``retry_on_status_code`` | additional origin status codes that trigger retry |
| ``--delay``             | ``delay``          | initial back-off (doubles each retry)  |
| ``--js / --no-js``      | part of ``extra_scrapfly_cfg["render_js"]`` |
| ``--extra-scrapfly-cfg``| ``extra_scrapfly_cfg`` | raw JSON merged over the default SDK config |

All values are forwarded **verbatim**; the CLI is intentionally
*provider-agnostic* and never inspects HTTP responses itself.
"""

from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Annotated, List, Optional, Dict, Any

import typer
from rich import print as rprint

from ingenious.dataprep.crawl import Crawler

# ─────────────────────────── Typer sub-application ──────────────────────────
dataprep = typer.Typer(
    no_args_is_help=True,
    help="Data-preparation utilities (Scrapfly crawler façade)",
)


# --------------------------------------------------------------------------- #
# _build_crawler_kwargs
# --------------------------------------------------------------------------- #
def _build_crawler_kwargs(
    *,
    api_key: str | None,
    max_attempts: int,
    retry_code: list[int],
    js: bool,
    delay: int,
    extra_scrapfly_cfg: str | None,
) -> Dict[str, Any]:
    """
    Translate raw CLI options into the ``Crawler(**kwargs)`` signature.

    The function does **no validation** beyond basic JSON parsing – anything
    unknown is handed down to the provider adapter, keeping this layer thin.

    Parameters
    ----------
    api_key
        Explicit Scrapfly key (overrides the environment variable).
    max_attempts
        How many total tries *fetch_pages* should make (1st + retries).
    retry_code
        Extra origin-site HTTP status codes that should be considered transient
        (e.g. 520 Cloudflare errors).
    js
        Convenience toggle for ``render_js`` inside the SDK config.
    delay
        Initial back-off delay in **seconds**; Scrapfly doubles it every retry.
    extra_scrapfly_cfg
        Raw JSON string merged over the default Scrapfly config allowing
        low-level knobs such as country, proxy, etc.

    Returns
    -------
    dict
        Ready-to-unpack ``**kwargs`` for :pyclass:`ingenious.dataprep.crawl.Crawler`.
    """
    # Base kwargs
    kw: Dict[str, Any] = {
        "api_key": api_key,
        "max_attempts": max_attempts,
        "delay": delay,
    }

    # Add optional retry codes
    if retry_code:
        kw["retry_on_status_code"] = retry_code

    # Build Scrapfly config (always inject render_js toggle)
    cfg: Dict[str, Any] = {"render_js": js}

    if extra_scrapfly_cfg:
        # Allow users to pass free-form JSON, but fail fast on syntax errors
        try:
            cfg.update(json.loads(extra_scrapfly_cfg))
        except JSONDecodeError as exc:  # pragma: no cover – user input path
            typer.secho(
                f"[red]Invalid JSON for --extra-scrapfly-cfg:[/red] {exc}",
                err=True,
            )
            raise typer.Exit(1)

    kw["extra_scrapfly_cfg"] = cfg
    return kw


# =========================================================================== #
# 1. Single-URL command
# =========================================================================== #
@dataprep.command("crawl")
def crawl_cmd(  # noqa: D401  (Typer callback)
    url: Annotated[str, typer.Argument(help="Absolute target URL (with scheme)")],
    pretty: Annotated[
        bool,
        typer.Option(
            "--pretty/--raw",
            help="Pretty-print JSON output (default: pretty)",
            rich_help_panel="Output",
        ),
    ] = True,
    # ───── Shared provider flags ───────────────────────────────────────────
    api_key: Annotated[
        Optional[str],
        typer.Option(
            "--api-key",
            envvar="SCRAPFLY_API_KEY",
            help="Override Scrapfly key for this invocation only",
            rich_help_panel="Scrapfly credentials",
        ),
    ] = None,
    max_attempts: Annotated[
        int,
        typer.Option("--max-attempts", min=1, help="Total tries per URL"),
    ] = 5,
    retry_code: Annotated[
        List[int],
        typer.Option(
            "--retry-code",
            help="Repeatable flag – add a status code that should be retried",
        ),
    ] = [],
    delay: Annotated[
        int,
        typer.Option("--delay", help="Initial back-off delay (s)"),
    ] = 1,
    js: Annotated[
        bool,
        typer.Option("--js/--no-js", help="Enable/disable JavaScript rendering"),
    ] = True,
    extra_scrapfly_cfg: Annotated[
        Optional[str],
        typer.Option(
            "--extra-scrapfly-cfg",
            help='Raw JSON merged over the SDK config (example: \'{"country": "us"}\')',
            rich_help_panel="Advanced SDK tuning",
        ),
    ] = None,
):
    """
    Fetch **one** web-page and dump a JSON envelope.

    Flow
    ----
    1. Build the provider kwarg-dict with :pyfunc:`_build_crawler_kwargs`.
    2. Instantiate :pyclass:`Crawler` and call :pyfunc:`Crawler.scrape`.
    3. Print the resulting dictionary – either compact or indented.

    The command exits **non-zero** on the *first* unrecoverable Scrapfly error
    so shell scripts can abort early.
    """
    kwargs = _build_crawler_kwargs(
        api_key=api_key,
        max_attempts=max_attempts,
        retry_code=retry_code,
        js=js,
        delay=delay,
        extra_scrapfly_cfg=extra_scrapfly_cfg,
    )

    try:
        result = Crawler(**kwargs).scrape(url)
        rprint(json.dumps(result, indent=4 if pretty else None, ensure_ascii=False))
    except Exception as exc:  # pragma: no cover – provider/IO errors
        typer.secho(f"Error: {exc}", fg="red", err=True)
        raise typer.Exit(1)


# =========================================================================== #
# 2. Batch command
# =========================================================================== #
@dataprep.command("batch")
def batch_cmd(  # noqa: D401
    urls: Annotated[
        list[str],
        typer.Argument(help="Two or more absolute URLs (space-separated)"),
    ],
    pretty: bool = True,
    # ───── Shared provider flags (same as above) ───────────────────────────
    api_key: str | None = typer.Option(None, "--api-key", envvar="SCRAPFLY_API_KEY"),
    max_attempts: int = typer.Option(5, "--max-attempts"),
    retry_code: list[int] = typer.Option([], "--retry-code"),
    delay: int = typer.Option(1, "--delay"),
    js: bool = typer.Option(True, "--js/--no-js"),
    extra_scrapfly_cfg: Optional[str] = typer.Option(None, "--extra-scrapfly-cfg"),
    output_file: Annotated[
        Path | None,
        typer.Option(
            "--out",
            help="If given, write NDJSON to FILE instead of stdout",
            rich_help_panel="Output",
        ),
    ] = None,
):
    """
    Fetch **multiple** pages and stream them as NDJSON.

    The function opens *output_file* (if provided) **lazily** so that the file
    is not created when the crawl fails early.  Each page is dumped on its own
    line (compact JSON) which makes the output easy to process with Unix tools.

    The `pretty` flag inserts an extra blank line *only* when writing to the
    terminal – NDJSON files stay machine-friendly.
    """
    kwargs = _build_crawler_kwargs(
        api_key=api_key,
        max_attempts=max_attempts,
        retry_code=retry_code,
        js=js,
        delay=delay,
        extra_scrapfly_cfg=extra_scrapfly_cfg,
    )

    sink = None  # will hold the opened file handle (if any)

    try:
        pages = Crawler(**kwargs).batch(urls)

        # Decide where to write each JSON line
        sink = output_file.open("w", encoding="utf-8") if output_file else None
        write = sink.write if sink else typer.echo

        for page in pages:
            write(json.dumps(page, ensure_ascii=False))
            if pretty and not output_file:
                typer.echo()  # human-friendly spacing

    except Exception as exc:  # pragma: no cover – propagate provider errors
        typer.secho(f"Error: {exc}", fg="red", err=True)
        raise typer.Exit(1)
    finally:
        if sink:
            sink.close()
