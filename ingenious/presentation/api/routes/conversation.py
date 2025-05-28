import logging

from fastapi import APIRouter, Depends, HTTPException
from typing_extensions import Annotated

from ingenious.domain.model.http_error import HTTPError
from ingenious.domain.model.message import Message
from ingenious.infrastructure.database.chat_history_repository import (
    ChatHistoryRepository,
)
from ingenious.presentation.api.dependencies import get_chat_history_repository

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/conversations/{thread_id}",
    responses={400: {"model": HTTPError, "description": "Bad Request"}},
)
async def get_conversation(
    thread_id: str,
    chat_history_repository: Annotated[
        ChatHistoryRepository, Depends(get_chat_history_repository)
    ],
) -> list[Message]:
    try:
        messages = await chat_history_repository.get_thread_messages(thread_id)
        return messages
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=400, detail=str(e))
