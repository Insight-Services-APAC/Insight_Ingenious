import os
import shutil
from pathlib import Path
from sysconfig import get_paths
from typing import Optional

import typer
import uvicorn
from rich.console import Console
from rich.theme import Theme
from typing_extensions import Annotated

app = typer.Typer(no_args_is_help=True, pretty_exceptions_show_locals=False)

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

    console.print("[info]🚀 Starting Insight Ingenious server...[/info]")
    console.print(f"[info]📁 Config: {project_dir}[/info]")
    console.print(f"[info]🔐 Profiles: {profile_dir}[/info]")
    console.print(f"[info]🌐 Server: http://{host}:{port}[/info]")

    # Set environment variables
    os.environ["INGENIOUS_PROJECT_PATH"] = str(project_dir).replace("\\", "/")
    os.environ["INGENIOUS_PROFILE_PATH"] = str(profile_dir).replace("\\", "/")

    from ingenious.configuration.domain.models import MinimalConfig

    try:
        config = MinimalConfig()
    except Exception as e:
        console.print(f"[error]Failed to load configuration: {e}[/error]")
        console.print("[info]💡 Make sure your API keys are set in profiles.yml[/info]")
        raise typer.Exit(1)

    # Import FastAPI app after setting environment variables
    from ingenious.main import FastAgentAPI

    os.environ["LOADENV"] = "False"
    console.print(f"[info]📂 Working directory: {os.getcwd()}[/info]")

    # Setup working directory
    ingenious_path = Path(get_paths()["purelib"]) / "ingenious"
    if ingenious_path.exists():
        src_path = ingenious_path
        dst_path = Path(os.getcwd()) / "ingenious"

        # Copy ingenious folder if it doesn't exist or is outdated
        if not dst_path.exists():
            console.print("[info]📦 Setting up framework files...[/info]")
            _copy_ingenious_folder(src_path, dst_path)

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
    # Legacy conversation flow discovery disabled - use DDD chat services instead

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
    🚀 Quick start command - starts your Insight Ingenious project with default settings.

    This is equivalent to 'run-rest-api-server' but with simpler syntax.
    Perfect for getting started after running 'initialize-new-project'.

    Example:
        uv run ingen run-project

    This will start your server on http://localhost:8000 with:
    - Chat UI at: http://localhost:8000/chainlit
    - API docs at: http://localhost:8000/docs
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

        try:
            # Create the destination folder
            destination.mkdir(parents=True, exist_ok=True)

            if folder_name == "ingenious_extensions":
                # Create the ingenious_extensions structure manually instead of relying on templates
                _create_ingenious_extensions_structure(destination, project_name)
            elif folder_name == "docker" and template_path and template_path.exists():
                # Copy docker template if it exists
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
        console.print("[info]✅ Created .gitignore file.[/info]")


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
    console.print("[info]✅ Created config.yml with helpful documentation.[/info]")

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
      # Get this from Azure Portal > Your OpenAI Resource > Keys and Endpoint
      api_key: "REPLACE_WITH_YOUR_AZURE_OPENAI_API_KEY"

      # 🌐 Your Azure OpenAI endpoint - REQUIRED
      # Format: https://YOUR_RESOURCE_NAME.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview
      # Replace YOUR_RESOURCE_NAME with your actual Azure OpenAI resource name
      base_url: "https://REPLACE_WITH_YOUR_RESOURCE_NAME.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"

  # ================================
  # CHAT HISTORY DATABASE
  # ================================
  chat_history:
    # For Cosmos DB (optional), provide connection string
    database_connection_string: ""

  # ================================
  # AZURE SEARCH CREDENTIALS (Optional)
  # ================================
  azure_search_services:
    - service: knowledge-base
      # 🔑 Azure Search admin key - OPTIONAL
      key: "YOUR_AZURE_SEARCH_ADMIN_KEY_HERE"

  # ================================
  # AZURE SQL CREDENTIALS (Optional)
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
      type: basic
      # 🔑 Basic auth credentials for API access
      # Change these default credentials!
      username: "admin"
      password: "CHANGE_THIS_PASSWORD_FOR_SECURITY"

  # ================================
  # CHAINLIT AUTHENTICATION (Optional)
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
    console.print("[info]✅ Created profiles.yml with example configuration.[/info]")
    console.print(
        "[warning]⚠️  Remember to update API keys and passwords in profiles.yml![/warning]"
    )


def _create_setup_readme(current_dir: Path, project_name: str):
    """Create a comprehensive setup README."""
    readme_path = current_dir / "SETUP.md"
    readme_content = f"""# {project_name} - Quick Start Guide

Welcome to your new Insight Ingenious project! This guide will get you up and running with a "Hello World: Bicycle Expert" example in just a few minutes.

## 🚀 Quick Start (5 minutes to Hello World!)

### Step 1: Set Environment Variables

```bash
# Copy and paste these commands in your terminal:
export INGENIOUS_PROJECT_PATH="$(pwd)/config.yml"
export INGENIOUS_PROFILE_PATH="$(pwd)/profiles.yml"

# To make these permanent, add them to your ~/.bashrc or ~/.zshrc:
echo 'export INGENIOUS_PROJECT_PATH="$(pwd)/config.yml"' >> ~/.zshrc
echo 'export INGENIOUS_PROFILE_PATH="$(pwd)/profiles.yml"' >> ~/.zshrc
```

### Step 2: Get Your Azure OpenAI Credentials

1. **Get Azure OpenAI Access:**
   - Go to [Azure Portal](https://portal.azure.com)
   - Create an Azure OpenAI resource (if you don't have one)
   - Deploy a GPT-4 model (name it "gpt-4o")
   - Go to "Keys and Endpoint" section and copy:
     - Your API key
     - Your endpoint URL

2. **Update profiles.yml:**
   ```yaml
   - name: dev
     models:
       - model: gpt-4o
         # Replace YOUR_API_KEY_HERE with your actual API key:
         api_key: "YOUR_API_KEY_HERE"
         # Replace YOUR_RESOURCE_NAME with your actual resource name:
         base_url: "https://YOUR_RESOURCE_NAME.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"
   ```

### Step 3: Test Your Setup

```bash
# Start the server:
uv run ingen run-rest-api-server

# You should see:
# "🚀 Starting Insight Ingenious on http://127.0.0.1:8000"
```

### Step 4: Try Your First Chat!

1. **Open your browser and go to:** http://localhost:8000/chainlit

2. **Try this hello world message:**
   ```
   Hello! Can you help me learn about bicycles?
   ```

3. **You should get a friendly response from your bicycle expert agent!**

## 🎯 What You Just Built

Your project includes:
- **Bicycle Expert Agent**: A friendly AI that knows everything about bicycles
- **Web Chat Interface**: Clean, modern chat UI powered by Chainlit
- **REST API**: Full API access at http://localhost:8000/docs
- **Sample Data**: Bicycle data in `ingenious_extensions/sample_data/bicycles.csv`

## 🌐 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Chat UI** | http://localhost:8000/chainlit | Interactive chat interface |
| **API Docs** | http://localhost:8000/docs | REST API documentation |
| **Main API** | http://localhost:8000 | API endpoint |

## 🔧 Configuration Files

### config.yml
Non-sensitive settings:
- AI models and versions
- Database configuration
- Web server settings
- Logging levels

### profiles.yml
Sensitive credentials:
- API keys
- Passwords
- Connection strings

⚠️ **Never commit profiles.yml to version control!**

## 🤖 Your Bicycle Expert Agent

Located in: `ingenious_extensions/models/agent.py`

This agent can help with:
- Bicycle maintenance and repair
- Choosing the right bicycle
- Safety tips and best practices
- Troubleshooting common problems

## 📝 Example Conversations

Try these prompts with your bicycle expert:

```
"What should I look for when buying my first road bike?"

"My bicycle chain keeps slipping. What could be wrong?"

"How do I properly maintain my bicycle brakes?"

"What's the difference between mountain bikes and hybrid bikes?"
```

## 🛠️ Next Steps: Customize Your Agent

### 1. Modify the Agent Personality

Edit: `ingenious_extensions/templates/prompts/bicycle_expert_prompt.jinja`

```jinja
### PERSONALITY
- Change from "friendly and knowledgeable" to your preferred style
- Add specific expertise areas
- Adjust the greeting message
```

### 2. Add New Agents

In `ingenious_extensions/models/agent.py`, add new agents:

```python
local_agents.append(
    Agent(
        agent_name="cooking_expert",
        agent_model_name="gpt-4o",
        agent_display_name="Cooking Expert",
        agent_description="A culinary expert that helps with recipes and cooking.",
        agent_type="expert",
        model=None,
        system_prompt=None,
        log_to_prompt_tuner=True,
        return_in_response=True,
    )
)
```

### 3. Create New Prompt Templates

Create: `ingenious_extensions/templates/prompts/cooking_expert_prompt.jinja`

## 🔍 Troubleshooting

### "API key not found"
- Check that profiles.yml has your actual API key (not "YOUR_API_KEY_HERE")
- Verify environment variables: `echo $INGENIOUS_PROFILE_PATH`

### "Template not found"
- Make sure you're in the project root directory
- Check that ingenious_extensions folder exists

### "Connection refused on port 8000"
- Another service might be using port 8000
- Try: `uv run ingen run-rest-api-server --port 8080`

### "Model 'gpt-4o' not found"
- Check your Azure OpenAI deployment name matches "gpt-4o"
- Verify the base_url points to the correct deployment

## 📚 Learn More

- [Insight Ingenious Documentation](https://github.com/Insight-Services-APAC/Insight_Ingenious/tree/main/docs)
- [Contributing Guide](https://github.com/Insight-Services-APAC/Insight_Ingenious/blob/main/CONTRIBUTING.md)

## 🎉 Success Indicators

✅ You've successfully set up Insight Ingenious when:
1. The server starts without errors
2. You can access the chat UI
3. The bicycle expert responds to your questions
4. You see logs in the tmp directory

**Congratulations! You're ready to build amazing AI agents! �‍♀️🎉**
"""

    with open(readme_path, "w") as f:
        f.write(readme_content)
    console.print(
        "[info]✅ Created comprehensive SETUP.md with bicycle expert guide.[/info]"
    )


def _print_completion_message(current_dir: Path, project_name: str):
    """Print a comprehensive completion message with next steps."""
    console.print("\n" + "=" * 70)
    console.print(
        f"[info]🎉 '{project_name}' initialized with Bicycle Expert example![/info]"
    )
    console.print("=" * 70 + "\n")

    console.print("[info]� Quick Start (2 minutes to Hello World):[/info]")
    console.print("")
    console.print("[info]1. 🔧 Set environment variables:[/info]")
    console.print(f'   export INGENIOUS_PROJECT_PATH="{current_dir}/config.yml"')
    console.print(f'   export INGENIOUS_PROFILE_PATH="{current_dir}/profiles.yml"')
    console.print("")
    console.print(
        "[info]2. 🔑 Update profiles.yml with your Azure OpenAI credentials:[/info]"
    )
    console.print("   - Replace YOUR_API_KEY_HERE with your actual API key")
    console.print("   - Replace YOUR_RESOURCE_NAME with your Azure resource name")
    console.print("   - Get these from: https://portal.azure.com")
    console.print("")
    console.print("[info]3. 🚀 Start the application:[/info]")
    console.print("   uv run ingen run-rest-api-server")
    console.print("")
    console.print("[info]4. 🌐 Test your Bicycle Expert:[/info]")
    console.print("   • Open: http://localhost:8000/chainlit")
    console.print("   • Type: 'Hello! Can you help me learn about bicycles?'")
    console.print("   • API Docs: http://localhost:8000/docs")
    console.print("")
    console.print("[info]📋 What you get out of the box:[/info]")
    console.print("   ✅ Bicycle Expert Agent (ready to chat!)")
    console.print("   ✅ Web Chat Interface (Chainlit UI)")
    console.print("   ✅ REST API with documentation")
    console.print("   ✅ Sample bicycle data")
    console.print("   ✅ Comprehensive setup guide")
    console.print("")
    console.print("[info]📖 For detailed instructions: SETUP.md[/info]")
    console.print(
        "[warning]⚠️  Security: Never commit profiles.yml (contains API keys)![/warning]"
    )
    console.print("")
    console.print("[info]🎯 Hello World Test:[/info]")
    console.print("   Ask: 'What should I look for when buying my first bike?'")
    console.print("")
    console.print("[info]Happy building! 🚴‍♀️✨[/info]")


if __name__ == "__cli__":
    app()


def _copy_ingenious_folder(src, dst):
    """Copy ingenious folder with all subdirectories and files."""
    if not os.path.exists(dst):
        os.makedirs(dst)  # Create the destination directory if it doesn't exist

    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)

        if os.path.isdir(src_path):
            # Recursively copy subdirectories
            _copy_ingenious_folder(src_path, dst_path)
        else:
            # Copy files
            if not os.path.exists(dst_path) or os.path.getmtime(
                src_path
            ) > os.path.getmtime(dst_path):
                shutil.copy2(src_path, dst_path)  # Copy file with metadata


def _create_ingenious_extensions_structure(destination: Path, project_name: str):
    """Create the ingenious_extensions directory structure with sample files."""

    # Create main directories
    (destination / "models").mkdir(exist_ok=True)
    (destination / "services" / "chat_services").mkdir(parents=True, exist_ok=True)
    (destination / "templates" / "prompts").mkdir(parents=True, exist_ok=True)
    (destination / "api").mkdir(exist_ok=True)
    (destination / "sample_data").mkdir(exist_ok=True)
    (destination / "tests").mkdir(exist_ok=True)

    # Create main __init__.py files
    (destination / "__init__.py").touch()
    (destination / "models" / "__init__.py").touch()
    (destination / "services" / "__init__.py").touch()
    (destination / "services" / "chat_services" / "__init__.py").touch()
    (destination / "templates" / "__init__.py").touch()
    (destination / "templates" / "prompts" / "__init__.py").touch()

    # Create the main agent model file
    agent_model_content = """# NOTE: Legacy model imports have been removed for DDD migration
# Please update your agent definitions to use the new DDD structure
# See documentation for migration guide

# from ingenious.chat.domain.models import Agent, ChatRequest
# from ingenious.configuration.application.services import ConfigurationRetrievalUseCase


class ProjectAgents:
    def get_project_agents(self, config_service) -> list:
        local_agents = []

        # Hello World Bicycle Expert Agent
        local_agents.append(
            Agent(
                agent_name="bicycle_expert",
                agent_model_name="gpt-4o",
                agent_display_name="Bicycle Expert",
                agent_description="A friendly bicycle expert that helps with all bicycle-related questions.",
                agent_type="expert",
                model=None,
                system_prompt=None,
                log_to_prompt_tuner=True,
                return_in_response=True,
            )
        )

        # User proxy for multi-agent conversations
        local_agents.append(
            Agent(
                agent_name="user_proxy",
                agent_model_name="gpt-4o",
                agent_display_name="User Proxy",
                agent_description="Manages user interactions and routes conversations.",
                agent_type="user_proxy",
                model=None,
                system_prompt=None,
                log_to_prompt_tuner=False,
                return_in_response=False,
            )
        )

        return Agents(agents=local_agents, config=config)
"""

    with open(destination / "models" / "agent.py", "w") as f:
        f.write(agent_model_content)

    # Create bicycle expert prompt template
    bicycle_prompt_content = """### ROLE
You are a friendly and knowledgeable bicycle expert. Your name is Ingenious, and you specialize in helping people with all aspects of bicycles.

### PERSONALITY
- Enthusiastic about cycling and bicycles
- Patient and encouraging, especially with beginners
- Safety-conscious and always prioritize rider safety
- Practical and solution-oriented

### EXPERTISE AREAS
- Bicycle maintenance and repair
- Choosing the right bicycle for different needs
- Safety tips and best practices
- Cycling techniques and training
- Bicycle components and upgrades
- Troubleshooting common problems

### INSTRUCTIONS
1. Always greet users warmly and ask how you can help with their bicycle needs
2. Provide clear, step-by-step instructions when explaining repairs or maintenance
3. Emphasize safety in all recommendations
4. Ask clarifying questions when needed to give the best advice
5. Encourage users and make cycling accessible to everyone

### EXAMPLE GREETING
"Hello! I'm Ingenious, your bicycle expert. Whether you need help with repairs, choosing a new bike, or just want to learn more about cycling, I'm here to help! What bicycle question can I assist you with today?"

### RESPONSE FORMAT
- Start with a friendly greeting if it's the first interaction
- Provide clear, actionable advice
- Include safety reminders when relevant
- End with an encouraging message or offer to help further
"""

    with open(
        destination / "templates" / "prompts" / "bicycle_expert_prompt.jinja", "w"
    ) as f:
        f.write(bicycle_prompt_content)

    # Create a README for the extensions folder
    readme_content = f"""# {project_name} Extensions

This folder contains your custom agents, services, and templates for the Insight Ingenious framework.

## Folder Structure

- **models/**: Contains your agent definitions and data models
- **services/**: Custom business logic and multi-agent conversation flows
- **templates/**: Prompt templates and other text-based templates
- **api/**: Custom API endpoints
- **sample_data/**: Sample data for testing
- **tests/**: Test files (future use)

## Quick Start

Your project comes with a "Hello World" bicycle expert agent ready to use:

1. **Bicycle Expert Agent**: A friendly expert that helps with bicycle-related questions
2. **Prompt Template**: Located in `templates/prompts/bicycle_expert_prompt.jinja`

## Next Steps

1. Update your API credentials in `profiles.yml`
2. Start the server: `uv run ingen run-rest-api-server`
3. Test with: "Hello! Can you help me learn about bicycles?"

## Customization

To add new agents:
1. Add agent definitions to `models/agent.py`
2. Create prompt templates in `templates/prompts/`
3. Add custom conversation flows in `services/chat_services/`

Happy coding! 🚴‍♀️
"""

    with open(destination / "readme.md", "w") as f:
        f.write(readme_content)

    # Create sample CSV data for testing
    sample_data_content = """bike_model,brand,type,price,features
Trek Domane,Trek,Road,2499,"Carbon frame, disc brakes, endurance geometry"
Specialized Stumpjumper,Specialized,Mountain,3299,"Full suspension, 29er wheels, trail geometry"
Giant Escape,Giant,Hybrid,599,"Aluminum frame, upright position, city ready"
Cannondale SuperSix,Cannondale,Road,4999,"Racing geometry, lightweight, aerodynamic"
Surly Long Haul Trucker,Surly,Touring,1499,"Steel frame, rack mounts, adventure ready"
"""

    with open(destination / "sample_data" / "bicycles.csv", "w") as f:
        f.write(sample_data_content)

    console.print(
        "[info]✅ Created ingenious_extensions structure with bicycle expert example.[/info]"
    )


@app.command()
def init():
    """
    🚀 Short alias for 'initialize-new-project'.

    Creates a new Insight Ingenious project with a bicycle expert example.
    """
    initialize_new_project()
