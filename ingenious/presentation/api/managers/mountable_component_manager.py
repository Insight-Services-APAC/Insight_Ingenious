"""
Module for managing mountable components in the FastAPI application.
This module contains classes and functions for mounting external components.
"""

import importlib.resources as pkg_resources

from chainlit.utils import mount_chainlit
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

from ingenious.domain.model.config import Config
from ingenious.presentation.api.managers.base_manager import IManager


class MountableComponentManager(IManager):
    """
    Manages the mounting of external components to a FastAPI application.

    This class handles mounting components like ChainLit and Flask applications.
    It follows the single responsibility principle by focusing solely on component mounting.
    """

    def __init__(self, app: FastAPI, config: Config):
        """
        Initialize the MountableComponentManager.

        Args:
            app: The FastAPI application instance to configure
            config: The Ingenious application configuration
        """
        self.app = app
        self.config = config

    def mount_chainlit(self):
        """
        Mount the ChainLit application if enabled in configuration.

        This mounts the ChainLit application to the /chainlit path.
        """
        if self.config.chainlit_configuration.enable:
            chainlit_path = (
                pkg_resources.files("ingenious.presentation.chainlit") / "app.py"
            )
            mount_chainlit(app=self.app, target=str(chainlit_path), path="/chainlit")

    def mount_flask_app(self, flask_app, path="/prompt-tuner"):
        """
        Mount a Flask application to the FastAPI application.

        Args:
            flask_app: The Flask application to mount
            path: The path to mount the Flask application at
        """
        self.app.mount(path, WSGIMiddleware(flask_app))

    def mount_all_components(self, flask_app=None):
        """
        Mount all components for the application.

        Args:
            flask_app: Optional Flask application to mount

        This is a convenience method that mounts all components in one call.
        """
        self.mount_chainlit()

        if flask_app:
            self.mount_flask_app(flask_app)

    def configure(self, flask_app=None):
        """
        Apply all component mounting configuration to the FastAPI application.

        Args:
            flask_app: Optional Flask application to mount

        This is a required method to implement the IManager interface.
        """
        self.mount_all_components(flask_app)
