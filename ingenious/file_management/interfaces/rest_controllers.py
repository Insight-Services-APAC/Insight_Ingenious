"""
File Management REST controllers for the file_management bounded context.

This module contains FastAPI route handlers for file operations including
file upload, download, listing, and directory management.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi import File as FastAPIFile
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasicCredentials
from pydantic import BaseModel
from typing_extensions import Annotated

import ingenious.dependencies as igen_deps
from ingenious.shared.domain.models import HTTPError

from ..application.services import FileManagementApplicationService

logger = logging.getLogger(__name__)


# Request/Response models
class CreateFileRequest(BaseModel):
    name: str
    path: str
    content: str = ""


class CreateDirectoryRequest(BaseModel):
    path: str


class FileResponseModel(BaseModel):
    file_id: str
    name: str
    path: str
    size: Optional[int] = None
    content_type: Optional[str] = None
    created_at: Optional[str] = None
    modified_at: Optional[str] = None


class DirectoryResponse(BaseModel):
    directory_id: str
    name: str
    path: str
    created_at: Optional[str] = None


class FileSystemObjectResponse(BaseModel):
    name: str
    path: str
    is_directory: bool
    size: Optional[int] = None


class FileManagementController:
    """REST controller for file management operations."""

    def __init__(self, file_app_service: FileManagementApplicationService):
        self._file_app_service = file_app_service
        self._router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        """Setup the file management routes."""
        # File operations
        self._router.post(
            "/files",
            responses={
                201: {"model": FileResponseModel, "description": "File created"},
                400: {"model": HTTPError, "description": "Bad request"},
            },
        )(self.create_file)

        self._router.post(
            "/files/upload",
            responses={
                201: {"model": FileResponseModel, "description": "File uploaded"},
                400: {"model": HTTPError, "description": "Bad request"},
            },
        )(self.upload_file)

        self._router.get(
            "/files/{file_id}",
            responses={
                200: {"model": FileResponseModel, "description": "File details"},
                404: {"model": HTTPError, "description": "File not found"},
            },
        )(self.get_file)

        self._router.get(
            "/files/{file_id}/download",
            responses={
                200: {"description": "File content"},
                404: {"model": HTTPError, "description": "File not found"},
            },
        )(self.download_file)

        self._router.delete(
            "/files/{file_id}",
            responses={
                200: {"model": dict, "description": "File deleted"},
                404: {"model": HTTPError, "description": "File not found"},
            },
        )(self.delete_file)

        # Directory operations
        self._router.post(
            "/directories",
            responses={
                201: {"model": DirectoryResponse, "description": "Directory created"},
                400: {"model": HTTPError, "description": "Bad request"},
            },
        )(self.create_directory)

        self._router.get(
            "/directories/{directory_path:path}/contents",
            responses={
                200: {
                    "model": List[FileSystemObjectResponse],
                    "description": "Directory contents",
                },
                404: {"model": HTTPError, "description": "Directory not found"},
            },
        )(self.list_directory_contents)

        self._router.delete(
            "/directories/{directory_path:path}",
            responses={
                200: {"model": dict, "description": "Directory deleted"},
                404: {"model": HTTPError, "description": "Directory not found"},
            },
        )(self.delete_directory)

    @property
    def router(self) -> APIRouter:
        """Get the FastAPI router."""
        return self._router

    async def create_file(
        self,
        file_request: CreateFileRequest,
        credentials: Annotated[
            HTTPBasicCredentials, Depends(igen_deps.get_security_service)
        ],
    ) -> FileResponse:
        """Create a new file."""
        try:
            result = await self._file_app_service.create_file(
                name=file_request.name,
                path=file_request.path,
                content=file_request.content,
            )

            if result.get("success", True):
                return FileResponse(
                    file_id=result["file_id"],
                    name=result["name"],
                    path=result["path"],
                    size=result.get("size"),
                    content_type=result.get("content_type"),
                    created_at=result.get("created_at"),
                    modified_at=result.get("modified_at"),
                )
            else:
                raise HTTPException(
                    status_code=400, detail=result.get("error", "File creation failed")
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=500, detail="File creation failed")

    async def upload_file(
        self,
        file: UploadFile = FastAPIFile(...),
        path: str = "/",
        credentials: Annotated[
            HTTPBasicCredentials, Depends(igen_deps.get_security_service)
        ] = None,
    ) -> FileResponse:
        """Upload a file."""
        try:
            content = await file.read()
            content_str = (
                content.decode("utf-8")
                if file.content_type and "text" in file.content_type
                else str(content)
            )

            result = await self._file_app_service.create_file(
                name=file.filename,
                path=path,
                content=content_str,
                metadata={"content_type": file.content_type, "size": file.size},
            )

            if result.get("success", True):
                return FileResponse(
                    file_id=result["file_id"],
                    name=result["name"],
                    path=result["path"],
                    size=result.get("size"),
                    content_type=result.get("content_type"),
                    created_at=result.get("created_at"),
                    modified_at=result.get("modified_at"),
                )
            else:
                raise HTTPException(
                    status_code=400, detail=result.get("error", "File upload failed")
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=500, detail="File upload failed")

    async def get_file(
        self,
        file_id: str,
        credentials: Annotated[
            HTTPBasicCredentials, Depends(igen_deps.get_security_service)
        ],
    ) -> FileResponse:
        """Get file details."""
        try:
            result = await self._file_app_service.get_file(file_id)

            if result.get("success", True):
                return FileResponse(
                    file_id=result["file_id"],
                    name=result["name"],
                    path=result["path"],
                    size=result.get("size"),
                    content_type=result.get("content_type"),
                    created_at=result.get("created_at"),
                    modified_at=result.get("modified_at"),
                )
            else:
                raise HTTPException(
                    status_code=404, detail=result.get("error", "File not found")
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=500, detail="Failed to get file")

    async def download_file(
        self,
        file_id: str,
        credentials: Annotated[
            HTTPBasicCredentials, Depends(igen_deps.get_security_service)
        ],
    ):
        """Download file content."""
        try:
            result = await self._file_app_service.get_file_content(file_id)

            if result.get("success", True):
                # TODO: Return actual file response - this is a simplified version
                return {"content": result["content"], "filename": result["name"]}
            else:
                raise HTTPException(
                    status_code=404, detail=result.get("error", "File not found")
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=500, detail="Failed to download file")

    async def delete_file(
        self,
        file_id: str,
        credentials: Annotated[
            HTTPBasicCredentials, Depends(igen_deps.get_security_service)
        ],
    ) -> dict:
        """Delete a file."""
        try:
            result = await self._file_app_service.delete_file(file_id)

            if result.get("success", True):
                return {"success": True, "message": "File deleted successfully"}
            else:
                raise HTTPException(
                    status_code=404, detail=result.get("error", "File not found")
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=500, detail="Failed to delete file")

    async def create_directory(
        self,
        directory_request: CreateDirectoryRequest,
        credentials: Annotated[
            HTTPBasicCredentials, Depends(igen_deps.get_security_service)
        ],
    ) -> DirectoryResponse:
        """Create a new directory."""
        try:
            result = await self._file_app_service.create_directory(
                directory_request.path
            )

            if result.get("success", True):
                return DirectoryResponse(
                    directory_id=result["directory_id"],
                    name=result["name"],
                    path=result["path"],
                    created_at=result.get("created_at"),
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=result.get("error", "Directory creation failed"),
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=500, detail="Directory creation failed")

    async def list_directory_contents(
        self,
        directory_path: str,
        credentials: Annotated[
            HTTPBasicCredentials, Depends(igen_deps.get_security_service)
        ],
    ) -> List[FileSystemObjectResponse]:
        """List directory contents."""
        try:
            result = await self._file_app_service.list_directory_contents(
                directory_path
            )

            if result.get("success", True):
                return [
                    FileSystemObjectResponse(
                        name=obj["name"],
                        path=obj["path"],
                        is_directory=obj["is_directory"],
                        size=obj.get("size"),
                    )
                    for obj in result["contents"]
                ]
            else:
                raise HTTPException(
                    status_code=404, detail=result.get("error", "Directory not found")
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=500, detail="Failed to list directory contents"
            )

    async def delete_directory(
        self,
        directory_path: str,
        credentials: Annotated[
            HTTPBasicCredentials, Depends(igen_deps.get_security_service)
        ],
    ) -> dict:
        """Delete a directory."""
        try:
            result = await self._file_app_service.delete_directory(directory_path)

            if result.get("success", True):
                return {"success": True, "message": "Directory deleted successfully"}
            else:
                raise HTTPException(
                    status_code=404, detail=result.get("error", "Directory not found")
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=500, detail="Failed to delete directory")


# Create router instance for FastAPI integration
# Note: In production, this should be managed by a DI container
from ..application.use_cases import DirectoryManagementUseCase, FileManagementUseCase
from ..infrastructure.services import (
    FileSystemDirectoryService,
    FileSystemFileRepository,
    FileSystemMetadataService,
    LocalFileStorageService,
)

# Default service instances (TODO: Move to proper DI configuration)
storage_service = LocalFileStorageService()
file_repo = FileSystemFileRepository(storage_service)
directory_service = FileSystemDirectoryService()
metadata_service = FileSystemMetadataService()

file_use_case = FileManagementUseCase(
    file_repo, storage_service, directory_service, metadata_service
)
directory_use_case = DirectoryManagementUseCase(directory_service)

file_app_service = FileManagementApplicationService(file_use_case, directory_use_case)

controller = FileManagementController(file_app_service)
router = controller.router
