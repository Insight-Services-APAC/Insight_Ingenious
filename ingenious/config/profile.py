import json
import yaml
import os
from pathlib import Path
from ingenious.models import profile as profile_models
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential


class Profiles(profile_models.Profiles):
    def __init__(self, profiles_path=None):
        self.profiles = Profiles._get_profiles(profiles_path)

    @staticmethod
    def from_yaml(file_path):
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            profiles = [profile_models.Profile(**profile) for profile in data]
            return profiles
    
    @staticmethod
    def from_yaml_str(profile_yml):
        data = yaml.safe_load(profile_yml)
        profiles = [profile_models.Profile(**profile) for profile in data]
        return profiles

    @staticmethod
    def _get_profiles(profiles_path=None):
        # Check if os.getenv('INGENIOUS_PROFILE') is set
        if os.getenv('APPSETTING_INGENIOUS_PROFILE', '') != '':
            print("Profile JSON loaded from environment variable")
            profile_string = os.getenv('APPSETTING_INGENIOUS_PROFILE', "{}")
            profile_object = json.loads(profile_string)
            # Convert the json string to a yaml string
            profile_yml = yaml.dump(profile_object)
            profile = Profiles.from_yaml_str(profile_yml)
            return profile

        # Load the configuration from the YAML file
        if profiles_path is None or profiles_path is '':
            if os.getenv('INGENIOUS_PROFILE_PATH', '') != '':
                print("Profile Path loaded from environment variable")
                profiles_path = Path(os.getenv('INGENIOUS_PROFILE_PATH'))
            else:
                print("Profile loaded from default path")
                home_directory = os.path.expanduser('~')
                profiles_path = Path(home_directory) / Path('.ingenious') / Path('profiles.yml')

        if Path(profiles_path).is_file(): #this might need to change to
            print("Profile loaded from file")
            profiles = Profiles.from_yaml(file_path=profiles_path)
        else:
            print("Profile loaded from key vault")
            profiles_yml = get_kv_secret(secretName="profileymlconfig")
            profiles = Profiles.from_yaml_str(profiles_yml)

        return profiles
    
    def get_profile_by_name(self, name):
        for profile in self.profiles:
            if profile.name == name:
                return profile
        return None

@staticmethod
def get_kv_secret(secretName):
    keyVaultName = os.environ["KEY_VAULT_NAME"]
    KVUri = f"https://{keyVaultName}.vault.azure.net"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=KVUri, credential=credential)
    secret = client.get_secret(secretName)
    return secret.value
