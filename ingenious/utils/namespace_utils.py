import importlib
import os
import pkgutil
import sys
from pathlib import Path
from sysconfig import get_paths


def normalize_workflow_name(workflow_name: str) -> str:
    """
    Normalize workflow names to support both hyphenated and underscored formats.
    Converts hyphens to underscores for module path compatibility.

    Args:
        workflow_name (str): The workflow name (e.g., "bike-insights" or "bike_insights")

    Returns:
        str: The normalized workflow name with underscores (e.g., "bike_insights")
    """
    if not workflow_name:
        return workflow_name
    return workflow_name.replace("-", "_").lower()


def print_namespace_modules(namespace):
    package = importlib.import_module(namespace)
    if hasattr(package, "__path__"):
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
            raise ValueError(
                f"Unsupported module import: {module_name}.{class_name}"
            ) from e
        except Exception as e:
            raise ValueError(
                f"An unexpected error occurred while importing {module_name}.{class_name}: {e}"
            ) from e
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
            raise ValueError(
                f"Unsupported module import: {module_name}.{class_name}"
            ) from e
        except Exception as e:
            raise ValueError(
                f"An unexpected error occurred while importing {module_name}.{class_name}: {e}"
            ) from e
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
    working_dir = Path(os.getcwd())
    # Check if sys.path contains the working directory
    if working_dir not in sys.path:
        sys.path.append(str(working_dir))

    modules = [f"{n}.{module_name}" for n in get_namespaces()]

    for i in range(len(modules)):
        m = modules[i]
        print(f"Trying to import module {m}")
        try:
            if importlib.util.find_spec(m) is not None:
                module = importlib.import_module(f"{m}")
                print(f"Module {m} found.")
                return module
        except ModuleNotFoundError as e:
            print(f"Module {m} not found in any namespace.{e}")
        except ImportError as e:
            print(f"ImportError occurred while importing module {m}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while importing module {m}: {e}")


def import_class_with_fallback(module_name, class_name):
    """
    This function tries to import a class from the Ingenious Extensions package and falls back to the Ingenious package if the module is not found.

    Args:
        module_name (str): The name of the module to import (excluding the top level of ingenious or ingenious_extensions).
        class_name (str): The name of the class to import.
    """
    try:
        module = import_module_with_fallback(module_name)
        class_object = getattr(module, class_name)
        return class_object
    except ModuleNotFoundError as e:
        raise ValueError(f"Module {module_name} not found in any namespace: {e}") from e
    except AttributeError as e:
        raise ValueError(
            f"Class {class_name} not found in module {module_name}: {e}"
        ) from e
    except ImportError as e:
        raise ValueError(
            f"ImportError occurred while importing module {module_name}: {e}"
        ) from e
    except Exception as e:
        raise ValueError(
            f"An unexpected error occurred while importing {module_name}.{class_name}: {e}"
        ) from e


def get_file_from_namespace_with_fallback(module_name, file_name):
    """
    This function tries to import a file from the Ingenious Extensions package and falls back to the Ingenious package if the file is not found.

    Args:
        module_name (str): The name of the module to import (excluding the top level of ingenious or ingenious_extensions).
        file_name (str): The name of the file to import.
    """

    dirs = [(d / Path(module_name) / Path(file_name)) for d in get_dir_roots()]

    for dir in dirs:
        if os.path.exists(str(dir)):
            with open(dir, "r") as file:
                return file.read()


def get_path_from_namespace_with_fallback(path: str):
    """
    This function tries to import a file from the Ingenious Extensions package and falls back to the Ingenious package if the file is not found.

    Args:
        module_name (str): The name of the module to import (excluding the top level of ingenious or ingenious_extensions).
    """

    dirs = [(d / Path(path)) for d in get_dir_roots()]
    for dir in dirs:
        if os.path.exists(str(dir)):
            return dir


def get_inbuilt_api_routes():
    """
    Retrieves a list of in-built API routes from the Ingenious package.
    Returns:
        list: A list of Path objects representing the in-built API routes.
    """
    working_dir = Path(os.getcwd()) / Path("ingenious") / Path("api") / Path("routes")
    install_dir = (
        Path(get_paths()["purelib"]) / Path("ingenious") / Path("api") / Path("routes")
    )

    dirs = [working_dir, install_dir]

    for dir in dirs:
        if os.path.exists(str(dir)):
            return dir


def get_dir_roots():
    """
    Retrieves a list of directory paths that are considered as root directories for the project.
    The function checks three potential locations for the root directories:
    1. The 'ingenious_extensions' folder in the current working directory.
    2. The 'ingenious_extensions_templates' folder in the 'ingenious' directory within the current working directory.
    3. The 'ingenious' folder in the site-packages directory of the current Python environment.
    Returns:
        list: A list of Path objects representing the root directories.
    """
    working_dir = Path(os.getcwd())
    # First try the project extensions folder.. this will override all else
    extensions_dir = working_dir / Path("ingenious_extensions")
    # next try the extensions template folder.. this will only exist if in development version
    extensions_template_dir = (
        working_dir / Path("ingenious") / Path("ingenious_extensions_template")
    )
    # finally try the ingenious folder in pip install location
    ingenious_dir = Path(get_paths()["purelib"]) / Path("ingenious/")

    dirs = [extensions_dir, extensions_template_dir, ingenious_dir]

    return dirs


def get_namespaces():
    namespaces = [
        "ingenious_extensions",
        "ingenious.ingenious_extensions_template",
        "ingenious",
    ]

    return namespaces


def discover_workflows():
    """
    Dynamically discover all available workflows from all namespaces.
    This function searches through core Ingenious and extension namespaces
    to find available workflow modules.

    Returns:
        list: A list of workflow names (normalized with underscores)
    """
    workflows = set()

    # Get all possible namespaces to search
    namespaces = get_namespaces()

    for namespace in namespaces:
        try:
            # Try to import the conversation flows package
            flows_module_name = f"{namespace}.services.chat_services.multi_agent.conversation_flows"
            print(f"DEBUG: Searching for workflows in {flows_module_name}")

            try:
                flows_package = importlib.import_module(flows_module_name)
                if hasattr(flows_package, "__path__"):
                    # Iterate through all modules in the conversation_flows package
                    for module_info in pkgutil.iter_modules(flows_package.__path__):
                        workflow_name = module_info.name
                        print(f"DEBUG: Found potential workflow: {workflow_name}")

                        # Try to import the workflow module to verify it has ConversationFlow class
                        try:
                            workflow_module_name = f"{flows_module_name}.{workflow_name}.{workflow_name}"
                            workflow_module = importlib.import_module(workflow_module_name)

                            # Check if it has a ConversationFlow class
                            if hasattr(workflow_module, "ConversationFlow"):
                                workflows.add(workflow_name)
                                print(f"DEBUG: Confirmed workflow: {workflow_name}")

                        except (ImportError, AttributeError) as e:
                            print(f"DEBUG: Skipping {workflow_name} - not a valid workflow: {e}")
                            continue

            except ImportError as e:
                print(f"DEBUG: No conversation flows found in {namespace}: {e}")
                continue

        except Exception as e:
            print(f"DEBUG: Error searching namespace {namespace}: {e}")
            continue

    # Convert to sorted list
    return sorted(list(workflows))


def get_workflow_metadata(workflow_name):
    """
    Get metadata for a specific workflow.

    Args:
        workflow_name (str): The workflow name

    Returns:
        dict: Workflow metadata including description, category, etc.
    """
    # Default metadata structure
    default_metadata = {
        "description": "Custom workflow",
        "category": "Custom Workflow",
        "required_config": ["models", "chat_service"],
        "optional_config": [],
        "external_services": ["Azure OpenAI"],
    }

    # Define known workflow metadata
    known_workflows = {
        "classification_agent": {
            "description": "Route input to specialized agents based on content",
            "category": "Minimal Configuration",
            "required_config": ["models", "chat_service"],
            "optional_config": [],
            "external_services": ["Azure OpenAI"],
        },
        "bike_insights": {
            "description": "Sample domain-specific workflow for bike sales analysis",
            "category": "Minimal Configuration",
            "required_config": ["models", "chat_service"],
            "optional_config": [],
            "external_services": ["Azure OpenAI"],
        },
        "knowledge_base_agent": {
            "description": "Search and retrieve information from knowledge bases",
            "category": "Azure Search Required",
            "required_config": ["models", "chat_service", "azure_search_services"],
            "optional_config": [],
            "external_services": ["Azure OpenAI", "Azure Cognitive Search"],
        },
        "sql_manipulation_agent": {
            "description": "Execute SQL queries based on natural language",
            "category": "Database Required",
            "required_config": ["models", "chat_service"],
            "optional_config": ["azure_sql_services", "local_sql_db"],
            "external_services": ["Azure OpenAI", "Database (Azure SQL or SQLite)"],
        },
        "submission_over_criteria": {
            "description": "Evaluate submissions against specified criteria using multi-agent analysis",
            "category": "Custom Workflow",
            "required_config": ["models", "chat_service"],
            "optional_config": ["azure_blob_storage"],
            "external_services": ["Azure OpenAI", "Azure Blob Storage (for templates)"],
        },
    }

    return known_workflows.get(workflow_name, default_metadata)
