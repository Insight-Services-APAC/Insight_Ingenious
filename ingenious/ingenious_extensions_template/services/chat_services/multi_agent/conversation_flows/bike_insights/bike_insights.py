import asyncio
from dataclasses import dataclass
import json
import os
from pathlib import Path
import threading
import time
from typing import List
from autogen_core import (
    CancellationToken,
    AgentId,
    ClosureAgent,
    ClosureContext,
    DefaultSubscription,
    DefaultTopicId,
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    TopicId,
    TypeSubscription,
    default_subscription,
    message_handler,
    type_subscription,
    TRACE_LOGGER_NAME,
    EVENT_LOGGER_NAME,
)
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console

from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.messages import TextMessage, ChatMessage
from autogen_agentchat.base import Response
from jinja2 import Environment, FileSystemLoader
import jsonpickle
from ingenious.ingenious_extensions_template.models.ag_agents import RelayAgent, RoutedAssistantAgent, RoutedResponseOutputAgent
from ingenious.utils.namespace_utils import get_path_from_namespace_with_fallback
from ingenious.services.chat_services.multi_agent.service import IConversationFlow
from ingenious.models.chat import ChatRequest, ChatResponse
from ingenious.models.agent import (
    AgentChat,
    Agent,
    AgentMessage,
    LLMUsageTracker,
    AgentChats,
)
import logging

# Custom class import from ingenious_extensions
from ingenious.ingenious_extensions_template.models.agent import ProjectAgents
from ingenious.ingenious_extensions_template.models.bikes import RootModel


class ConversationFlow(IConversationFlow):
    async def get_conversation_response(
        self,
        chat_request: ChatRequest, # This needs to be an object that implements the IChatRequest model so you can extend this by creating a new model in the models folder
    ) -> ChatResponse:
        
        message = json.loads(chat_request.user_prompt)
        event_type = chat_request.event_type
        
        #  Get your agents and agent chats from your custom class in models folder
        project_agents = ProjectAgents()
        agents = project_agents.Get_Project_Agents(self._config)

        # Process your data payload using your custom data model class 
        bike_sales_data = RootModel.model_validate(message)

        # Get the revision id and identifier from the message payload
        revision_id = message["revision_id"]
        identifier = message["identifier"]

        # Instantiate the logger and handler
        logger = logging.getLogger(EVENT_LOGGER_NAME)
        logger.setLevel(logging.INFO)

        llm_logger = LLMUsageTracker(
            agents=agents,
            config=self._config,
            revision_id=revision_id,
            identifier=identifier,
            event_type="default"
        )

        logger.handlers = [llm_logger]

        # Note you can access llm models from the configuration array
        llm_config = self.Get_Models()[0]
        # Note the base IConversationFlow gives you a logger for logging purposes
        self._logger.debug("Starting Flow")

        # Now add your system prompts to your agents from the prompt templates
        # Modify this if you want to modify the pattern used to correlate the agent name to the prompt template
        for agent in agents.get_agents():
            template_name = f"{agent.agent_name}_prompt.jinja"
            agent.system_prompt = await self.Get_Template(
                file_name=template_name, revision_id=revision_id
            )

        # Now construct your autogen conversation pattern the way you want
        # In this sample I'll first define my topic agents
        runtime = SingleThreadedAgentRuntime()

        async def register_research_agent(agent_name: str):
            agent = agents.get_agent_by_name(agent_name=agent_name)
            reg_agent = await RoutedAssistantAgent.register(
                runtime=runtime,
                type=agent.agent_name,
                factory=lambda: RoutedAssistantAgent(agent=agent, data_identifier=identifier, next_agent_topic="user_proxy")
            )
            await runtime.add_subscription(
                TypeSubscription(topic_type=agent_name, agent_type=reg_agent.type)
            )

        await register_research_agent(agent_name="customer_sentiment_agent")
        await register_research_agent(agent_name="fiscal_analysis_agent")

        user_proxy = await RelayAgent.register(
            runtime,
            "user_proxy",
            lambda: RelayAgent(
                agents.get_agent_by_name("user_proxy"),
                data_identifier=identifier,
                next_agent_topic="summary",
                number_of_messages_before_next_agent=2
            ),
        )
        await runtime.add_subscription(
                TypeSubscription(topic_type="user_proxy", agent_type=user_proxy.type)
            )

        async def register_output_agent(agent_name: str):
            agent = agents.get_agent_by_name(agent_name=agent_name)
            summary = await RoutedResponseOutputAgent.register(
                runtime,
                agent.agent_name,
                lambda: RoutedResponseOutputAgent(
                    agent=agent,
                    data_identifier=identifier
                ),
            )
            await runtime.add_subscription(
                TypeSubscription(topic_type=agent_name, agent_type=summary.type)
            )

        await register_output_agent(agent_name="summary")

        results = []
        tasks = []

        runtime.start()

        initial_message: AgentMessage = AgentMessage(content=json.dumps(message))
        fiscal_analysis_agent_message: AgentMessage = AgentMessage(content=bike_sales_data.display_bike_sales_as_table())
        await asyncio.gather(
            runtime.publish_message(
                initial_message,
                topic_id=TopicId(type="customer_sentiment_agent", source="default"),
            ),
            runtime.publish_message(
                fiscal_analysis_agent_message,
                topic_id=TopicId(type="fiscal_analysis_agent", source="default"),
            )
        )
        
        await runtime.stop_when_idle()

        # If you want to use the prompt tuner you need to write the responses to a file with the method provided in the logger
        await llm_logger.write_llm_responses_to_file()

        # Lastly return your chat response object
        chat_response = ChatResponse(
            thread_id=chat_request.thread_id,
            message_id="",
            agent_response=jsonpickle.encode(unpicklable=False, value=llm_logger._queue),
            token_count=llm_logger.prompt_tokens,
            max_token_count=0,
            memory_summary=""
        )

        return chat_response
