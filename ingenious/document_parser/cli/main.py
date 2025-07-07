"""
Command-line interface for the document parser.
"""

import click
import os
import sys
from pathlib import Path

from ..core.parser import DocumentParser
from ..utils.exceptions import DocumentParsingError
from ..utils.logging import setup_logger, logger
from ..utils.templates import TEMPLATE_EXAMPLES


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--log-file", type=click.Path(), help="Log file path")
def cli(verbose: bool, log_file: str) -> None:
    """Document Parser CLI - Parse PDF and DOCX files to JSON."""
    log_level = 10 if verbose else 20  # DEBUG if verbose, INFO otherwise
    setup_logger(level=log_level, log_file=log_file)


@cli.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=True)
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option(
    "--output-dir", type=click.Path(), help="Output directory for multiple files"
)
@click.option("--pretty", is_flag=True, help="Pretty print JSON output")
def parse(files: tuple, output: str, output_dir: str, pretty: bool) -> None:
    """
    Parse document files and convert to JSON.

    FILES: One or more document files to parse
    """
    try:
        parser = DocumentParser()

        # Convert files tuple to list
        file_list = list(files)

        # Validate arguments
        if len(file_list) > 1 and output:
            click.echo(
                "Error: Cannot use --output with multiple files. Use --output-dir instead.",
                err=True,
            )
            sys.exit(1)

        # Process files
        for file_path in file_list:
            try:
                logger.info(f"Processing: {file_path}")

                # Check if file type is supported
                if not parser.supports_file(file_path):
                    click.echo(f"Warning: Unsupported file type: {file_path}", err=True)
                    continue

                # Parse the file
                result = parser.parse_file(file_path)

                # Determine output path
                if output:
                    output_path = output
                elif output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                    base_name = Path(file_path).stem
                    output_path = os.path.join(output_dir, f"{base_name}.json")
                else:
                    # Output to stdout
                    click.echo(result.to_json(pretty=pretty))
                    continue

                # Save to file
                result.save_to_file(output_path, pretty=pretty)
                click.echo(f"Saved: {output_path}")

            except DocumentParsingError as e:
                click.echo(f"Error parsing {file_path}: {str(e)}", err=True)
                continue
            except Exception as e:
                click.echo(
                    f"Unexpected error processing {file_path}: {str(e)}", err=True
                )
                continue

    except Exception as e:
        click.echo(f"Fatal error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def info() -> None:
    """Show information about supported file types."""
    parser = DocumentParser()
    extensions = parser.get_supported_extensions()

    click.echo("Document Parser Information")
    click.echo("=" * 30)
    click.echo(f"Supported file types: {', '.join(extensions)}")
    click.echo("\nExample usage:")
    click.echo("  document-parser parse document.pdf --output result.json")
    click.echo("  document-parser parse *.pdf *.docx --output-dir results/")


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--template", "-t", help="Template string to render")
@click.option(
    "--template-file", type=click.Path(exists=True), help="Template file to use"
)
@click.option(
    "--template-example",
    type=click.Choice(["summary", "detailed_report", "json_summary"]),
    help="Use a predefined template example",
)
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option(
    "--template-dir", type=click.Path(), help="Directory containing template files"
)
def render(
    file_path: str,
    template: str,
    template_file: str,
    template_example: str,
    output: str,
    template_dir: str,
) -> None:
    """
    Parse a document and render it with a Jinja2 template.

    FILE_PATH: Path to the document file to parse and render
    """
    try:
        # Configure parser with template directory if provided
        config = {}
        if template_dir:
            config["template_dir"] = template_dir

        parser = DocumentParser(config)

        # Determine which template to use
        template_string = None
        if template:
            template_string = template
        elif template_example:
            template_string = TEMPLATE_EXAMPLES.get(template_example)
            if not template_string:
                click.echo(
                    f"Error: Template example '{template_example}' not found", err=True
                )
                return
        elif template_file:
            # Parse document first, then render from file
            result = parser.parse_file(file_path)
            rendered = parser.render_template_file(
                os.path.basename(template_file), result
            )
        else:
            click.echo(
                "Error: Must specify --template, --template-file, or --template-example",
                err=True,
            )
            return

        # Render template (if not already rendered from file)
        if template_string:
            result = parser.parse_file(file_path)
            rendered = parser.render_template(template_string, result)

        # Output result
        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(rendered)
            click.echo(f"Rendered output saved to: {output}")
        else:
            click.echo(rendered)

    except DocumentParsingError as e:
        click.echo(f"Error parsing document: {str(e)}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error rendering template: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def templates() -> None:
    """Show available template examples."""
    click.echo("Available Template Examples")
    click.echo("=" * 30)

    for name, template in TEMPLATE_EXAMPLES.items():
        click.echo(f"\n{name}:")
        click.echo("-" * len(name))
        # Show first few lines of template
        lines = template.split("\n")[:5]
        for line in lines:
            click.echo(f"  {line}")
        if len(template.split("\n")) > 5:
            click.echo("  ...")

        click.echo(
            f"\nUsage: document-parser render document.pdf --template-example {name}"
        )

    click.echo("\nCustom Template Usage:")
    click.echo(
        'document-parser render document.pdf --template "{{ document.filename }}: {{ total_pages }} pages"'
    )

    click.echo("\nTemplate Variables Available:")
    click.echo("- document: Document metadata (filename, file_type, total_pages, etc.)")
    click.echo("- pages: List of page objects with content and metadata")
    click.echo("- total_pages, total_words, total_chars: Summary statistics")
    click.echo("- all_text, all_paragraphs, all_headings: Aggregated content")
    click.echo("- Helper functions: get_page(n), get_headings_by_level(level), etc.")


if __name__ == "__main__":
    cli()
