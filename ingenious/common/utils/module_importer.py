import importlib
import importlib.util
import os
import sys
from pathlib import Path
from sysconfig import get_paths
from typing import Any, Dict, List, Optional


class ModuleNotFoundInNamespacesError(Exception):
    """Raised when a module cannot be found in any namespace."""

    pass


class ClassNotFoundInModuleError(Exception):
    """Raised when a class cannot be found in a module."""

    pass


class ModuleImportError(Exception):
    """Raised when there's an error importing a module."""

    pass


class ModuleImporter:
    """
    A class to handle importing modules from different namespaces,
    with support for fallbacks between namespaces.
    """

    def __init__(self, namespaces: List[str] = None):
        """
        Initialize the ModuleImporter with a list of namespaces.

        Args:
            namespaces: A list of namespace strings to search in order
        """
        self.namespaces = namespaces or self._get_default_namespaces()

        # Ensure working directory is in sys.path
        working_dir = Path(os.getcwd())
        if working_dir not in sys.path:
            sys.path.append(str(working_dir))

    def _get_default_namespaces(self) -> List[str]:
        """
        Returns the default namespaces to search for modules.

        Returns:
            A list of namespace strings
        """
        return [
            "ingenious_extensions",
            "ingenious.ingenious_extensions_template",
            "ingenious",
        ]

    def _get_full_module_names(self, module_name: str) -> List[str]:
        """
        Constructs full module names by prepending namespaces.

        Args:
            module_name: The base module name

        Returns:
            A list of full module names
        """
        return [f"{namespace}.{module_name}" for namespace in self.namespaces]

    def _find_module_spec(self, module_name: str) -> Optional[str]:
        """
        Finds the first namespace where the module exists.

        Args:
            module_name: The base module name

        Returns:
            The full module name if found, None otherwise
        """
        full_module_names = self._get_full_module_names(module_name)

        for full_name in full_module_names:
            try:
                if importlib.util.find_spec(full_name) is not None:
                    return full_name
            except ModuleNotFoundError:
                continue

        return None

    def import_module(self, module_name: str) -> Any:
        """
        Imports a module from the first namespace where it exists.

        Args:
            module_name: The base module name

        Returns:
            The imported module

        Raises:
            ModuleNotFoundInNamespacesError: If the module cannot be found
            ModuleImportError: If there's an error importing the module
        """
        full_module_name = self._find_module_spec(module_name)

        if not full_module_name:
            raise ModuleNotFoundInNamespacesError(
                f"Module {module_name} not found in any namespace"
            )

        try:
            return importlib.import_module(full_module_name)
        except ImportError as e:
            raise ModuleImportError(f"Error importing {full_module_name}: {e}") from e
        except Exception as e:
            raise ModuleImportError(
                f"Unexpected error importing {full_module_name}: {e}"
            ) from e

    def import_class(self, module_name: str, class_name: str) -> Any:
        """
        Imports a class from a module in the first namespace where it exists.

        Args:
            module_name: The base module name
            class_name: The name of the class to import

        Returns:
            The imported class

        Raises:
            ModuleNotFoundInNamespacesError: If the module cannot be found
            ClassNotFoundInModuleError: If the class cannot be found
            ModuleImportError: If there's an error importing the module
        """
        module = self.import_module(module_name)

        try:
            return getattr(module, class_name)
        except AttributeError as e:
            raise ClassNotFoundInModuleError(
                f"Class {class_name} not found in module {module.__name__}: {e}"
            ) from e

    def get_namespace_paths(self) -> Dict[str, Path]:
        """
        Gets the filesystem paths for each namespace.

        Returns:
            A dictionary mapping namespace names to Path objects
        """
        working_dir = Path(os.getcwd())

        paths = {
            "ingenious_extensions": working_dir / Path("ingenious_extensions"),
            "ingenious.ingenious_extensions_template": (
                working_dir / Path("ingenious") / Path("ingenious_extensions_template")
            ),
            "ingenious": Path(get_paths()["purelib"]) / Path("ingenious/"),
        }

        return {k: v for k, v in paths.items() if v.exists()}
