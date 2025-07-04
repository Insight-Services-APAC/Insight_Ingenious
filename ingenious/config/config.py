import json
import logging
import os
import re
from pathlib import Path

import yaml
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from pydantic import ValidationError

from ingenious.config.profile import Profiles
from ingenious.models import config as config_models
from ingenious.models import config_ns as config_ns_models
from ingenious.models import profile as profile_models

logger = logging.getLogger(__name__)


def substitute_environment_variables(yaml_content: str) -> str:
    """
    Substitute environment variables in YAML content.
    Supports patterns like ${VAR_NAME} and ${VAR_NAME:default_value}
    """

    def replacer(match):
        var_expr = match.group(1)
        if ":" in var_expr:
            var_name, default_value = var_expr.split(":", 1)
            return os.getenv(var_name, default_value)
        else:
            var_name = var_expr
            env_value = os.getenv(var_name)
            if env_value is None:
                logger.warning(
                    f"Environment variable {var_name} not found and no default provided"
                )
                return match.group(0)  # Return original if no env var found
            return env_value

    # Pattern matches ${VAR_NAME} or ${VAR_NAME:default}
    pattern = r"\$\{([^}]+)\}"
    return re.sub(pattern, replacer, yaml_content)


class Config(config_models.Config):
    """
    Class to handle loading the configuration file
    """

    @staticmethod
    def from_yaml(file_path):
        with open(file_path, "r") as file:
            file_str = file.read()
            # Substitute environment variables before parsing
            file_str = substitute_environment_variables(file_str)
            return Config.from_yaml_str(file_str)

    @staticmethod
    def from_yaml_str(config_yml):
        # Substitute environment variables in the YAML string
        config_yml = substitute_environment_variables(config_yml)
        yaml_data = yaml.safe_load(config_yml)
        json_data = json.dumps(yaml_data)
        config_ns: config_ns_models.Config
        try:
            config_ns = config_ns_models.Config.model_validate_json(json_data)
        except ValidationError as e:
            # Enhanced error messages with helpful suggestions
            error_messages = []
            for error in e.errors():
                field_path = ".".join(str(part) for part in error["loc"])
                error_msg = error["msg"]
                error_type = error["type"]

                # Provide helpful suggestions based on common errors
                suggestion = ""
                if "string_type" in error_type and "endpoint" in field_path:
                    suggestion = "\n💡 Suggestion: Use a placeholder like 'https://placeholder.search.windows.net' if you don't have Azure Search"
                elif "string_type" in error_type and "database" in field_path:
                    suggestion = "\n💡 Suggestion: Use a placeholder like 'placeholder_db' if you don't have a database"
                elif "string_type" in error_type and "csv_path" in field_path:
                    suggestion = "\n💡 Suggestion: Use a placeholder like './sample_data.csv' if you don't have CSV files"
                elif "string_type" in error_type and any(
                    x in field_path for x in ["key", "secret", "password"]
                ):
                    suggestion = "\n💡 Suggestion: Use a placeholder like 'placeholder_key' for unused services"
                elif "string_type" in error_type and "url" in field_path:
                    suggestion = "\n💡 Suggestion: Use a placeholder like 'placeholder_url' for unused services"

                enhanced_msg = (
                    f"❌ Configuration Error in '{field_path}': {error_msg}{suggestion}"
                )
                error_messages.append(enhanced_msg)
                logger.debug(enhanced_msg)

            # Create a comprehensive error message
            full_error_msg = "\n🔧 Configuration Validation Failed:\n" + "\n".join(
                error_messages
            )
            full_error_msg += "\n\n🚀 Quick Fix: Run 'ingen init' to regenerate config files with valid placeholders"
            full_error_msg += (
                "\n📖 Or see: docs/QUICKSTART.md for configuration examples"
            )

            # Create a new exception with enhanced message
            enhanced_error = ValidationError.from_exception_data("Config", e.errors())
            enhanced_error.args = (full_error_msg,)
            raise enhanced_error
        except Exception as e:
            logger.debug(f"Unexpected error during validation: {e}")
            enhanced_msg = f"🔧 Configuration Error: {str(e)}\n💡 Try running 'ingen validate' to diagnose issues"
            e.args = (enhanced_msg,)
            raise e

        profile_data: profile_models.Profiles = Profiles(
            os.getenv("INGENIOUS_PROFILE_PATH", "")
        )
        profile_object: profile_models.Profile = profile_data.get_profile_by_name(
            config_ns.profile
        )
        if profile_object is None:
            raise ValueError(f"Profile {config_ns.profile} not found in profiles.yml")

        config: config_models.Config = config_models.Config(config_ns, profile_object)

        return config


@staticmethod
def get_kv_secret(secretName):
    # check if the key vault name is set in the environment variables
    if "KEY_VAULT_NAME" in os.environ:
        keyVaultName = os.environ["KEY_VAULT_NAME"]
        KVUri = f"https://{keyVaultName}.vault.azure.net"
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=KVUri, credential=credential)
        secret = client.get_secret(secretName)
        return secret.value
    else:
        raise ValueError("KEY_VAULT_NAME environment variable not set")


@staticmethod
def get_config(config_path=None) -> config_models.Config:
    # Check if os.getenv('INGENIOUS_CONFIG') is set
    if os.getenv("APPSETTING_INGENIOUS_CONFIG"):
        config_string = os.getenv("APPSETTING_INGENIOUS_CONFIG", "")
        config_object = json.loads(config_string)
        # Convert the json string to a yaml string
        config_yml = yaml.dump(config_object)
        config = Config.from_yaml_str(config_yml)
        return config

    if config_path is None:
        env_config_path = os.getenv("INGENIOUS_PROJECT_PATH")
        if env_config_path:
            # INGENIOUS_PROJECT_PATH should point directly to the config file
            config_path = Path(env_config_path)
        else:
            # Use the default config file
            current_path = Path.cwd()
            config_path = current_path / "config.yml"

    path = Path(config_path)

    if path.exists():
        if path.is_file():
            logger.debug("Config loaded from file")
            config = Config.from_yaml(config_path)
            return config

        else:
            logger.debug(
                f"Config file at {config_path} is not a file. Falling back to key vault"
            )
            try:
                config_str = get_kv_secret("config")
                config = Config.from_yaml_str(config_str)
                return config
            except Exception:
                raise ValueError(
                    f"Config file at {config_path} is not a file. Tried falling back to key vault but KEY_VAULT_NAME environment variable not set"
                )

    else:
        logger.debug(f"No config file found at {config_path}")
        exit(1)
