"""
Module for managing API routes in the FastAPI application.
This module contains classes and functions for registering and managing routes.
"""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from ingenious.common.utils.namespace_utils import (
    import_class_with_fallback,
    import_module_with_fallback,
)
from ingenious.domain.model.api_routes import IApiRoutes
from ingenious.domain.model.config import Config
from ingenious.presentation.api.managers.base_manager import IManager


class RouterManager(IManager):
    """
    Manages the registration of routes for a FastAPI application.

    This class handles setting up both built-in and custom routes for the application.
    It follows the single responsibility principle by focusing solely on route management.
    """

    def __init__(self, app: FastAPI, config: Config):
        """
        Initialize the RouterManager.

        Args:
            app: The FastAPI application instance to configure
            config: The Ingenious application configuration
        """
        self.app = app
        self.config = config

    def register_built_in_routes(self):
        """
        Register the built-in API routes.

        This includes chat, diagnostic, prompts, and message feedback routes.
        """
        from ingenious.presentation.api.routes import chat as chat_route
        from ingenious.presentation.api.routes import diagnostic as diagnostic_route
        from ingenious.presentation.api.routes import (
            message_feedback as message_feedback_route,
        )
        from ingenious.presentation.api.routes import prompts as prompts_route

        # Add in-built routes
        self.app.include_router(chat_route.router, prefix="/api/v1", tags=["Chat"])
        self.app.include_router(
            diagnostic_route.router, prefix="/api/v1", tags=["Diagnostic"]
        )
        self.app.include_router(
            prompts_route.router, prefix="/api/v1", tags=["Prompts"]
        )
        self.app.include_router(
            message_feedback_route.router, prefix="/api/v1", tags=["Message Feedback"]
        )

    def register_custom_routes(self):
        """
        Register custom API routes from extensions.

        This finds and registers any custom routes defined in extensions.
        """
        # Add custom routes from ingenious extensions
        custom_api_routes_module = import_module_with_fallback(
            "presentation.api.routes.custom"
        )
        if (
            custom_api_routes_module.__name__
            != "ingenious.presentation.api.routes.custom"
        ):
            custom_api_routes_class = import_class_with_fallback(
                "presentation.api.routes.custom", "Api_Routes"
            )
            custom_api_routes_class_instance: IApiRoutes = custom_api_routes_class(
                self.config, self.app
            )
            custom_api_routes_class_instance.add_custom_routes()

    def register_utility_routes(self):
        """
        Register utility routes like the root redirect.

        This includes routes that are not part of the API but are useful for the application.
        """
        # Redirect `/` to `/docs`
        self.app.get("/", tags=["Root"])(self._redirect_to_docs)

    async def _redirect_to_docs(self):
        """
        Redirect the root endpoint to /docs.

        Returns:
            RedirectResponse to the /docs endpoint
        """
        return RedirectResponse(url="/docs")

    def register_all_routes(self):
        """
        Register all routes for the application.

        This is a convenience method that registers all routes in one call.
        """
        self.register_built_in_routes()
        self.register_custom_routes()
        self.register_utility_routes()

    def configure(self):
        """
        Apply all routing configuration to the FastAPI application.

        This is a required method to implement the IManager interface.
        """
        self.register_all_routes()
