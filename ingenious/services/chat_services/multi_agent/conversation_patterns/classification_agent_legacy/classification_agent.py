import autogen.retrieve_utils
import autogen.runtime_logging
import autogen
import ingenious.config.config as config
import ingenious.dependencies as deps
from ingenious.services.chat_services.multi_agent.agent_factory import AgentFactory
from ingenious.models.chat import Action, ChatRequest, ChatResponse, KnowledgeBaseLink, Product


class ConversationPattern:

    class Request:
        def __init__(
                self,
                message: str, 
                agents: list[autogen.ConversableAgent] = [],
                agent_chats: list[AgentFactory.agent_chat] = [],
                classifier_agent_name: str = "Classifier", 
                classifier_prompt: str = "Classify this message..",
                reporter_agent_name: str = "Reporter",
                summary_agent_name: str = "Summarizer"):
            self.message = message
            self.agents = agents
            self.agent_chats = agent_chats
            self.classifier_agent_name = classifier_agent_name
            self.classifier_prompt = classifier_prompt            
            self.reporter_agent_name = reporter_agent_name
            self.summary_agent_name = summary_agent_name
            
    def __init__(self, default_llm_config: dict):
        self.default_llm_config = default_llm_config

        self.classification_agent: autogen.ConversableAgent = autogen.ConversableAgent(
            name="Classifier",
            system_message="You analyse a message and determine its topics. If it is about one or the other you simply return the topic as a single word. If it is about neither simply return 'neither'. if it is about both return 'both'.",
            llm_config=self.default_llm_config
        )

        self.summary_agent: autogen.ConversableAgent = autogen.ConversableAgent(
            name="Summarizer",
            system_message="You create succinct summaries.",
            llm_config=self.default_llm_config
        )

        self.reporter_agent: autogen.ConversableAgent = autogen.ConversableAgent(
            name="Reporter",
            system_message="You generate a final result.",
            llm_config=self.default_llm_config
        )

        self.agent_topic_chats: list[AgentFactory.agent_chat] = []
        self.topic_agents: list[autogen.ConversableAgent] = []

    def add_topic_agent_chat(self, topic_agent: autogen.ConversableAgent, topic: str, max_turns: int = 1, clear_history: bool = True, message: str = "", summary_method: str = "reflection_with_llm"):
        self.agent_topic_chats.append(
            AgentFactory.agent_chat(
                    question_agent=self.summary_agent,
                    answer_agent=topic_agent,
                    max_turns=max_turns,
                    clear_history=clear_history,
                    message=message,
                    summary_method=summary_method,
                    topic=topic
                )
            )

    def add_topic_agent(self, agent: autogen.ConversableAgent):
        self.topic_agents.append(agent)

    async def get_conversation_response(self, 
                                        message: str,
                                        memory_record_switch=None,
                                        thread_memory=None,
                                        topics=None
                                        ) -> str:
        """
        This function is the main entry point for the conversation pattern. It takes a message as input and returns a 
        response. Make sure that you have added the necessary topic agents and agent topic chats before 
        calling this function.
        """        
        input_message = message
    
        topics = []
        for agent_chat in self.agent_topic_chats:
            topics.append(agent_chat.topic)
        
        # get distinct topics
        topics = list(set(topics))
 
        # Check if the question is related to the topics of the agents
        msg = "Classify this message as one of the following topics: " + ", ".join(topics) + "." + "\n"
        msg = msg + str(input_message)
        res = self.reporter_agent.initiate_chat(
                                                    self.classification_agent, 
                                                    clear_history=False, 
                                                    message=msg, 
                                                    max_turns=1, 
                                                    summary_method="reflection_with_llm"
                                                )
        topic = res.chat_history[1]["content"]
        
        if (res.chat_history[1]["content"] == "neither"):
            return "The message is not related to the topics of the agents."
        
        agent_fac = AgentFactory()
        agent_fac.agents = self.topic_agents + [self.summary_agent, self.reporter_agent]
        chat_responses = await agent_fac.run_agents_async(chats=self.agent_topic_chats, topics=[topic])

        msg = "Summarize this conversation.."
        for r in chat_responses:
            msg = msg + "\n" + r.summary
        res = self.reporter_agent.initiate_chat(
                                                    self.summary_agent, 
                                                    clear_history=False, 
                                                    message=msg, 
                                                    max_turns=1, 
                                                    summary_method="reflection_with_llm"
                                                )
        print(res.summary)

        # Send a response back to the user
        return res.summary