"""Models for handling API responses."""

from typing import Any, Dict, Optional

from flask import Response, jsonify


class ApiResponse:
    """Standard API response model."""

    def __init__(
        self,
        success: bool = True,
        message: str = "",
        data: Optional[Dict[str, Any]] = None,
        status_code: int = 200,
    ):
        """Initialize a new API response."""
        self.success = success
        self.message = message
        self.data = data or {}
        self.status_code = status_code

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
        }

    def to_response(self) -> Response:
        """Convert to Flask response."""
        return jsonify(self.to_dict()), self.status_code


class ApiError(ApiResponse):
    """API error response model."""

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a new API error response."""
        super().__init__(
            success=False,
            message=message,
            data={"error": True, "details": details or {}},
            status_code=status_code,
        )
