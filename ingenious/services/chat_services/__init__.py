# N.B.
# This will add to the package’s __path__ all subdirectories of directories on sys.path named after the package which
# combines both modules into a single namespace (dbt.adapters)
# The matching statement is in plugins/postgres/dbt/__init__.py

from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)
