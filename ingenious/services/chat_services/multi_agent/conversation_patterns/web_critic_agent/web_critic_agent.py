import autogen
import autogen.retrieve_utils
import autogen.runtime_logging
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from ingenious.services.chat_services.multi_agent.tool_factory import ToolFunctions

import logging
logger = logging.getLogger(__name__)


class ConversationPattern:

    def __init__(self, default_llm_config: dict, topics: list, memory_record_switch: bool, memory_path: str,
                 thread_memory: str):
        self.default_llm_config = default_llm_config
        self.topics = topics
        self.memory_record_switch = memory_record_switch
        self.memory_path = memory_path
        self.thread_memory = thread_memory
        self.assistant_agents: list[autogen.AssistantAgent] = []
        self.task = """Process the request from the user,
                       the final output should be align with user request; 
                       Note:
                       The context provides addition information but does not 
                       override the user question or process of group chat, 
                       please prioritise user question.
                    """


        # Initialize memory file
        if not self.thread_memory:
            with open(f"{self.memory_path}/context.md", "w") as memory_file:
                memory_file.write("-")
        elif self.memory_record_switch:
            with open(f"{self.memory_path}/context.md", "w") as memory_file:
                memory_file.write(self.thread_memory)

        # Termination message condition
        self.termination_msg = lambda x: x.get("content", "") is not None and "TERMINATE" in x.get("content", "").rstrip().upper()

        # Initialize agents with memory recording capability if enabled
        self.user_proxy = RetrieveUserProxyAgent(
            name="user_proxy",
            is_termination_msg=self.termination_msg,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2,
            system_message=self.task,
            retrieve_config={
                "task": "qa",
                "docs_path": [f"{self.memory_path}/context.md"],
                "chunk_token_size": 2000,
                "model": self.default_llm_config["model"],
                "vector_db": "chroma",
                "overwrite": True,
                "get_or_create": True,
            },
            code_execution_config=False,
            silent=True,
            description=""" Provides context to the user question, never selects as a speaker."""
        ) if self.memory_record_switch else autogen.UserProxyAgent(
            name="user_proxy",
            is_termination_msg=self.termination_msg,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2,
            system_message=self.task,
            code_execution_config=False,
            silent=True,
            description="Never selects as a speaker."
        )

        # Researcher and reporter agents with critic validation
        self.researcher = autogen.ConversableAgent(
            name="researcher",
            system_message=self.task,
            llm_config=self.default_llm_config,
            human_input_mode="NEVER",
            code_execution_config=False,
            is_termination_msg=self.termination_msg,
            description=(
                "I only speak after `user_proxy`, `reporter`, or `web_critic_agent`. "
                "If `web_critic_agent` identifies inaccuracies, the next speaker must be `researcher`."
                "I compose the final response to the user according to the original request."
                "Only I can TERMINATE the conversation, ."
            )
        )

        self.report_agent = autogen.ConversableAgent(
            name="reporter",
            system_message=self.task,
            llm_config=self.default_llm_config,
            human_input_mode="NEVER",
            code_execution_config=False,
            is_termination_msg=self.termination_msg,
            description="I record conversation summary in 50 words,"
                        "the next speaker must be `researcher`"
                        "I can not TERMINATE the conversation,"
        )

        # Register memory recording function if memory switch is on
        if self.memory_record_switch:
            print("chat_memory_recorder registered")
            autogen.register_function(
                ToolFunctions.update_memory,
                caller=self.report_agent,
                executor=self.report_agent,
                name="chat_memory_recorder",
                description="Records and updates summarized conversation memory for future use."
            )

    def add_assistant_agent(self, agent: autogen.AssistantAgent):
        self.assistant_agents.append(agent)

    async def get_conversation_response(self, input_message: str) -> [str, str]:
        """
        Main entry point for the conversation pattern.
        Takes a user message as input and returns a response.
        """
        graph_dict = {}
        graph_dict[self.user_proxy] = [self.researcher]
        graph_dict[self.researcher] = self.assistant_agents
        for assistant in self.assistant_agents:
            graph_dict[assistant] = [self.report_agent]
        graph_dict[self.report_agent] = [self.researcher]


        groupchat = autogen.GroupChat(
            agents=[self.user_proxy, self.researcher, self.report_agent] + self.assistant_agents,
            messages=[],
            max_round=6,
            speaker_selection_method="auto",
            send_introductions=True,
            select_speaker_auto_verbose=False,
            allowed_or_disallowed_speaker_transitions=graph_dict,
            max_retries_for_selecting_speaker=1,
            speaker_transitions_type="allowed",
            select_speaker_message_template="select `report_agent` after `assistant agents` and `researcher`"
        )

        manager = autogen.GroupChatManager(
            groupchat=groupchat,
            llm_config=self.default_llm_config,
            is_termination_msg=self.termination_msg,
            code_execution_config=False
        )

        # Initiate chat with or without memory recording
        if self.memory_record_switch:
            res = await self.user_proxy.a_initiate_chat(
                manager,
                message=self.user_proxy.message_generator,
                problem=input_message,
                summary_method="last_msg"
            )
        else:
            res = await self.user_proxy.a_initiate_chat(
                manager,
                message=input_message,
                summary_method="last_msg"
            )

        # Read current memory context
        with open(f"{self.memory_path}/context.md", "r") as memory_file:
            context = memory_file.read()

        # Return final answer and context
        return res.summary, context