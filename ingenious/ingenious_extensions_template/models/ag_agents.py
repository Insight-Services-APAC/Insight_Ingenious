

from abc import ABC
from typing import List
from autogen_agentchat.agents import AssistantAgent
from autogen_core import (
    Agent, MessageContext, RoutedAgent, message_handler, TopicId
)
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.messages import TextMessage, ChatMessage
from ingenious.models.agent import (
    AgentChat,
    Agent,
    AgentMessage,
    LLMUsageTracker,
    AgentChats,
)


class RoutedAssistantAgent(RoutedAgent, ABC):
    def __init__(self, agent: Agent, data_identifier: str, next_agent_topic: str) -> None:
        super().__init__(agent.agent_name)
        model_client = AzureOpenAIChatCompletionClient(**agent.model.__dict__)
        assistant_agent = AssistantAgent(
            name=agent.agent_name,
            system_message=agent.system_prompt,
            description="I am an AI assistant that helps with research.",
            model_client=model_client,
        )
        self._delegate = assistant_agent
        self._agent: Agent = agent
        self._data_identifier = data_identifier
        self._next_agent_topic = next_agent_topic

    @message_handler
    async def handle_my_message_type(
        self, message: AgentMessage, ctx: MessageContext
    ) -> None:
        """
            Receives the message and sends it to the assistant agent to make a llm call. It then calls publish message to send the response to the next agent.
        """
        agent_chat = self._agent.add_agent_chat(
            content=message.content,
            identifier=self._data_identifier,
            ctx=ctx
        )
        agent_chat.chat_response = await self._delegate.on_messages(
            messages=[TextMessage(content=message.content, source=ctx.topic_id.source)],
            cancellation_token=ctx.cancellation_token
        )

        await self.publish_my_message(agent_chat)

    async def publish_my_message(self, agent_chat: AgentChat) -> None:
        """
            Publishes the response to the next agent.
        """
        # Publish the outgoing message to the next agent
        await self.publish_message(
            AgentMessage(content=agent_chat.chat_response.chat_message.content),
            topic_id=TopicId(type=self._next_agent_topic, source=self.id.key),
        )


class RelayAgent(RoutedAgent):
    _response_count: int = 0
    _agent: Agent
    _agent_message: AgentMessage
    _data_identifier: str

    def __init__(self, agent: Agent, data_identifier: str, next_agent_topic: str, number_of_messages_before_next_agent: int) -> None:
        super().__init__("UserProxyAgent")
        self._agent = agent
        self._agent_messages: List[str] = []
        self.number_of_messages_before_next_agent = number_of_messages_before_next_agent
        self._data_identifier = data_identifier
        self._next_agent_topic = next_agent_topic

    @message_handler
    async def handle_user_message(
        self, message: AgentMessage, ctx: MessageContext
    ) -> None:
        self._response_count += 1
        content = "## " + ctx.sender.type + "\n" + message.content
        self._agent_messages.append(content)
        agent_chat = self._agent.add_agent_chat(
            content=content,
            identifier=self._data_identifier,
            ctx=ctx
        )
        #await self._agent.log(agent_chat=agent_chat, queue=queue)

        if self._response_count >= self.number_of_messages_before_next_agent:
            await self.publish_message(
                AgentMessage(content="\n\n".join(self._agent_messages)),
                topic_id=TopicId(self._next_agent_topic, source=self.id.key),
            )


class RoutedResponseOutputAgent(RoutedAgent, ABC):
    def __init__(self, agent: Agent, data_identifier: str) -> None:
        super().__init__(agent.agent_name)
        model_client = AzureOpenAIChatCompletionClient(**agent.model.__dict__)
        assistant_agent = AssistantAgent(
            name=agent.agent_name,
            system_message=agent.system_prompt,
            description="I am an AI assistant that helps with research.",
            model_client=model_client,
        )
        self._delegate = assistant_agent
        self._agent: Agent = agent
        self._data_identifier = data_identifier

    @message_handler
    async def handle_my_message_type(
        self, message: AgentMessage, ctx: MessageContext
    ) -> None:
        """
            Receives the message and sends it to the assistant agent to make a llm call. It then calls publish message to send the response to the next agent.
        """
        content = message.content
        agent_chat = self._agent.add_agent_chat(
            content=content,
            identifier=self._data_identifier,
            ctx=ctx
        )
        agent_chat.chat_response = await self._delegate.on_messages(
            messages=[TextMessage(content=content, source=ctx.topic_id.source)],
            cancellation_token=ctx.cancellation_token
        )
