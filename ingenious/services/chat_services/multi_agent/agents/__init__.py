# Extend path to allow partial namespaces
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)
