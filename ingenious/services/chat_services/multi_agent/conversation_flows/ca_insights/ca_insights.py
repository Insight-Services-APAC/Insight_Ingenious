import json
import logging
import os
from datetime import datetime
from pathlib import Path
import autogen
import autogen.runtime_logging
from jinja2 import Environment, FileSystemLoader
from ingenious.files.files_repository import FileStorage
import ingenious.config.config as config
from ingenious.services.chat_services.multi_agent.service import IConversationFlow 
from ingenious.services.chat_services.multi_agent.conversation_patterns.ca_insights.ca_insights import \
    ConversationPattern
from ingenious.utils.namespace_utils import get_file_from_namespace_with_fallback, get_path_from_namespace_with_fallback
import yaml

logger = logging.getLogger(__name__)


def generate_final_insight(response, metadata):
    """
    Generate cricket match insights with player entities.

    Parameters:
    - response (dict): Contains 'insight' and 'entityIds'.
    - metadata (dict): Contains extracted details including 'match_id', 'feed_id', 'timestamp', 'over_ball', 'batsmen', and 'bowlers'.

    Returns:
    - dict: A structured representation of the player-based insight payload.
    """
    payload = {
        "response_id": metadata.get("feed_id", ""),
        "error_flag": False,
        "error_detail": '',
        "response": {
            "content": response,
        },
        "metadata": metadata
    }
    return payload


def maintain_memory(file_path, new_content, max_words=150):

    # Write the truncated content back to the file
    with open(file_path, "w") as memory_file:
        memory_file.write(new_content)


class ConversationFlow(IConversationFlow):
    async def get_conversation_response(
            self,
            message: str,
            event_type: str = '',
            thread_memory: str = '',
            memory_record_switch=True,
            thread_chat_history: list = []
    ) -> tuple[str, str]:

        try:
            message_json = json.loads(message)
            # message_object = gm.RootModel.model_validate_json(**message_json)
            # self.message_data.Set_Current_Ball(self.message_data.Get_All_Balls()[0])
            logger.debug(f"Message data loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to parse message: {message}")
            final_res = ['Failed to parse message.']
            memory_summary = ''
            return final_res, memory_summary


        _config = config.get_config()
        fs = FileStorage(_config)
        llm_config = _config.models[0].__dict__
        prompt_path = str(Path(f'prompts/{message_json["Revision"]}'))
        

        # quick local memory
        memory_path = _config.chat_history.memory_path
        file_path = f"{memory_path}/context.md"

        _classification_agent_pattern = ConversationPattern(default_llm_config=llm_config,
                                                            topics=[event_type],
                                                            memory_record_switch=memory_record_switch,
                                                            memory_path=memory_path,
                                                            thread_memory=thread_memory)
        
        await _classification_agent_pattern.add_summary_agent(prompt_path, fs)

        ################################################################################################################
        # Render system prompt
        # Get appropriate prompt template based on event_type
        input_messages = []
        for sub_agent in ['batsmen', 'bowlers', 'score_card', 'trivia']:
            data_template_path = get_path_from_namespace_with_fallback(str(Path("templates") / Path("data_structure")))
            if sub_agent in ['batsmen', 'bowlers', 'score_card']:
                data_methods = get_file_from_namespace_with_fallback(data_template_path, sub_agent + "_data.yml")
            else:
                data_methods = get_file_from_namespace_with_fallback(data_template_path, "all_data.yml")

            data_methods_obj = yaml.safe_load(data_methods)
            agent_val = ""
            for data_method in data_methods_obj:
                method = getattr(self.message_data, data_method["Method"])
                if "Parameters" in data_method.keys():
                    params = data_method["Parameters"]
                    if params not in [None, ""]:
                        agent_val += method(**data_method["Parameters"])
                    else:
                        agent_val += method()
                else:
                    agent_val += method()
                agent_val += "\n\n"
            input_messages.append(agent_val)

            template_name = f"{event_type}_{sub_agent}_prompt.jinja" if event_type else "undefined_prompt.jinja"
            file_contents = await fs.read_file(file_name=template_name, file_path=prompt_path)
            env = Environment()
            template = env.from_string(source=file_contents)
            system_prompt = template.render(topic=event_type)
            topic_agent = autogen.AssistantAgent(
                name=event_type + "_" + sub_agent,
                system_message=system_prompt,
                description=f"I focus solely on insights using {event_type} logic with focus on {sub_agent}.",
                llm_config=llm_config,
            )
            _classification_agent_pattern.add_topic_agent(topic_agent)

        ################################################################################################################
        # Extract necessary information from message_json
        metadata = {
            "match_id": str(message_json.get("Fixture","-").get("Competition","-").get("Id", "-")),
            "entities": {
                "players": [str(i.get('PlayerId', '')) for i in message_json.get("Innings", "-")[0].get("Batsmen", [])]+
                           [str(i.get('PlayerId', '')) for i in message_json.get("Innings", "-")[0].get("Bowlers", [])],
                "teams": [
                     str(message_json.get("Fixture","-").get("HomeTeam", {}).get("Id", "")),
                     str(message_json.get("Fixture", "-").get("AwayTeam", {}).get("Id", "")),
                ]
            }
        }

        res, memory_summary = await _classification_agent_pattern.get_conversation_response(input_messages)

        # Decide which insight function to use
        final_res = generate_final_insight(res, metadata)
        final_res = json.dumps(final_res)
        maintain_memory(file_path, memory_summary)

        return final_res, memory_summary
