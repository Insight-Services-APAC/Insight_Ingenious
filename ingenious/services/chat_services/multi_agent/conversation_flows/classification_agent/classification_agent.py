import autogen.runtime_logging
import autogen
import ingenious.config.config as config
from ingenious.models.chat import Action, ChatRequest, ChatResponse, KnowledgeBaseLink, Product
from ingenious.services.chat_services.multi_agent.conversation_patterns.classification_agent.classification_agent import ConversationPattern


class ConversationFlow:
    @staticmethod
    async def get_conversation_response(message: str, topics: list = [], thread_memory: str='', memory_record_switch = True, thread_chat_history: list[str, str] = []) -> [str, str]:
        _config = config.get_config()      
        llm_config = _config.models[0].__dict__
        memory_path = _config.chat_history.memory_path

        # Initialize the classification agent pattern
        _classification_agent_pattern = ConversationPattern(default_llm_config=llm_config,
                                                            topics= topics,
                                                            memory_record_switch = memory_record_switch,
                                                            memory_path = memory_path,
                                                            thread_memory = thread_memory)


        # Add the topic agents to the classification agent pattern
        for topic in topics:
            topic_agent = autogen.AssistantAgent(
                name= topic,
                system_message=(f"I am a topic agent responsible for answering queries about {topic}. "
                               "I provide accurate and concise answers and formatted for easy readability."
                               "I do not provide memory or update context."
                               "I do not respond multiple time in one conversation."
                               "If the research sends me the question out of my expertise, I response by 'The question is out of scope.' "),
                description=f"You are a topic agent focused on providing information about {topic}.",
                llm_config=llm_config,
            )

            _classification_agent_pattern.add_topic_agent(topic_agent)


        res, memory_summary  = await _classification_agent_pattern.get_conversation_response(message)

        # Send a response back to the user
        return res, memory_summary

