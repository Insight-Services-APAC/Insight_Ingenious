import logging

import autogen
import autogen.retrieve_utils
import autogen.runtime_logging
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent

from ingenious.services.chat_services.multi_agent.tool_factory import ToolFunctions

logger = logging.getLogger(__name__)


class ConversationPattern:

    def __init__(self, default_llm_config: dict, topics: list, memory_record_switch: bool, memory_path: str,
                 thread_memory: str):
        self.default_llm_config = default_llm_config
        self.topics = topics
        self.memory_record_switch = memory_record_switch
        self.memory_path = memory_path
        self.thread_memory = thread_memory
        self.topic_agents: list[autogen.AssistantAgent] = []

        if self.thread_memory == None or self.thread_memory == '':
            with open(f"{self.memory_path}/context.md", "w") as memory_file:
                memory_file.write("This is a new conversation, please continue the conversation given user question")

        if self.memory_record_switch and self.thread_memory != None and self.thread_memory != '':
            logger.log(level=logging.DEBUG,
                       msg="memory_record = True, check pattern requires optional dependencies: 'ChatHistorySummariser'.")
            with open(f"{self.memory_path}/context.md", "w") as memory_file:
                memory_file.write(self.thread_memory)

        self.termination_msg = lambda x: x.get("content", "") is not None and "TERMINATE" in x.get("content",
                                                                                                   "").rstrip().upper()

        # Initialize agents
        if self.memory_record_switch:
            self.user_proxy = RetrieveUserProxyAgent(
            name="user_proxy",
            is_termination_msg=self.termination_msg,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2,
            system_message="I am a proxy for the user, give the context to the researcher.",
            retrieve_config={
                "task": "qa",
                "docs_path": [
                    f"{self.memory_path}/context.md"
                ],
                "chunk_token_size": 2000,
                "model": self.default_llm_config["model"],
                "vector_db": "chroma",
                "overwrite": True,  # set to True if you want to overwrite an existing collection
                "get_or_create": True,  # set to False if don't want to reuse an existing collection
            },
            code_execution_config=False,  # we don't want to execute code in this case.
            silent=True
            )
        else:
            self.user_proxy = autogen.UserProxyAgent(
                name="user_proxy",
                is_termination_msg=self.termination_msg,
                human_input_mode="NEVER",
                max_consecutive_auto_reply=2,
                system_message="I am a proxy for the user, give the context to the researcher.",
                code_execution_config=False,
                silent=True
            )


        self.researcher = autogen.ConversableAgent(
            name="researcher",
            system_message=("I am a planner. "
                            f"I determine if the question requires interacting with the predefined topic agents: {', '.join(self.topics)}. "
                            "Tasks: "
                            " - I classify the question based on the intent of the question and prioritise the topic of current question."
                            " - if the topic of the current question is ambiguous, i derive the topic from context."
                            " - if the context also does not fall into the predefined topics, ask the reporter to end the conversation."
                            "When talk with the topic agent:"
                            " - I compose a query for the topic agent, wait for its response, and collect the necessary information. "
                            "To end the group chat:"
                            " - I ask the reporter to provide the user with a response without involving the topic agent. "
                            "Rules: "
                            "- I do not send commands like UPDATE CONTEXT."
                            "- I do not repeating the same call. "
                            "- I do not communicate with myself or send empty queries."
                            "- I return TERMINATE if no new information"),
            description="I am a researcher planning the query and resource,I cannot provide direct answers, add extra info, or call functions.",
            llm_config=self.default_llm_config,
            human_input_mode="NEVER",
            code_execution_config=False,
            is_termination_msg=self.termination_msg,

        )

        self.report_agent = autogen.AssistantAgent(
            name="reporter",
            system_message=("I report the conversation result to the user in a concise and formatted way. "
                            f"{'At the end of conversation, I ALWAYS call and execute chat_memory_recorder to record user '
                               'question/intention and the summarised conversation in one sentence. The function takes 2 argument: '
                               'conversation_text: str, last_response: str' if self.memory_record_switch else ''} "
                            "I keep the memory concise with factual information."
                            "I do not talk to my self."
                            "I do not talk to my topic agent multiple times."
                            "I can TERMINATE the conversation if no useful information is available."),
            description="I **ONLY** report conversation result",
            llm_config=self.default_llm_config,
            is_termination_msg=self.termination_msg,
        )

        if self.memory_record_switch:
            print("chat_memory_recorder registered")
            autogen.register_function(
                ToolFunctions.update_memory,
                caller=self.report_agent,
                executor=self.report_agent,
                name="chat_memory_recorder",
                description=("A function responsible for recording and updating summarized conversation memory. "
                             "It ensures that the conversation history is accurately and concisely saved to a specified location for future reference.")
            )

    def add_topic_agent(self, agent: autogen.AssistantAgent):
        self.topic_agents.append(agent)

    async def get_conversation_response(self, input_message: str) -> [str, str]:
        """
        This function is the main entry point for the conversation pattern. It takes a message as input and returns a 
        response. Make sure that you have added the necessary topic agents and agent topic chats before 
        calling this function.
        """
        graph_dict = {}
        graph_dict[self.user_proxy] = [self.researcher]
        graph_dict[self.researcher] = self.topic_agents
        for topic_agent in self.topic_agents:
            graph_dict[topic_agent] = [self.researcher]
        graph_dict[self.researcher] = [self.report_agent]
        graph_dict[self.report_agent] = [self.researcher]

        groupchat = autogen.GroupChat(
            agents=[self.user_proxy, self.researcher, self.report_agent] + self.topic_agents,
            messages=[],
            max_round=6,
            speaker_selection_method="auto",
            send_introductions=True,
            select_speaker_auto_verbose=False,
            allowed_or_disallowed_speaker_transitions=graph_dict,
            speaker_transitions_type="allowed",
            select_speaker_prompt_template=(
                "First, route the conversation to the 'researcher', "
                "next select the topic agent chosen by  researcher,"
                "next select researcher to chose next topic agent if necessary,"
                "after talk to all required topic agent, "
                "select 'reporter' record memory and end the conversation with the summarized information."
            )
        )

        manager = autogen.GroupChatManager(groupchat=groupchat,
                                           llm_config=self.default_llm_config,
                                           is_termination_msg=self.termination_msg,
                                           code_execution_config=False)
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

        with open(f"{self.memory_path}/context.md", "r") as memory_file:
            context = memory_file.read()

        # Send a response back to the user
        return res.summary, context
