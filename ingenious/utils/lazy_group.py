from __future__ import annotations

import importlib
from typing import Dict, List, Optional, Tuple, TypeAlias

import typer
from click import Command, Context
from typer.core import TyperGroup

# Type aliases & loader registry
LoadSpec: TypeAlias = Tuple[str, str, str]
LoadRegistry: TypeAlias = Dict[str, LoadSpec]


class LazyGroup(TyperGroup):
    """A Typer command group that lazy-loads its sub-CLIs."""

    _loaders: LoadRegistry = {
        "document-processing": (
            "ingenious.document_processing.cli",
            "doc_app",
            "document-processing",
        ),
        "dataprep": (
            "ingenious.dataprep.cli",
            "dataprep",
            "dataprep",
        ),
        "chunk": (
            "ingenious.chunk.cli",
            "cli",
            "chunk",
        ),
    }

    def list_commands(self, ctx: Context) -> List[str]:
        """Return sorted sub-command names for Click's help generator."""
        # Get the main commands from the parent class
        main_commands = super().list_commands(ctx)
        # Combine with lazy-loaded commands
        all_commands = set(main_commands + list(self._loaders.keys()))
        return sorted(all_commands)

    def get_command(self, ctx: Context, name: str) -> Optional[Command]:
        """Import name on first use and hand the resulting command to Click."""
        # First check if it's a main command
        main_command = super().get_command(ctx, name)
        if main_command is not None:
            return main_command

        # Then check if it's a lazy-loaded command
        if name not in self._loaders:
            return None

        module_path, attr_name, extra = self._loaders[name]

        try:
            # Import only now that we know the user really wants this feature.
            module = importlib.import_module(module_path)
            sub_app = getattr(module, attr_name)
        except ModuleNotFoundError as exc:
            # Provide a short, actionable installation message instead of a stack-trace.
            message = (
                f"\n[{extra}] extra not installed.\n"
                "Install with:\n\n"
                f"    pip install 'insight-ingenious[{extra}]'\n"
            )
            typer.echo(message, err=True)
            raise typer.Exit(code=1) from exc

        # Typer >= 0.15 requires us to return a Click command, not a Typer app.
        if isinstance(sub_app, Command):
            return sub_app  # Already a Click object.

        # Convert Typer -> Click exactly once.
        return typer.main.get_command(sub_app)


__all__ = [
    "LazyGroup",
]
