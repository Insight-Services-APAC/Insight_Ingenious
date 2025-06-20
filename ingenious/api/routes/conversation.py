import logging

from fastapi import APIRouter, HTTPException

from ingenious.models.http_error import HTTPError
from ingenious.models.message import Message

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/conversations/{thread_id}",
    responses={400: {"model": HTTPError, "description": "Bad Request"}},
)
async def get_conversation(
    thread_id: str,
) -> list[Message]:
    """
    Get conversation history for a thread.
    Note: Chat history repository was removed, so this returns an empty list.
    """
    try:
        # Since chat history repository was removed, return empty list
        return []
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=400, detail=str(e))
