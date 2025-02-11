import ingenious.dependencies as ig_deps
from ingenious.files.files_repository import IFileStorage
from pathlib import Path
import aiofiles


class local_FileStorageRepository(IFileStorage):

    def __init__(self):
        self.config = ig_deps.config
        self.base_path = Path(self.config.file_storage.path)

    async def write_file(self, contents: str, file_name: str, file_path: str, container_name: str):
        """
        Write data to a local file.

        :param contents: Data to write to the file.
        :param file_name: Name of the file to create.
        :param file_path: Path to the file.
        """
        try:
            path = Path(self.config.file_storage.path) / Path(file_path) / Path(file_name)
            path.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(path, "w") as f:
                await f.write(contents)
            # print(f"Successfully wrote {path}.")
        except Exception as e:
            print(f"Failed to write {path}: {e}")

    async def read_file(self, file_name: str, file_path: str, container_name: str):
        """
        Read data from a local file.

        :param file_name: Name of the file to read.
        :param file_path: Path to the file.
        :return: Contents of the file.
        """
        try:
            path = Path(self.config.file_storage.path) / Path(file_path) / Path(file_name)
            async with aiofiles.open(path, "r") as f:
                contents = await f.read()
                # print(f"Successfully read {path}.")
                return contents
        except Exception as e:
            print(f"Failed to read {path}: {e}")
            return None
        
    async def delete_file(self, file_name: str, file_path: str, container_name: str):
        """
        Delete a local file.

        :param file_name: Name of the file to delete.
        :param file_path: Path to the file.
        """
        try:
            path = Path(self.config.file_storage.path) / Path(file_path) / Path(file_name)
            Path(path).unlink()
            # print(f"Successfully deleted {path}.")
        except Exception as e:
            print(f"Failed to delete {path}: {e}")
    
    async def list_files(self, file_path: str, container_name: str):
        """
        List files in a local directory.

        :param file_path: Path to the directory.
        """
        try:
            path = Path(self.config.file_storage.path) / Path(file_path)
            files = [f.name for f in path.iterdir() if f.is_file()]
            # print(f"Files in {path}: {files}")
            return files
        except Exception as e:
            print(f"Failed to list files in {path}: {e}")
            return None
        
    async def check_if_file_exists(self, file_path: str, file_name: str, container_name: str) -> bool:
        """
        Check if a local file exists.

        :param file_path: Path to the file.
        :param file_name: Name of the file.
        :return: True if the file exists, False otherwise.
        """
        try:
            path = Path(self.config.file_storage.path) / Path(file_path) / Path(file_name)
            exists = path.exists()
            # print(f"File {file_name} exists in {path}: {exists}")
            return exists
        except Exception as e:
            print(f"Failed to check if {file_name} exists in {path}: {e}")
            return False
