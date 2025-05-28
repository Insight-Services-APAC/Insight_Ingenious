"""
Middleware for handling exceptions and logging in the Ingenious framework.

This module provides middleware for FastAPI to handle exceptions and
maintain consistent logging across the application.
"""

import time
from typing import Callable, Dict, List, Optional, Type

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ingenious.common.errors import IngeniousError, handle_exception
from ingenious.common.logging import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""

    def __init__(
        self,
        app: FastAPI,
        include_paths: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None,
        log_request_headers: bool = False,
        log_response_headers: bool = False,
        log_request_body: bool = False,
        log_response_body: bool = False,
    ):
        """
        Initialize the logging middleware.

        Args:
            app: The FastAPI application
            include_paths: List of paths to include in logging
            exclude_paths: List of paths to exclude from logging
            log_request_headers: Whether to log request headers
            log_response_headers: Whether to log response headers
            log_request_body: Whether to log request bodies
            log_response_body: Whether to log response bodies
        """
        super().__init__(app)
        self.include_paths = include_paths or []
        self.exclude_paths = exclude_paths or []
        self.log_request_headers = log_request_headers
        self.log_response_headers = log_response_headers
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process a request and log relevant information.

        Args:
            request: The incoming request
            call_next: The next middleware or route handler

        Returns:
            The response from the route handler
        """
        # Check if this path should be logged
        path = request.url.path
        if self.exclude_paths and any(path.startswith(p) for p in self.exclude_paths):
            return await call_next(request)

        if self.include_paths and not any(
            path.startswith(p) for p in self.include_paths
        ):
            return await call_next(request)

        # Start timing
        start_time = time.time()

        # Prepare request logging data
        request_data = {
            "method": request.method,
            "path": path,
            "query_params": str(request.query_params),
            "client": request.client.host if request.client else None,
        }

        # Log request headers if enabled
        if self.log_request_headers:
            request_data["headers"] = dict(request.headers)

        # Log request body if enabled
        if self.log_request_body:
            try:
                body = await request.json()
                request_data["body"] = body
            except Exception:
                # Body might not be JSON
                pass

        logger.info(f"Request: {request_data}")

        # Process the request
        try:
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Prepare response logging data
            response_data = {
                "status_code": response.status_code,
                "duration": f"{duration:.4f}s",
            }

            # Log response headers if enabled
            if self.log_response_headers:
                response_data["headers"] = dict(response.headers)

            # Log response body if enabled
            if self.log_response_body:
                # This is tricky as the response body is a stream
                # In most cases, we shouldn't attempt to log the full body
                pass

            logger.info(f"Response: {response_data}")

            return response

        except Exception:
            # Let the exception handler middleware handle the exception
            logger.error(f"Exception in request: {path}", exc_info=True)
            raise


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling exceptions."""

    def __init__(
        self,
        app: FastAPI,
        error_handlers: Optional[Dict[Type[Exception], Callable]] = None,
    ):
        """
        Initialize the exception handling middleware.

        Args:
            app: The FastAPI application
            error_handlers: Optional dictionary mapping exception types to handlers
        """
        super().__init__(app)
        self.error_handlers = error_handlers or {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process a request and handle any exceptions.

        Args:
            request: The incoming request
            call_next: The next middleware or route handler

        Returns:
            The response from the route handler or an error response
        """
        try:
            return await call_next(request)
        except IngeniousError as exc:
            # Handle our custom error type
            exc.log()
            return JSONResponse(status_code=exc.status_code, content=exc.to_dict())
        except Exception as exc:
            # For other exceptions, use the registered handlers or default handling
            error_handler = self.error_handlers.get(type(exc))

            if error_handler:
                return await error_handler(request, exc)

            # Use our central error handling system
            error_dict = handle_exception(exc)
            status_code = error_dict.get("status_code", 500)

            return JSONResponse(status_code=status_code, content=error_dict)


def add_middleware(
    app: FastAPI,
    logging_config: Optional[Dict] = None,
    error_handlers: Optional[Dict[Type[Exception], Callable]] = None,
) -> FastAPI:
    """
    Add middleware to a FastAPI application.

    This function adds the logging and exception handling middleware to
    a FastAPI application with the specified configuration.

    Args:
        app: The FastAPI application
        logging_config: Configuration for the logging middleware
        error_handlers: Dictionary mapping exception types to handlers

    Returns:
        The FastAPI application with middleware added
    """
    # Add exception handling middleware first (innermost)
    app.add_middleware(ExceptionHandlingMiddleware, error_handlers=error_handlers)

    # Add logging middleware
    if logging_config is None:
        logging_config = {}

    app.add_middleware(LoggingMiddleware, **logging_config)

    return app
