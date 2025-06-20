import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasicCredentials
from typing_extensions import Annotated

from ..domain.models import ChatRequest, ChatResponse
from ..application.services import ChatApplicationService
from ..infrastructure.services import LegacyChatServiceAdapter
from ingenious.dependencies import get_chat_service
from ingenious.errors.content_filter_error import ContentFilterError
from ingenious.errors.token_limit_exceeded_error import TokenLimitExceededError
from ingenious.models.http_error import HTTPError
import ingenious.dependencies as igen_deps


logger = logging.getLogger(__name__)


class ChatController:
    """REST API controller for chat operations."""

    def __init__(self, chat_app_service: ChatApplicationService):
        self._chat_app_service = chat_app_service
        self._router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        """Setup API routes."""
        self._router.post(
            "/chat",
            responses={
                400: {"model": HTTPError, "description": "Bad Request"},
                406: {"model": HTTPError, "description": "Not Acceptable"},
                413: {"model": HTTPError, "description": "Payload Too Large"},
            },
        )(self.chat)

    @property
    def router(self) -> APIRouter:
        """Get the FastAPI router."""
        return self._router

    async def chat(
        self,
        chat_request: ChatRequest,
        credentials: Annotated[
            HTTPBasicCredentials, Depends(igen_deps.get_security_service)
        ],
    ) -> ChatResponse:
        """Handle chat requests."""
        try:
            if not chat_request.conversation_flow:
                raise ValueError(f"conversation_flow not set {chat_request}")

            return await self._chat_app_service.process_chat(chat_request)

        except ValueError as e:
            logger.exception(e)
            raise HTTPException(status_code=400, detail=str(e))
        except ContentFilterError as cfe:
            logger.exception(cfe)
            raise HTTPException(
                status_code=406, detail=ContentFilterError.DEFAULT_MESSAGE
            )
        except TokenLimitExceededError as tle:
            logger.exception(tle)
            raise HTTPException(
                status_code=413, detail=TokenLimitExceededError.DEFAULT_MESSAGE
            )
        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=500, detail=str(e))
