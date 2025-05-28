"""Ingenious Prompt Tuner - A modular Flask app for prompt tuning and testing."""

import os
import sys

from flask import Flask

# Add parent directory to sys.path if not already there
current_dir = os.path.abspath(os.getcwd())
if current_dir not in sys.path:
    sys.path.append(current_dir)

from ingenious_prompt_tuner.config import APP_CONFIG
from ingenious_prompt_tuner.services import FileService
from ingenious_prompt_tuner.services.event_service import EventService


def create_app(test_config=None):
    """Create and configure the Flask application."""
    # Create the Flask app instance
    app = Flask(
        __name__,
        static_folder="static",
        static_url_path="/static",
        template_folder="templates",
    )

    # Configure the app
    app.secret_key = APP_CONFIG["SECRET_KEY"]
    app.config.update(APP_CONFIG)

    if test_config:
        app.config.update(test_config)

    # Setup service providers
    file_service = FileService(app.config)
    event_service = EventService(file_service)

    # Add services to app context for access in blueprints
    app.file_service = file_service
    app.event_service = event_service

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
        os.makedirs(APP_CONFIG["REVISIONS_FOLDER"], exist_ok=True)
    except OSError:
        pass

    # Register blueprints
    from ingenious_prompt_tuner import auth

    app.register_blueprint(auth.bp)

    from ingenious_prompt_tuner.routes import home

    app.register_blueprint(home.bp)

    from ingenious_prompt_tuner.routes import prompts

    app.register_blueprint(prompts.bp)

    from ingenious_prompt_tuner.routes import responses

    app.register_blueprint(responses.bp)

    return app
