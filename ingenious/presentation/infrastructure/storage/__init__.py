"""
Storage implementation modules.
"""

from pkgutil import extend_path

from ingenious.presentation.infrastructure.storage.factory import BlobStorageFactory

__path__ = extend_path(__path__, __name__)
__all__ = ["BlobStorageFactory"]
# This will add to the package's __path__ all subdirectories of directories on sys.path named after
# the package which effectively combines both modules into a single namespace (dbt.adapters)
# The matching statement is in plugins/postgres/dbt/__init__.py
