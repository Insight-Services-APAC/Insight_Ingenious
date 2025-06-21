# Package Management: uv

This project uses uv for Python package and environment management.

## Common Commands
- **Run a command in the project environment:**
  `uv run <command>` (e.g., `uv run app.py` instead of `uv run python app.py`)

- **Add a dependency:**
  `uv add <package>` or `uv add <package> --dev` for dev dependencies

- **Remove a dependency:**
  `uv remove <package>` or `uv remove <package> --group dev` for dev dependencies

- **Sync environment with pyproject.toml and lockfile:**
  `uv sync`

- **Run tests (run after implementing changes to ensure nothing broke):**
  `uv run pytest --asyncio-mode=auto --tb=short -q`

- **List out packages in environment in a tree structure**
  `uv tree`

## Architectural Consistency

- For all actions and code generated, strictly follow the project's Domain-Driven Design (DDD), bounded contexts, and clean architecture conventions.

## Note

- Do **not** use `pip` or `pip-tools` directly; use `uv` commands above.
