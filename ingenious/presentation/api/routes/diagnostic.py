import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBasicCredentials
from typing_extensions import Annotated

import ingenious.presentation.api.dependencies as igen_deps
from ingenious.domain.model.http_error import HTTPError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.api_route(
    "/diagnostic",
    methods=["GET", "OPTIONS"],
    responses={
        200: {"model": dict, "description": "Diagnostic information"},
        400: {"model": HTTPError, "description": "Bad Request"},
        406: {"model": HTTPError, "description": "Not Acceptable"},
        413: {"model": HTTPError, "description": "Payload Too Large"},
    },
)
async def diagnostic(
    request: Request,
    credentials: Annotated[
        HTTPBasicCredentials, Depends(igen_deps.get_security_service)
    ],
):
    if request.method == "OPTIONS":
        return {"Allow": "GET, OPTIONS"}

    try:
        diagnostic = {}

        prompt_dir = Path(
            await igen_deps.get_file_storage_revisions().get_base_path()
        ) / Path(
            await igen_deps.get_file_storage_revisions().get_prompt_template_path()
        )

        data_dir = Path(await igen_deps.get_file_storage_data().get_base_path()) / Path(
            await igen_deps.get_file_storage_data().get_data_path()
        )

        output_dir = Path(
            await igen_deps.get_file_storage_revisions().get_base_path()
        ) / Path(await igen_deps.get_file_storage_revisions().get_output_path())

        events_dir = Path(
            await igen_deps.get_file_storage_revisions().get_base_path()
        ) / Path(await igen_deps.get_file_storage_revisions().get_events_path())

        diagnostic["Prompt Directory"] = prompt_dir
        diagnostic["Data Directory"] = data_dir
        diagnostic["Output Directory"] = output_dir
        diagnostic["Events Directory"] = events_dir

        return diagnostic

    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))
