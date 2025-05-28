import logging
from abc import ABC, abstractmethod

from fastapi import APIRouter, FastAPI
from fastapi.security import HTTPBasicCredentials

from ingenious.domain.model.config import Config
from ingenious.presentation.api.dependencies import (
    get_chat_history_repository,
    get_security_service,
)


class IApiRoutes(ABC):
    def __init__(self, config: Config, app: FastAPI):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.app = app
        self.security_service = get_security_service(HTTPBasicCredentials)
        self.chat_history_repository = get_chat_history_repository()

    @abstractmethod
    def add_custom_routes(self) -> APIRouter:
        """
        Adds custom routes to the FastAPI app instance. Always returns the router instance.
        """
        pass
