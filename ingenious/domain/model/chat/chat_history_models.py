from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Literal, Optional, TypedDict, Union
from uuid import UUID

# Type definitions
MessageStepType = Literal["user_message", "assistant_message", "system_message"]
TrueStepType = Literal[
    "assistant_streaming", "code", "tool", "thread", "assistant_step", "user_step"
]
StepType = Union[TrueStepType, MessageStepType]

# Constants
mime_types = {
    "text": "text/plain",
    "tasklist": "application/json",
    "plotly": "application/json",
}

ElementType = Literal[
    "image", "text", "pdf", "tasklist", "audio", "video", "file", "plotly", "component"
]
ElementDisplay = Literal["inline", "side", "page"]
ElementSize = Literal["small", "medium", "large"]


@dataclass
class ElementDict(TypedDict):
    id: str
    threadId: Optional[str]
    type: ElementType
    chainlitKey: Optional[str]
    url: Optional[str]
    objectKey: Optional[str]
    name: str
    display: ElementDisplay
    size: Optional[ElementSize]
    language: Optional[str]
    page: Optional[int]
    autoPlay: Optional[bool]
    playerConfig: Optional[dict]
    forId: Optional[str]
    mime: Optional[str]


@dataclass
class ChatHistory:
    user_id: str
    thread_id: str
    message_id: str
    positive_feedback: Optional[bool]
    timestamp: str
    role: str
    content: str
    content_filter_results: Optional[str]
    tool_calls: Optional[str]
    tool_call_id: Optional[str]
    tool_call_function: Optional[str]


@dataclass
class User:
    id: UUID
    identifier: str
    metadata: dict
    createdAt: Optional[str]


@dataclass
class Thread:
    id: UUID
    createdAt: Optional[str]
    name: Optional[str]
    userId: UUID
    userIdentifier: Optional[str]
    tags: Optional[List[str]]
    metadata: Optional[dict]


@dataclass
class Step:
    id: UUID
    name: str
    type: str
    threadId: UUID
    parentId: Optional[UUID]
    disableFeedback: bool
    streaming: bool
    waitForAnswer: Optional[bool]
    isError: Optional[bool]
    metadata: Optional[dict]
    tags: Optional[List[str]]
    input: Optional[str]
    output: Optional[str]
    createdAt: Optional[str]
    start: Optional[str]
    end: Optional[str]
    generation: Optional[dict]
    showInput: Optional[str]
    language: Optional[str]
    indent: Optional[int]


@dataclass
class Element:
    id: UUID
    threadId: Optional[UUID]
    type: Optional[str]
    url: Optional[str]
    chainlitKey: Optional[str]
    name: str
    display: Optional[str]
    objectKey: Optional[str]
    size: Optional[str]
    page: Optional[int]
    language: Optional[str]
    forId: Optional[UUID]
    mime: Optional[str]


@dataclass
class Feedback:
    id: UUID
    forId: UUID
    threadId: UUID
    value: int
    comment: Optional[str]


@dataclass
class FeedbackDict(TypedDict):
    forId: str
    id: Optional[str]
    value: Literal[0, 1]
    comment: Optional[str]


# Forward references need to be created
class StepDictClass(TypedDict, total=False):
    name: str
    type: StepType
    id: str
    threadId: str
    parentId: Optional[str]
    disableFeedback: bool
    streaming: bool
    waitForAnswer: Optional[bool]
    isError: Optional[bool]
    metadata: Dict
    tags: Optional[List[str]]
    input: str
    output: str
    createdAt: Optional[str]
    start: Optional[str]
    end: Optional[str]
    generation: Optional[Dict]
    showInput: Optional[Union[bool, str]]
    language: Optional[str]
    indent: Optional[int]
    feedback: Optional["FeedbackDict"]


StepDict = StepDictClass


@dataclass
class ThreadDict(TypedDict):
    id: str
    createdAt: str
    name: Optional[str]
    userId: Optional[str]
    userIdentifier: Optional[str]
    tags: Optional[List[str]]
    metadata: Optional[Dict]
    steps: List[StepDict]
    elements: Optional[List[ElementDict]]


def get_now():
    return datetime.now(timezone.utc)


def get_now_as_string():
    return get_now().strftime("%Y-%m-%d %H:%M:%S.%f%z")
