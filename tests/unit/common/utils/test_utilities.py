"""
Tests for utility modules in ingenious.common.utils.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from rich.console import Console

from ingenious.common.utils.namespace_utils import (
    get_file_from_namespace_with_fallback,
    get_path_from_namespace_with_fallback,
    import_class_with_fallback,
    import_module_with_fallback,
)
from ingenious.common.utils.project_setup_manager import ProjectSetupManager


class TestNamespaceUtils:
    """Test suite for namespace utilities."""

    def test_import_module_with_fallback(self):
        """Test importing a module with fallback."""
        # Import an existing module
        module = import_module_with_fallback("ingenious.common.utils.namespace_utils")
        assert module is not None
        assert hasattr(module, "import_module_with_fallback")

        # Import a non-existent module, should fallback to extension
        with patch("importlib.import_module") as mock_import:
            # First import will fail
            mock_import.side_effect = [ImportError, Mock()]

            # Call the function
            import_module_with_fallback("nonexistent.module")

            # Verify the fallback was attempted
            assert mock_import.call_count == 2
            assert "extension" in mock_import.call_args_list[1][0][0].lower()

    def test_import_class_with_fallback(self):
        """Test importing a class with fallback."""
        # Import an existing class
        cls = import_class_with_fallback(
            "ingenious.common.utils.project_setup_manager", "ProjectSetupManager"
        )
        assert cls is not None
        assert cls.__name__ == "ProjectSetupManager"

        # Import a non-existent class, should fallback to extension
        with patch("importlib.import_module") as mock_import:
            # Set up mocks for module and class
            mock_module = Mock()
            mock_module.NonexistentClass = Mock()
            mock_import.side_effect = [ImportError, mock_module]

            # Call the function
            import_class_with_fallback("nonexistent.module", "NonexistentClass")

            # Verify the fallback was attempted
            assert mock_import.call_count == 2
            assert "extension" in mock_import.call_args_list[1][0][0].lower()

    def test_get_path_from_namespace_with_fallback(self):
        """Test getting a path from namespace with fallback."""
        # Create a temporary directory and file
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            test_dir = temp_path / "test_dir"
            test_dir.mkdir()

            # Mock the get_dir_roots function to include our temp path
            with patch(
                "ingenious.common.utils.namespace_utils.get_dir_roots"
            ) as mock_get_roots:
                mock_get_roots.return_value = [temp_path]

                # Test with existing path
                result = get_path_from_namespace_with_fallback("test_dir")
                assert result == str(test_dir)

                # Test with non-existent path, should return a default path
                result = get_path_from_namespace_with_fallback("nonexistent_dir")
                assert "nonexistent_dir" in result

    def test_get_file_from_namespace_with_fallback(self):
        """Test getting a file from namespace with fallback."""
        # Create a temporary directory and file
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            test_file = temp_path / "test_file.txt"
            with open(test_file, "w") as f:
                f.write("Test content")

            # Mock the import_module_with_fallback function
            with patch(
                "ingenious.common.utils.namespace_utils.import_module_with_fallback"
            ) as mock_import:
                mock_module = Mock()
                mock_module.__file__ = str(temp_path / "__init__.py")
                mock_import.return_value = mock_module

                # Test with existing file
                result = get_file_from_namespace_with_fallback(
                    "test_module", "test_file.txt"
                )
                assert result == str(test_file)

                # Test with non-existent file
                with pytest.raises(FileNotFoundError):
                    get_file_from_namespace_with_fallback(
                        "test_module", "nonexistent_file.txt"
                    )


class TestProjectSetupManager:
    """Test suite for project setup manager."""

    def setup_method(self):
        """Set up the test environment."""
        self.console = Console()
        self.manager = ProjectSetupManager(self.console)

    def test_copy_file(self):
        """Test copying a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            source_file = temp_path / "source.txt"
            dest_file = temp_path / "dest.txt"

            # Create source file
            with open(source_file, "w") as f:
                f.write("Test content")

            # Copy the file
            result = self.manager.copy_file(source_file, dest_file)

            # Verify the result
            assert result is True
            assert dest_file.exists()
            with open(dest_file, "r") as f:
                assert f.read() == "Test content"

    def test_copy_directory(self):
        """Test copying a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            source_dir = temp_path / "source"
            source_dir.mkdir()

            # Create files in source directory
            (source_dir / "file1.txt").write_text("Content 1")
            (source_dir / "file2.txt").write_text("Content 2")
            (source_dir / "ignore_me.tmp").write_text("Temp content")

            # Create subdirectory with files
            sub_dir = source_dir / "subdir"
            sub_dir.mkdir()
            (sub_dir / "file3.txt").write_text("Content 3")

            # Destination directory
            dest_dir = temp_path / "dest"

            # Copy the directory with ignore pattern
            result = self.manager.copy_directory(
                source_dir, dest_dir, ignore_patterns=["*.tmp"]
            )

            # Verify the result
            assert result is True
            assert dest_dir.exists()
            assert (dest_dir / "file1.txt").exists()
            assert (dest_dir / "file2.txt").exists()
            assert not (dest_dir / "ignore_me.tmp").exists()  # Should be ignored
            assert (dest_dir / "subdir" / "file3.txt").exists()

    def test_process_file_content(self):
        """Test processing file content with replacements."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            test_file = temp_path / "test_file.txt"

            # Create the file with placeholder content
            with open(test_file, "w") as f:
                f.write("Hello {{name}}! Your age is {{age}}.")

            # Process the file
            replacements = {"{{name}}": "John", "{{age}}": "30"}
            result = self.manager.process_file_content(test_file, replacements)

            # Verify the result
            assert result is True
            with open(test_file, "r") as f:
                content = f.read()
                assert content == "Hello John! Your age is 30."

    def test_create_file(self):
        """Test creating a file with content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            test_file = temp_path / "new_file.txt"

            # Create the file
            content = "This is a new file."
            result = self.manager.create_file(test_file, content)

            # Verify the result
            assert result is True
            assert test_file.exists()
            with open(test_file, "r") as f:
                assert f.read() == content
