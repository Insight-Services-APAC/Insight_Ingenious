"""Lazy‑loading command group for Typer/Click CLIs
==============================================

``lazy_group.py`` introduces :class:`LazyGroup`, a specialised
:class:`typer.core.TyperGroup` that **defers importing sub‑command modules
until the user explicitly invokes them**.  This design keeps the *Insight Ingenious*
entry‑point (`ingen_cli`) fast to start and avoids hard dependencies on
optional extras (e.g. *document‑processing*, *dataprep*) unless they are
really needed.

Motivation
----------
* **Startup latency** – A monolithic CLI that imports *everything* up‑front can
  take seconds to boot, especially when heavy libraries like pandas, PyMuPDF,
  or torch are involved.  By lazy‑loading, the base CLI remains snappy even in
  constrained environments.
* **Optional feature sets** – Power‑users may install
  ``insight‑ingenious[document‑processing]`` or ``[dataprep]`` extras, while
  others stick to the core package.  The loader detects the absence of an
  extra and prints an actionable *pip install* hint instead of raising a long
  traceback.
* **Tiny implementation** – Achieves the above in < 60 LOC by piggy‑backing on
  Click/Typer’s existing extension hooks.

Architecture overview
~~~~~~~~~~~~~~~~~~~~~
#. ``ingen_cli`` is declared with ``cls=LazyGroup``.
#. When ``--help`` is requested, Typer → Click calls
   :meth:`LazyGroup.list_commands`, which simply returns the *keys* of the
   private :pyattr:`LazyGroup._loaders` registry so they appear in the help
   footer.
#. When the user executes a sub‑command (e.g. ``ingen_cli dataprep``), Click
   invokes :meth:`LazyGroup.get_command`.  This method:
   • Looks up the *LoadSpec* tuple ``(module_path, attr_name, extra_label)``.
   • Attempts to ``importlib.import_module(module_path)`` *on demand*.
   • If successful → retrieves the attribute (can be a Typer *app* or pure
     Click *Command*), converts Typer→Click when necessary via
     :pyfunc:`typer.main.get_command`, and returns it to Click for execution.
   • If the import fails → issues :class:`typer.Exit` with a clear message and
     installation instructions (using *extra_label*).

Extending the registry
----------------------
To expose a new lazy sub‑CLI:

>>> LazyGroup._loaders["my‑feature"] = (
...     "ingenious.my_feature.cli",  # dotted‑path to module
...     "app",                       # attribute exposing the Typer/Click object
...     "my‑feature",               # pip extra label for nice error text
... )

No further changes are required—the command appears in ``--help``
automatically.

Thread‑safety & re‑entrancy
---------------------------
Importing is inherently serialised by Python’s import lock, so there is no
risk of race conditions when multiple commands are executed in rapid
succession (e.g. in shell completion scripts).

Return type guarantees
----------------------
:meth:`get_command` *always* returns an object that Click recognises as a
command:

* If the attribute is already a :class:`click.Command`, it is passed through.
* If it is a :class:`typer.Typer` app, it is converted exactly once via
  :pyfunc:`typer.main.get_command` to avoid duplicate callback creation.

"""

from __future__ import annotations

import importlib
from typing import Dict, List, Optional, Tuple, TypeAlias

import typer
from click import Command
from typer.core import TyperGroup

# ---------------------------------------------------------------------------
# Type aliases & loader registry
# ---------------------------------------------------------------------------
LoadSpec: TypeAlias = Tuple[str, str, str]
"""Tuple structure used in :pyattr:`LazyGroup._loaders`:

* **module_path** – importable dotted path (e.g. ``"ingenious.dataprep.cli"``)
* **attr_name** – attribute exposing a Typer *app* **or** Click *Command*
* **extra_label** – pip *extra* name for helpful error messaging
"""

LoadRegistry: TypeAlias = Dict[str, LoadSpec]
"""Mapping from *public* sub‑command name to its :pydata:`LoadSpec`."""


class LazyGroup(TyperGroup):
    """A *Typer* command group that lazy‑loads its sub‑CLIs.

    The class overrides two Click hooks to implement its magic:

    * :meth:`list_commands` advertises available sub‑command names.  It does
      **not** import any heavy modules—just echoes the keys of the private
      registry.
    * :meth:`get_command` performs the on‑demand import and returns a fully
      initialised Click command to Click/Typer.  If the module import fails
      because the optional dependency is missing, the method exits the CLI
      with a brief installation hint.

    Add new entries to :pyattr:`_loaders` to extend the CLI without touching
    the core boot code.
    """

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
    }

    # ------------------------------------------------------------------
    # Click hook – discovery
    # ------------------------------------------------------------------
    def list_commands(self, ctx) -> List[str]:
        """Return *sorted* sub‑command names for Click’s help generator.

        Parameters
        ----------
        ctx
            Click context object (not used here).

        Returns
        -------
        list[str]
            Sorted view of the keys from :pyattr:`_loaders`.
        """
        return sorted(self._loaders)

    # ------------------------------------------------------------------
    # Click hook – lazy import
    # ------------------------------------------------------------------
    def get_command(self, ctx, name: str) -> Optional[Command]:
        """Import *name* on first use and hand the resulting command to Click.

        The method fetches ``(module_path, attr_name, extra_label)`` from
        :pyattr:`_loaders`, attempts to import the module, retrieves the
        attribute, and ensures the returned object is a :class:`click.Command`.

        Failure modes
        -------------
        * **Unknown name** – returns ``None`` so Click can show *unknown
          command* error.
        * **Missing dependency** – catches :class:`ModuleNotFoundError` and
          terminates with :class:`typer.Exit`, printing an installation hint
          that references the missing *extra*.

        Parameters
        ----------
        ctx
            Click context (present for API compatibility; not used).
        name
            Sub‑command as typed by the user (e.g. ``"dataprep"``).

        Returns
        -------
        click.Command | None
            Ready‑to‑invoke command object or ``None`` if *name* is not
            registered.
        """
        if name not in self._loaders:
            return None

        module_path, attr_name, extra = self._loaders[name]

        try:
            # Import only now that we know the user really wants this feature.
            module = importlib.import_module(module_path)
            sub_app = getattr(module, attr_name)
        except ModuleNotFoundError as exc:
            # Provide a short, actionable installation message instead of a stack‑trace.
            raise typer.Exit(
                (
                    f"\n[{extra}] extra not installed.\n"
                    "Install with:\n\n"
                    f"    pip install 'insight-ingenious[{extra}]'\n"
                ),
            ) from exc

        # Typer ≥ 0.15 requires us to return a Click command, not a Typer app.
        if isinstance(sub_app, Command):
            return sub_app  # Already a Click object.

        # Convert Typer → Click exactly once.
        return typer.main.get_command(sub_app)


__all__ = [
    "LazyGroup",
]
