"""
Tests for extension loading functionality.
"""

from unittest.mock import patch

import pytest

from ingenious.extensions.loader import (
    TemplateNotFoundException,
    copy_template_directory,
    get_extension_path,
    list_extensions,
)


class TestExtensionLoader:
    """Test suite for extension loader functionality."""

    def test_list_extensions(self):
        """Test listing available extensions."""
        with patch("ingenious.extensions.loader.os.listdir") as mock_listdir:
            # Mock the directory listing
            mock_listdir.return_value = [
                "template",
                "custom_extension",
                "__pycache__",
                "loader.py",
            ]

            # Get the extensions
            extensions = list_extensions()

            # Verify the result (should filter out non-extension entries)
            assert "template" in extensions
            assert "custom_extension" in extensions
            assert "__pycache__" not in extensions
            assert "loader.py" not in extensions

    def test_get_extension_path(self):
        """Test getting the path to an extension."""
        with patch("ingenious.extensions.loader.os.path.exists") as mock_exists:
            # Mock the path exists check
            mock_exists.return_value = True

            # Get the path
            with patch("ingenious.extensions.loader.os.path.dirname") as mock_dirname:
                mock_dirname.return_value = "/path/to/extensions"

                path = get_extension_path("template")

                # Verify the path
                assert path == "/path/to/extensions/template"
                mock_exists.assert_called_once_with("/path/to/extensions/template")

    def test_get_extension_path_not_found(self):
        """Test error when extension is not found."""
        with patch("ingenious.extensions.loader.os.path.exists") as mock_exists:
            # Mock the path exists check
            mock_exists.return_value = False

            # Try to get the path
            with pytest.raises(TemplateNotFoundException):
                get_extension_path("nonexistent_extension")

    def test_copy_template_directory(self):
        """Test copying a template directory."""
        with patch("ingenious.extensions.loader.get_extension_path") as mock_get_path:
            # Mock the extension path
            mock_get_path.return_value = "/path/to/extensions/template"

            # Mock the path existence checks
            with patch("ingenious.extensions.loader.os.path.exists") as mock_exists:
                mock_exists.return_value = True

                # Mock the directory operations
                with patch(
                    "ingenious.extensions.loader.shutil.copytree"
                ) as mock_copytree:
                    # Run the function
                    result = copy_template_directory("template", "/destination/path")

                    # Verify the result
                    assert result is True
                    mock_get_path.assert_called_once_with("template")
                    mock_copytree.assert_called_once_with(
                        "/path/to/extensions/template",
                        "/destination/path",
                        dirs_exist_ok=True,
                    )

    def test_copy_template_directory_error(self):
        """Test error when copying a template directory."""
        with patch("ingenious.extensions.loader.get_extension_path") as mock_get_path:
            # Mock the extension path
            mock_get_path.return_value = "/path/to/extensions/template"

            # Mock the path existence checks
            with patch("ingenious.extensions.loader.os.path.exists") as mock_exists:
                mock_exists.return_value = True

                # Mock the directory operations to raise an error
                with patch(
                    "ingenious.extensions.loader.shutil.copytree"
                ) as mock_copytree:
                    mock_copytree.side_effect = Exception("Copy error")

                    # Run the function
                    result = copy_template_directory("template", "/destination/path")

                    # Verify the result
                    assert result is False
