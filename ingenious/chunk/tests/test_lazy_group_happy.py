"""
Happy‑path smoke‑test for LazyGroup: verifies that a correctly installed
[chunk] extra is imported, the sub‑command is discovered, and runs.
"""
from types import ModuleType
import sys
import typer
from typer.testing import CliRunner

from ingenious.utils.lazy_group import LazyGroup


def test_lazy_group_happy_path(monkeypatch):
    # ── 1. Build a dummy sub‑CLI  ──────────────────────────────────────────
    sub_app = typer.Typer()

    # Typer ≥ 0.15 collapses a single‑command app into a plain click.Command
    # unless a callback is present.  Adding this no‑op callback forces
    # Typer to return a click.Group, mirroring the real `ingen chunk` CLI.
    @sub_app.callback()  # noqa: D401
    def _sub_root() -> None:  # noqa: D401
        """no‑op – keeps sub_app a group"""

    @sub_app.command()
    def ping() -> None:  # noqa: D401
        """Emit a friendly pong."""
        typer.echo("pong")

    dummy_mod = ModuleType("ingenious.chunk.cli")
    dummy_mod.cli = sub_app

    # ── 2. Pretend this module is already installed ───────────────────────
    monkeypatch.setitem(sys.modules, "ingenious.chunk.cli", dummy_mod)

    # ── 3. Root Typer application that uses LazyGroup ─────────────────────
    root = typer.Typer(cls=LazyGroup)

    @root.callback()  # Needed so Typer can build the Click command
    def _root():
        """no‑op"""

    # ── 4. Invoke “chunk ping” and assert success ─────────────────────────
    result = CliRunner().invoke(root, ["chunk", "ping"])
    assert result.exit_code == 0, result.output
    assert "pong" in result.output
