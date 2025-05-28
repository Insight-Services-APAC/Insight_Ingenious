"""
Main module for the Ingenious framework.
This module contains the FastAPI application and its configuration.
"""

import importlib.resources as pkg_resources
import logging
import os
from typing import Any, Optional, cast

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse

import ingenious.common.config.config as ingen_config
from ingenious.common.config.config import Config as CommonConfig
from ingenious.common.di.bindings import register_bindings
from ingenious.common.di.container import get_container
from ingenious.domain.interfaces.api.fast_agent_api import IFastAgentAPI
from ingenious.domain.model.config import Config as DomainConfig
from ingenious.presentation.api.application_factory import ApplicationFactory
from ingenious.presentation.api.managers.app_configuration_manager import (
    AppConfigurationManager,
)
from ingenious.presentation.api.managers.mountable_component_manager import (
    MountableComponentManager,
)
from ingenious.presentation.api.managers.router_manager import RouterManager

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Get config
config = ingen_config.get_config(os.getenv("INGENIOUS_PROJECT_PATH", ""))

# Register dependencies with the appropriate config type
if hasattr(config, "__class__") and config.__class__.__name__ == "Config":
    # Use config as is if it's already the right type
    register_bindings(cast(DomainConfig, config))
else:
    # Handle other config types or use as is
    register_bindings(cast(DomainConfig, config))


class FastAgentAPI(IFastAgentAPI):
    """
    FastAPI application for the Ingenious framework.

    This class initializes and configures a FastAPI application with all the necessary
    components for the Ingenious framework. It follows the Single Responsibility Principle
    by delegating specific tasks to manager classes.
    """

    def __init__(self, config: Any):
        """
        Initialize the FastAgentAPI.

        Args:
            config: The Ingenious application configuration
        """
        # Set the working directory
        os.chdir(os.environ["INGENIOUS_WORKING_DIR"])

        # Store configuration
        self._config = config

        # Initialize FastAPI app using the factory
        # Handle different config types for compatibility with ApplicationFactory
        common_config: Optional[CommonConfig] = None
        if isinstance(config, CommonConfig):
            common_config = config
        else:
            # Create a compatible config object
            common_config = CommonConfig()
            # Copy compatible attributes if possible
            for attr in dir(config):
                if not attr.startswith("_") and hasattr(common_config, attr):
                    try:
                        setattr(common_config, attr, getattr(config, attr))
                    except (AttributeError, TypeError):
                        # Skip attributes that can't be set
                        pass

        self._app = ApplicationFactory.create_app(
            config=common_config,
            title="Ingenious API",
            version="1.0.0",
            managers=[AppConfigurationManager, RouterManager],
        )

        # Initialize Flask app for prompt tuner
        import ingenious_prompt_tuner as prompt_tuner

        self._flask_app = prompt_tuner.create_app()

        # Mount components (done separately because it needs the flask_app)
        component_manager = get_container().resolve(MountableComponentManager)
        component_manager.configure(flask_app=self._flask_app)

    @property
    def app(self) -> FastAPI:
        """Get the FastAPI application instance."""
        return self._app

    @property
    def config(self) -> Any:
        """Get the application configuration."""
        return self._config

    async def redirect_to_docs(self):
        """
        Redirect the root endpoint to /docs.

        This method handles the root endpoint of the API and redirects it to the
        API documentation page.

        Returns:
            RedirectResponse: A redirection to the /docs endpoint
        """
        return RedirectResponse(url="/docs")

    async def generic_exception_handler(self, request: Request, exc: Exception):
        """
        Generic exception handler for the application.

        Args:
            request: The request that caused the exception
            exc: The exception that was raised

        Returns:
            JSONResponse with error details
        """
        # Use the factory's exception handler
        from ingenious.presentation.api.application_factory import ApplicationFactory

        return await ApplicationFactory._generic_exception_handler(request, exc)

    async def root(self):
        """
        Root endpoint handler.

        Returns:
            HTMLResponse with the index.html content
        """
        # Locate the HTML file in ingenious.api
        html_path = pkg_resources.files("ingenious.chainlit") / "index.html"
        with html_path.open("r") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
