import os
from pathlib import Path
from sysconfig import get_paths
from typing import Optional

import typer
import uvicorn
from rich import print
from rich.console import Console
from rich.theme import Theme
from typing_extensions import Annotated

import ingenious.common.utils.namespace_utils as namespace_utils

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
def run(
    project_dir: Annotated[
        Optional[str],
        typer.Argument(help="The path to the config file. "),
    ] = None,
    profile_dir: Annotated[
        Optional[str],
        typer.Argument(
            help="The path to the profile file. If left blank it will use '$HOME/.ingenious/profiles.yml'"
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
):
    """
    This command will run a fastapi server and present your agent workflows via a rest endpoint.
    """
    # Set environment variables
    if project_dir is not None:
        os.environ["INGENIOUS_PROJECT_PATH"] = project_dir

    if profile_dir is None:
        # get home directory
        home_dir = os.path.expanduser("~")
        profile_path = Path(home_dir) / Path(".ingenious") / Path("profiles.yml")
        profile_dir = str(profile_path)

    console.print(f"Profile path: {profile_dir}", style="info")
    os.environ["INGENIOUS_PROFILE_PATH"] = str(profile_dir).replace("\\", "/")

    # Import configuration
    import ingenious.common.config.config as ingen_config

    config = ingen_config.get_config()

    # Import FastAgentAPI after setting environment variables
    from ingenious.main import FastAgentAPI

    os.environ["LOADENV"] = "False"
    console.print(f"Running all elements of the project in {project_dir}", style="info")

    # Handle project setup
    from ingenious.common.utils.cli_command_executor import ProjectSetupExecutor

    setup_executor = ProjectSetupExecutor(console=console)

    # If the code has been pip installed then recursively copy the ingenious folder into the site-packages directory
    if setup_executor.pure_lib_include_dir_exists():
        src = Path(os.getcwd()) / Path("ingenious/")
        if os.path.exists(src):
            setup_executor.copy_ingenious_folder(
                src, Path(get_paths()["purelib"]) / Path("ingenious/")
            )

    print(f"Current working directory: {os.getcwd()}")

    os.environ["INGENIOUS_WORKING_DIR"] = str(Path(os.getcwd()))
    os.chdir(str(Path(os.getcwd())))
    namespace_utils.print_namespace_modules(
        "ingenious.services.chat_services.multi_agent.conversation_flows"
    )

    # Initialize the FastAPI application
    fast_agent_api = FastAgentAPI(config)

    # Access the FastAPI app instance
    app = fast_agent_api.app

    # Run the server
    uvicorn.run(
        app,
        host=host,
        port=port,
    )


@app.command()
def init():
    """Generate template folders for a new project using the Ingenious framework."""
    from ingenious.common.utils.cli_command_executor import ProjectSetupExecutor

    # Create a project setup executor
    executor = ProjectSetupExecutor(console=console)

    # Initialize a new project
    executor.initialize_new_project()


@app.command()
def run_prompt_tuner():
    """Run the prompt tuner web application."""
    from ingenious_prompt_tuner import create_app as prompt_tuner

    app = prompt_tuner()
    app.run(debug=True, host="0.0.0.0", port=80)


if __name__ == "__cli__":
    app()
