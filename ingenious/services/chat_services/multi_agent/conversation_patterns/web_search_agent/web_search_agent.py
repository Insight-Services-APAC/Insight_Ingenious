import autogen
import autogen.retrieve_utils
import autogen.runtime_logging
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from ingenious.services.chat_services.multi_agent.tool_factory import ToolFunctions


class ConversationPattern:
    def __init__(self, default_llm_config: dict, topics: list, memory_record_switch: bool, memory_path: str, thread_memory: str):
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
            print(
                "Warning: if memory_record = True, the pattern requires optional dependencies: 'ChatHistorySummariser'.")
            with open(f"{self.memory_path}/context.md", "w") as memory_file:
                memory_file.write(self.thread_memory)

        self.termination_msg = lambda x: x.get("content", "") is not None and "TERMINATE" in x.get("content",
                                                                                                   "").rstrip().upper()

        # Initialize agents
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

        # Update the system message of the classification agent to include the topics
        self.classification_agent = autogen.AssistantAgent(
            name="classifier",
            system_message=(
                f"I am a classifier tasked with categorizing messages into the predefined topics: {', '.join(self.topics)}. "
                "I classify based on the intent of the question and prioritise the topic of current question rather than exisiting context."
                "if multiple topics are applicable, list all relevant topics."
                "If the topic is unclear, please first check the context and try classification "
                "if still cannot be classified please return 'ambiguous'. "
                "I am **ONLY** allowed to respond once **immediately** after `user_proxy` for one session."
                "I do not classify casual greetings such as 'Hi!'. and will return 'general conversation'"
                ),
            description="I **ONLY** classify user messages to a appropriate topic and record in the conversation",
            llm_config=self.default_llm_config,
            is_termination_msg=self.termination_msg,

        )

        self.researcher = autogen.ConversableAgent(
            name="researcher",
            system_message=("I am a planner. "
                            "decide if the question requires interacting with the search agent. "
                            "If yes, I compose a query for the search agent to do AI search, wait for its response, and collect the necessary information. "
                            "If no, I engage with the reporter to provide the user with a response without involving the search agent. "
                            "If the context does not fall into the predefined topics, "
                            "i pass the user query as AMBIGUOUS + keywords and ask the search agent to search (for example, what is contact number, the keyword is AMBIGUOUS contact number)."
                            "I do not say UPDATE CONTEXT"
                            "I only initiate search once, without repeating them after the first round. "
                            "I do not communicate with myself or send empty queries."),
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
                               'question and the summarised conversation in one sentence. The function takes 2 argument: '
                               'conversation_text: str, last_response: str' if self.memory_record_switch else ''};"
                            "I do not add extra information."
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


    def add_function_agent(self, topic_agent: autogen.ConversableAgent,
                        executor: autogen.UserProxyAgent,
                        tool: callable,
                        tool_name: str = "",
                        tool_description: str = ""):
        """
        Adds a topic-specific agent to the list of topic agents and registers a tool (function)
        that the agent can invoke using the provided executor.
        """

        self.topic_agents.append(topic_agent)
        # Register the tool (function) with the agent and executor
        autogen.register_function(
            tool,  # The callable tool function that the agent will use
            caller=topic_agent,  # The agent that will invoke the tool
            executor=executor,  # The executor responsible for running the tool
            name=tool_name,  # Name of the tool being registered
            description=tool_description  # Description of the tool for documentation
        )

        topic_agent.register_nested_chats(
            trigger=self.researcher,
            chat_queue=[
                {
                    "sender": self.user_proxy,
                    "recipient": self.researcher,
                    "summary_method": "last_msg",
                }
            ],
        )



    async def get_conversation_response(self, input_message: str) -> [str, str]:
        """
        Main entry point for the conversation pattern. Takes a message as input and returns a response.
        """

        graph_dict = {}
        graph_dict[self.user_proxy] = [self.classification_agent]
        graph_dict[self.classification_agent] = [self.researcher]
        graph_dict[self.researcher] = self.topic_agents
        for topic_agent in self.topic_agents:
            graph_dict[topic_agent] = [self.report_agent]
        graph_dict[self.report_agent] = [self.researcher]


        groupchat = autogen.GroupChat(
            agents=[self.user_proxy, self.classification_agent, self.researcher, self.report_agent ] + self.topic_agents,
            messages=[],
            max_round=10,
            speaker_selection_method="auto",
            send_introductions=True,
            select_speaker_auto_verbose=False,
            allowed_or_disallowed_speaker_transitions=graph_dict,
            speaker_transitions_type="allowed",
            select_speaker_prompt_template=(
                "First, route the conversation to the 'classifier', "
                "next select 'researcher' to choose the query, "
                "next select the search agent as requested the researcher,"
                "next select 'reporter' to summarize, "
                "finally select 'reporter' to record memory and TERMINATE."
            )
        )

        manager = autogen.GroupChatManager(groupchat=groupchat,
                                           llm_config=self.default_llm_config,
                                           is_termination_msg=self.termination_msg,
                                           code_execution_config=False, )

        #This pattern is required for RAG
        res = await self.user_proxy.a_initiate_chat(
            manager,
            message=self.user_proxy.message_generator,
            problem=input_message,
            summary_method="last_msg",
        )

        with open(f"{self.memory_path}/context.md", "r") as memory_file:
            context = memory_file.read()

        return res.summary, context
