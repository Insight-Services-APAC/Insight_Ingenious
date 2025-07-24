# ingenious/chunk/tests/test_lazy_group.py
import importlib
from typer.testing import CliRunner
import typer
import pytest

from ingenious.utils.lazy_group import LazyGroup


def test_lazy_group_missing_extra(monkeypatch):
    """
    Simulate an un-installed `[chunk]` extra and assert that LazyGroup
    prints the helpful install message and exits with code 1 – **without**
    raising a traceback.
    """

    def _fake_import(name, *_, **__):
        if name == "ingenious.chunk.cli":
            raise ModuleNotFoundError("boom")  # pretend extra is missing
        return importlib.import_module(name)

    monkeypatch.setattr(importlib, "import_module", _fake_import)

    # Minimal Typer app using LazyGroup
    app = typer.Typer(cls=LazyGroup)

    @app.callback()  # needed so typer.testing can build the Click command
    def _root():
        pass

    runner = CliRunner()
    result = runner.invoke(app, ["chunk"])

    assert result.exit_code == 1
    assert "[chunk] extra not installed" in result.output.lower()
