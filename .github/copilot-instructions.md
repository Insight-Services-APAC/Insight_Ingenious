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

## Mock Azure Service APIs

You can start and stop local mock Azure service APIs using the provided bash script:

- **Start mock services:**
  `./mock-azure-services.sh start`

- **Stop mock services:**
  `./mock-azure-services.sh stop`

## Note

- Do **not** use `pip` or `pip-tools` directly; use `uv` commands above.

## Using uv Workspaces

A uv workspace lets you manage multiple related Python packages in a single repository with a shared lockfile and consistent dependencies.

### Setting up a Workspace

1. In your root `pyproject.toml`, add a `[tool.uv.workspace]` table:
    ```toml
    [tool.uv.workspace]
    members = ["packages/*"]  # or list your package directories
    exclude = ["packages/some-excluded-package"]  # optional
    ```
2. Each workspace member must have its own `pyproject.toml`.

3. To add a new package to the workspace, run:
    ```
    uv init packages/new-package
    ```
   This will add the new package and update the workspace members.

### Workspace Dependencies

- To depend on another workspace member, add it to `dependencies` in your `pyproject.toml` and declare it in `[tool.uv.sources]`:
    ```toml
    [project]
    dependencies = ["other-package"]

    [tool.uv.sources]
    other-package = { workspace = true }
    ```

### Running Commands

- By default, `uv run` and `uv sync` operate on the workspace root.
- To run a command in a specific workspace member:
    ```
    uv run --package <member-name> <command>
    ```
  Example:
    ```
    uv run --package my-lib pytest
    ```

### Syncing and Locking

- `uv sync` will sync all workspace members.
- `uv lock` will update the lockfile for the entire workspace.

### More Info

- See: https://docs.astral.sh/uv/concepts/projects/workspaces/
