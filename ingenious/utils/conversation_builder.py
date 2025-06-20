"""
Conversation builder utilities

This module contains utilities for building OpenAI chat completion messages.
"""

import logging

from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

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
