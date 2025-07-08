# Package Management: uv

This project uses uv for Python package and environment management.

## Common Commands
- **Run a command in the project environment:**
  `uv run <command>`

- **Add a dependency:**
  `uv add <package>` or `uv add <package> --dev` for dev dependencies

- **Remove a dependency:**
  `uv remove <package>` or `uv remove <package> --group dev` for dev dependencies

- **List out packages in environment in a tree structure**
  `uv tree`

- **Run tests (run after implementing changes to ensure nothing broke):**
  `uv run pytest`

## Note

- Do **not** use `pip` or `pip-tools` directly; use `uv` commands above.
