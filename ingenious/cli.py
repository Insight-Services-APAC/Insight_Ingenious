from __future__ import annotations

import asyncio
import importlib
import os
import pkgutil
import shutil
import stat
from pathlib import Path
from sysconfig import get_paths
from typing import Optional

import typer
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
import uvicorn
from rich import print
from rich.console import Console
from rich.theme import Theme
from typing_extensions import Annotated

import ingenious.config.config as ingen_config
import ingenious.utils.stage_executor as stage_executor_module
from ingenious.utils.lazy_group import LazyGroup
from ingenious.utils.log_levels import LogLevel
from ingenious.utils.namespace_utils import import_class_with_fallback

# ────────────────────────────────────────────────────────────────────────────
# Typer application singleton
# ────────────────────────────────────────────────────────────────────────────
#: Root command group – exported via ``__all__`` so that *pipx* / entry‑points
#: can reference ``ingenious.cli:app``.
app: typer.Typer = typer.Typer(
    cls=LazyGroup,
    no_args_is_help=True,  # `ingen` → show help when no args
    pretty_exceptions_show_locals=False,  # cleaner tracebacks in production
    help="""
🚀 Insight Ingenious - GenAI Accelerator

A powerful framework for building and deploying AI agent workflows.

Quick Start:
  ingen init                    # Initialize a new project
  ingen serve                   # Start the API server
  ingen workflows               # List available workflows

Common Commands:
  init, serve, test, workflows, prompt-tuner, document-parse

Data Processing:
  dataprep, document-processing, document-parse

Get help for any command with: ingen <command> --help
    """.strip(),
)

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


@app.command(name="serve", help="Start the API server with web interface")
def serve(
    config: Annotated[
        Optional[str],
        typer.Option(
            "--config",
            "-c",
            help="Path to config.yml file (default: ./config.yml or $INGENIOUS_PROJECT_PATH)",
        ),
    ] = None,
    profile: Annotated[
        Optional[str],
        typer.Option(
            "--profile",
            "-p",
            help="Path to profiles.yml file (default: ./profiles.yml or $INGENIOUS_PROFILE_PATH)",
        ),
    ] = None,
    host: Annotated[
        str,
        typer.Option("--host", "-h", help="Host to bind the server (default: 0.0.0.0)"),
    ] = "0.0.0.0",
    port: Annotated[
        int,
        typer.Option(
            "--port", help="Port to bind the server (default: 80 or $WEB_PORT)"
        ),
    ] = int(os.getenv("WEB_PORT", "80")),
    no_prompt_tuner: Annotated[
        bool,
        typer.Option("--no-prompt-tuner", help="Disable the prompt tuner interface"),
    ] = False,
):
    """
    🚀 Start the Insight Ingenious API server with web interface.

    The server provides:
    • REST API endpoints for agent workflows
    • Chainlit chat interface at /chainlit
    • Prompt tuning interface at /prompt-tuner (unless disabled)

    AVAILABLE WORKFLOWS & CONFIGURATION REQUIREMENTS:

    ✅ Minimal Configuration (Azure OpenAI only):
      • classification-agent - Route input to specialized agents
      • bike-insights - Sample domain-specific workflow

    🔍 Requires Azure Search Services:
      • knowledge-base-agent - Search knowledge bases

    📊 Requires Database Configuration:
      • sql-manipulation-agent - Execute SQL queries

    📄 Optional Azure Document Intelligence:
      • document-processing - Extract text from PDFs/images

    QUICK TEST:
      curl -X POST http://localhost:{port}/api/v1/chat \\
        -H "Content-Type: application/json" \\
        -d '{{"user_prompt": "Hello", "conversation_flow": "classification-agent"}}'

    For detailed configuration: ingen workflows --help
    """
    return run_rest_api_server(
        project_dir=config,
        profile_dir=profile,
        host=host,
        port=port,
        run_dir="",
        enable_prompt_tuner=not no_prompt_tuner,
    )


# Keep old command for backward compatibility
@app.command(hidden=True)
def run_rest_api_server(
    project_dir: Annotated[
        str,
        typer.Argument(help="The path to the config file. "),
    ] = None,
    profile_dir: Annotated[
        str,
        typer.Argument(
            help="The path to the profile file. If left blank it will use './profiles.yml' if it exists, otherwise '$HOME/.ingenious/profiles.yml'"
        ),
    ] = None,
    host: Annotated[
        str,
        typer.Argument(
            help="The host to run the server on. Default is 0.0.0.0. For local development outside of docker use 127.0.0.1"
        ),
    ] = "0.0.0.0",
    port: Annotated[
        int,
        typer.Argument(help="The port to run the server on. Default is 80."),
    ] = 80,
    run_dir: Annotated[
        str,
        typer.Argument(help="The directory in which to launch the web server."),
    ] = "",
    enable_prompt_tuner: Annotated[
        bool,
        typer.Option(help="Enable the prompt tuner interface. Default is True."),
    ] = True,
):
    """
    Run a FastAPI server that presents your agent workflows via REST endpoints.

    AVAILABLE WORKFLOWS & CONFIGURATION REQUIREMENTS:

    ⭐ "Hello World" Workflow (Azure OpenAI only):
      • bike-insights - **RECOMMENDED STARTING POINT** - Multi-agent bike sales analysis

    ✅ Simple Text Processing (Azure OpenAI only):
      • classification_agent - Route input to specialized agents

    🔍 Requires Azure Search Services:
      • knowledge_base_agent - Search knowledge bases

    📊 Requires Database Configuration:
      • sql_manipulation_agent - Execute SQL queries

    📄 Optional Azure Document Intelligence:
      • document-processing - Extract text from PDFs/images

    For detailed configuration requirements, see:
    docs/workflows/README.md

    QUICK TEST (Hello World):
    curl -X POST http://localhost:PORT/api/v1/chat \\
      -H "Content-Type: application/json" \\
      -d '{
        "user_prompt": "{\\"stores\\": [{\\"name\\": \\"Hello Store\\", \\"location\\": \\"NSW\\", \\"bike_sales\\": [{\\"product_code\\": \\"HELLO-001\\", \\"quantity_sold\\": 1, \\"sale_date\\": \\"2023-04-01\\", \\"year\\": 2023, \\"month\\": \\"April\\", \\"customer_review\\": {\\"rating\\": 5.0, \\"comment\\": \\"Great first experience!\\"}}], \\"bike_stock\\": []}], \\"revision_id\\": \\"hello-1\\", \\"identifier\\": \\"world\\"}",
        "conversation_flow": "bike-insights"
      }'
    """
    if project_dir is not None:
        os.environ["INGENIOUS_PROJECT_PATH"] = project_dir
    elif os.getenv("INGENIOUS_PROJECT_PATH") is None:
        # Default to config.yml in current directory
        default_config_path = Path.cwd() / "config.yml"
        if default_config_path.exists():
            os.environ["INGENIOUS_PROJECT_PATH"] = str(default_config_path)
            print(f"Using default config path: {default_config_path}")

    if profile_dir is None:
        # Check if environment variable is set
        if os.getenv("INGENIOUS_PROFILE_PATH") is None:
            # Try project directory first
            project_profile_path = Path.cwd() / "profiles.yml"
            if project_profile_path.exists():
                profile_dir = project_profile_path
                print(f"Using profiles.yml from project directory: {profile_dir}")
            else:
                # Fall back to home directory
                home_dir = os.path.expanduser("~")
                profile_dir = Path(home_dir) / Path(".ingenious") / Path("profiles.yml")
                print(f"Using profiles.yml from home directory: {profile_dir}")
        else:
            profile_dir = Path(os.getenv("INGENIOUS_PROFILE_PATH"))
    else:
        profile_dir = Path(profile_dir)

    print(f"Profile path: {profile_dir}")
    os.environ["INGENIOUS_PROFILE_PATH"] = str(profile_dir).replace("\\", "/")
    import ingenious.config.config as ingen_config

    config = ingen_config.get_config()

    # Override prompt tuner setting based on CLI flag
    config.prompt_tuner.enable = enable_prompt_tuner

    # Override host and port from CLI parameters
    config.web_configuration.ip_address = host
    config.web_configuration.port = port

    # We need to clean this up and probrably separate overall system config from fast api, eg. set the config here in cli and then pass it to FastAgentAPI
    # As soon as we import FastAgentAPI, config will be loaded hence to ensure that the environment variables above are loaded first we need to import FastAgentAPI after setting the environment variables
    from ingenious.main import FastAgentAPI

    os.environ["LOADENV"] = "False"
    console.print(f"Running all elements of the project in {project_dir}", style="info")
    # If the code has been pip installed then recursively copy the ingenious folder into the site-packages directory
    if CliFunctions.PureLibIncludeDirExists():
        src = Path(os.getcwd()) / Path("ingenious/")
        if os.path.exists(src):
            CliFunctions.copy_ingenious_folder(
                src, Path(get_paths()["purelib"]) / Path("ingenious/")
            )

    print(f"Current working directory: {os.getcwd()}")

    def print_namespace_modules(namespace):
        package = importlib.import_module(namespace)
        if hasattr(package, "__path__"):
            for module_info in pkgutil.iter_modules(package.__path__):
                print(f"Found module: {module_info.name}")
        else:
            print(f"{namespace} is not a package")

    os.environ["INGENIOUS_WORKING_DIR"] = str(Path(os.getcwd()))
    os.chdir(str(Path(os.getcwd())))
    print_namespace_modules(
        "ingenious.services.chat_services.multi_agent.conversation_flows"
    )

    fast_agent_api = FastAgentAPI(config)

    # Access the FastAPI app instance
    app = fast_agent_api.app

    # change directory to project dir
    uvicorn.run(
        app,
        host=config.web_configuration.ip_address,
        port=config.web_configuration.port,
    )
    # import subprocess
    # subprocess.run(["fastapi", "dev", "./ingenious/main.py"])


@app.command(name="test", help="Run agent workflow tests")
def test(
    log_level: Annotated[
        Optional[str],
        typer.Option(
            "--log-level",
            "-l",
            help="Set logging verbosity (DEBUG, INFO, WARNING, ERROR)",
        ),
    ] = "WARNING",
    test_args: Annotated[
        Optional[str],
        typer.Option(
            "--args",
            help="Additional test arguments: '--test-name=MyTest --test-type=Unit'",
        ),
    ] = "",
):
    """
    🧪 Run all agent workflow tests in the project.

    This command executes the test suite to validate your agent configurations,
    prompts, and workflow logic.

    Examples:
      ingen test                                    # Run all tests
      ingen test --log-level DEBUG                 # Run with debug logging
      ingen test --args="--test-name=MySpecificTest" # Run specific test
    """
    return run_test_batch(log_level=log_level, run_args=test_args)


# Keep old command for backward compatibility
@app.command(hidden=True)
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


@app.command(name="init", help="Initialize a new Insight Ingenious project")
def init():
    """
    🏗️  Initialize a new Insight Ingenious project in the current directory.

    Creates a complete project structure with:
    • config.yml - Project configuration (non-sensitive settings)
    • profiles.yml - Environment profiles (API keys, secrets)
    • .env.example - Example environment variables
    • ingenious_extensions/ - Your custom agents and workflows
    • templates/prompts/quickstart-1/ - Ready-to-use bike-insights workflow templates
    • Dockerfile - Docker containerization setup
    • .dockerignore - Docker build exclusions
    • tmp/ - Temporary files and memory storage

    🎯 INCLUDES: Pre-configured quickstart-1 templates for immediate bike-insights testing!

    NEXT STEPS after running this command:
    1. Copy .env.example to .env and add your credentials
    2. Update config.yml and profiles.yml for your environment
    3. Set environment variables:
       export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml
       export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml
    4. Start the server: ingen serve

    For detailed configuration help: igen workflows --help
    """
    return initialize_new_project()


# Keep old command for backward compatibility
@app.command(hidden=True)
def initialize_new_project():
    """
    Generate template folders for a new project using the Ingenious framework.

    Creates the following structure:
    • config.yml - Project configuration (non-sensitive settings) in project directory
    • profiles.yml - Environment profiles (API keys, secrets) in project directory
    • .env.example - Example environment variables file
    • ingenious_extensions/ - Your custom agents and workflows
    • templates/prompts/quickstart-1/ - Pre-configured bike-insights workflow templates
    • Dockerfile - Docker containerization setup at project root
    • .dockerignore - Docker build exclusions at project root
    • tmp/ - Temporary files and memory

    NEXT STEPS after running this command:
    1. Copy .env.example to .env and fill in your credentials
    2. Update config.yml and profiles.yml as needed for your project
    3. Set environment variables:
       export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml
       export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml
    4. Start the server: ingen serve

    For workflow-specific configuration requirements, see:
    docs/workflows/README.md
    """
    base_path = Path(__file__).parent
    templates_paths = {
        "ingenious_extensions": base_path / "ingenious_extensions_template",
        "tmp": None,  # No template, just create the folder
    }

    for folder_name, template_path in templates_paths.items():
        destination = Path.cwd() / folder_name

        # Skip if the destination folder already exists
        if destination.exists():
            console.print(
                f"[warning]Folder '{folder_name}' already exists. Skipping...[/warning]"
            )
            continue

        # Check if a template path exists (if applicable)
        if template_path and not template_path.exists():
            console.print(
                f"[error]Template directory '{template_path}' not found. Skipping...[/error]"
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

                    # Skip Docker files when copying to ingenious_extensions - they'll be copied to project root separately
                    if folder_name == "ingenious_extensions" and item.name in [
                        "Dockerfile",
                        ".dockerignore",
                        "start.sh",
                    ]:
                        continue

                    if src_path.is_dir():
                        if "__pycache__" not in src_path.parts:
                            shutil.copytree(
                                src_path,
                                dst_path,
                                ignore=shutil.ignore_patterns("__pycache__"),
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

            console.print(f"[info]Folder '{folder_name}' created successfully.[/info]")

        except Exception as e:
            console.print(
                f"[error]Error processing folder '{folder_name}': {e}[/error]"
            )

    # create a gitignore file
    gitignore_path = Path.cwd() / ".gitignore"
    if not gitignore_path.exists():
        with open(gitignore_path, "w") as f:
            git_ignore_content = [
                "*.pyc",
                "__pycache__",
                "*.log",
                "/files/",
                "/tmp/",
                ".env",
            ]
            f.write("\n".join(git_ignore_content))

    # create a config file in project directory - prefer minimal template
    minimal_config_path = templates_paths["ingenious_extensions"] / "config.minimal.yml"
    template_config_path = (
        templates_paths["ingenious_extensions"] / "config.template.yml"
    )

    # Use minimal template if available, otherwise fall back to full template
    source_config_path = (
        minimal_config_path if minimal_config_path.exists() else template_config_path
    )

    if source_config_path.exists():
        config_path = Path.cwd() / "config.yml"
        if not config_path.exists():
            shutil.copy2(source_config_path, config_path)
            template_type = (
                "minimal" if source_config_path == minimal_config_path else "full"
            )
            console.print(
                f"[info]Config file created successfully at {config_path} using {template_type} template.[/info]"
            )
        else:
            console.print(
                f"[info]Config file already exists at {config_path}. Preserving existing configuration.[/info]"
            )
    else:
        console.print("[warning]Config file templates not found. Skipping...[/warning]")

    # create profile file in project directory - prefer minimal template
    minimal_profile_path = (
        templates_paths["ingenious_extensions"] / "profiles.minimal.yml"
    )
    template_profile_path = (
        templates_paths["ingenious_extensions"] / "profiles.template.yml"
    )

    # Use minimal template if available, otherwise fall back to full template
    source_profile_path = (
        minimal_profile_path if minimal_profile_path.exists() else template_profile_path
    )

    if source_profile_path.exists():
        profile_path = Path.cwd() / "profiles.yml"
        if not profile_path.exists():
            shutil.copy2(source_profile_path, profile_path)
            template_type = (
                "minimal" if source_profile_path == minimal_profile_path else "full"
            )
            console.print(
                f"[info]Profile file created successfully at {profile_path} using {template_type} template[/info]"
            )
        else:
            console.print(
                f"[info]Profile file already exists at {profile_path}. Preserving existing configuration.[/info]"
            )
    else:
        console.print(
            "[warning]Profile file templates not found. Skipping...[/warning]"
        )

    # create .env.example file - prefer minimal template
    minimal_env_path = templates_paths["ingenious_extensions"] / ".env.minimal"
    template_env_example_path = templates_paths["ingenious_extensions"] / ".env.example"

    # Use minimal template if available, otherwise fall back to full template
    source_env_path = (
        minimal_env_path if minimal_env_path.exists() else template_env_example_path
    )

    if source_env_path.exists():
        env_example_path = Path.cwd() / ".env.example"
        if not env_example_path.exists():
            shutil.copy2(source_env_path, env_example_path)
            template_type = "minimal" if source_env_path == minimal_env_path else "full"
            console.print(
                f"[info].env.example file created successfully at {env_example_path} using {template_type} template[/info]"
            )
        else:
            console.print(
                f"[info].env.example file already exists at {env_example_path}. Preserving existing file.[/info]"
            )
    else:
        console.print(
            "[warning].env.example templates not found. Skipping...[/warning]"
        )

    # Create Docker files at project root
    docker_file_path = templates_paths["ingenious_extensions"] / "Dockerfile"
    dockerignore_file_path = templates_paths["ingenious_extensions"] / ".dockerignore"
    start_sh_file_path = templates_paths["ingenious_extensions"] / "start.sh"

    if docker_file_path.exists():
        project_docker_path = Path.cwd() / "Dockerfile"
        if not project_docker_path.exists():
            shutil.copy2(docker_file_path, project_docker_path)
            console.print(
                f"[info]Dockerfile created successfully at {project_docker_path}[/info]"
            )
        else:
            console.print(
                f"[info]Dockerfile already exists at {project_docker_path}. Preserving existing file.[/info]"
            )
    else:
        console.print("[warning]Dockerfile template not found. Skipping...[/warning]")

    if dockerignore_file_path.exists():
        project_dockerignore_path = Path.cwd() / ".dockerignore"
        if not project_dockerignore_path.exists():
            shutil.copy2(dockerignore_file_path, project_dockerignore_path)
            console.print(
                f"[info].dockerignore created successfully at {project_dockerignore_path}[/info]"
            )
        else:
            console.print(
                f"[info].dockerignore already exists at {project_dockerignore_path}. Preserving existing file.[/info]"
            )
    else:
        console.print(
            "[warning].dockerignore template not found. Skipping...[/warning]"
        )

    if start_sh_file_path.exists():
        project_start_sh_path = Path.cwd() / "start.sh"
        if not project_start_sh_path.exists():
            shutil.copy2(start_sh_file_path, project_start_sh_path)
            # Make start.sh executable
            import stat

            project_start_sh_path.chmod(
                project_start_sh_path.stat().st_mode | stat.S_IEXEC
            )
            console.print(
                f"[info]start.sh created successfully at {project_start_sh_path}[/info]"
            )
        else:
            console.print(
                f"[info]start.sh already exists at {project_start_sh_path}. Preserving existing file.[/info]"
            )
    else:
        console.print("[warning]start.sh template not found. Skipping...[/warning]")

    # Create quickstart-1 templates folder and copy prompt templates
    console.print("\n[bold]Setting up quickstart-1 prompt templates...[/bold]")
    quickstart_templates_destination = (
        Path.cwd() / "templates" / "prompts" / "quickstart-1"
    )

    # First try to copy from existing ingenious_extensions in the project
    existing_quickstart_source = (
        Path.cwd() / "ingenious_extensions" / "templates" / "prompts" / "quickstart-1"
    )
    # Fallback to the template directory
    template_quickstart_source = (
        templates_paths["ingenious_extensions"]
        / "templates"
        / "prompts"
        / "quickstart-1"
    )

    quickstart_templates_source = None
    if existing_quickstart_source.exists():
        quickstart_templates_source = existing_quickstart_source
        console.print("[info]Found existing quickstart-1 templates in project[/info]")
    elif template_quickstart_source.exists():
        quickstart_templates_source = template_quickstart_source
        console.print("[info]Using template quickstart-1 templates[/info]")

    if quickstart_templates_source and quickstart_templates_source.exists():
        try:
            # Create the templates directory structure
            quickstart_templates_destination.mkdir(parents=True, exist_ok=True)

            # Copy all prompt template files
            templates_copied = 0
            for template_file in quickstart_templates_source.iterdir():
                if template_file.is_file() and template_file.suffix == ".jinja":
                    dst_file = quickstart_templates_destination / template_file.name
                    if not dst_file.exists():
                        shutil.copy2(template_file, dst_file)
                        console.print(f"[info]  ✓ {template_file.name}[/info]")
                        templates_copied += 1
                    else:
                        console.print(
                            f"[info]  ↺ {template_file.name} (already exists)[/info]"
                        )

            if templates_copied > 0:
                console.print(
                    f"[info]✅ {templates_copied} quickstart-1 templates created successfully at {quickstart_templates_destination}[/info]"
                )
                console.print(
                    "[info]🎯 Ready for bike-insights workflow testing![/info]"
                )
            else:
                console.print(
                    "[info]✅ Quickstart-1 templates already configured[/info]"
                )

        except Exception as e:
            console.print(f"[error]Error creating quickstart-1 templates: {e}[/error]")
    else:
        console.print(
            "[warning]Quickstart-1 template source not found. Creating templates from base prompts...[/warning]"
        )

        # Fallback: copy base templates from ingenious_extensions_template
        base_prompts_source = (
            templates_paths["ingenious_extensions"] / "templates" / "prompts"
        )
        if base_prompts_source.exists():
            try:
                quickstart_templates_destination.mkdir(parents=True, exist_ok=True)

                # Copy core template files
                template_files = [
                    "bike_lookup_agent_prompt.jinja",
                    "customer_sentiment_agent_prompt.jinja",
                    "fiscal_analysis_agent_prompt.jinja",
                    "summary_agent_prompt.jinja",
                    "summary_prompt.jinja",
                ]

                templates_copied = 0
                for template_name in template_files:
                    src_file = base_prompts_source / template_name
                    dst_file = quickstart_templates_destination / template_name

                    if src_file.exists() and not dst_file.exists():
                        shutil.copy2(src_file, dst_file)
                        console.print(f"[info]  ✓ {template_name}[/info]")
                        templates_copied += 1

                # Create a basic user_proxy_prompt.jinja if it doesn't exist
                user_proxy_file = (
                    quickstart_templates_destination / "user_proxy_prompt.jinja"
                )
                if not user_proxy_file.exists():
                    with open(user_proxy_file, "w") as f:
                        f.write(
                            "### ROLE\nYou are a user proxy agent that coordinates multi-agent conversations for bike sales analysis.\n"
                        )
                    console.print("[info]  ✓ user_proxy_prompt.jinja (created)[/info]")
                    templates_copied += 1

                if templates_copied > 0:
                    console.print(
                        f"[info]✅ {templates_copied} quickstart-1 templates created from base templates[/info]"
                    )
                    console.print(
                        "[info]🎯 Ready for bike-insights workflow testing![/info]"
                    )

            except Exception as e:
                console.print(
                    f"[error]Error creating quickstart-1 templates from base: {e}[/error]"
                )

    console.print("[info]✅ Project initialization completed![/info]")
    console.print("[warning]⚠️  Next steps:[/warning]")
    console.print("1. Copy .env.example to .env and fill in your credentials")
    console.print("2. Set environment variables:")
    console.print("[info]   export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml[/info]")
    console.print("[info]   export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml[/info]")
    console.print("3. Start the server:")
    console.print("[info]   ingen serve[/info]")
    console.print("\n[bold yellow]💡 Tips:[/bold yellow]")
    console.print("• Check configuration: ingen status")
    console.print("• List workflows: ingen workflows")
    console.print("• Get help: ingen --help")
    console.print("\n[bold green]🎯 Ready for bike-insights workflow![/bold green]")
    console.print("• Quickstart-1 templates are pre-configured")
    console.print(
        "• Test immediately with: curl -X POST http://localhost:80/api/v1/chat ..."
    )


@app.command(name="workflows", help="Show available workflows and their requirements")
def workflows(
    workflow: Annotated[
        str,
        typer.Argument(help="Specific workflow to check, or 'all' to list everything"),
    ] = "all",
):
    """
    📋 Display available conversation workflows and their configuration requirements.

    Use this command to understand what external services and configuration
    are needed for each workflow before attempting to use them.

    Examples:
      ingen workflows                      # List all available workflows
      ingen workflows classification-agent # Show specific workflow details
      ingen workflows knowledge-base-agent # Show requirements for KB agent
    """
    return workflow_requirements(workflow=workflow)


# Keep old command for backward compatibility
@app.command(hidden=True)
def workflow_requirements(
    workflow: Annotated[
        str,
        typer.Argument(
            help="Workflow name to check requirements for, or 'all' to list all workflows"
        ),
    ] = "all",
):
    """
    Show configuration requirements for conversation workflows.

    Use this command to understand what external services and configuration
    are needed for each workflow before attempting to use them.
    """
    workflows = {
        "classification-agent": {
            "description": "Simple text classification and routing (easier alternative to bike-insights)",
            "category": "✅ Simple Text Processing",
            "requirements": ["Azure OpenAI"],
            "config_needed": [
                "config.yml: models, chat_service",
                "profiles.yml: models with api_key and base_url",
            ],
            "optional": [],
            "example_curl": """curl -X POST http://localhost:80/api/v1/chat \\
  -H "Content-Type: application/json" \\
  -d '{
    "user_prompt": "Analyze this customer feedback: Great product!",
    "conversation_flow": "classification_agent"
  }'""",
            "note": "Simple text classification - try this if bike-insights seems too complex",
        },
        "bike-insights": {
            "description": "⭐ **HELLO WORLD WORKFLOW** - Multi-agent bike sales analysis (RECOMMENDED START HERE!)",
            "category": "⭐ Hello World Workflow",
            "requirements": ["Azure OpenAI"],
            "config_needed": [
                "config.yml: models, chat_service",
                "profiles.yml: models with api_key and base_url",
            ],
            "optional": [],
            "example_curl": """curl -X POST http://localhost:80/api/v1/chat \\
  -H "Content-Type: application/json" \\
  -d '{
    "user_prompt": "{\\"stores\\": [{\\"name\\": \\"Hello Store\\", \\"location\\": \\"NSW\\", \\"bike_sales\\": [{\\"product_code\\": \\"HELLO-001\\", \\"quantity_sold\\": 1, \\"sale_date\\": \\"2023-04-01\\", \\"year\\": 2023, \\"month\\": \\"April\\", \\"customer_review\\": {\\"rating\\": 5.0, \\"comment\\": \\"Perfect introduction to Ingenious!\\"}}], \\"bike_stock\\": []}], \\"revision_id\\": \\"hello-1\\", \\"identifier\\": \\"world\\"}",
    "conversation_flow": "bike-insights"
  }'""",
            "note": "🌟 This is the recommended first workflow - showcases multi-agent coordination!",
        },
        "knowledge-base-agent": {
            "description": "Search and retrieve information from knowledge bases",
            "category": "🔍 Requires Azure Search",
            "requirements": ["Azure OpenAI", "Azure Cognitive Search"],
            "config_needed": [
                "config.yml: azure_search_services with endpoint",
                "profiles.yml: azure_search_services with API key",
                "Pre-configured search indexes",
            ],
            "optional": [],
        },
        "sql-manipulation-agent": {
            "description": "Execute SQL queries based on natural language",
            "category": "📊 Requires Database",
            "requirements": ["Azure OpenAI", "Database (Azure SQL or SQLite)"],
            "config_needed": [
                "For Azure SQL: profiles.yml: azure_sql_services with connection_string",
                "For Local: config.yml: local_sql_db with database_path and CSV",
                "config.yml: azure_sql_services with database_name/table_name",
            ],
            "optional": [],
        },
        # Legacy names for backward compatibility
        "classification_agent": {
            "description": "✅ Simple text processing - Use 'classification-agent' or 'classification_agent' (both work!)",
            "category": "✅ Simple Text Processing",
            "requirements": ["Azure OpenAI"],
            "config_needed": [
                "config.yml: models, chat_service",
                "profiles.yml: models with api_key and base_url",
            ],
            "optional": [],
            "example_curl": """curl -X POST http://localhost:80/api/v1/chat \\
  -H "Content-Type: application/json" \\
  -d '{"user_prompt": "Hello, can you help me?", "conversation_flow": "classification_agent"}'""",
            "note": "Simple alternative if bike-insights seems too complex",
        },
        "bike_insights": {
            "description": "⭐ **HELLO WORLD WORKFLOW** - Use 'bike-insights' or 'bike_insights' (both work!)",
            "category": "⭐ Hello World Workflow",
            "requirements": ["Azure OpenAI"],
            "config_needed": [
                "config.yml: models, chat_service",
                "profiles.yml: models with api_key and base_url",
            ],
            "optional": [],
            "example_curl": """curl -X POST http://localhost:80/api/v1/chat \\
  -H "Content-Type: application/json" \\
  -d '{
    "user_prompt": "{\\"stores\\": [{\\"name\\": \\"Hello Store\\", \\"location\\": \\"NSW\\", \\"bike_sales\\": [{\\"product_code\\": \\"HELLO-001\\", \\"quantity_sold\\": 1, \\"sale_date\\": \\"2023-04-01\\", \\"year\\": 2023, \\"month\\": \\"April\\", \\"customer_review\\": {\\"rating\\": 5.0, \\"comment\\": \\"Perfect introduction!\\"}}], \\"bike_stock\\": []}], \\"revision_id\\": \\"hello-1\\", \\"identifier\\": \\"world\\"}",
    "conversation_flow": "bike-insights"
  }'""",
            "note": "🌟 This is the Hello World workflow - try it first!",
        },
        "knowledge_base_agent": {
            "description": "⚠️  DEPRECATED: Use 'knowledge-base-agent' instead",
            "category": "🔍 Requires Azure Search",
            "requirements": ["Azure OpenAI", "Azure Cognitive Search"],
            "config_needed": ["See 'knowledge-base-agent' for details"],
            "optional": [],
        },
        "sql_manipulation_agent": {
            "description": "⚠️  DEPRECATED: Use 'sql-manipulation-agent' instead",
            "category": "📊 Requires Database",
            "requirements": ["Azure OpenAI", "Database (Azure SQL or SQLite)"],
            "config_needed": ["See 'sql-manipulation-agent' for details"],
            "optional": [],
        },
    }

    if workflow == "all":
        console.print(
            "\n[bold blue]📋 INSIGHT INGENIOUS WORKFLOW REQUIREMENTS[/bold blue]\n"
        )

        # Group by category, prioritizing new hyphenated names
        categories = {}
        for name, info in workflows.items():
            # Skip deprecated workflow names in the main listing
            if "DEPRECATED" in info["description"]:
                continue

            cat = info["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append((name, info))

        for category, workflow_list in categories.items():
            console.print(f"[bold]{category}[/bold]")
            for name, info in workflow_list:
                console.print(f"  • [cyan]{name}[/cyan]: {info['description']}")
            console.print()

        console.print(
            '[bold yellow]💡 TIP:[/bold yellow] Start with bike-insights (the "Hello World" of Ingenious)'
        )
        console.print(
            "[bold yellow]📖 DOCS:[/bold yellow] See docs/workflows/README.md for complete configuration guide"
        )
        console.print(
            "[bold yellow]🧪 TEST:[/bold yellow] Try 'ingen workflows bike-insights' for a working example"
        )

    elif workflow in workflows:
        info = workflows[workflow]
        console.print(f"\n[bold blue]📋 {workflow.upper()} REQUIREMENTS[/bold blue]\n")
        console.print(f"[bold]Description:[/bold] {info['description']}")
        console.print(f"[bold]Category:[/bold] {info['category']}")
        console.print("[bold]External Services Needed:[/bold]")
        for req in info["requirements"]:
            console.print(f"  • {req}")
        console.print("\n[bold]Configuration Required:[/bold]")
        for config in info["config_needed"]:
            console.print(f"  • {config}")
        if info["optional"]:
            console.print("\n[bold]Optional:[/bold]")
            for opt in info["optional"]:
                console.print(f"  • {opt}")

        # Show special note if available
        if "note" in info:
            console.print(f"\n[bold yellow]⚠️  Note:[/bold yellow] {info['note']}")

        console.print("\n[bold yellow]🧪 TEST COMMAND:[/bold yellow]")
        if "example_curl" in info:
            console.print(info["example_curl"])
        else:
            console.print("curl -X POST http://localhost:80/api/v1/chat \\")
            console.print('  -H "Content-Type: application/json" \\')
            console.print(
                f'  -d \'{{"user_prompt": "Hello", "conversation_flow": "{workflow}"}}\''
            )

    else:
        console.print(f"[bold red]❌ Unknown workflow: {workflow}[/bold red]")
        console.print("\n[bold]Available workflows:[/bold]")
        # Show only the current (non-deprecated) workflow names
        for name, info in workflows.items():
            if "DEPRECATED" not in info["description"]:
                console.print(f"  • {name}")
        console.print("\nUse 'ingen workflows' to see all workflows with descriptions")


@app.command(name="help", help="Show detailed help and getting started guide")
def help_command(
    topic: Annotated[
        Optional[str],
        typer.Argument(help="Specific topic: setup, workflows, config, deployment"),
    ] = None,
):
    """
    📚 Show comprehensive help for getting started with Insight Ingenious.

    Topics available:
    • setup - Initial project setup steps
    • workflows - Understanding and configuring workflows
    • config - Configuration file details
    • deployment - Deployment options and best practices
    """
    if topic is None:
        console.print(
            "[bold blue]🚀 Insight Ingenious - Quick Start Guide[/bold blue]\n"
        )

        console.print("[bold]1. Initialize a new project:[/bold]")
        console.print("   ingen init")
        console.print("")

        console.print("[bold]2. Configure your project:[/bold]")
        console.print("   • Copy .env.example to .env and add your API keys")
        console.print("   • Update config.yml and profiles.yml as needed")
        console.print("")

        console.print("[bold]3. Set environment variables:[/bold]")
        console.print("   export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml")
        console.print("   export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml")
        console.print("")

        console.print("[bold]4. Start the server:[/bold]")
        console.print("   ingen serve")
        console.print("")

        console.print("[bold]5. Access the interfaces:[/bold]")
        console.print("   • API: http://localhost:80")
        console.print("   • Chat: http://localhost:80/chainlit")
        console.print("   • Prompt Tuner: http://localhost:80/prompt-tuner")
        console.print("")

        console.print("[bold yellow]💡 Helpful Commands:[/bold yellow]")
        console.print("   ingen status      # Check configuration")
        console.print("   ingen workflows   # List available workflows")
        console.print("   ingen test        # Run tests")
        console.print("   ingen help <topic> # Get detailed help on specific topics")
        console.print("")

        console.print("[bold yellow]📖 Documentation:[/bold yellow]")
        console.print("   GitHub: https://github.com/Insight-Services-APAC/ingenious")

    elif topic == "setup":
        console.print("[bold blue]🛠️  Project Setup Guide[/bold blue]\n")
        console.print("To set up your Insight Ingenious project:")
        console.print("1. Run `ingen init` to generate project files")
        console.print("2. Configure API keys and settings in `.env`")
        console.print("3. Update `config.yml` and `profiles.yml` as needed")
        console.print("4. Set environment variables:")
        console.print("   export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml")
        console.print("   export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml")
        console.print("5. Start the server with `ingen serve`")

    elif topic == "workflows":
        console.print("[bold blue]🔄 Workflows Guide[/bold blue]\n")
        console.print(
            "Workflows are the core of Insight Ingenious. They define how agents"
        )
        console.print("process and respond to user inputs.\n")
        console.print(
            "Use 'ingen workflows' to see all available workflows and their requirements."
        )

    elif topic == "config":
        console.print("[bold blue]⚙️  Configuration Guide[/bold blue]\n")
        console.print("Configuration is split between two files:")
        console.print("• config.yml - Non-sensitive project settings")
        console.print("• profiles.yml - API keys and sensitive configuration")

    elif topic == "deployment":
        console.print("[bold blue]🚀 Deployment Guide[/bold blue]\n")
        console.print("Insight Ingenious can be deployed in several ways:")
        console.print("• Local development: ingen serve")
        console.print("• Docker: Use provided Docker templates")
        console.print("• Cloud: Deploy to Azure, AWS, or other cloud providers")

    else:
        console.print(f"[red]❌ Unknown help topic: {topic}[/red]")
        console.print("\nAvailable topics: setup, workflows, config, deployment")
        console.print("Use 'ingen help' for general help.")


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

                await repository_class.run()

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


@app.command(name="prompt-tuner", help="Start standalone prompt tuning interface")
def prompt_tuner(
    port: Annotated[
        int,
        typer.Option("--port", "-p", help="Port for the prompt tuner (default: 5000)"),
    ] = 5000,
    host: Annotated[
        str,
        typer.Option(
            "--host", "-h", help="Host to bind the prompt tuner (default: 127.0.0.1)"
        ),
    ] = "127.0.0.1",
):
    """
    🎯 Start the standalone prompt tuning web interface.

    The prompt tuner allows you to:
    • Edit and test agent prompts
    • Run batch tests with sample data
    • Compare different prompt versions
    • Download test results

    Access the interface at: http://{host}:{port}

    Note: This starts only the prompt tuner, not the full API server.
    For the complete server with all interfaces, use: ingen serve
    """
    console.print(f"🎯 Starting prompt tuner at http://{host}:{port}")
    console.print(
        "💡 Tip: Use 'ingen serve' to start the full server with all interfaces"
    )

    # Import and start the Flask app for prompt tuning
    try:
        from ingenious_prompt_tuner.run_flask_app import app as flask_app

        flask_app.run(host=host, port=port, debug=True)
    except ImportError:
        console.print("[red]❌ Prompt tuner dependencies not available[/red]")
        console.print("Install with: uv add flask")
        raise typer.Exit(1)


@app.command(name="status", help="Check system status and configuration")
def status():
    """
    🔍 Check the status of your Insight Ingenious configuration.

    Validates:
    • Configuration files existence and validity
    • Environment variables
    • Required dependencies
    • Available workflows
    """
    console.print("[bold blue]🔍 Insight Ingenious System Status[/bold blue]\n")

    # Check environment variables
    console.print("[bold]Environment Variables:[/bold]")
    project_path = os.getenv("INGENIOUS_PROJECT_PATH")
    profile_path = os.getenv("INGENIOUS_PROFILE_PATH")

    if project_path:
        console.print(f"  ✅ INGENIOUS_PROJECT_PATH: {project_path}")
        if not Path(project_path).exists():
            console.print("  ⚠️  [yellow]Config file not found at path[/yellow]")
    else:
        console.print("  ❌ INGENIOUS_PROJECT_PATH not set")

    if profile_path:
        console.print(f"  ✅ INGENIOUS_PROFILE_PATH: {profile_path}")
        if not Path(profile_path).exists():
            console.print("  ⚠️  [yellow]Profile file not found at path[/yellow]")
    else:
        console.print("  ❌ INGENIOUS_PROFILE_PATH not set")

    # Check local files
    console.print("\n[bold]Local Files:[/bold]")
    local_config = Path.cwd() / "config.yml"
    local_profile = Path.cwd() / "profiles.yml"
    local_env = Path.cwd() / ".env"

    console.print(f"  {'✅' if local_config.exists() else '❌'} config.yml")
    console.print(f"  {'✅' if local_profile.exists() else '❌'} profiles.yml")
    console.print(f"  {'✅' if local_env.exists() else '❌'} .env")

    # Quick setup guidance
    if not project_path or not profile_path:
        console.print("\n[bold yellow]💡 Quick Setup:[/bold yellow]")
        console.print("  export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml")
        console.print("  export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml")

    if not local_config.exists():
        console.print("\n[bold yellow]💡 Initialize project:[/bold yellow] ingen init")


@app.command(name="version", help="Show version information")
def version():
    """
    📦 Display version information for Insight Ingenious.
    """
    try:
        # Try to get version from package metadata
        from importlib.metadata import version as get_version

        version_str = get_version("insight-ingenious")
        console.print(
            f"[bold blue]Insight Ingenious[/bold blue] version [bold]{version_str}[/bold]"
        )
    except Exception:
        console.print("[bold blue]Insight Ingenious[/bold blue] - Development Version")

    console.print("🚀 GenAI Accelerator Framework")
    console.print(
        "📖 Documentation: https://github.com/Insight-Services-APAC/ingenious"
    )


@app.command(name="validate", help="Validate system configuration and requirements")
def validate():
    """
    ✅ Comprehensive validation of your Insight Ingenious setup.

    Performs deep validation of:
    • Configuration file syntax and required fields
    • Profile file syntax and credentials
    • Azure OpenAI connectivity
    • Workflow requirements
    • Dependencies

    This command helps identify issues before starting the server.
    """
    console.print(
        "[bold blue]✅ Insight Ingenious Configuration Validation[/bold blue]\n"
    )

    validation_passed = True

    # 1. Check environment variables
    console.print("[bold]1. Environment Variables:[/bold]")
    project_path = os.getenv("INGENIOUS_PROJECT_PATH")
    profile_path = os.getenv("INGENIOUS_PROFILE_PATH")

    if not project_path:
        console.print("  ❌ INGENIOUS_PROJECT_PATH not set")
        console.print(
            "     [dim]Fix: export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml[/dim]"
        )
        validation_passed = False
    elif not Path(project_path).exists():
        console.print(f"  ❌ Config file not found: {project_path}")
        console.print("     [dim]Fix: Run 'ingen init' to create config.yml[/dim]")
        validation_passed = False
    else:
        console.print(f"  ✅ INGENIOUS_PROJECT_PATH: {project_path}")

    if not profile_path:
        console.print("  ❌ INGENIOUS_PROFILE_PATH not set")
        console.print(
            "     [dim]Fix: export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml[/dim]"
        )
        validation_passed = False
    elif not Path(profile_path).exists():
        console.print(f"  ❌ Profile file not found: {profile_path}")
        console.print("     [dim]Fix: Run 'ingen init' to create profiles.yml[/dim]")
        validation_passed = False
    else:
        console.print(f"  ✅ INGENIOUS_PROFILE_PATH: {profile_path}")

    # 2. Validate configuration files
    console.print("\n[bold]2. Configuration File Validation:[/bold]")
    try:
        if project_path and Path(project_path).exists():
            import ingenious.config.config as ingen_config

            _ = ingen_config.get_config()
            console.print("  ✅ config.yml syntax and validation passed")
        else:
            console.print("  ❌ Cannot validate config.yml - file not found")
            validation_passed = False
    except Exception as e:
        console.print(f"  ❌ config.yml validation failed: {str(e)}")
        console.print("     [dim]Common fixes:[/dim]")
        console.print("     [dim]• Check YAML syntax (indentation, quotes)[/dim]")
        console.print(
            "     [dim]• Ensure required sections exist (models, profile)[/dim]"
        )
        console.print(
            "     [dim]• Comment out optional services if not using them[/dim]"
        )
        validation_passed = False

    try:
        if profile_path and Path(profile_path).exists():
            import ingenious.dependencies as igen_deps

            _ = igen_deps.get_profile()
            console.print("  ✅ profiles.yml syntax and validation passed")
        else:
            console.print("  ❌ Cannot validate profiles.yml - file not found")
            validation_passed = False
    except Exception as e:
        console.print(f"  ❌ profiles.yml validation failed: {str(e)}")
        console.print("     [dim]Common fixes:[/dim]")
        console.print("     [dim]• Set AZURE_OPENAI_API_KEY in .env file[/dim]")
        console.print("     [dim]• Set AZURE_OPENAI_BASE_URL in .env file[/dim]")
        console.print("     [dim]• Check YAML syntax and structure[/dim]")
        console.print(
            "     [dim]• Comment out optional services if not configured[/dim]"
        )
        validation_passed = False

    # 3. Check Azure OpenAI connectivity
    console.print("\n[bold]3. Azure OpenAI Connectivity:[/bold]")
    azure_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_BASE_URL")

    if not azure_key:
        console.print("  ❌ AZURE_OPENAI_API_KEY not set in environment")
        console.print(
            "     [dim]Fix: Add AZURE_OPENAI_API_KEY=your-key to .env file[/dim]"
        )
        validation_passed = False
    else:
        console.print("  ✅ AZURE_OPENAI_API_KEY found")

    if not azure_endpoint:
        console.print("  ❌ AZURE_OPENAI_BASE_URL not set in environment")
        console.print(
            "     [dim]Fix: Add AZURE_OPENAI_BASE_URL=https://your-resource.openai.azure.com/ to .env[/dim]"
        )
        validation_passed = False
    else:
        console.print("  ✅ AZURE_OPENAI_BASE_URL found")

    # 4. Check workflow availability
    console.print("\n[bold]4. Workflow Availability:[/bold]")
    try:
        # Check if bike-insights workflow files exist
        extensions_path = Path.cwd() / "ingenious_extensions"
        if extensions_path.exists():
            console.print("  ✅ ingenious_extensions directory found")

            # Check for key workflow files
            services_path = extensions_path / "services"
            if services_path.exists():
                console.print("  ✅ Services directory found")
            else:
                console.print("  ⚠️  Services directory not found")
        else:
            console.print(
                "  ❌ ingenious_extensions directory not found - run 'ingen init'"
            )
            validation_passed = False
    except Exception as e:
        console.print(f"  ❌ Workflow validation failed: {str(e)}")
        validation_passed = False

    # 5. Summary and recommendations
    console.print(
        f"\n[bold]{'✅ Validation Summary' if validation_passed else '❌ Validation Summary'}:[/bold]"
    )

    if validation_passed:
        console.print(
            "  🎉 [green]All validations passed! Your Ingenious setup is ready.[/green]"
        )
        console.print("  🚀 You can now run: [bold]ingen serve[/bold]")
    else:
        console.print(
            "  ⚠️  [yellow]Some validations failed. Please fix the issues above.[/yellow]"
        )
        console.print("\n[bold]🔧 Quick Fix Commands:[/bold]")
        console.print("  • Missing files: [bold]ingen init[/bold]")
        console.print("  • Set environment variables:")
        console.print(
            "    [bold]export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml[/bold]"
        )
        console.print(
            "    [bold]export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml[/bold]"
        )
        console.print("  • Create .env file with Azure OpenAI credentials:")
        console.print("    [bold]echo 'AZURE_OPENAI_API_KEY=your-key' > .env[/bold]")
        console.print(
            "    [bold]echo 'AZURE_OPENAI_BASE_URL=https://your-resource.openai.azure.com/' >> .env[/bold]"
        )
        console.print(
            "  • Set environment: [bold]export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml[/bold]"
        )
        console.print("  • Edit credentials: [bold]nano .env[/bold]")

    if not validation_passed:
        raise typer.Exit(1)


@app.command(name="document-parse", help="Parse documents and extract structured data")
def document_parse(
    files: Annotated[
        list[str],
        typer.Argument(help="One or more document files to parse")
    ],
    output: Annotated[
        Optional[str],
        typer.Option(
            "--output", "-o",
            help="Output file path (for single file)"
        )
    ] = None,
    output_dir: Annotated[
        Optional[str],
        typer.Option(
            "--output-dir",
            help="Output directory for multiple files"
        )
    ] = None,
    pretty: Annotated[
        bool,
        typer.Option(
            "--pretty",
            help="Pretty print JSON output"
        )
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose", "-v",
            help="Enable verbose logging"
        )
    ] = False,
    template: Annotated[
        Optional[str],
        typer.Option(
            "--template", "-t",
            help="Template string to render"
        )
    ] = None,
    template_file: Annotated[
        Optional[str],
        typer.Option(
            "--template-file",
            help="Template file to use"
        )
    ] = None,
    template_example: Annotated[
        Optional[str],
        typer.Option(
            "--template-example",
            help="Use a predefined template example: summary, detailed_report, json_summary"
        )
    ] = None,
):
    """
    📄 Parse documents and extract structured data.
    
    Supports PDF and DOCX files. Can output raw JSON or render with templates.
    
    Examples:
      ingen document-parse document.pdf --output result.json
      ingen document-parse *.pdf *.docx --output-dir results/
      ingen document-parse document.pdf --template-example summary
      ingen document-parse document.pdf --template "{{ document.filename }}: {{ total_pages }} pages"
    """
    try:
        from ingenious.document_parser.core.parser import DocumentParser
        from ingenious.document_parser.utils.exceptions import DocumentParsingError
        from ingenious.document_parser.utils.logging import setup_logger
        from ingenious.document_parser.utils.templates import TEMPLATE_EXAMPLES
        
        # Setup logging
        log_level = 10 if verbose else 20  # DEBUG if verbose, INFO otherwise
        setup_logger(level=log_level)
        
        # Validate arguments
        if len(files) > 1 and output:
            typer.secho(
                "Error: Cannot use --output with multiple files. Use --output-dir instead.",
                fg="red", err=True
            )
            raise typer.Exit(1)
        
        # Check if file exists
        for file_path in files:
            if not Path(file_path).exists():
                typer.secho(f"Error: File not found: {file_path}", fg="red", err=True)
                raise typer.Exit(1)
        
        parser = DocumentParser()
        
        # Process files
        for file_path in files:
            try:
                typer.echo(f"Processing: {file_path}")
                
                # Check if file type is supported
                if not parser.supports_file(file_path):
                    typer.secho(f"Warning: Unsupported file type: {file_path}", fg="yellow", err=True)
                    continue
                
                # Parse the file
                result = parser.parse_file(file_path)
                
                # Handle template rendering if specified
                if template or template_file or template_example:
                    if template:
                        rendered = parser.render_template(template, result)
                    elif template_example:
                        if template_example not in TEMPLATE_EXAMPLES:
                            typer.secho(f"Error: Template example '{template_example}' not found", fg="red", err=True)
                            continue
                        template_string = TEMPLATE_EXAMPLES[template_example]
                        rendered = parser.render_template(template_string, result)
                    elif template_file:
                        if not Path(template_file).exists():
                            typer.secho(f"Error: Template file not found: {template_file}", fg="red", err=True)
                            continue
                        rendered = parser.render_template_file(Path(template_file).name, result)
                    
                    # Output rendered result
                    if output:
                        with open(output, "w", encoding="utf-8") as f:
                            f.write(rendered)
                        typer.echo(f"Rendered output saved to: {output}")
                    elif output_dir:
                        Path(output_dir).mkdir(parents=True, exist_ok=True)
                        base_name = Path(file_path).stem
                        output_path = Path(output_dir) / f"{base_name}.txt"
                        with open(output_path, "w", encoding="utf-8") as f:
                            f.write(rendered)
                        typer.echo(f"Rendered output saved to: {output_path}")
                    else:
                        typer.echo(rendered)
                else:
                    # Output JSON
                    if output:
                        result.save_to_file(output, pretty=pretty)
                        typer.echo(f"Saved: {output}")
                    elif output_dir:
                        Path(output_dir).mkdir(parents=True, exist_ok=True)
                        base_name = Path(file_path).stem
                        output_path = Path(output_dir) / f"{base_name}.json"
                        result.save_to_file(str(output_path), pretty=pretty)
                        typer.echo(f"Saved: {output_path}")
                    else:
                        typer.echo(result.to_json(pretty=pretty))
                
            except DocumentParsingError as e:
                typer.secho(f"Error parsing {file_path}: {str(e)}", fg="red", err=True)
                continue
            except Exception as e:
                typer.secho(f"Unexpected error processing {file_path}: {str(e)}", fg="red", err=True)
                continue
                
    except ImportError:
        typer.secho("Error: Document parser dependencies not available", fg="red", err=True)
        typer.secho("Install with: uv add python-docx PyPDF2 jinja2", fg="yellow")
        raise typer.Exit(1)
    except Exception as e:
        typer.secho(f"Fatal error: {str(e)}", fg="red", err=True)
        raise typer.Exit(1)


@app.command(name="document-info", help="Show document parser information")
def document_info():
    """
    📄 Show information about supported document types and template examples.
    """
    try:
        from ingenious.document_parser.core.parser import DocumentParser
        from ingenious.document_parser.utils.templates import TEMPLATE_EXAMPLES
        
        parser = DocumentParser()
        extensions = parser.get_supported_extensions()
        
        console.print("[bold blue]Document Parser Information[/bold blue]")
        console.print("=" * 30)
        console.print(f"[bold]Supported file types:[/bold] {', '.join(extensions)}")
        
        console.print("\n[bold]Example usage:[/bold]")
        console.print("  [cyan]ingen document-parse document.pdf --output result.json[/cyan]")
        console.print("  [cyan]ingen document-parse *.pdf *.docx --output-dir results/[/cyan]")
        console.print("  [cyan]ingen document-parse document.pdf --template-example summary[/cyan]")
        
        console.print("\n[bold]Available Template Examples:[/bold]")
        for name, template in TEMPLATE_EXAMPLES.items():
            console.print(f"  • [cyan]{name}[/cyan]: {template.split('\\n')[0][:50]}...")
            
        console.print("\n[bold]Template Variables Available:[/bold]")
        console.print("  • document: Document metadata (filename, file_type, total_pages, etc.)")
        console.print("  • pages: List of page objects with content and metadata")
        console.print("  • total_pages, total_words, total_chars: Summary statistics")
        console.print("  • all_text, all_paragraphs, all_headings: Aggregated content")
        
    except ImportError:
        console.print("[red]Error: Document parser dependencies not available[/red]")
        console.print("[yellow]Install with: uv add python-docx PyPDF2 jinja2[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)
