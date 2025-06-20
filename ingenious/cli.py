import asyncio
import importlib
import os
import pkgutil
import shutil
from pathlib import Path
from sysconfig import get_paths
from typing import Optional

import typer
import uvicorn
from rich import print
from rich.console import Console
from rich.theme import Theme
from typing_extensions import Annotated

import ingenious.utils.stage_executor as stage_executor_module
from ingenious.utils.log_levels import LogLevel
from ingenious.utils.namespace_utils import import_class_with_fallback
from ingenious.dataprep.cli import dataprep as _dataprep

app = typer.Typer(no_args_is_help=True, pretty_exceptions_show_locals=False)

app.add_typer(_dataprep, name="dataprep")

custom_theme = Theme(
    {
        "info": "dim cyan",
        "warning": "dark_orange",
        "danger": "bold red",
        "error": "bold red",
        "debug": "khaki1",
    }
)

console = Console(theme=custom_theme)


def docs_options():
    return ["generate", "serve"]


def log_levels():
    return ["DEBUG", "INFO", "WARNING", "ERROR"]


@app.command()
def run_rest_api_server(
    project_dir: Annotated[
        Optional[str],
        typer.Option(
            "--project-dir", help="Path to config.yml file. Defaults to ./config.yml"
        ),
    ] = None,
    profile_dir: Annotated[
        Optional[str],
        typer.Option(
            "--profile-dir",
            help="Path to profiles.yml file. Defaults to ./profiles.yml",
        ),
    ] = None,
    host: Annotated[
        str,
        typer.Option(
            "--host", help="Host to bind to. Use 127.0.0.1 for local development"
        ),
    ] = "127.0.0.1",
    port: Annotated[
        int,
        typer.Option("--port", help="Port to run the server on"),
    ] = 8000,
):
    """
    Start the Insight Ingenious FastAPI server with Chainlit UI.

    This command will automatically look for config.yml and profiles.yml in the current directory
    unless you specify different paths with --project-dir and --profile-dir.
    """

    # Set up default paths if not provided
    current_dir = Path.cwd()

    if project_dir is None:
        # Look for config.yml in current directory
        default_config = current_dir / "config.yml"
        if default_config.exists():
            project_dir = str(default_config)
        else:
            console.print(
                "[error]No config.yml found in current directory. Please run 'uv run ingen initialize-new-project' first or specify --project-dir[/error]"
            )
            raise typer.Exit(1)

    if profile_dir is None:
        # Look for profiles.yml in current directory first, then home directory
        local_profiles = current_dir / "profiles.yml"
        home_profiles = Path.home() / ".ingenious" / "profiles.yml"

        if local_profiles.exists():
            profile_dir = str(local_profiles)
        elif home_profiles.exists():
            profile_dir = str(home_profiles)
        else:
            console.print(
                "[error]No profiles.yml found. Please run 'uv run ingen initialize-new-project' first or specify --profile-dir[/error]"
            )
            raise typer.Exit(1)

    console.print(f"[info]🚀 Starting Insight Ingenious server...[/info]")
    console.print(f"[info]📁 Config: {project_dir}[/info]")
    console.print(f"[info]🔐 Profiles: {profile_dir}[/info]")
    console.print(f"[info]🌐 Server: http://{host}:{port}[/info]")

    # Set environment variables
    os.environ["INGENIOUS_PROJECT_PATH"] = str(project_dir).replace("\\", "/")
    os.environ["INGENIOUS_PROFILE_PATH"] = str(profile_dir).replace("\\", "/")

    import ingenious.config.config as ingen_config

    try:
        config = ingen_config.get_config()
    except Exception as e:
        console.print(f"[error]Failed to load configuration: {e}[/error]")
        console.print("[info]💡 Make sure your API keys are set in profiles.yml[/info]")
        raise typer.Exit(1)

    # Import FastAPI app after setting environment variables
    from ingenious.main import FastAgentAPI

    os.environ["LOADENV"] = "False"
    console.print(f"[info]📂 Working directory: {os.getcwd()}[/info]")

    # Setup working directory
    if CliFunctions.PureLibIncludeDirExists():
        src_path = CliFunctions.GetIncludeDir()
        dst_path = Path(os.getcwd()) / "ingenious"

        # Copy ingenious folder if it doesn't exist or is outdated
        if not dst_path.exists():
            console.print("[info]📦 Setting up framework files...[/info]")
            CliFunctions.copy_ingenious_folder(src_path, dst_path)

    def print_namespace_modules(namespace):
        try:
            import importlib.util
            import pkgutil

            spec = importlib.util.find_spec(namespace)
            if spec is None:
                console.print(f"[warning]Namespace {namespace} not found[/warning]")
                return

            if spec.submodule_search_locations:
                for importer, modname, ispkg in pkgutil.iter_modules(
                    spec.submodule_search_locations
                ):
                    console.print(f"[debug]Found module: {namespace}.{modname}[/debug]")
        except Exception as e:
            console.print(
                f"[debug]Could not enumerate modules in {namespace}: {e}[/debug]"
            )

    os.environ["INGENIOUS_WORKING_DIR"] = str(Path(os.getcwd()))
    print_namespace_modules(
        "ingenious.services.chat_services.multi_agent.conversation_flows"
    )

    # Initialize and run the FastAPI app
    fast_agent_api = FastAgentAPI(config)
    app = fast_agent_api.app

    console.print("")
    console.print("[info]✨ Server starting successfully![/info]")
    console.print(f"[info]🌐 Main API: http://{host}:{port}[/info]")
    console.print(f"[info]💬 Chat UI: http://{host}:{port}/chainlit[/info]")
    console.print(f"[info]📚 API Docs: http://{host}:{port}/docs[/info]")
    console.print("")
    console.print(
        "[info]🎯 Try asking: 'Hello! Can you help me learn about bicycles?'[/info]"
    )
    console.print("")

    # Start the server
    uvicorn.run(app, host=host, port=port)


@app.command()
def run_project():
    """
    Quick start command - starts the server with default settings.

    This is equivalent to 'run-rest-api-server' but with simpler syntax.
    Perfect for getting started after running 'initialize-new-project'.
    """
    console.print("[info]🚀 Quick starting your Insight Ingenious project![/info]")
    console.print(
        "[info]💡 This is equivalent to 'uv run ingen run-rest-api-server'[/info]"
    )
    console.print("")

    # Call run_rest_api_server with default parameters
    ctx = typer.Context(run_rest_api_server)
    ctx.invoke(run_rest_api_server)


@app.command()
def run_test_batch(
    log_level: Annotated[
        Optional[str],
        typer.Option(
            help="The option to set the log level. This controls the verbosity of the output. Allowed values are `DEBUG`, `INFO`, `WARNING`, `ERROR`. Default is `WARNING`.",
        ),
    ] = "WARNING",
    run_args: Annotated[
        Optional[str],
        typer.Option(
            help="Key value pairs to pass to the test runner. For example, `--run_args='--test_name=TestName --test_type=TestType'`",
        ),
    ] = "",
):
    """
    This command will run all the tests in the project
    """
    _log_level: LogLevel = LogLevel.from_string(log_level)

    se: stage_executor_module.stage_executor = stage_executor_module.stage_executor(
        log_level=_log_level, console=console
    )

    # Parse the run_args string into a dictionary
    kwargs = {}
    if run_args:
        for arg in run_args.split("--"):
            if not arg:
                continue
            key, value = arg.split("=")
            kwargs[key] = value

    asyncio.run(
        se.perform_stage(
            option=True,
            action_callables=[CliFunctions.RunTestBatch()],
            stage_name="Batch Tests",
            **kwargs,
        )
    )


@app.command()
def initialize_new_project():
    """Generate template folders and configuration files for a new project using the Ingenious framework."""
    base_path = Path(__file__).parent
    current_dir = Path.cwd()
    project_name = current_dir.name

    console.print(
        f"[info]🚀 Initializing new Insight Ingenious project: '{project_name}'[/info]"
    )

    templates_paths = {
        "docker": base_path / "docker_template",
        "ingenious_extensions": base_path / "ingenious_extensions_template",
        "tmp": None,  # No template, just create the folder
    }

    for folder_name, template_path in templates_paths.items():
        destination = current_dir / folder_name

        # Skip if the destination folder already exists
        if destination.exists():
            console.print(
                f"[warning]Folder '{folder_name}' already exists. Skipping...[/warning]"
            )
            continue

        # Check if a template path exists (if applicable)
        if template_path and not template_path.exists():
            console.print(
                f"[warning]Template directory '{template_path}' not found. Skipping...[/warning]"
            )
            continue

        try:
            # Create the destination folder
            destination.mkdir(parents=True, exist_ok=True)

            if template_path:
                # Copy template contents if a template path is provided
                for item in template_path.iterdir():
                    src_path = template_path / item
                    dst_path = destination / item.name

                    if src_path.is_dir():
                        if "__pycache__" not in src_path.parts:
                            shutil.copytree(
                                src_path,
                                dst_path,
                                ignore=shutil.ignore_patterns("__pycache__"),
                                dirs_exist_ok=True,
                            )
                        # replace all instances of 'ingenious_extensions_template' with the project name:
                        for root, dirs, files in os.walk(dst_path):
                            for file in files:
                                try:
                                    file_path = os.path.join(root, file)
                                    with open(file_path, "r") as f:
                                        file_contents = f.read()
                                    file_contents = file_contents.replace(
                                        "ingenious.ingenious_extensions_template",
                                        destination.name,
                                    )
                                    with open(file_path, "w") as f:
                                        f.write(file_contents)
                                except Exception as e:
                                    console.print(
                                        f"[error]Error processing file '{file_path}': {e}[/error]"
                                    )
                    else:
                        try:
                            shutil.copy2(src_path, dst_path)
                        except Exception as e:
                            console.print(
                                f"[error]Error copying files in  '{src_path}': {e}[/error]"
                            )
            elif folder_name == "tmp":
                # Create an empty context.md file in the 'tmp' folder
                (destination / "context.md").touch()

            console.print(
                f"[info]✅ Folder '{folder_name}' created successfully.[/info]"
            )

        except Exception as e:
            console.print(
                f"[error]Error processing folder '{folder_name}': {e}[/error]"
            )

    # Create .gitignore file
    _create_gitignore_file(current_dir)

    # Create config files in project directory (not home directory)
    _create_config_files(current_dir, project_name)

    # Create README with setup instructions
    _create_setup_readme(current_dir, project_name)

    # Print completion message with next steps
    _print_completion_message(current_dir, project_name)


def _create_gitignore_file(current_dir: Path):
    """Create a comprehensive .gitignore file for the project."""
    gitignore_path = current_dir / ".gitignore"
    if not gitignore_path.exists():
        gitignore_content = [
            "# Python",
            "*.pyc",
            "__pycache__/",
            "*.pyo",
            "*.pyd",
            ".Python",
            "env/",
            "venv/",
            ".venv/",
            "pip-log.txt",
            "pip-delete-this-directory.txt",
            "",
            "# Project specific",
            "*.log",
            "/files/",
            "/tmp/",
            "/.tmp/",
            "",
            "# Environment files",
            ".env",
            ".env.local",
            ".env.production",
            "",
            "# IDE",
            ".vscode/",
            ".idea/",
            "",
            "# OS",
            ".DS_Store",
            "Thumbs.db",
            "",
            "# Credentials (IMPORTANT: Keep these secret!)",
            "profiles.yml",
            "config_local.yml",
            "",
        ]
        with open(gitignore_path, "w") as f:
            f.write("\n".join(gitignore_content))
        console.print(f"[info]✅ Created .gitignore file.[/info]")


def _create_config_files(current_dir: Path, project_name: str):
    """Create config.yml and profiles.yml files with helpful documentation."""

    # Create config.yml in project directory
    config_path = current_dir / "config.yml"
    config_content = f"""# Insight Ingenious Configuration File
# Project: {project_name}
#
# This file contains non-sensitive configuration settings.
# For sensitive data (API keys, passwords), see profiles.yml

# ================================
# PROFILE SELECTION
# ================================
# Specify which profile to use from profiles.yml
# Common values: dev, staging, prod
profile: dev

# ================================
# AI MODELS CONFIGURATION
# ================================
# Configure the AI models your agents will use
models:
  - model: gpt-4o  # Model name in your Azure OpenAI deployment
    api_type: azure  # Use 'azure' for Azure OpenAI, 'openai' for OpenAI directly
    api_version: "2024-08-01-preview"  # Azure OpenAI API version

# ================================
# LOGGING SETTINGS
# ================================
logging:
  root_log_level: info     # Global log level: debug, info, warning, error
  log_level: debug         # Application-specific log level

# ================================
# CHAT HISTORY STORAGE
# ================================
# Choose how to store conversation history
chat_history:
  database_type: sqlite               # Options: sqlite, cosmos
  database_path: ./.tmp/chat_history.db  # Path for SQLite database
  database_name: {project_name}_chats    # Database name (for Cosmos DB)
  memory_path: ./.tmp                 # Temporary memory files location

# ================================
# CHAT SERVICE TYPE
# ================================
# Defines the conversation engine
chat_service:
  type: multi_agent  # Use multi-agent conversation system

# ================================
# TOOL SERVICES
# ================================
# Enable/disable additional agent tools
tool_service:
  enable: true  # Set to false to disable tool usage

# ================================
# WEB INTERFACE SETTINGS
# ================================
web_configuration:
  type: fastapi          # Web framework (currently only FastAPI supported)
  ip_address: "127.0.0.1"  # IP address to bind to (127.0.0.1 for local only)
  port: 8000            # Port to run the web server on
  authentication:
    enable: true        # Require authentication to access the API
    type: basic         # Authentication method

# ================================
# CHAINLIT UI (Optional)
# ================================
# Enable the Chainlit chat interface
chainlit_configuration:
  enable: true  # Set to true to enable the web chat UI

# ================================
# PROMPT TUNER (Optional)
# ================================
# Tool for developing and testing prompts
prompt_tuner:
  mode: "fast_api"  # Options: fast_api, flask

# ================================
# AZURE SEARCH (Optional)
# ================================
# Configure Azure Cognitive Search for knowledge bases
azure_search_services:
  - service: knowledge-base
    endpoint: https://YOUR_SEARCH_SERVICE.search.windows.net

# ================================
# DATABASE CONNECTIONS (Optional)
# ================================
# Local SQLite database for SQL agents
local_sql_db:
  database_path: /tmp/sample.db
  sample_csv_path: ./sample_data/data.csv
  sample_database_name: sample_data

# Azure SQL Database configuration
azure_sql_services:
  database_name: your_database
  table_name: your_table

# ================================
# FILE STORAGE
# ================================
# Configure where files are stored
file_storage:
  revisions:
    enable: true
    storage_type: local        # Options: local, azure
    container_name: revisions  # For Azure storage
    path: ./files             # Local storage path
    add_sub_folders: true
  data:
    enable: true
    storage_type: local
    container_name: data
    path: ./files
    add_sub_folders: true
"""

    with open(config_path, "w") as f:
        f.write(config_content)
    console.print(f"[info]✅ Created config.yml with helpful documentation.[/info]")

    # Create profiles.yml in project directory (not home directory)
    profiles_path = current_dir / "profiles.yml"
    profiles_content = f"""# Insight Ingenious Profiles Configuration
# Project: {project_name}
#
# 🚨 IMPORTANT: This file contains sensitive information (API keys, passwords)
# - Keep this file secure and do not commit it to version control
# - The .gitignore file excludes this file by default
# - Copy this to a secure location for production deployments

# ================================
# DEVELOPMENT PROFILE
# ================================
- name: dev
  # ================================
  # AI MODEL CREDENTIALS
  # ================================
  models:
    - model: gpt-4o
      # 🔑 Your Azure OpenAI API key - REQUIRED
      api_key: "YOUR_AZURE_OPENAI_API_KEY_HERE"
      # 🌐 Your Azure OpenAI endpoint - REQUIRED
      base_url: "https://YOUR_RESOURCE_NAME.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"

  # ================================
  # CHAT HISTORY DATABASE
  # ================================
  chat_history:
    # For Cosmos DB, provide connection string
    database_connection_string: ""

  # ================================
  # AZURE SEARCH CREDENTIALS
  # ================================
  azure_search_services:
    - service: knowledge-base
      # 🔑 Azure Search admin key - OPTIONAL
      key: "YOUR_AZURE_SEARCH_ADMIN_KEY_HERE"

  # ================================
  # AZURE SQL CREDENTIALS
  # ================================
  azure_sql_services:
    # SQL Server connection string - OPTIONAL
    database_connection_string: "Server=tcp:your-server.database.windows.net,1433;Database=your-db;User ID=your-user;Password=your-password;Encrypt=true;TrustServerCertificate=false;Connection Timeout=30;"

  # ================================
  # WEB AUTHENTICATION
  # ================================
  web_configuration:
    authentication:
      enable: true
      # 🔑 Basic auth credentials for API access
      username: "admin"
      password: "CHANGE_THIS_PASSWORD"

  # ================================
  # CHAINLIT AUTHENTICATION
  # ================================
  chainlit_configuration:
    enable: true
    authentication:
      enable: false  # Set to true to require GitHub OAuth
      # For GitHub OAuth (optional):
      github_client_id: "YOUR_GITHUB_CLIENT_ID"
      github_secret: "YOUR_GITHUB_SECRET"

  # ================================
  # AZURE BLOB STORAGE (Optional)
  # ================================
  file_storage:
    revisions:
      url: https://YOUR_STORAGE_ACCOUNT.blob.core.windows.net/
      authentication_method: default_credential  # Options: msi, default_credential
    data:
      url: https://YOUR_STORAGE_ACCOUNT.blob.core.windows.net/
      authentication_method: default_credential

  # ================================
  # EXTERNAL INTEGRATIONS (Optional)
  # ================================
  receiver_configuration:
    enable: false
    api_url: "https://your-webhook-endpoint.com/api/ai-response/publish"
    api_key: "YOUR_WEBHOOK_API_KEY"

# ================================
# PRODUCTION PROFILE TEMPLATE
# ================================
# Uncomment and configure for production:
# - name: prod
#   models:
#     - model: gpt-4o
#       api_key: "PRODUCTION_API_KEY"
#       base_url: "https://prod-resource.openai.azure.com/..."
#   web_configuration:
#     authentication:
#       enable: true
#       username: "prod_admin"
#       password: "STRONG_PRODUCTION_PASSWORD"
#   # ... other production settings
"""

    with open(profiles_path, "w") as f:
        f.write(profiles_content)
    console.print(f"[info]✅ Created profiles.yml with example configuration.[/info]")
    console.print(
        f"[warning]⚠️  Remember to update API keys and passwords in profiles.yml![/warning]"
    )


def _create_setup_readme(current_dir: Path, project_name: str):
    """Create a comprehensive setup README."""
    readme_path = current_dir / "SETUP.md"
    readme_content = f"""# {project_name} - Insight Ingenious Setup Guide

Welcome to your new Insight Ingenious project! This guide will help you get a "Hello World" example running.

## 🚀 Quick Start

### Step 1: Set Environment Variables

Set these environment variables to point to your configuration files:

```bash
# In your terminal or add to your ~/.bashrc or ~/.zshrc
export INGENIOUS_PROJECT_PATH="$(pwd)/config.yml"
export INGENIOUS_PROFILE_PATH="$(pwd)/profiles.yml"
```

### Step 2: Configure Your AI Model

1. **Get Azure OpenAI Access:**
   - Go to [Azure Portal](https://portal.azure.com)
   - Create an Azure OpenAI resource
   - Deploy a GPT-4 model
   - Copy the API key and endpoint

2. **Update profiles.yml:**
   ```yaml
   - name: dev
     models:
       - model: gpt-4o
         api_key: "YOUR_ACTUAL_API_KEY_HERE"
         base_url: "https://YOUR_RESOURCE_NAME.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"
   ```

### Step 3: Test Your Setup

Run the application:

```bash
uv run ingen run-rest-api-server
```

### Step 4: Try Your First Chat

Open your browser and go to:
- Main API: http://localhost:8000
- Chat Interface: http://localhost:8000/chainlit
- API Docs: http://localhost:8000/docs

## 🔧 Configuration Files

### config.yml
Non-sensitive settings like:
- Which AI models to use
- Database settings
- Web server configuration
- Logging levels

### profiles.yml
Sensitive credentials like:
- API keys
- Passwords
- Connection strings

⚠️ **Never commit profiles.yml to version control!**

## 🤖 Available Agent Flows

Your project comes with these pre-built agent flows:

1. **classification_agent** - Routes questions to specialized agents
2. **knowledge_base_agent** - Answers from uploaded documents
3. **pandas_agent** - Analyzes data and creates visualizations
4. **sql_manipulation_agent** - Generates and runs SQL queries
5. **web_critic_agent** - Searches web and fact-checks information

## 📁 Project Structure

```
{project_name}/
├── config.yml              # Non-sensitive configuration
├── profiles.yml             # Sensitive credentials (keep secret!)
├── SETUP.md                 # This file
├── .gitignore              # Excludes sensitive files
├── ingenious_extensions/    # Your custom agents and extensions
├── docker/                 # Docker configuration
└── tmp/                    # Temporary files
```

## 🛠️ Next Steps

### Create a Custom Agent

1. **Add an agent definition:**
   ```bash
   mkdir -p ingenious_extensions/services/chat_services/multi_agent/agents/bicycle_agent
   ```

2. **Create agent.md:**
   ```markdown
   # Bicycle Expert Agent

   ## Name and Persona
   * Name: You are Ingenious, a Bicycle Expert
   * Description: You are a bicycle maintenance and repair expert.

   ## System Message
   You help people with bicycle-related questions, from basic maintenance
   to advanced repairs. Always provide safe, practical advice.
   ```

3. **Create tasks/task.md:**
   ```markdown
   # Bicycle Agent Tasks

   You help users with:
   - Bicycle maintenance and repair
   - Choosing the right bicycle
   - Safety tips and best practices
   - Troubleshooting common problems
   ```

### Test Your Agent

```bash
uv run ingen run-test-batch
```

## 🔍 Debugging

### Check Configuration
```bash
# Verify environment variables
echo $INGENIOUS_PROJECT_PATH
echo $INGENIOUS_PROFILE_PATH

# Test configuration loading
uv run python -c "import ingenious.config.config as config; print(config.get_config())"
```

### View Logs
```bash
# Check logs in the tmp directory
tail -f tmp/*.log
```

### Common Issues

1. **"API key not found"**
   - Check your profiles.yml has the correct API key
   - Verify environment variables are set

2. **"Template not found"**
   - Make sure you're running commands from the project root
   - Check that ingenious_extensions folder exists

3. **"Connection refused"**
   - Check if another service is using port 8000
   - Try a different port: `uv run ingen run-rest-api-server --port 8080`

## 📚 Learn More

- [Insight Ingenious Documentation](https://github.com/Insight-Services-APAC/Insight_Ingenious/tree/main/docs)
- [Contributing Guide](https://github.com/Insight-Services-APAC/Insight_Ingenious/blob/main/CONTRIBUTING.md)

## 🎉 Hello World Test

Try this simple test:

1. Start the server: `uv run ingen run-rest-api-server`
2. Go to: http://localhost:8000/chainlit
3. Type: "Hello! Can you help me learn about bicycles?"
4. The classification agent should route you to the appropriate expert!

Happy coding! 🚀
"""

    with open(readme_path, "w") as f:
        f.write(readme_content)
    console.print(f"[info]✅ Created SETUP.md with comprehensive instructions.[/info]")


def _print_completion_message(current_dir: Path, project_name: str):
    """Print a comprehensive completion message with next steps."""
    console.print("\n" + "=" * 60)
    console.print(f"[info]🎉 Project '{project_name}' initialized successfully![/info]")
    console.print("=" * 60 + "\n")

    console.print("[info]📋 Next Steps:[/info]")
    console.print("   1. 🔧 Set environment variables:")
    console.print(f'      export INGENIOUS_PROJECT_PATH="{current_dir}/config.yml"')
    console.print(f'      export INGENIOUS_PROFILE_PATH="{current_dir}/profiles.yml"')
    console.print("")
    console.print("   2. 🔑 Update profiles.yml with your Azure OpenAI credentials")
    console.print("      (Get these from https://portal.azure.com)")
    console.print("")
    console.print("   3. 🚀 Start the application:")
    console.print("      uv run ingen run-rest-api-server")
    console.print("")
    console.print("   4. 🌐 Open your browser:")
    console.print("      Main API:      http://localhost:8000")
    console.print("      Chat UI:       http://localhost:8000/chainlit")
    console.print("      API Docs:      http://localhost:8000/docs")
    console.print("")
    console.print("[info]📖 For detailed instructions, see: SETUP.md[/info]")
    console.print(
        "[warning]⚠️  Remember: Never commit profiles.yml (contains API keys)![/warning]"
    )
    console.print("")
    console.print(
        "[info]🎯 Test with: 'Hello! Can you help me learn about bicycles?'[/info]"
    )


@app.command()
def run_prompt_tuner():
    """Run the prompt tuner web application."""
    from ingenious_prompt_tuner import create_app as prompt_tuner

    app = prompt_tuner()
    app.run(debug=True, host="0.0.0.0", port=80)


if __name__ == "__cli__":
    app()


class CliFunctions:
    class RunTestBatch(stage_executor_module.IActionCallable):
        async def __call__(self, progress, task_id, **kwargs):
            module_name = "tests.run_tests"
            class_name = "RunBatches"
            try:
                repository_class_import = import_class_with_fallback(
                    module_name, class_name
                )
                repository_class = repository_class_import(
                    progress=progress, task_id=task_id
                )

                await repository_class.run(progress, task_id, **kwargs)

            except (ImportError, AttributeError) as e:
                raise ValueError(f"Batch Run Failed: {module_name}") from e

    @staticmethod
    def PureLibIncludeDirExists():
        ChkPath = Path(get_paths()["purelib"]) / Path("ingenious/")
        return os.path.exists(ChkPath)

    @staticmethod
    def GetIncludeDir():
        ChkPath = Path(get_paths()["purelib"]) / Path("ingenious/")
        # print(ChkPath)
        # Does Check for the path
        if os.path.exists(ChkPath):
            return ChkPath
        else:
            path = Path(os.getcwd()) / Path("ingenious/")
            # print(str(path))
            return path

    @staticmethod
    def copy_ingenious_folder(src, dst):
        if not os.path.exists(dst):
            os.makedirs(dst)  # Create the destination directory if it doesn't exist

        for item in os.listdir(src):
            src_path = os.path.join(src, item)
            dst_path = os.path.join(dst, item)

            if os.path.isdir(src_path):
                # Recursively copy subdirectories
                CliFunctions.copy_ingenious_folder(src_path, dst_path)
            else:
                # Copy files
                if not os.path.exists(dst_path) or os.path.getmtime(
                    src_path
                ) > os.path.getmtime(dst_path):
                    shutil.copy2(src_path, dst_path)  # Copy file with metadata
