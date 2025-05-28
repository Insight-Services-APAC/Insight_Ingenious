"""
Interface for configuration service.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class ConfigurationServiceInterface(ABC):
    """Interface for configuration service implementations."""

    @abstractmethod
    def get_config(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: The configuration key
            default: Optional default value if key is not found

        Returns:
            The configuration value
        """
        pass

    @abstractmethod
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get a configuration section.

        Args:
            section: The configuration section

        Returns:
            The configuration section
        """
        pass

    @abstractmethod
    def set_config(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: The configuration key
            value: The configuration value
        """
        pass

    @abstractmethod
    def reload(self) -> None:
        """
        Reload the configuration.
        """
        pass
