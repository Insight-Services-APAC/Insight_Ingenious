import logging

from fastapi import APIRouter, HTTPException

from ingenious.models.http_error import HTTPError
from ingenious.models.message_feedback import (
    MessageFeedbackRequest,
    MessageFeedbackResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.put(
    "/messages/{message_id}/feedback",
    responses={400: {"model": HTTPError, "description": "Bad Request"}},
)
async def submit_message_feedback(
    message_id: str,
    message_feedback_request: MessageFeedbackRequest,
) -> MessageFeedbackResponse:
    """
    Submit message feedback.
    Note: MessageFeedbackService was removed, so this returns a simple response.
    """
    try:
        # Since MessageFeedbackService was removed, return simple success response
        return MessageFeedbackResponse(
            message_id=message_id,
            feedback_type=message_feedback_request.feedback_type,
            success=True,
            message="Feedback received (not persisted - feedback service removed)",
        )
    except ValueError as e:
        logger.exception(e)
        raise HTTPException(status_code=400, detail=str(e))
