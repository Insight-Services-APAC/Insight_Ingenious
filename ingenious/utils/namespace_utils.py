import importlib
import pkgutil
import sys
import os
from pathlib import Path
from sysconfig import get_paths


def print_namespace_modules(namespace):
    package = importlib.import_module(namespace)
    if hasattr(package, '__path__'):
        for module_info in pkgutil.iter_modules(package.__path__):
            print(f"Found module: {module_info.name}")
    else:
        print(f"{namespace} is not a package. Importing now...")


def import_module_safely(module_name, class_name):
    if not sys.modules.get(module_name):
        try:
            module = importlib.import_module(f"{module_name}")
            service_class = getattr(module, class_name)
            return service_class
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Unsupported module import: {module_name}.{class_name}") from e
        except Exception as e:
            raise ValueError(f"An unexpected error occurred while importing {module_name}.{class_name}: {e}") from e
    else:
        module = importlib.import_module(f"{module_name}")
        service_class = getattr(module, class_name)   
        return service_class


def import_class_safely(module_name, class_name):
    if not sys.modules.get(module_name):
        try:
            module = importlib.import_module(f"{module_name}")
            service_class = getattr(module, class_name)
            return service_class
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Unsupported module import: {module_name}.{class_name}") from e
        except Exception as e:
            raise ValueError(f"An unexpected error occurred while importing {module_name}.{class_name}: {e}") from e
    else:
        module = importlib.import_module(f"{module_name}")
        service_class = getattr(module, class_name)   
        return service_class


def import_module_with_fallback(module_name):
    """
        This function tries to import a module from the Ingenious Extensions package and falls back to the Ingenious package if the module is not found.

        Args:
            module_name (str): The name of the module to import (excluding the top level of ingenious or ingenious_extensions).            
    """
    module_full_name = f"ingenious.{module_name}"
    working_dir = Path(os.getcwd())
    # Check if sys.path contains the working directory
    if working_dir not in sys.path:
        sys.path.append(str(working_dir))
    if importlib.util.find_spec(module_full_name) is not None:
        module = importlib.import_module(f"{module_full_name}")
    else:
        module_full_name = f"ingenious.{module_name}"
        module = importlib.import_module(f"{module_full_name}")
    return module


def import_class_with_fallback(module_name, class_name):
    """
        This function tries to import a class from the Ingenious Extensions package and falls back to the Ingenious package if the module is not found.

        Args:
            module_name (str): The name of the module to import (excluding the top level of ingenious or ingenious_extensions).
            class_name (str): The name of the class to import.            
    """
    module = import_module_with_fallback(module_name)
    class_object = getattr(module, class_name)    
    return class_object


def get_file_from_namespace_with_fallback(module_name, file_name):
    """
        This function tries to import a file from the Ingenious Extensions package and falls back to the Ingenious package if the file is not found.

        Args:
            module_name (str): The name of the module to import (excluding the top level of ingenious or ingenious_extensions).
            file_name (str): The name of the file to import.            
    """
    
    # Get working directory
    working_dir = Path(os.getcwd())

    module_full_name = working_dir / Path('ingenious_extensions') / Path(module_name) / Path(file_name)

    if os.path.exists(str(module_full_name)):
        with open(module_full_name, 'r') as file:
            return file.read()
    else:
        module_full_name = working_dir / Path('ingenious') / Path(module_name) / Path(file_name)
        with open(module_full_name, 'r') as file:
            return file.read()


def get_path_from_namespace_with_fallback(path: str):
    """
        This function tries to import a file from the Ingenious Extensions package and falls back to the Ingenious package if the file is not found.

        Args:
            module_name (str): The name of the module to import (excluding the top level of ingenious or ingenious_extensions).
    """
    
    # Get working directory
    working_dir = Path(os.getcwd())    
    install_dir = Path(get_paths()['purelib']) / Path('ingenious/')
    template_path = working_dir / "ingenious_extensions" / Path(path)
    if not template_path.exists():
        template_path = install_dir / "ingenious" / Path(path)
    return template_path