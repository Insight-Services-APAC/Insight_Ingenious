"""
Template processing utilities using Jinja2.
"""

import os
from typing import Dict, Any, Optional, List
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from ..core.models import DocumentResult
from ..utils.exceptions import InvalidConfigurationError
from ..utils.logging import logger


class TemplateProcessor:
    """
    Process document parsing results with Jinja2 templates.

    This class provides functionality to bind parsed document content
    to Jinja2 templates for generating formatted output strings.
    """

    def __init__(self, template_dir: Optional[str] = None) -> None:
        """
        Initialize the template processor.

        Args:
            template_dir: Directory containing template files (optional)
        """
        self.template_dir = template_dir
        self._env = None
        self._setup_environment()
        logger.info("TemplateProcessor initialized")

    def _setup_environment(self) -> None:
        """Set up Jinja2 environment."""
        if self.template_dir and os.path.exists(self.template_dir):
            # Use FileSystemLoader if template directory exists
            loader = FileSystemLoader(self.template_dir)
            self._env = Environment(
                loader=loader, autoescape=True, trim_blocks=True, lstrip_blocks=True
            )
            logger.info(
                f"Template environment setup with directory: {self.template_dir}"
            )
        else:
            # Use default environment for string templates
            self._env = Environment(
                autoescape=True, trim_blocks=True, lstrip_blocks=True
            )
            logger.info("Template environment setup for string templates")

    def render_from_string(
        self,
        template_string: str,
        document_result: DocumentResult,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render a template string with document data.

        Args:
            template_string: Jinja2 template as string
            document_result: Parsed document result
            extra_context: Additional context variables

        Returns:
            Rendered template string

        Raises:
            InvalidConfigurationError: If template rendering fails
        """
        try:
            template = self._env.from_string(template_string)
            context = self._build_context(document_result, extra_context)

            logger.debug("Rendering template from string")
            rendered = template.render(**context)
            logger.info("Template rendered successfully from string")

            return rendered

        except Exception as e:
            raise InvalidConfigurationError(
                f"Failed to render template from string: {str(e)}"
            )

    def render_from_file(
        self,
        template_filename: str,
        document_result: DocumentResult,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render a template file with document data.

        Args:
            template_filename: Name of template file
            document_result: Parsed document result
            extra_context: Additional context variables

        Returns:
            Rendered template string

        Raises:
            InvalidConfigurationError: If template file not found or rendering fails
        """
        if not self.template_dir:
            raise InvalidConfigurationError(
                "Template directory not configured for file-based templates"
            )

        try:
            template = self._env.get_template(template_filename)
            context = self._build_context(document_result, extra_context)

            logger.debug(f"Rendering template from file: {template_filename}")
            rendered = template.render(**context)
            logger.info(
                f"Template rendered successfully from file: {template_filename}"
            )

            return rendered

        except TemplateNotFound:
            raise InvalidConfigurationError(
                f"Template file not found: {template_filename}"
            )
        except Exception as e:
            raise InvalidConfigurationError(
                f"Failed to render template from file '{template_filename}': {str(e)}"
            )

    def render_multiple(
        self,
        templates: List[Dict[str, Any]],
        document_result: DocumentResult,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """
        Render multiple templates with the same document data.

        Args:
            templates: List of template definitions with 'name' and either 'string' or 'file'
            document_result: Parsed document result
            extra_context: Additional context variables

        Returns:
            Dictionary mapping template names to rendered content

        Example:
            templates = [
                {"name": "summary", "string": "Document: {{ document.filename }}"},
                {"name": "report", "file": "report_template.html"}
            ]
        """
        results = {}

        for template_def in templates:
            template_name = template_def.get("name")
            if not template_name:
                logger.warning("Template definition missing 'name', skipping")
                continue

            try:
                if "string" in template_def:
                    rendered = self.render_from_string(
                        template_def["string"], document_result, extra_context
                    )
                elif "file" in template_def:
                    rendered = self.render_from_file(
                        template_def["file"], document_result, extra_context
                    )
                else:
                    logger.warning(
                        f"Template '{template_name}' missing 'string' or 'file'"
                    )
                    continue

                results[template_name] = rendered

            except Exception as e:
                logger.error(f"Failed to render template '{template_name}': {str(e)}")
                results[template_name] = f"Error: {str(e)}"

        return results

    def _build_context(
        self,
        document_result: DocumentResult,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Build template context from document result and extra context.

        Args:
            document_result: Parsed document result
            extra_context: Additional context variables

        Returns:
            Complete context dictionary for template rendering
        """
        # Convert document result to dictionary
        context = {
            "document_info": document_result.document_info,  # Keep as object for easier access
            "document": document_result.document_info.to_dict(),  # Dictionary version for compatibility
            "pages": document_result.pages,  # Keep as objects for easier access
            "pages_dict": [
                page.to_dict() for page in document_result.pages
            ],  # Dictionary version
            "total_pages": len(document_result.pages),
            "total_words": sum(
                page.metadata.word_count for page in document_result.pages
            ),
            "total_chars": sum(
                page.metadata.char_count for page in document_result.pages
            ),
            "all_text": "\n\n".join(
                page.content.text for page in document_result.pages
            ),
            "all_paragraphs": [
                para
                for page in document_result.pages
                for para in page.content.paragraphs
            ],
            "all_headings": [
                heading
                for page in document_result.pages
                for heading in page.content.headings
            ],
        }

        # Add helper functions to context
        context.update(
            {
                "get_page": lambda n: document_result.pages[n - 1]
                if 1 <= n <= len(document_result.pages)
                else None,
                "get_headings_by_level": lambda level: [
                    h
                    for page in document_result.pages
                    for h in page.content.headings
                    if h.level == level
                ],
                "word_count_range": lambda min_words, max_words: [
                    page
                    for page in document_result.pages
                    if min_words <= page.metadata.word_count <= max_words
                ],
            }
        )

        # Merge with extra context
        if extra_context:
            context.update(extra_context)

        return context

    def save_rendered_template(
        self,
        template_string: str,
        document_result: DocumentResult,
        output_path: str,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Render template and save to file.

        Args:
            template_string: Jinja2 template as string
            document_result: Parsed document result
            output_path: Path to save rendered output
            extra_context: Additional context variables
        """
        rendered = self.render_from_string(
            template_string, document_result, extra_context
        )

        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered)

        logger.info(f"Rendered template saved to: {output_path}")


# Pre-defined template examples
TEMPLATE_EXAMPLES = {
    "summary": """
Document Summary
================
Filename: {{ document.filename }}
Type: {{ document.file_type.upper() }}
Total Pages: {{ total_pages }}
Total Words: {{ total_words }}
File Size: {{ document.file_size }} bytes
Created: {{ document.created_at }}

{% if all_headings %}
Table of Contents:
{% for heading in all_headings %}
{{ "  " * (heading.level - 1) }}{{ heading.level }}. {{ heading.text }}
{% endfor %}
{% endif %}

{% if pages|length > 0 %}
First Page Preview:
{{ pages[0].content.text[:200] }}{% if pages[0].content.text|length > 200 %}...{% endif %}
{% endif %}
""".strip(),
    "detailed_report": """
# Document Analysis Report

## Document Information
- **Filename**: {{ document.filename }}
- **Type**: {{ document.file_type.upper() }}
- **Pages**: {{ total_pages }}
- **Total Words**: {{ total_words }}
- **Total Characters**: {{ total_chars }}
- **File Size**: {{ document.file_size }} bytes
- **Processed**: {{ document.created_at }}

## Content Structure

{% if all_headings %}
### Headings Found
{% for heading in all_headings %}
- Level {{ heading.level }}: {{ heading.text }}
{% endfor %}
{% endif %}

## Page-by-Page Analysis

{% for page in pages %}
### Page {{ page.page_number }}
- **Word Count**: {{ page.metadata.word_count }}
- **Character Count**: {{ page.metadata.char_count }}

{% if page.content.headings %}
**Headings on this page**:
{% for heading in page.content.headings %}
- {{ heading.text }}
{% endfor %}
{% endif %}

**Content Preview**:
```
{{ page.content.text[:300] }}{% if page.content.text|length > 300 %}...{% endif %}
```

---
{% endfor %}
""".strip(),
    "json_summary": """
{
  "summary": {
    "filename": "{{ document.filename }}",
    "type": "{{ document.file_type }}",
    "pages": {{ total_pages }},
    "words": {{ total_words }},
    "characters": {{ total_chars }},
    "size_bytes": {{ document.file_size }}
  },
  "headings": [
    {% for heading in all_headings %}
    {
      "level": {{ heading.level }},
      "text": "{{ heading.text|replace('"', '\\"') }}"
    }{% if not loop.last %},{% endif %}
    {% endfor %}
  ],
  "page_stats": [
    {% for page in pages %}
    {
      "page": {{ page.page_number }},
      "words": {{ page.metadata.word_count }},
      "characters": {{ page.metadata.char_count }}
    }{% if not loop.last %},{% endif %}
    {% endfor %}
  ]
}
""".strip(),
}
