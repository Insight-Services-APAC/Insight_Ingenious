import logging
import os
import sys

from fastapi import APIRouter, HTTPException

import ingenious.common.utils.namespace_utils as ns_utils
from ingenious.application.factory import Factory
from ingenious.common.config.config import get_config
from ingenious.common.errors.content_filter_error import ContentFilterError
from ingenious.common.errors.token_limit_exceeded_error import TokenLimitExceededError
from ingenious.domain.model.chat import ChatRequest, ChatResponse
from ingenious.domain.model.http_error import HTTPError

logger = logging.getLogger(__name__)
router = APIRouter()

parent_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../../../../..")
)
sys.path.append(parent_dir)


@router.post(
    "/chat",
    responses={
        400: {"model": HTTPError, "description": "Bad Request"},
        406: {"model": HTTPError, "description": "Not Acceptable"},
        413: {"model": HTTPError, "description": "Payload Too Large"},
    },
)
async def chat(
    chat_request: ChatRequest,
) -> ChatResponse:
    try:
        config = get_config()
        factory = Factory(config)
        chat_service = factory.get_chat_service(chat_request.conversation_flow)

        ns_utils.print_namespace_modules(
            "ingenious.application.service.chat.multi_agent.conversation_flows"
        )
        if not chat_request.conversation_flow:
            raise ValueError(f"conversation_flow not set {chat_request}")
        return await chat_service.get_chat_response(chat_request)
    except ValueError as e:
        logger.exception(e)
        raise HTTPException(status_code=400, detail=str(e))
    except ContentFilterError as cfe:
        logger.exception(cfe)
        raise HTTPException(status_code=406, detail=ContentFilterError.DEFAULT_MESSAGE)
    except TokenLimitExceededError as tle:
        logger.exception(tle)
        raise HTTPException(
            status_code=413, detail=TokenLimitExceededError.DEFAULT_MESSAGE
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))
