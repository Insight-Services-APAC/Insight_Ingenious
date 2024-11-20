import os
import uuid
from datetime import datetime
from pathlib import Path
import json

import autogen
import autogen.runtime_logging
from jinja2 import Environment, FileSystemLoader

import ingenious.config.config as config
import ingenious.utils.match_parser as mp
from ingenious.services.chat_services.multi_agent.conversation_patterns.classification_agent.classification_agent import \
    ConversationPattern


class ConversationFlow:
    @staticmethod
    async def get_conversation_response(message: str,
                                        topics: list = [],
                                        thread_memory: str = '',
                                        memory_record_switch=True,
                                        event_type: str = '',
                                        thread_chat_history: list = []) -> [str, str]:
        _config = config.get_config()
        llm_config = _config.models[0].__dict__
        memory_path = _config.chat_history.memory_path

        # Load Jinja environment for prompts
        working_dir = Path(os.getcwd())
        template_path = working_dir / "ingenious" / "templates" / "prompts"
        print(template_path)
        env = Environment(loader=FileSystemLoader(template_path), autoescape=True)

        try:
            match = mp.MatchDataParser(payload=message, event_type=event_type)
            message, overBall, timestamp, match_id, feed_id = match.create_detailed_summary()
        except:
            message = "payload undefined"
            timestamp = str(datetime.now())
            match_id = '-'
            feed_id = '-'
            overBall = '-'

        _classification_agent_pattern = ConversationPattern(default_llm_config=llm_config,
                                                            topics=topics,
                                                            memory_record_switch=memory_record_switch,
                                                            memory_path=memory_path,
                                                            thread_memory=thread_memory)

        response_id = str(uuid.uuid4())

        for topic in ['is_wicket_ball', 'score_card_insight', 'game_status_changed', 'new_batter', 'undefined']:
            template = env.get_template(f'{topic}_prompt.jinja')
            system_message = template.render(
                topic=topic,
                response_id=response_id,
                feedTimestamp=timestamp,
                match_id=match_id,
                feedId=feed_id,
                overBall=overBall
            )

            description = f"I **ONLY** respond when addressed by `planner`, focusing solely on insights using {topic} logic."
            if topic == 'undefined':
                description = f"I **ONLY** respond when addressed by `planner` when the payload is undefined."

            topic_agent = autogen.AssistantAgent(
                name=topic,
                system_message=system_message,
                description=description,
                llm_config=llm_config,
            )

            _classification_agent_pattern.add_topic_agent(topic_agent)

        res, memory_summary = await _classification_agent_pattern.get_conversation_response(message)


        return res, memory_summary
