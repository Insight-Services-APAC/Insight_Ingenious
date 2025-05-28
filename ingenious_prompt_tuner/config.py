"""Configuration management for the prompt tuner app."""

import os
import sys
from pathlib import Path

# Set up parent directory and import dependencies
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

import ingenious.dependencies as ig_deps

# Load core configuration
config = ig_deps.get_config()

# App configuration
APP_CONFIG = {
    "SECRET_KEY": config.web_configuration.authentication.password,
    "USERNAME": config.web_configuration.authentication.username,
    "PASSWORD": config.web_configuration.authentication.password,
    "PORT": config.web_configuration.port,
    "HOST": config.web_configuration.ip_address,
    "REVISIONS_FOLDER": str(Path("revisions")),
    "TEMPLATE_FOLDER": os.path.abspath(
        os.path.join(parent_dir, "ingenious_extensions", "templates", "prompts")
    ),
    "FUNCTIONAL_TEST_DIR": os.path.abspath(
        os.path.join(parent_dir, "functional_test_outputs")
    ),
}

# Create required directories
os.makedirs(APP_CONFIG["FUNCTIONAL_TEST_DIR"], exist_ok=True)
os.makedirs(APP_CONFIG["REVISIONS_FOLDER"], exist_ok=True)
