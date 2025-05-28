"""
Base Manager Interface for API managers.

This module defines the base interface that all API managers should implement.
"""

from abc import ABC, abstractmethod

from fastapi import FastAPI

from ingenious.domain.model.config import Config


class IManager(ABC):
    """
    Interface for API managers.

    All API managers should implement this interface to ensure a consistent
    way of configuring different aspects of the API.
    """

    @abstractmethod
    def __init__(self, app: FastAPI, config: Config):
        """
        Initialize the manager.

        Args:
            app: The FastAPI application instance to configure
            config: The Ingenious application configuration
        """
        pass

    @abstractmethod
    def configure(self):
        """
        Apply the manager's configuration to the FastAPI application.

        This method should apply all configurations handled by this manager.
        """
        pass
