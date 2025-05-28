"""
FastAgentAPI Interface module.

This module defines the interface for the Fast Agent API application.
"""

from abc import ABC, abstractmethod

from fastapi import FastAPI, Request

from ingenious.domain.model.config import Config


class IFastAgentAPI(ABC):
    """
    Interface for the Fast Agent API application.

    This interface defines the required methods and properties for an API application.
    """

    @property
    @abstractmethod
    def app(self) -> FastAPI:
        """Get the FastAPI application instance."""
        pass

    @property
    @abstractmethod
    def config(self) -> Config:
        """Get the application configuration."""
        pass

    @abstractmethod
    async def redirect_to_docs(self):
        """
        Redirect the root endpoint to /docs.

        Returns:
            RedirectResponse: A redirection to the /docs endpoint
        """
        pass

    @abstractmethod
    async def generic_exception_handler(self, request: Request, exc: Exception):
        """
        Generic exception handler for the application.

        Args:
            request: The request that caused the exception
            exc: The exception that was raised

        Returns:
            JSONResponse with error details
        """
        pass

    @abstractmethod
    async def root(self):
        """
        Root endpoint handler.

        Returns:
            HTMLResponse with the index.html content
        """
        pass
