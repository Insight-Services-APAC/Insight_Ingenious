"""Command-line interface for running the prompt tuner app."""

import os
import sys

import click

# Add parent directory to sys.path if not already there
current_dir = os.path.abspath(os.getcwd())
if current_dir not in sys.path:
    sys.path.append(current_dir)

from ingenious_prompt_tuner.config import APP_CONFIG


@click.command()
@click.option("--host", default=APP_CONFIG["HOST"], help="Host to bind the server to")
@click.option("--port", default=APP_CONFIG["PORT"], help="Port to bind the server to")
@click.option("--debug", is_flag=True, help="Enable debug mode")
def run_app(host, port, debug):
    """Run the Flask application."""
    # Import app inside function to prevent circular imports
    from ingenious_prompt_tuner import create_app

    app = create_app()

    click.echo(f"Starting prompt tuner app on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_app()
