import asyncio
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBasicCredentials
from pydantic import BaseModel
from typing_extensions import Annotated

import ingenious.presentation.api.dependencies as igen_deps
from ingenious.infrastructure.storage.files_repository import FileStorage

logger = logging.getLogger(__name__)
router = APIRouter()


class UpdatePromptRequest(BaseModel):
    content: str


@router.get("/prompts/view/{revision_id}/{filename}")
def view(
    revision_id: str,
    filename: str,
    request: Request,
    credentials: Annotated[
        HTTPBasicCredentials, Depends(igen_deps.get_security_service)
    ],
    fs: FileStorage = Depends(igen_deps.get_file_storage_revisions),
):
    prompt_template_folder = asyncio.run(
        fs.get_prompt_template_path(revision_id=revision_id)
    )
    content = asyncio.run(
        fs.read_file(file_name=filename, file_path=prompt_template_folder)
    )
    return content


@router.get("/prompts/list/{revision_id}")
def list(
    revision_id: str,
    request: Request,
    credentials: Annotated[
        HTTPBasicCredentials, Depends(igen_deps.get_security_service)
    ],
    fs: FileStorage = Depends(igen_deps.get_file_storage_revisions),
):
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


@router.post("/prompts/update/{revision_id}/{filename}")
async def update(
    revision_id: str,
    filename: str,
    request: Request,
    update_request: UpdatePromptRequest,
    credentials: Annotated[
        HTTPBasicCredentials, Depends(igen_deps.get_security_service)
    ],
    fs: FileStorage = Depends(igen_deps.get_file_storage_revisions),
):
    prompt_template_folder = await fs.get_prompt_template_path(revision_id=revision_id)
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
