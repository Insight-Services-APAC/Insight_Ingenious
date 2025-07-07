"""
Main document parser class that coordinates different parsers.
"""

import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from .models import DocumentResult, DocumentInfo
from ..parsers import PDFParser, DOCXParser, ExcelParser, CSVParser, BaseParser
from ..utils.exceptions import (
    UnsupportedFileTypeError,
    FileNotFoundError as CustomFileNotFoundError,
    DocumentParsingError,
)
from ..utils.logging import logger
from ..utils.templates import TemplateProcessor


class DocumentParser:
    """
    Main document parser that handles multiple file types.

    This class acts as a facade for different document parsers,
    automatically selecting the appropriate parser based on file type.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the document parser.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self._parsers: List[BaseParser] = [
            PDFParser(),
            DOCXParser(),
            ExcelParser(),
            CSVParser(),
        ]

        # Initialize template processor
        template_dir = self.config.get("template_dir")
        self._template_processor = TemplateProcessor(template_dir)

        logger.info("DocumentParser initialized")

    def parse_file(self, file_path: str) -> DocumentResult:
        """
        Parse a single document file.

        Args:
            file_path: Path to the document file

        Returns:
            DocumentResult containing parsed content

        Raises:
            FileNotFoundError: If file doesn't exist
            UnsupportedFileTypeError: If file type is not supported
            DocumentParsingError: If parsing fails
        """
        # Validate file exists
        if not os.path.exists(file_path):
            raise CustomFileNotFoundError(f"File not found: {file_path}", file_path)

        # Find appropriate parser
        parser = self._get_parser_for_file(file_path)
        if not parser:
            raise UnsupportedFileTypeError(
                f"Unsupported file type: {file_path}", file_path
            )

        try:
            # Parse the file
            logger.info(f"Parsing file: {file_path}")
            pages = parser.parse(file_path)

            # Create document info
            doc_info = self._create_document_info(file_path, len(pages))

            # Create and return result
            result = DocumentResult(document_info=doc_info, pages=pages)

            logger.info(f"Successfully parsed file: {file_path}")
            return result

        except Exception as e:
            if isinstance(e, DocumentParsingError):
                raise
            else:
                raise DocumentParsingError(
                    f"Unexpected error parsing file: {str(e)}", file_path
                )

    def parse_files(self, file_paths: List[str]) -> List[DocumentResult]:
        """
        Parse multiple document files.

        Args:
            file_paths: List of file paths to parse

        Returns:
            List of DocumentResult objects
        """
        results = []

        for file_path in file_paths:
            try:
                result = self.parse_file(file_path)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to parse {file_path}: {str(e)}")
                # Continue with other files
                continue

        return results

    def supports_file(self, file_path: str) -> bool:
        """
        Check if a file type is supported.

        Args:
            file_path: Path to check

        Returns:
            True if file type is supported
        """
        return self._get_parser_for_file(file_path) is not None

    def get_supported_extensions(self) -> List[str]:
        """
        Get list of supported file extensions.

        Returns:
            List of supported extensions (e.g., ['.pdf', '.docx'])
        """
        extensions = []
        test_files = {
            ".pdf": "test.pdf",
            ".docx": "test.docx",
            ".xlsx": "test.xlsx",
            ".xls": "test.xls",
            ".csv": "test.csv",
        }

        for ext, test_file in test_files.items():
            if any(parser.supports_file_type(test_file) for parser in self._parsers):
                extensions.append(ext)

        return extensions

    def _get_parser_for_file(self, file_path: str) -> Optional[BaseParser]:
        """
        Get the appropriate parser for a file.

        Args:
            file_path: Path to the file

        Returns:
            Parser instance or None if unsupported
        """
        for parser in self._parsers:
            if parser.supports_file_type(file_path):
                return parser
        return None

    def _create_document_info(self, file_path: str, total_pages: int) -> DocumentInfo:
        """
        Create DocumentInfo object for a file.

        Args:
            file_path: Path to the file
            total_pages: Number of pages parsed

        Returns:
            DocumentInfo object
        """
        path = Path(file_path)
        file_stats = os.stat(file_path)

        # Determine file type from extension
        file_type = path.suffix.lower().replace(".", "")

        return DocumentInfo(
            filename=path.name,
            file_type=file_type,
            total_pages=total_pages,
            created_at=datetime.now(),
            file_size=file_stats.st_size,
        )

    # Template processing methods

    def render_template(
        self,
        template_string: str,
        document_result: DocumentResult,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render a Jinja2 template string with document data.

        Args:
            template_string: Jinja2 template as string
            document_result: Parsed document result
            extra_context: Additional context variables

        Returns:
            Rendered template string

        Example:
            template = "Document: {{ document.filename }} has {{ total_pages }} pages"
            rendered = parser.render_template(template, result)
        """
        return self._template_processor.render_from_string(
            template_string, document_result, extra_context
        )

    def render_template_file(
        self,
        template_filename: str,
        document_result: DocumentResult,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render a Jinja2 template file with document data.

        Args:
            template_filename: Name of template file
            document_result: Parsed document result
            extra_context: Additional context variables

        Returns:
            Rendered template string
        """
        return self._template_processor.render_from_file(
            template_filename, document_result, extra_context
        )

    def parse_and_render(
        self,
        file_path: str,
        template_string: str,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Parse a document file and immediately render it with a template.

        Args:
            file_path: Path to the document file
            template_string: Jinja2 template as string
            extra_context: Additional context variables

        Returns:
            Rendered template string

        Example:
            template = '''
            # Summary of {{ document.filename }}
            Pages: {{ total_pages }}
            Words: {{ total_words }}
            '''
            result = parser.parse_and_render("document.pdf", template)
        """
        document_result = self.parse_file(file_path)
        return self.render_template(template_string, document_result, extra_context)

    def parse_and_render_multiple(
        self,
        file_path: str,
        templates: List[Dict[str, Any]],
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """
        Parse a document and render multiple templates.

        Args:
            file_path: Path to the document file
            templates: List of template definitions
            extra_context: Additional context variables

        Returns:
            Dictionary mapping template names to rendered content

        Example:
            templates = [
                {"name": "summary", "string": "{{ document.filename }}: {{ total_pages }} pages"},
                {"name": "toc", "string": "{% for h in all_headings %}{{ h.text }}\\n{% endfor %}"}
            ]
            results = parser.parse_and_render_multiple("doc.pdf", templates)
        """
        document_result = self.parse_file(file_path)
        return self._template_processor.render_multiple(
            templates, document_result, extra_context
        )

    def get_template_processor(self) -> TemplateProcessor:
        """
        Get the template processor instance for advanced usage.

        Returns:
            TemplateProcessor instance
        """
        return self._template_processor

    def render_simple_template(
        self, template_string: str, context: Dict[str, Any]
    ) -> str:
        """
        Render a simple template string with custom context (no document required).

        Args:
            template_string: Jinja2 template as string
            context: Context variables for template

        Returns:
            Rendered template string

        Example:
            template = "Hello {{ name }}! Today is {{ date }}."
            result = parser.render_simple_template(template, {
                'name': 'World',
                'date': '2025-07-02'
            })
        """
        from jinja2 import Template

        try:
            template = Template(template_string)
            rendered = template.render(**context)
            logger.debug("Successfully rendered simple template")
            return rendered
        except Exception as e:
            raise DocumentParsingError(f"Error rendering simple template: {str(e)}")

    def render_simple_template_file(
        self, template_filename: str, context: Dict[str, Any]
    ) -> str:
        """
        Render a simple template file with custom context (no document required).

        Args:
            template_filename: Name of template file in template directory
            context: Context variables for template

        Returns:
            Rendered template string

        Example:
            # With simple_template.j2 containing: {{ content }}
            result = parser.render_simple_template_file('simple_template.j2', {
                'content': 'Hello, World!'
            })
        """
        if not self._template_processor._env:
            raise DocumentParsingError(
                "No template directory configured for file templates"
            )

        try:
            template = self._template_processor._env.get_template(template_filename)
            rendered = template.render(**context)
            logger.info(
                f"Successfully rendered simple template file: {template_filename}"
            )
            return rendered
        except Exception as e:
            raise DocumentParsingError(
                f"Error rendering simple template file: {str(e)}"
            )

    def render_data_file_to_template(
        self,
        data_file_path: str,
        template_filename: str,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Parse a data file and render it using a Jinja template file.

        This method combines parsing a document file with rendering it through
        a template file in one convenient operation.

        Args:
            data_file_path: Path to the document file to parse
            template_filename: Name of the Jinja template file
            extra_context: Additional context variables for the template

        Returns:
            Rendered template string

        Example:
            # Parse data.xlsx and render it with report_template.j2
            result = parser.render_data_file_to_template(
                'data/sales.xlsx',
                'report_template.j2',
                extra_context={'report_date': '2025-07-02'}
            )
        """
        try:
            # Parse the data file
            logger.info(f"Parsing data file: {data_file_path}")
            document_result = self.parse_file(data_file_path)

            # Render with template file
            logger.info(f"Rendering with template: {template_filename}")
            rendered = self.render_template_file(
                template_filename, document_result, extra_context
            )

            logger.info("Successfully rendered data file to template")
            return rendered

        except Exception as e:
            raise DocumentParsingError(
                f"Error rendering data file '{data_file_path}' to template '{template_filename}': {str(e)}"
            )

    def render_multiple_data_files_to_template(
        self,
        data_file_paths: List[str],
        template_filename: str,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """
        Parse multiple data files and render each with the same template file.

        Args:
            data_file_paths: List of paths to document files to parse
            template_filename: Name of the Jinja template file
            extra_context: Additional context variables for the template

        Returns:
            Dictionary mapping file names to rendered content

        Example:
            files = ['jan_sales.csv', 'feb_sales.csv', 'mar_sales.csv']
            results = parser.render_multiple_data_files_to_template(
                files,
                'monthly_report.j2'
            )
        """
        results = {}

        for file_path in data_file_paths:
            try:
                file_name = Path(file_path).name
                rendered = self.render_data_file_to_template(
                    file_path, template_filename, extra_context
                )
                results[file_name] = rendered

            except Exception as e:
                logger.error(f"Failed to render {file_path}: {str(e)}")
                results[Path(file_path).name] = f"Error: {str(e)}"

        return results

    def render_data_file_to_multiple_templates(
        self,
        data_file_path: str,
        template_filenames: List[str],
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """
        Parse a data file and render it with multiple template files.

        Args:
            data_file_path: Path to the document file to parse
            template_filenames: List of template file names
            extra_context: Additional context variables for templates

        Returns:
            Dictionary mapping template names to rendered content

        Example:
            templates = ['summary.j2', 'detailed_report.j2', 'chart_data.j2']
            results = parser.render_data_file_to_multiple_templates(
                'quarterly_data.xlsx',
                templates
            )
        """
        try:
            # Parse the data file once
            logger.info(f"Parsing data file: {data_file_path}")
            document_result = self.parse_file(data_file_path)

            results = {}

            # Render with each template
            for template_filename in template_filenames:
                try:
                    rendered = self.render_template_file(
                        template_filename, document_result, extra_context
                    )
                    # Use template name without extension as key
                    template_key = Path(template_filename).stem
                    results[template_key] = rendered

                except Exception as e:
                    logger.error(
                        f"Failed to render template {template_filename}: {str(e)}"
                    )
                    results[Path(template_filename).stem] = f"Error: {str(e)}"

            return results

        except Exception as e:
            raise DocumentParsingError(
                f"Error parsing data file '{data_file_path}': {str(e)}"
            )

    def render_data_file_to_template_with_save(
        self,
        data_file_path: str,
        template_filename: str,
        output_file_path: str,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Parse a data file, render it with a template, and save to file.

        Args:
            data_file_path: Path to the document file to parse
            template_filename: Name of the Jinja template file
            output_file_path: Path where to save the rendered output
            extra_context: Additional context variables for the template

        Returns:
            Rendered template string (also saved to file)

        Example:
            parser.render_data_file_to_template_with_save(
                'data/inventory.csv',
                'inventory_report.html.j2',
                'reports/inventory_report.html'
            )
        """
        # Render the template
        rendered = self.render_data_file_to_template(
            data_file_path, template_filename, extra_context
        )

        # Save to file
        try:
            output_path = Path(output_file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(rendered)

            logger.info(f"Rendered output saved to: {output_file_path}")
            return rendered

        except Exception as e:
            raise DocumentParsingError(
                f"Error saving rendered output to '{output_file_path}': {str(e)}"
            )
