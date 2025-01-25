from abc import ABC, abstractmethod
import asyncio
from autogen_core import MessageContext
from pydantic import BaseModel
from ingenious.files.files_repository import FileStorage
from ingenious.models.config import Config, ModelConfig
import ingenious.config.config as ig_config
from typing import List, Optional
import logging
from autogen_core.logging import LLMCallEvent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import TextMessage, ChatMessage


class AgentChat(BaseModel):
    """
    A class used to represent a chat between an agent and a user or between agents

    Attributes
    ----------
    agent_name : str
        The name of the agent.
    user_message : str
        The message sent by the user.
    system_prompt : str
        The message sent by the agent.
    """
    chat_name: str
    target_agent_name: str
    source_agent_name: str
    user_message: str
    system_prompt: str
    chat_response: Optional[Response] = None
    completion_tokens: int = 0
    prompt_tokens: int = 0


class AgentChats(BaseModel):
    """
    A class used to represent a list of AgentChats.

    Attributes
    ----------
    agent_chats : List[AgentChat]
        A list of AgentChat objects.
    """

    _agent_chats: List[AgentChat] = []

    def __init__(self):
        super().__init__()

    def add_agent_chat(self, agent_chat: AgentChat):
        self._agent_chats.append(agent_chat)

    def get_agent_chats(self):
        return self._agent_chats

    def get_agent_chat_by_name(self, agent_name: str) -> AgentChat:
        for agent_chat in self._agent_chats:
            if agent_chat.agent_name == agent_name:
                return agent_chat
        raise ValueError(f"AgentChat with name {agent_name} not found")
    
    def get_agent_chats_by_name(self, agent_name: str) -> List[AgentChat]:
        agent_chats = []
        for agent_chat in self._agent_chats:
            if agent_chat.agent_name == agent_name:
                agent_chats.append(agent_chat)
        return agent_chats


class Agent(BaseModel):
    """
    A class used to represent an Agent.

    Attributes
    ----------
    agent_name : str
        The name of the agent.
    agent_model_name : str
        The name of the model associated with the agent. This should match the name of the associated model in config.yml
    agent_display_name : str
        The display name of the agent.
    agent_description : str
        A brief description of the agent.
    agent_type : str
        The type/category of the agent.
    """
    agent_name: str
    agent_model_name: str
    agent_display_name: str
    agent_description: str
    agent_type: str
    model: Optional[ModelConfig] = None
    system_prompt: Optional[str] = None
    log_to_prompt_tuner: bool = True
    return_in_response: bool = False

    def get_agent_chat(self, content: str,  ctx: MessageContext = None, source=None) -> AgentChat:
        if ctx:
            source = ctx.topic_id.source
        
        agent_chat: AgentChat = AgentChat(
            chat_name=self.agent_name + "",
            target_agent_name=self.agent_name,
            source_agent_name=source,
            user_message=content,
            system_prompt=self.system_prompt,
            chat_response=Response(chat_message=TextMessage(content=content, source=source))
        )
        return agent_chat

    async def log(self, agent_chat: AgentChat, queue: asyncio.Queue[AgentChat]):
        if self.log_to_prompt_tuner or self.return_in_response:
            await queue.put(agent_chat)


class Agents(BaseModel):
    """
    A class used to represent a list of Agents.

    Attributes
    ----------
    agents : List[Agent]
        A list of Agent objects.
    """

    _agents: List[Agent]

    def __init__(self, agents: List[Agent], config: Config):
        super().__init__()
        self._agents = agents       
        for agent in self._agents:
            for model in config.models:
                if model.model == agent.agent_model_name:
                    agent.model = model
                    break
        if not agent.model:
            raise ValueError(f"Model {agent.model_name} not found in config.yml")
        
    def get_agents(self):
        return self._agents
    
    def get_agent_by_name(self, agent_name: str) -> Agent:
        for agent in self._agents:
            if agent.agent_name == agent_name:
                return agent
        raise ValueError(f"Agent with name {agent_name} not found")


class AgentMessage(BaseModel):
    content: str


class LLMUsageTracker(logging.Handler):
    def __init__(self, agents: Agents, config: ig_config.Config, revision_id: str, identifier: str, event_type: str) -> None:
        """Logging handler that tracks the number of tokens used in the prompt and completion."""
        super().__init__()
        self._prompt_tokens = 0
        self._agents = agents
        self._completion_tokens = 0
        self._queue: List[AgentChat] = []
        self._config = config
        self._revision_id: str = revision_id
        self._identifier: str = identifier
        self._event_type: str = event_type

    @property
    def tokens(self) -> int:
        return self._prompt_tokens + self._completion_tokens

    @property
    def prompt_tokens(self) -> int:
        return self._prompt_tokens

    @property
    def completion_tokens(self) -> int:
        return self._completion_tokens

    def reset(self) -> None:
        self._prompt_tokens = 0
        self._completion_tokens = 0

    async def write_llm_responses_to_file(
            self
    ):
        for agent_chat in self._queue:
            agent = self._agents.get_agent_by_name(agent_chat.target_agent_name)
            if agent.log_to_prompt_tuner:
                output_path = f"functional_test_outputs/{self._revision_id}"
                fs = FileStorage(self._config)
                content = agent_chat.model_dump_json()
                await fs.write_file(
                    content,
                    f"agent_response_{self._event_type}_{agent_chat.source_agent_name}_{agent_chat.target_agent_name}_{self._identifier}.md",
                    output_path
                )

    async def post_chats_to_queue(self, target_queue: asyncio.Queue[AgentChat]):
        for agent_chat in self._queue:
            agent = self._agents.get_agent_by_name(agent_chat.target_agent_name)
            await agent.log(agent_chat, target_queue) 

    def emit(self, record: logging.LogRecord) -> None:
        """Emit the log record."""
        try:
            if isinstance(record.msg, LLMCallEvent):
                event: LLMCallEvent = record.msg
                agent_name = event.kwargs["agent_id"].split("/")[0]
                source_name = event.kwargs["agent_id"].split("/")[1]
                agent = self._agents.get_agent_by_name(agent_name)
                response = "\n\n".join([r['message']['content'] for r in event.kwargs['response']['choices']])
                chat = agent.get_agent_chat(content=response, source=source_name)
                self._prompt_tokens += event.prompt_tokens
                self._completion_tokens += event.completion_tokens
                chat.prompt_tokens = event.prompt_tokens
                chat.completion_tokens = event.completion_tokens
                self._queue.append(chat)
                
        except Exception as e:
            print(e)
            self.handleError(record)


class IProjectAgents(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def Get_Project_Agents(self, config: Config) -> Agents:
        pass
