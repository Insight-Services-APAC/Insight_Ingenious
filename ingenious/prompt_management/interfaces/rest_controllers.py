"""
Prompt Management REST controllers for the prompt_management bounded context.

This module contains FastAPI route handlers for prompt management operations.
"""

import asyncio
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBasicCredentials
from pydantic import BaseModel
from typing_extensions import Annotated

import ingenious.dependencies as igen_deps
from ingenious.file_management.application.services import (
    FileManagementApplicationService,
)

logger = logging.getLogger(__name__)


class UpdatePromptRequest(BaseModel):
    """Request model for updating prompts."""

    content: str


class PromptManagementController:
    """REST controller for prompt management operations."""

    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        """Setup the prompt management routes."""
        self.router.get("/prompts/view/{revision_id}/{filename}")(self.view_prompt)
        self.router.get("/prompts/list/{revision_id}")(self.list_prompts)
        self.router.post("/prompts/update/{revision_id}/{filename}")(self.update_prompt)

    def view_prompt(
        self,
        revision_id: str,
        filename: str,
        request: Request,
        credentials: Annotated[
            HTTPBasicCredentials, Depends(igen_deps.get_security_service)
        ],
        fs: FileManagementApplicationService = Depends(
            igen_deps.get_file_management_service
        ),
    ):
        """View a specific prompt template."""
        prompt_template_folder = asyncio.run(
            fs.get_prompt_template_path(revision_id=revision_id)
        )
        content = asyncio.run(
            fs.read_file(file_name=filename, file_path=prompt_template_folder)
        )
        return content

    def list_prompts(
        self,
        revision_id: str,
        request: Request,
        credentials: Annotated[
            HTTPBasicCredentials, Depends(igen_deps.get_security_service)
        ],
        fs: FileManagementApplicationService = Depends(
            igen_deps.get_file_management_service
        ),
    ):
        """List all prompt templates for a revision."""
        prompt_template_folder = asyncio.run(
            fs.get_prompt_template_path(revision_id=revision_id)
        )

        try:
            files_raw = asyncio.run(fs.list_files(file_path=prompt_template_folder))
            files = sorted(
                [Path(f).name for f in files_raw if f.endswith((".md", ".jinja"))]
            )
        except FileNotFoundError:
            files = []
        return files

    async def update_prompt(
        self,
        revision_id: str,
        filename: str,
        request: Request,
        update_request: UpdatePromptRequest,
        credentials: Annotated[
            HTTPBasicCredentials, Depends(igen_deps.get_security_service)
        ],
        fs: FileManagementApplicationService = Depends(
            igen_deps.get_file_management_service
        ),
    ):
        """Update a prompt template."""
        prompt_template_folder = await fs.get_prompt_template_path(
            revision_id=revision_id
        )
        try:
            await fs.write_file(
                contents=update_request.content,
                file_name=filename,
                file_path=prompt_template_folder,
            )
            return {"message": "File updated successfully"}
        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=500, detail="Failed to update file")


# Create router instance for FastAPI integration
router = APIRouter()
controller = PromptManagementController()
router.include_router(controller.router)
