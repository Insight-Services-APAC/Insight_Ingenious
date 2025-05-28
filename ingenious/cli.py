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
        str,
        typer.Argument(help="The path to the config file. "),
    ] = None,
    profile_dir: Annotated[
        str,
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
    if project_dir is not None:
        os.environ["INGENIOUS_PROJECT_PATH"] = project_dir

    if profile_dir is None:
        # get home directory
        home_dir = os.path.expanduser("~")
        profile_dir = Path(home_dir) / Path(".ingenious") / Path("profiles.yml")

    print(f"Profile path: {profile_dir}")
    os.environ["INGENIOUS_PROFILE_PATH"] = str(profile_dir).replace("\\", "/")
    import ingenious.config.config as ingen_config

    config = ingen_config.get_config()

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
    """Generate template folders for a new project using the Ingenious framework."""
    base_path = Path(__file__).parent
    templates_paths = {
        "docker": base_path / "docker_template",
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
            git_ignore_content = ["*.pyc", "__pycache__", "*.log", "/files/", "/tmp/"]
            f.write("\n".join(git_ignore_content))

    # create a config file
    template_config_path = (
        templates_paths["ingenious_extensions"] / "config.template.yml"
    )
    if template_config_path.exists():
        config_path = Path.cwd() / "config.yml"
        shutil.copy2(template_config_path, config_path)
        console.print(
            f"[info]Config file created successfully at {config_path}.[/info]"
        )
    else:
        console.print(
            f"[warning]Config file template not found at {template_config_path}. Skipping...[/warning]"
        )

    # create profile file
    template_profile_path = (
        templates_paths["ingenious_extensions"] / "profiles.template.yml"
    )
    if template_profile_path.exists():
        # Get user home directory
        home_dir = os.path.expanduser("~")
        profile_dir_path = Path(home_dir) / Path(".ingenious")
        os.makedirs(profile_dir_path, exist_ok=True)
        profile_path = profile_dir_path / Path("profiles.yml")
        shutil.copy2(template_profile_path, profile_path)
        console.print(
            f"[info]Profile file created successfully created at {profile_path}[/info]"
        )
    else:
        console.print(
            f"[warning]Profile file template not found at {template_profile_path}. Skipping...[/warning]"
        )

    console.print("[info]Folder generation process completed.[/info]")
    console.print(
        "[warning]Before executing set the environment variables INGENIOUS_PROJECT_PATH and INGENIOUS_PROFILE_PATH [/warning]"
    )
    console.print(
        "[warning]Before executing update config.yml and profiles.yml [/warning]"
    )
    console.print("[info]To execute use ingen_cli[/info]")


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
