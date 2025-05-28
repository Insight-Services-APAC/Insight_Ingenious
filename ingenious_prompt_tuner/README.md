# Ingenious Prompt Tuner

This package provides a modular Flask-based UI for prompt tuning and agent testing in the Insight Ingenious framework.

## Structure
- `__init__.py`: App factory and blueprint registration
- `auth.py`: Authentication blueprint and login/logout functionality
- `cli.py`: Command-line interface for running the app
- `config.py`: Centralized configuration management
- `models.py`: Data models for API responses
- `utilities.py`: Utility functions and helpers
- `event_handler.py`: Event handling (moved to services/event_service.py)
- `routes/`: All Flask blueprints (home, prompts, responses)
  - `home.py`: Home page and revision management
  - `prompts.py`: Prompt template management
  - `responses.py`: Response testing and viewing
- `services/`: Business logic services
  - `__init__.py`: FileService implementation
  - `event_service.py`: Event data processing
- `templates/`: HTML templates
- `static/`: Static assets

## Usage

### Running the app

```python
# Import and use create_app() from the package
from ingenious_prompt_tuner import create_app

app = create_app()
app.run(host="0.0.0.0", port=5000)
```

### Command-line

```bash
# Run directly from the CLI
python -m ingenious_prompt_tuner.cli --host 0.0.0.0 --port 5000 --debug
```

## Development

The application follows a standard Flask blueprint structure:

1. Routes are organized in the `routes/` package
2. Business logic is in the `services/` package
3. HTML templates are in the `templates/` directory
4. Authentication is handled in `auth.py`
5. Configuration is centralized in `config.py`

## Authentication

The app uses basic session-based authentication with credentials from the configuration.
