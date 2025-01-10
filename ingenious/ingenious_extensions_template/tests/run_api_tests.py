import json
import jsonpickle
import asyncio
from pathlib import Path
from rich.progress import Progress, SpinnerColumn, TextColumn
from ingenious.utils.stage_executor import ProgressConsoleWrapper
from ingenious.utils.log_levels import LogLevel
import ingenious.config.config as ingen_config
import ingenious.dependencies as ingen_deps
from ingenious.files.files_repository import FileStorage
import ingenious_extensions.models.ca_raw_fixture_data as gm
from ingenious.utils.model_utils import Object_To_Yaml
from ingenious.services.chat_service import ChatService
from ingenious.models.chat import ChatRequest
import datetime
import requests


# Ensure environment variables are set
config = ingen_config.get_config()
USERNAME = ingen_deps.config.web_configuration.authentication.username
PASSWORD = ingen_deps.config.web_configuration.authentication.password

# Log level for the progress console
log_level = LogLevel.INFO

# Create the raw Progress object
raw_progress = Progress(
    SpinnerColumn(spinner_name="dots", style="progress.spinner", finished_text="📦"),
    TextColumn("[progress.description]{task.description}"),
    transient=False
)

# Wrap the Progress object with ProgressConsoleWrapper
progress = ProgressConsoleWrapper(progress=raw_progress, log_level=log_level)


async def process_json_files():
    # File storage and directory setup
    fs = FileStorage(config=config)
    directory = "example_payload/raw"

    # Get a sorted list of JSON files
    json_files = sorted([f for f in await fs.list_files(file_path=directory) if f.endswith(".json")])

    # Task for processing JSON files
    task_id = progress.add_task(description="[Initializing] Processing JSON files", total=len(json_files))

    history_files = sorted([f for f in await fs.list_files(file_path='ball_history') if f.endswith(".json")])
    for j in history_files:
        file_name = Path(j).name
        await fs.delete_file(file_name=file_name, file_path='ball_history')

    for json_file in json_files:
        file_name = Path(json_file).name
        file_contents = await fs.read_file(file_name=file_name, file_path=directory)
        message_object = '{json}'


    thread_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    user_prompt = jsonpickle.dumps(message_object, unpicklable=False)
    event_type = '_____'
    chat_request = ChatRequest(
        thread_id=thread_id,
        user_prompt=user_prompt,
        conversation_flow="____",
        event_type=event_type)

    response = requests.post(
        url="http://localhost:80/api/v1/chat_test",
        json=chat_request.model_dump(),
        auth=(USERNAME, PASSWORD)
    )


# Main execution block
if __name__ == "__main__":
    asyncio.run(process_json_files())
