import json
import logging
import os
from pathlib import Path

import yaml
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from ingenious.models import profile as profile_models

logger = logging.getLogger(__name__)


class Profiles:
    def __init__(self, profiles_path=None):
        self.profiles: profile_models.Profiles = Profiles._get_profiles(profiles_path)

    @staticmethod
    def from_yaml_str(profile_yml):
        yaml_data = yaml.safe_load(profile_yml)
        json_data = json.dumps(yaml_data)
        try:
            profiles = profile_models.Profiles.model_validate_json(json_data).root
        except profile_models.ValidationError as e:
            for error in e.errors():
                print(
                    f"Validation error in \
                    field '{error['loc']}': {error['msg']}"
                )
            raise e
        except Exception as e:
            print(f"Unexpected error during validation: {e}")
            raise e
        return profiles

    @staticmethod
    def from_yaml(file_path):
        with open(file_path, "r") as file:
            file_str = file.read()
            profiles = Profiles.from_yaml_str(file_str)
            return profiles

    @staticmethod
    def _get_profiles(profiles_path=None):
        # Check if os.getenv('INGENIOUS_PROFILE') is set
        if os.getenv("APPSETTING_INGENIOUS_PROFILE", "") != "":
            profile_string = os.getenv("APPSETTING_INGENIOUS_PROFILE", "{}")

            # Try YAML first (new standard)
            try:
                profile = Profiles.from_yaml_str(profile_string)
                logger.debug("Profile loaded as YAML")
                return profile
            except yaml.YAMLError:
                # Fallback to JSON for backward compatibility
                try:
                    profile_object = json.loads(profile_string)
                    profile_yml = yaml.dump(profile_object)
                    profile = Profiles.from_yaml_str(profile_yml)
                    logger.debug("Profile loaded as JSON")
                    return profile
                except json.JSONDecodeError as e:
                    raise ValueError(f"Contains invalid YAML or JSON: {e}")

        # Load the configuration from the YAML file
        if profiles_path is None or profiles_path == "":
            if os.getenv("INGENIOUS_PROFILE_PATH", "") != "":
                print("Profile Path loaded from environment variable")
                profiles_path_object = Path(os.getenv("INGENIOUS_PROFILE_PATH"))
            else:
                print("Profile loaded from default path")
                home_directory = os.path.expanduser("~")
                profiles_path_object = (
                    Path(home_directory) / Path(".ingenious") / Path("profiles.yml")
                )
        else:
            profiles_path_object = Path(profiles_path)

        if profiles_path_object.is_file():
            print("Profile loaded from file")
            profiles = Profiles.from_yaml(file_path=str(profiles_path_object))
        else:
            print(f"Profile not found at {profiles_path}")
            print("Trying to load profile from key vault")
            profiles_yml = get_kv_secret(secretName="profile")
            profiles = Profiles.from_yaml_str(profiles_yml)

        return profiles

    def get_profile_by_name(self, name):
        for profile in self.profiles:
            if profile.name == name:
                return profile
        return None


@staticmethod
def get_kv_secret(secretName):
    try:
        keyVaultName = os.environ["KEY_VAULT_NAME"]
    except KeyError:
        raise ValueError("KEY_VAULT_NAME environment variable not set")

    KVUri = f"https://{keyVaultName}.vault.azure.net"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=KVUri, credential=credential)
    secret = client.get_secret(secretName)
    return secret.value
