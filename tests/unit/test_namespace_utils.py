import sys
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from ingenious.utils.namespace_utils import (
    get_dir_roots,
    get_file_from_namespace_with_fallback,
    get_inbuilt_api_routes,
    get_namespaces,
    get_path_from_namespace_with_fallback,
    import_class_safely,
    import_class_with_fallback,
    import_module_safely,
    import_module_with_fallback,
    normalize_workflow_name,
    print_namespace_modules,
)


@pytest.mark.unit
class TestNamespaceUtils:
    """Test namespace utility functions"""

    def test_normalize_workflow_name_with_hyphens(self):
        """Test normalizing workflow name with hyphens"""
        result = normalize_workflow_name("bike-insights")
        assert result == "bike_insights"

    def test_normalize_workflow_name_with_underscores(self):
        """Test normalizing workflow name with underscores"""
        result = normalize_workflow_name("bike_insights")
        assert result == "bike_insights"

    def test_normalize_workflow_name_mixed_case(self):
        """Test normalizing workflow name with mixed case"""
        result = normalize_workflow_name("Bike-Insights")
        assert result == "bike_insights"

    def test_normalize_workflow_name_empty(self):
        """Test normalizing empty workflow name"""
        result = normalize_workflow_name("")
        assert result == ""

    def test_normalize_workflow_name_none(self):
        """Test normalizing None workflow name"""
        result = normalize_workflow_name(None)
        assert result is None

    def test_get_namespaces(self):
        """Test getting list of namespaces"""
        namespaces = get_namespaces()
        expected = [
            "ingenious_extensions",
            "ingenious.ingenious_extensions_template",
            "ingenious",
        ]
        assert namespaces == expected

    @patch("ingenious.utils.namespace_utils.Path.exists")
    @patch("ingenious.utils.namespace_utils.get_paths")
    def test_get_dir_roots(self, mock_get_paths, mock_exists):
        """Test getting directory roots"""
        mock_get_paths.return_value = {"purelib": "/path/to/site-packages"}
        mock_exists.return_value = True

        with patch("ingenious.utils.namespace_utils.Path.cwd") as mock_cwd:
            mock_cwd.return_value = Path("/current/working/dir")

            dirs = get_dir_roots()

            assert len(dirs) == 3
            assert str(dirs[0]).endswith("ingenious_extensions")
            assert str(dirs[1]).endswith("ingenious_extensions_template")
            assert str(dirs[2]).endswith("ingenious")

    @patch("ingenious.utils.namespace_utils.get_paths")
    def test_get_inbuilt_api_routes_working_dir(self, mock_get_paths):
        """Test getting inbuilt API routes from working directory"""
        mock_get_paths.return_value = {"purelib": "/path/to/site-packages"}

        with (
            patch("ingenious.utils.namespace_utils.os.getcwd") as mock_getcwd,
            patch("ingenious.utils.namespace_utils.os.path.exists") as mock_exists,
        ):
            mock_getcwd.return_value = "/current/working/dir"
            mock_exists.side_effect = lambda path: "/current/working/dir" in path

            result = get_inbuilt_api_routes()

            assert result is not None
            assert str(result).endswith("api/routes")

    @patch("ingenious.utils.namespace_utils.importlib.import_module")
    def test_import_module_safely_success(self, mock_import_module):
        """Test successful module import"""
        mock_module = Mock()
        mock_class = Mock()
        mock_module.TestClass = mock_class
        mock_import_module.return_value = mock_module

        with patch.dict("sys.modules", {}, clear=True):
            result = import_module_safely("test.module", "TestClass")

            assert result == mock_class
            # The function calls import_module twice, so we check it was called
            assert mock_import_module.call_count >= 1

    @patch("ingenious.utils.namespace_utils.importlib.import_module")
    def test_import_module_safely_import_error(self, mock_import_module):
        """Test module import with ImportError"""
        mock_import_module.side_effect = ImportError("Module not found")

        # Mock sys.modules to not contain the test module
        with patch.object(sys, "modules", {}):
            with pytest.raises(ValueError, match="Unsupported module import"):
                import_module_safely("test.module", "TestClass")

    @patch("ingenious.utils.namespace_utils.importlib.import_module")
    def test_import_module_safely_attribute_error(self, mock_import_module):
        """Test module import with AttributeError"""
        mock_module = Mock()
        del mock_module.TestClass  # Remove attribute
        mock_import_module.return_value = mock_module

        with patch.dict("sys.modules", {}, clear=True):
            with pytest.raises(ValueError, match="Unsupported module import"):
                import_module_safely("test.module", "TestClass")

    @patch("ingenious.utils.namespace_utils.importlib.import_module")
    def test_import_module_safely_cached_module(self, mock_import_module):
        """Test module import with cached module"""
        mock_module = Mock()
        mock_class = Mock()
        mock_module.TestClass = mock_class
        mock_import_module.return_value = mock_module

        with patch.dict("sys.modules", {"test.module": mock_module}):
            result = import_module_safely("test.module", "TestClass")

            assert result == mock_class

    def test_import_class_safely_same_as_import_module_safely(self):
        """Test that import_class_safely works same as import_module_safely"""
        with patch(
            "ingenious.utils.namespace_utils.importlib.import_module"
        ) as mock_import_module:
            mock_module = Mock()
            mock_class = Mock()
            mock_module.TestClass = mock_class
            mock_import_module.return_value = mock_module

            with patch.dict("sys.modules", {}, clear=True):
                result = import_class_safely("test.module", "TestClass")

                assert result == mock_class

    @patch("ingenious.utils.namespace_utils.import_module_with_fallback")
    def test_import_class_with_fallback_success(self, mock_import_module_fallback):
        """Test successful class import with fallback"""
        mock_module = Mock()
        mock_class = Mock()
        mock_module.TestClass = mock_class
        mock_import_module_fallback.return_value = mock_module

        result = import_class_with_fallback("test.module", "TestClass")

        assert result == mock_class

    @patch("ingenious.utils.namespace_utils.import_module_with_fallback")
    def test_import_class_with_fallback_module_not_found(
        self, mock_import_module_fallback
    ):
        """Test class import with fallback when module not found"""
        mock_import_module_fallback.side_effect = ModuleNotFoundError(
            "Module not found"
        )

        with pytest.raises(
            ValueError, match="Module test.module not found in any namespace"
        ):
            import_class_with_fallback("test.module", "TestClass")

    @patch("ingenious.utils.namespace_utils.import_module_with_fallback")
    def test_import_class_with_fallback_attribute_error(
        self, mock_import_module_fallback
    ):
        """Test class import with fallback when class not found"""
        mock_module = Mock()
        del mock_module.TestClass  # Remove attribute
        mock_import_module_fallback.return_value = mock_module

        with pytest.raises(
            ValueError, match="Class TestClass not found in module test.module"
        ):
            import_class_with_fallback("test.module", "TestClass")

    @patch("ingenious.utils.namespace_utils.get_dir_roots")
    def test_get_file_from_namespace_with_fallback_success(self, mock_get_dir_roots):
        """Test successful file retrieval with fallback"""
        mock_dir = Path("/test/dir")
        mock_get_dir_roots.return_value = [mock_dir]

        file_content = "test file content"

        with (
            patch("ingenious.utils.namespace_utils.os.path.exists") as mock_exists,
            patch("builtins.open", mock_open(read_data=file_content)),
        ):
            mock_exists.return_value = True

            result = get_file_from_namespace_with_fallback(
                "test.module", "test_file.txt"
            )

            assert result == file_content

    @patch("ingenious.utils.namespace_utils.get_dir_roots")
    def test_get_file_from_namespace_with_fallback_file_not_found(
        self, mock_get_dir_roots
    ):
        """Test file retrieval with fallback when file not found"""
        mock_dir = Path("/test/dir")
        mock_get_dir_roots.return_value = [mock_dir]

        with patch("ingenious.utils.namespace_utils.os.path.exists") as mock_exists:
            mock_exists.return_value = False

            result = get_file_from_namespace_with_fallback(
                "test.module", "test_file.txt"
            )

            assert result is None

    @patch("ingenious.utils.namespace_utils.get_dir_roots")
    def test_get_path_from_namespace_with_fallback_success(self, mock_get_dir_roots):
        """Test successful path retrieval with fallback"""
        mock_dir = Path("/test/dir")
        mock_get_dir_roots.return_value = [mock_dir]

        with patch("ingenious.utils.namespace_utils.os.path.exists") as mock_exists:
            mock_exists.return_value = True

            result = get_path_from_namespace_with_fallback("test/path")

            assert result == mock_dir / "test/path"

    @patch("ingenious.utils.namespace_utils.get_dir_roots")
    def test_get_path_from_namespace_with_fallback_not_found(self, mock_get_dir_roots):
        """Test path retrieval with fallback when path not found"""
        mock_dir = Path("/test/dir")
        mock_get_dir_roots.return_value = [mock_dir]

        with patch("ingenious.utils.namespace_utils.os.path.exists") as mock_exists:
            mock_exists.return_value = False

            result = get_path_from_namespace_with_fallback("test/path")

            assert result is None

    @patch("ingenious.utils.namespace_utils.get_namespaces")
    @patch("ingenious.utils.namespace_utils.importlib.import_module")
    @patch("ingenious.utils.namespace_utils.importlib.util.find_spec")
    def test_import_module_with_fallback_success(
        self, mock_find_spec, mock_import_module, mock_get_namespaces
    ):
        """Test successful module import with fallback"""
        mock_get_namespaces.return_value = ["test_namespace"]
        mock_find_spec.return_value = Mock()  # Module spec found
        mock_module = Mock()
        mock_import_module.return_value = mock_module

        with (
            patch("ingenious.utils.namespace_utils.Path.cwd") as mock_cwd,
            patch("builtins.print"),
        ):  # Mock print to avoid output
            mock_cwd.return_value = Path("/test/dir")

            result = import_module_with_fallback("test.module")

            assert result == mock_module

    def test_print_namespace_modules_with_package(self):
        """Test printing namespace modules for a package"""
        # Test with a real package that we know exists
        import contextlib
        import io

        # Capture stdout to verify the function works
        captured_output = io.StringIO()

        # Use a real package for testing
        with contextlib.redirect_stdout(captured_output):
            print_namespace_modules(
                "unittest"
            )  # unittest is a real package with modules

        output = captured_output.getvalue()

        # Verify that the function found and printed some modules
        # unittest package has several modules like case, loader, mock, etc.
        assert "Found module:" in output

        # Check for some known unittest modules
        known_modules = ["case", "mock", "loader", "result"]
        found_any = any(module in output for module in known_modules)
        assert found_any, (
            f"Expected to find at least one of {known_modules} in output: {output}"
        )

    def test_print_namespace_modules_without_package(self):
        """Test printing namespace modules for a non-package"""
        with patch(
            "ingenious.utils.namespace_utils.importlib.import_module"
        ) as mock_import_module:
            # Mock module without __path__ attribute by using spec
            mock_module_spec = Mock(spec=[])
            mock_import_module.return_value = mock_module_spec

            # Just verify the function runs without error
            print_namespace_modules("test.namespace")

            # Verify the mock was called appropriately
            mock_import_module.assert_called_once_with("test.namespace")
