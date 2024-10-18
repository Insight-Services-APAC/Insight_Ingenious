# agent_factory.py
from typing import Optional
import autogen
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
import ingenious.config.config as config
from ingenious.config.profile import Profiles


class ToolFunctions:
    @staticmethod
    def aisearch(search: str, index_name: str) -> str:
        _config = config.get_config()
        credential = AzureKeyCredential(_config.azure_search_services[0].key)
        client = SearchClient(
                endpoint=_config.azure_search_services[0].endpoint,
                index_name=index_name,
                credential=credential,
            )
        results = client.search(search_text=search, top=5,
                                query_type = "semantic", #semantic, full or simple
                                query_answer = "extractive",
                                query_caption="extractive",
                                vector_queries = None) #vector_queries can input the query as a vector
        text_results = ""
        title = ""
        for result in results:
            captions = result['@search.captions']
            for caption in captions:
                text_results = text_results + "; " + caption.text
                if 'title' in result:
                    title = result['title']
                else:
                    title = ""
        return text_results

    def update_memory(conversation_text: str, last_response: str) -> str:
        _config = config.get_config()
        memory_path = _config.chat_history.memory_path
        with open(f"{memory_path}/context.md", "w") as memory_file:
            memory_file.write(conversation_text)
        print("Memory Updated:", conversation_text)
        return last_response



#
# class AgentFactory:
#     """ AgentFactory is a class that is wrapped around the creation and management of agents in the multi-agent system. It allows us to augment agent
#     functionality with generic functions such as the ability to execute a group of agents asynchronously. """
#
#     def __init__(self):
#         """ Initialize the AgentFactory class. """
#         #autogen.runtime_logging.start()
#         self.agent_history = []
#         self.agents: list[autogen.ConversableAgent] = []
#
#     class agent_chat:
#         """ agent_chat is a class that is used to store the parameters
#         required to initiate a chat between two agents. """
#
#         def __init__(self, question_agent, answer_agent, max_turns, clear_history, message,  summary_method, topic=None, tool=None):
#             self.question_agent = question_agent
#             self.answer_agent = answer_agent
#             self.max_turns = max_turns
#             self.clear_history = clear_history
#             self.message = message
#             self.summary_method = summary_method
#             self.topic = topic
#             self.tool = tool
#
#     def add_agent(self, agent):
#         """ Add an agent to the list of agents available to and stored in the class instance. """
#         agent = self.auto_reg_custom_reply_function(agent)
#         self.agents.append(agent)
#         return agent
#
#
#
#     async def run_agents_async(self, chats: list[agent_chat], topics=[]):
#         """ Run a list of agent chats asynchronously. """
#         agent_chat_results = []
#         tasks = []
#         for chat in chats:
#             if chat.topic in topics or len(topics) == 0:
#                 tasks.append(
#                     chat.question_agent.a_initiate_chat(
#                         chat.answer_agent,
#                         max_turns=chat.max_turns,
#                         clear_history=chat.clear_history,
#                         message=chat.message,
#                         summary_method=chat.summary_method
#
#                     )
#
#                 )
#
#         agent_chat_results = await asyncio.gather(*tasks)
#         return agent_chat_results
#
#     def auto_reg_custom_reply_function(self, agent):
#         agent.register_reply(
#             [autogen.Agent, None],
#             reply_func=self.update_history,
#             config={"callback": None}
#         )
#         return agent
#
#     def update_history(self, recipient, messages, sender, config):
#         msg = {
#             "sender": sender.name,
#             "receiver": recipient.name,
#             "message": messages
#         }
#         self.agent_history.append(msg)
#         return False, None  # required to ensure the agent communication flow continues
#
#     def get_agent_by_name(self, name) -> autogen.ConversableAgent:
#         for agent in self.agents:
#             if agent.name == name:
#                 return agent
#
#         # raise exception if agent not found
#         raise Exception(f"Agent with name '{name}' not found.")
#
#         my_dict = dict(
#             key1="value1",
#             key2="value2",
#             key3="value3"
#         )
#
#         ret_agent: autogen.ConversableAgent = autogen.ConversableAgent(
#             name="AgentNotSet",
#             llm_config=my_dict
#         )
#
#         return ret_agent
