"""
Module for handling FastAPI app configuration.
This module contains classes and functions for initializing and configuring FastAPI application settings.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ingenious.domain.model.config import Config
from ingenious.presentation.api.managers.base_manager import IManager

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class AppConfigurationManager(IManager):
    """
    Manages the configuration of a FastAPI application.

    This class handles setting up middleware, CORS, and other application-level settings.
    It follows the single responsibility principle by focusing solely on app configuration.
    """

    def __init__(self, app: FastAPI, config: Config):
        """
        Initialize the AppConfigurationManager.

        Args:
            app: The FastAPI application instance to configure
            config: The Ingenious application configuration
        """
        self.app = app
        self.config = config

    def configure_cors(self, origins=None):
        """
        Configure CORS for the FastAPI application.

        Args:
            origins: List of allowed origins for CORS. If None, defaults to localhost settings.
        """
        if origins is None:
            origins = [
                "http://localhost",
                "http://localhost:5173",
                "http://localhost:4173",
            ]

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def configure_exception_handling(self):
        """
        Configure exception handling for the FastAPI application.

        This adds a generic exception handler to the application.
        """
        self.app.add_exception_handler(Exception, self._generic_exception_handler)

    async def _generic_exception_handler(self, request: Request, exc: Exception):
        """
        Handler for all exceptions in the application.

        Args:
            request: The FastAPI request instance
            exc: The exception that was raised

        Returns:
            JSONResponse with error details
        """
        # Log the exception
        logger.exception(exc)

        return JSONResponse(
            status_code=500, content={"detail": f"An error occurred: {str(exc)}"}
        )

    def configure(self):
        """
        Apply all configurations to the FastAPI application.

        This is a convenience method that applies all configurations in one call.
        """
        self.configure_cors()
        self.configure_exception_handling()
