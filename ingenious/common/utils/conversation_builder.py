import logging
from pathlib import Path

from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from ingenious.common.config.config import Config
from ingenious.infrastructure.storage.files_repository import FileStorage

logger = logging.getLogger(__name__)


def build_system_prompt(
    system_prompt: str, user_name: str | None = None
) -> ChatCompletionSystemMessageParam:
    system_prompt_message: ChatCompletionSystemMessageParam = {
        "role": "system",
        "content": system_prompt,
    }
    if user_name:
        system_prompt_message["name"] = user_name
    return system_prompt_message


def build_user_message(
    user_prompt: str, user_name: str | None
) -> ChatCompletionUserMessageParam:
    user_message: ChatCompletionUserMessageParam = {
        "role": "user",
        "content": user_prompt,
    }
    if user_name:
        user_message["name"] = user_name
    return user_message


def build_assistant_message(
    content: str | None, tool_calls: list[dict[str, object]] | None = None
) -> ChatCompletionAssistantMessageParam:
    assistant_message: ChatCompletionAssistantMessageParam = {"role": "assistant"}

    if content is not None:
        assistant_message["content"] = content

    if tool_calls:
        assistant_message["tool_calls"] = tool_calls  # type: ignore

    return assistant_message


def build_message(
    role: str, content: str | None, user_name: str | None = None
) -> ChatCompletionMessageParam:
    if role == "system":
        return build_system_prompt(system_prompt=str(content))
    elif role == "user":
        return build_user_message(str(content), user_name=user_name)
    elif role == "assistant":
        return build_assistant_message(content=content)
    else:
        raise ValueError("Invalid message role.")


async def Sync_Prompt_Templates(_config: Config, revision: str):
    fs = FileStorage(_config, Category="revisions")
    # Check the storage type and handle Jinja files accordingly
    azure_template_dir = "prompts/" + revision
    if _config.file_storage.revisions.storage_type != "local":
        # Define the file path in Azure storage
        jinja_files = sorted(
            [
                f
                for f in await fs.list_files(file_path=azure_template_dir)
                if f.endswith(".jinja")
            ]
        )

        # Local directory to save the Jinja files
        local_template_dir = Path("ingenious_extensions/templates/prompts")
        local_template_dir.mkdir(parents=True, exist_ok=True)

        for file in jinja_files:
            file_name = file.split("/")[-1]  # Extract the actual file name
            logger.debug(f"Downloading template: {file_name}")
            temp_file_content = await fs.read_file(
                file_name=file_name, file_path=azure_template_dir
            )
            local_file_path = local_template_dir / file_name
            with open(local_file_path, "w", encoding="utf-8") as f:
                f.write(temp_file_content)
            logger.debug(f"Template saved (overwritten if existing): {local_file_path}")
    else:
        logger.debug("Local storage type detected")
