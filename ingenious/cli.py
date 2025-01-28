import shutil
from sysconfig import get_paths
import time
from typing import Optional
import typer
import asyncio
from typing_extensions import Annotated
from rich.console import Console
from rich.theme import Theme
from rich import panel
from rich import print
from pathlib import Path
import os
import uvicorn
import importlib
import pkgutil
import ingenious.config.config as ingen_config
from ingenious.utils.log_levels import LogLevel
from ingenious.utils.namespace_utils import import_class_with_fallback
import ingenious.utils.stage_executor as stage_executor_module


app = typer.Typer(no_args_is_help=True)

custom_theme = Theme({"info": "dim cyan", "warning": "dark_orange", "danger": "bold red", "error": "bold red", "debug": "khaki1"})

console = Console(theme=custom_theme)


def docs_options():
    return ["generate", "serve"]


def log_levels():
    return ["DEBUG", "INFO", "WARNING", "ERROR"]

@app.command()
def run_all(
    project_dir: Annotated[
        str,
        typer.Argument(
            help="The path to the config file. "
        ),
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
        typer.Argument(
            help="The port to run the server on. Default is 80."
        ),
    ] = 80,
    run_dir: Annotated[
        str,
        typer.Argument(
            help="The directory in which to launch the web server."
        ),
    ] = ""
):
    """
    This command will run all elements of the project. 
    """    
    if (project_dir is not None):
        os.environ["INGENIOUS_PROJECT_PATH"] = project_dir
    
    if profile_dir is None:
        # get home directory
        home_dir = os.path.expanduser("~")
        profile_dir = Path(home_dir) / Path(".ingenious") / Path("profiles.yml")
    
    print(f"Profile path: {profile_dir}")
    os.environ["INGENIOUS_PROFILE_PATH"] = str(profile_dir).replace("\\", "/")

    config = ingen_config.get_config()
    
    # We need to clean this up and probrably separate overall system config from fast api, eg. set the config here in cli and then pass it to FastAgentAPI
    # As soon as we import FastAgentAPI, config will be loaded hence to ensure that the environment variables above are loaded first we need to import FastAgentAPI after setting the environment variables
    from ingenious.main import FastAgentAPI

    os.environ["LOADENV"] = "False"
    console.print(f"Running all elements of the project in {project_dir}", style="info")
    # If the code has been pip installed then recursively copy the ingenious folder into the site-packages directory
    if CliFunctions.PureLibIncludeDirExists():
        src = Path(os.getcwd()) / Path('ingenious/')
        if os.path.exists(src):
            CliFunctions.copy_ingenious_folder(src, Path(get_paths()['purelib']) / Path(f'ingenious/'))

        src = Path(os.getcwd()) / Path('ingenious_extensions/')
        if os.path.exists(src):
            CliFunctions.copy_ingenious_folder(src, Path(get_paths()['purelib']) / Path(f'ingenious_extensions/'))
    
    print(f"Current working directory: {os.getcwd()}")    
    
    def print_namespace_modules(namespace):
        package = importlib.import_module(namespace)
        if hasattr(package, '__path__'):
            for module_info in pkgutil.iter_modules(package.__path__):
                print(f"Found module: {module_info.name}")
        else:
            print(f"{namespace} is not a package")
    os.environ["INGENIOUS_WORKING_DIR"] = str(Path(os.getcwd()))
    os.chdir(str(Path(os.getcwd())))
    print_namespace_modules('ingenious.services.chat_services.multi_agent.conversation_flows')
    print_namespace_modules('ingenious_extensions.services.chat_services.multi_agent.conversation_flows')


    fast_agent_api = FastAgentAPI(config)

    # Access the FastAPI app instance
    app = fast_agent_api.app
    
    # change directory to project dir    
    uvicorn.run(app, host=config.web_configuration.ip_address, port=config.web_configuration.port)



@app.command()
def run_test_batch(
        log_level: Annotated[
        Optional[str],
        typer.Option(
            help="The option to set the log level. This controls the verbosity of the output. Allowed values are `DEBUG`, `INFO`, `WARNING`, `ERROR`. Default is `WARNING`.",
        ),
        ] = "WARNING"
):
    """
        This command will run all the tests in the project
        """
    _log_level: LogLevel = LogLevel.from_string(log_level)    
    
    se: stage_executor_module.stage_executor = stage_executor_module.stage_executor(log_level=_log_level, console=console)
    
    asyncio.run(se.perform_stage(option=True, action_callables=[CliFunctions.RunTestBatch()], stage_name="Batch Tests"))



@app.command()
def generate_template_folders():
    """Generate 'docker', 'ingenious_extensions', and 'tmp' folders in the current working directory."""
    base_path = Path(__file__).parent
    templates_paths = {
        "docker": base_path / "docker_template",
        "ingenious_extensions": base_path / "ingenious_extensions_template",
        "tmp": None,  # No template, just create the folder
        "functional_test_outputs": None  # No template, just create the folder
    }

    for folder_name, template_path in templates_paths.items():
        destination = Path.cwd() / folder_name

        # Skip if the destination folder already exists
        if destination.exists():
            console.print(f"[warning]Folder '{folder_name}' already exists. Skipping...[/warning]")
            continue

        # Check if a template path exists (if applicable)
        if template_path and not template_path.exists():
            console.print(f"[error]Template directory '{template_path}' not found. Skipping...[/error]")
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
                        shutil.copytree(src_path, dst_path)
                    else:
                        shutil.copy2(src_path, dst_path)
            elif folder_name == "tmp":
                # Create an empty context.md file in the 'tmp' folder
                (destination / "context.md").touch()

            console.print(f"[info]Folder '{folder_name}' created successfully.[/info]")

        except Exception as e:
            console.print(f"[error]Error processing folder '{folder_name}': {e}[/error]")

    console.print("[info]Folder generation process completed.[/info]")



if __name__ == "__cli__":
    app()


class CliFunctions:
    class RunTestBatch(stage_executor_module.IActionCallable):
        async def __call__(self, progress, task_id, **kwargs):
            module_name = f"tests.run_tests"
            class_name = "RunBatches"
            try:                
                repository_class_import = import_class_with_fallback(module_name, class_name)
                repository_class = repository_class_import(progress=progress, task_id=task_id)
                await repository_class.run()

            except (ImportError, AttributeError) as e:
                raise ValueError(f"Batch Run Failed: {module_name}") from e
    
    @staticmethod
    def PureLibIncludeDirExists():
        ChkPath = Path(get_paths()['purelib']) / Path(f'ingenious/')
        return os.path.exists(ChkPath)
            
    @staticmethod
    def GetIncludeDir():
        ChkPath = Path(get_paths()['purelib']) / Path(f'ingenious/')
        # print(ChkPath)
        # Does Check for the path
        if os.path.exists(ChkPath):
            return ChkPath
        else:        
            path = Path(os.getcwd()) / Path('ingenious/')
            # print(str(path))
            return (path)
    
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
                if not os.path.exists(dst_path) or os.path.getmtime(src_path) > os.path.getmtime(dst_path):
                    shutil.copy2(src_path, dst_path)  # Copy file with metadata