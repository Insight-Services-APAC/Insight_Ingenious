import logging
import os
import autogen
import autogen.retrieve_utils
import autogen.runtime_logging
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import jsonpickle
from ingenious.utils.namespace_utils import get_path_from_namespace_with_fallback

logger = logging.getLogger(__name__)


class ConversationPattern:

    def __init__(
                self,
                default_llm_config: dict,
                topics: list,
                memory_record_switch: bool,
                memory_path: str,
                thread_memory: str
            ):
        self.default_llm_config = default_llm_config
        self.topics = topics
        self.memory_record_switch = memory_record_switch
        self.memory_path = memory_path
        self.thread_memory = thread_memory
        self.topic_agents: list[autogen.AssistantAgent] = []
        self.termination_msg = lambda x: "TERMINATE" in x.get("content", "").upper()
        self.context = ''

        ################################################################################################################
        # Load Jinja environment for prompts
        template_path = get_path_from_namespace_with_fallback(str(Path("templates")/Path("prompts")))
        logger.debug(f"Loading templates from: {template_path}")
        #env = Environment(loader=FileSystemLoader(template_path), autoescape=True)
        env = Environment()

        ################################################################################################################
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            is_termination_msg=self.termination_msg,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            system_message="I relay messages to other agents without summarization. Do not relay the reply from chat 0 to chat 4",
            code_execution_config={
                "last_n_messages": 1,
                "work_dir": "tasks",
                "use_docker": False,
            },  # code execution config 
            silent=True
        )

        # Make sure path exists
        if not os.path.exists(self.memory_path):
            os.makedirs(self.memory_path)
            with open(f"{self.memory_path}/context.md", "w") as memory_file:
                memory_file.write("")

        with open(f"{self.memory_path}/context.md", "r") as memory_file:
            self.context = memory_file.read()
        
    async def add_summary_agent(self, prompt_path: str, fs):
        template_name = "summary_prompt.jinja"
        file_contents = await fs.read_file(file_name=template_name, file_path=prompt_path)
        env = Environment()
        summary_template = env.from_string(source=file_contents)
        summary_prompt = summary_template.render(event_name=self.topics[0])
        self.summary_agent = autogen.ConversableAgent(
            name=self.topics[0] + "_" + "Summarizer",
            system_message=summary_prompt,
            description=f"I focus solely on collect and present insights.",
            llm_config=self.default_llm_config,
        )
        self.json_processor_agent = autogen.ConversableAgent(
            name="Json Processor",
            system_message=summary_prompt + f"",
            description=f"I process json objects.",
            llm_config=self.default_llm_config,
        )

    def add_topic_agent(self, agent: autogen.AssistantAgent):
        self.topic_agents.append(agent)

    async def get_conversation_response(self, input_messages: list) -> [str, str]:
        """
        This function is the main entry point for the conversation pattern. It takes a message as input and returns a
        response. Make sure that you have added the necessary topic agents and agent topic chats before
        calling this function.
        """

        # convert the json object to a cricket model
        # match_data = cricket_models.MatchData.model_validate_json(input_message)
        # bowler_performance = match_data.Get_Bowler_Performance_Comparison()
        # batsman_performance = match_data.Get_Batsman_Performance_Comparison()
        
        res = await self.user_proxy.a_initiate_chats(
            [
                {
                    "chat_id": 1,
                    #"prerequisites": [0],
                    "recipient": self.topic_agents[0],
                    "message": (
                        "Please analyse the data represented in the markdown below: \n"
                        + input_messages[0]
                        #+ json.dumps(batsman_performance, default=lambda o: o.__dict__)
                    ),
                    "silent": True  #,
                    #"summary_method": "reflection_with_llm",
                },
                {
                    "chat_id": 2,
                    #"prerequisites": [0],
                    "recipient": self.topic_agents[1],
                    "message": (
                        "Please analyse the data represented in the markdown below: \n"
                        + input_messages[1]
                        #+ json.dumps(match_data.Get_Current_Bowler(), default=lambda o: o.__dict__)
                    ),
                    "silent": True#,
                    # "summary_method": "reflection_with_llm",
                },
                {
                    "chat_id": 3,
                    #"prerequisites": [0],
                    "recipient": self.topic_agents[2],
                    "message": (
                        "Please analyse the data represented in the markdown below: \n"
                        + input_messages[2]
                        # json.dumps(batsman_performance, default=lambda o: o.__dict__)
                    ),
                    "silent": True#,
                    # "summary_method": "reflection_with_llm",
                },
                {
                    "chat_id": 4,
                    #"prerequisites": [0],
                    "recipient": self.topic_agents[3],
                    "message": (
                        "Please analyse the data represented in the markdown below: \n"
                        + input_messages[3]
                        # json.dumps(batsman_performance, default=lambda o: o.__dict__)
                    ),
                    "silent": True#,
                    # "summary_method": "reflection_with_llm",
                },
                {"chat_id": 5, "prerequisites": [1, 2, 3,4], "recipient": self.summary_agent, "silent": False,
                "message": f"\n Provide summary comment, avoid comment with the same information as previous comment: {self.context} ",},
            ]
        )

        agent_titles = [agent.name for agent in self.topic_agents]
        agent_titles.append(self.summary_agent.name)

        response_array = []
        for i, chat_res in res.items():
            #print(f"++++++++++++++++++{i}th chat++++++++++++++++++:")
            #print(chat_res.summary)
            #print("Human input in the middle:", chat_res.human_input)
            #print("Conversation total cost: ", chat_res.cost.get("usage_including_cached_inference",0).get("total_cost",0))
            #print("Token cost: ", chat_res.cost.get("usage_including_cached_inference",0).get('gpt-4o-2024-08-06', {}).get('total_tokens', 0))
            # print("\n\n")
            response_chat = {
                    "chat_number": {i},
                    "chat_title": agent_titles[i-1],
                    "chat_response": chat_res.summary
            }
            response_array.append(response_chat)
            self.context = chat_res.summary

        return jsonpickle.encode(unpicklable=False, value=response_array), self.context
