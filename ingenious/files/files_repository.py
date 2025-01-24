import importlib
from abc import ABC, abstractmethod
from ingenious.config.config import Config


class IFileStorage(ABC):
    def __init__(self, config: Config):
        self.config = config

    @abstractmethod
    async def write_file(self, contents: str, file_name: str, file_path: str, container_name: str) -> str:
        """ writes a file to the file storage """
        pass

    @abstractmethod
    async def read_file(self, file_name: str, file_path: str, container_name: str) -> str:
        """ reads a file to the file storage """
        pass

    @abstractmethod
    async def delete_file(self, file_name: str, file_path: str, container_name: str) -> str:
        """ deletes a file to the file storage """
        pass

    @abstractmethod
    async def list_files(self, file_path: str, container_name: str) -> str:
        """ lists files in the file storage """
        pass

    @abstractmethod
    async def check_if_file_exists(self, file_path: str, file_name: str, container_name: str) -> bool:
        """ checks if a file exists in the file storage """
        pass


class FileStorage:

    def __init__(self, config: Config):
        self.config = config
        module_name = \
            f"ingenious.files.{self.config.file_storage.storage_type.lower()}"
        class_name = \
            f"{self.config.file_storage.storage_type.lower()}_FileStorageRepository"

        try:
            module = importlib.import_module(module_name)
            repository_class = getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            raise ValueError(
                f"Unsupported File Storage client type: {module_name}.{class_name}"
            ) from e

        self.repository = repository_class()

    async def write_file(self, contents: str, file_name: str, file_path: str , container_name: str = 'container-app-deps'):
        return await self.repository.write_file(contents=contents, file_name=file_name, file_path=file_path, container_name=container_name)

    async def read_file(self, file_name: str, file_path: str, container_name: str= 'container-app-deps'):
        return await self.repository.read_file(file_name, file_path, container_name)

    async def delete_file(self, file_name: str, file_path: str, container_name: str= 'container-app-deps'):
        return await self.repository.delete_file(file_name, file_path, container_name)

    async def list_files(self, file_path: str, container_name: str = 'container-app-deps'):
        return await self.repository.list_files(file_path, container_name)
    
    async def check_if_file_exists(self, file_path: str, file_name: str, container_name: str= 'container-app-deps'):
        return await self.repository.check_if_file_exists(file_path, file_name, container_name)
