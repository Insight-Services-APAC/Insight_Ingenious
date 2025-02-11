from azure.storage.blob import BlobServiceClient
from azure.identity import ManagedIdentityCredential
import ingenious.dependencies as ig_deps
from ingenious.files.files_repository import IFileStorage
from pathlib import Path


class azure_FileStorageRepository(IFileStorage):

    def __init__(self):
        self.config = ig_deps.config
        self.url = self.config.file_storage.url
        self.token  = self.config.file_storage.token
        self.client_id = self.config.file_storage.token
        self.container_name = 'container-app-deps' #self.config.file_storage.container_name
        self.test = False

        if self.test:
            self.blob_service_client = BlobServiceClient(account_url=self.url, credential=self.token)
        else:
            self.blob_service_client = BlobServiceClient(account_url=self.url, credential=ManagedIdentityCredential(client_id=self.client_id))


    async def write_file(self, contents: str, file_name: str, file_path: str, container_name: str = 'container-app-deps'):
        """
        Asynchronously writes the given contents to a file in Azure Blob Storage.
        Args:
            contents (str): The contents to write to the file.
            file_name (str): The name of the file to write.
            file_path (str): The path within the storage container where the file will be written.
        Raises:
            Exception: If there is an error during the upload process.
        Example:
            await write_file("Hello, World!", "example.txt", "path/to/directory")
        """
        self.container_name = container_name
        if self.test:
            self.blob_service_client = BlobServiceClient(account_url=self.url, credential=self.token)
            if container_name == "container-app-deps":
                self.token = self.config.azure_search_services[0].key
            else:
                self.token = self.config.file_storage.token
        else:
            self.blob_service_client = BlobServiceClient(account_url=self.url, credential=ManagedIdentityCredential(client_id=self.client_id))

        try:
            path = Path(self.config.file_storage.path) / Path(file_path) / Path(file_name)
            # Create the container if it does not exist
            container_client = self.blob_service_client.get_container_client(self.container_name)
            if not container_client.container_name:
                container_client.create_container()

            # Create a blob client
            blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=str(path))

            # Upload the data
            blob_client.upload_blob(contents, overwrite=True)
            #print(f"Successfully uploaded {path} to container {self.container_name}.")
        except Exception as e:
            print(f"Failed to upload {path} to container {self.container_name}: {e}")

    async def read_file(self, file_name: str, file_path: str, container_name: str = 'container-app-deps') -> str:
        """
        Download data from Azure Blob Storage.

        :param file_name: Name of the blob (file) to read.
        :param file_path: Path of the blob (file) to read.
        """
        self.container_name = container_name
        if self.test:
            self.blob_service_client = BlobServiceClient(account_url=self.url, credential=self.token)
            if container_name == "container-app-deps":
                self.token = self.config.azure_search_services[0].key
            else:
                self.token = self.config.file_storage.token
        else:
            self.blob_service_client = BlobServiceClient(account_url=self.url,
                                                         credential=ManagedIdentityCredential(client_id=self.client_id))


        try:
            path = Path(self.config.file_storage.path) / Path(file_path) / Path(file_name)
            # Create a blob client
            blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=str(path))

            # encoding param is necessary for readall() to return str, otherwise it returns bytes
            downloader = blob_client.download_blob(max_concurrency=1, encoding='UTF-8')
            data = downloader.readall()

            #print(f"Successfully downloaded {path} from container {self.container_name}.")
            return data
        except Exception as e:
            print(f"Failed to download {path} from container {self.container_name}: {e}")
            return ""

    async def delete_file(self, file_name: str, file_path: str, container_name: str = 'container-app-deps'):
        """
        Delete a blob from Azure Blob Storage.

        :param file_name: Name of the blob (file) to delete.
        :param file_path: Path of the blob (file) to delete.
        """
        self.container_name = container_name
        if self.test:
            self.blob_service_client = BlobServiceClient(account_url=self.url, credential=self.token)
            if container_name == "container-app-deps":
                self.token = self.config.azure_search_services[0].key
            else:
                self.token = self.config.file_storage.token
        else:
            self.blob_service_client = BlobServiceClient(account_url=self.url,
                                                         credential=ManagedIdentityCredential(client_id=self.client_id))

        try:
            path = Path(self.config.file_storage.path) / Path(file_path) / Path(file_name)
            # Create a blob client
            blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=str(path))

            # Delete the blob
            blob_client.delete_blob()
            #print(f"Successfully deleted {path} from container {self.container_name}.")
        except Exception as e:
            print(f"Failed to delete {path} from container {self.container_name}: {e}")


    async def list_files(self, file_path: str, container_name: str = 'container-app-deps'):
        """
        List blobs in an Azure Blob container based on a path.

        :param file_path: Path within the storage container to list blobs from.
        """
        self.container_name = container_name
        if self.test:
            self.blob_service_client = BlobServiceClient(account_url=self.url, credential=self.token)
            if container_name == "container-app-deps":
                self.token = self.config.azure_search_services[0].key
            else:
                self.token = self.config.file_storage.token
        else:
            self.blob_service_client = BlobServiceClient(account_url=self.url,
                                                         credential=ManagedIdentityCredential(client_id=self.client_id))


        try:
            path = Path(self.config.file_storage.path) / Path(file_path)
            prefix = str(path).replace("\\", "/")  # Ensure the path is in the correct format for Azure

            # List blobs in the container with the specified prefix
            container_client = self.blob_service_client.get_container_client(self.container_name)
            blobs = [blob.name for blob in container_client.list_blobs(name_starts_with=prefix)]
            #print(f"Blobs in container {self.container_name} with prefix {prefix}: {blobs}")
            return blobs
        except Exception as e:
            print(f"Failed to list blobs in container {self.container_name} with prefix {prefix}: {e}")
            return []

    async def check_if_file_exists(self, file_path: str, file_name: str, container_name: str = 'container-app-deps') -> bool:
        """
        Check if a blob exists in an Azure Blob container.

        :param container_name: Name of the Azure Blob container.
        :param blob_name: Name of the blob (file) to check.
        :param connection_string: Connection string to Azure Storage account.
        :return: True if the blob exists, False otherwise.
        """
        self.container_name = container_name
        if self.test:
            self.blob_service_client = BlobServiceClient(account_url=self.url, credential=self.token)
            if container_name == "container-app-deps":
                self.token = self.config.azure_search_services[0].key
            else:
                self.token = self.config.file_storage.token
        else:
            self.blob_service_client = BlobServiceClient(account_url=self.url,
                                                         credential=ManagedIdentityCredential(client_id=self.client_id))


        try:
            path = Path(self.config.file_storage.path) / Path(file_path) / Path(file_name)
            # Create a blob client
            blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=str(path))
            exists = blob_client.exists()
            #print(f"Blob {path} exists in container {self.container_name}: {exists}")
            return exists
        except Exception as e:
            print(f"Failed to check if blob {path} exists in container {self.container_name}: {e}")
            return False