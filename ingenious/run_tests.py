import json
import datetime
from pydantic import BaseModel
from pathlib import Path
import jsonpickle
import markdown
import os
from jinja2 import Environment, FileSystemLoader
import yaml
import time

# Ingenious imports
import ingenious.config.config as ingen_config
from ingenious.models.chat import ChatRequest
from ingenious.services.chat_service import ChatService
from ingenious.files.files_repository import FileStorage
import ingenious.dependencies as ingen_deps
from ingenious.utils.stage_executor import ProgressConsoleWrapper
from ingenious.utils.namespace_utils import get_file_from_namespace_with_fallback, get_path_from_namespace_with_fallback
import ingenious.models.ca_raw_fixture_data as gm


class Event(BaseModel):
    file_name: str
    event_type: str
    response_content: str
    ball_identifier: str



class RunBatches:
    def __init__(self, progress: ProgressConsoleWrapper, task_id: str = None):
        self.config = ingen_config.get_config()
        self.fs = FileStorage(config=self.config)
        self.progress = progress
        self.task_id = task_id
        self.directory = "example_payload/raw"
        self.active_event_type = "all"
        self.past_game_status = '-'  # Track across files
        self.ball_count = 0  # Track across files
        self.processed_events = 0  # Track across files
        self.max_processed_events = 1000
        self.chat_service: ChatService = None
        self.starting_file = 0
        self.starting_new_ball = 0
        self.make_llm_calls = True
        self.events = []
        self.prompt_folder = ""
        self.chat_response_object = {}

    async def run(self, progress, task_id, **kwargs):
        # Clear old history files
        await self.clear_history_files()

        # Get kwargs
        if "active_event_type" in kwargs:
            self.active_event_type = kwargs["active_event_type"]
        else:
            self.active_event_type = "all"
        
        if "max_processed_events" in kwargs:
            self.max_processed_events = int(kwargs["max_processed_events"])
        else:
            self.max_processed_events = 1000

        if "test_run_session_id" in kwargs:
            self.test_run_session_id = str(kwargs["test_run_session_id"])
        else:
            self.test_run_session_id = "73f0036f-7478-4b03-a969-cf8484f5c1d2"

        # check if prompt folder is in local_files and if not copy the files from the template folder
        self.prompt_folder = f"prompts/{self.test_run_session_id}"
        file_check = await self.fs.list_files(file_path=f"prompts/{self.test_run_session_id}")
        if file_check is None:
            for file in os.listdir("ingenious_extensions/templates/prompts"):
                # read the file and write it to the local_files
                with open(f"ingenious_extensions/templates/prompts/{file}", "r") as f:
                    content = f.read()
                    await self.fs.write_file(content, file, self.prompt_folder)
            
        # Process JSON files
        json_files = sorted(
            [f for f in await self.fs.list_files(file_path=self.directory, container_name='matchfeed') if f.endswith(".json")]
        )
        output_path = await self.get_output_path(self.test_run_session_id)
        # self.write_markdown_header(output_path)

        total_files = len(json_files)
        idx = self.starting_file
        start_time = time.time()
        for json_file in json_files[self.starting_file:]:
            try:
                remaining_files = total_files - idx
                elapsed_time = time.time() - start_time
                avg_time_per_file = elapsed_time / idx if idx > 0 else 0
                estimated_time_remaining = avg_time_per_file * remaining_files

                self.progress.progress.update(
                    task_id=self.task_id,
                    description=(
                        f"Processing {json_file} ({idx}/{total_files})\n"
                        f"Remaining files: {remaining_files}, Estimated time left: {estimated_time_remaining:.2f}s\n"
                    )
                )
                if self.processed_events >= self.max_processed_events:
                    break
                await self.process_file(json_file, output_path)
                self.progress.progress.print(
                    f"Progress: {idx}/{total_files}, Remaining files: {remaining_files}, Estimated time left: {estimated_time_remaining:.2f}s"
                )
                self.progress.progress.print(f"***************************************************************************")

            except Exception as e:
                await self.handle_processing_error(json_file, e)
            idx += 1
        # self.write_markdown_footer(output_path)
        # self.convert_markdown_to_html(output_path)
        
        response_object_path = Path(output_path).parent
        response_object_file = "events.yml"
        # write the response object to a file
        await self.fs.write_file(yaml.dump(self.events, default_flow_style=False), response_object_file,  response_object_path)

    async def clear_history_files(self):
        history_files = sorted(
            [f for f in await self.fs.list_files(file_path='ball_history') if f.endswith(".json")]
        )
        for file_name in history_files:
            await self.fs.delete_file(
                file_name=Path(file_name).name,
                file_path='ball_history'
            )

    async def process_file(self, json_file, output_path):
        file_name = Path(json_file).name
        file_contents = await self.fs.read_file(file_name=file_name, file_path=self.directory)
        json_object = json.loads(file_contents)
        file_data = gm.RootModel.model_validate_json(json.dumps(json_object, indent=4))
        file_data._progress = self.progress 
        file_data.Revision = self.test_run_session_id

        self.chat_service = ChatService(
            chat_service_type="multi_agent",
            chat_history_repository=ingen_deps.get_chat_history_repository(),
            conversation_flow="ca_insights",
            config=self.config
        )
        self.chat_service.service_class.message_data = file_data
        current_game_status = file_data.Fixture.GameStatus

        self.progress.progress.update(task_id=self.task_id, description=f"Processing {file_name} - Game Status: {current_game_status}\n")
        self.progress.progress.print(f"Processing {file_name}")
        self.progress.progress.print(f"Current Game Status: {current_game_status} - Pre Game Status: {self.past_game_status} - Ball Count: {self.ball_count}")

        new_ball_data = await file_data.Get_New_Balls(
            config=ingen_deps.config, progress=self.progress, task_id=self.task_id
        )

        bad_count = 0

        for ball in new_ball_data[self.starting_new_ball:]:    
            self.chat_service.service_class.message_data.Set_Current_Ball(ball)
            self.ball_count += 1

            if (
                ball.IsWicket and bad_count == 0
                    and (
                        self.active_event_type == "iswicket" or self.active_event_type == "all")
            ):
                self.ball_count = 0
                self.processed_events += 1
                val = await self.get_data_from_method_calls(file_data=file_data)
                # print(str(self.processed_events))
                await self.handle_wicket_ball(
                    file_name,
                    file_data.model_dump(),
                    output_path,
                    val
                )
                bad_count = 1
            elif (
                self.ball_count == 42
                and (
                    self.active_event_type == "scorecard"
                    or self.active_event_type == "all"
                )
            ):
                self.processed_events += 1
                val = await self.get_data_from_method_calls(file_data=file_data)
                await self.handle_score_card(
                    file_name,
                    file_data.model_dump(),
                    output_path,
                    val
                )
                self.ball_count = 0
            elif (
                current_game_status != self.past_game_status 
                and bad_count == 0
                and
                (
                    self.active_event_type == "gamestatuschange"
                    or self.active_event_type == "all"
                )
            ):
                self.processed_events += 1
                val = await self.get_data_from_method_calls(file_data=file_data)
                await self.handle_game_status_change(
                    file_name,
                    file_data.model_dump(),
                    output_path,
                    val
                )
                bad_count = 1
            else:
                continue

        self.past_game_status = current_game_status

    async def get_data_from_method_calls(self, file_data):
        data_template_path = get_path_from_namespace_with_fallback(str(Path("templates") / Path("data_structure")))
        data_methods = get_file_from_namespace_with_fallback(
            data_template_path,
            "all_data.yml")
        data_methods_obj = yaml.safe_load(data_methods)
        val = ""
        for data_method in data_methods_obj:
            method = getattr(file_data, data_method["Method"])
            if "Parameters" in data_method.keys():
                params = data_method["Parameters"]
                if params not in [None, ""]:
                    val += method(**data_method["Parameters"])
                else:
                    val += method()
            else:
                val += method()
            val += "\n\n"

        return val

    async def handle_wicket_ball(self, file_name, json_object, output_path, val):
        self.progress.progress.print("Processing wicket ball!")
        await self.generate_and_save_insights(
            file_name, json_object, "is_wicket_ball", output_path, val
        )

    async def handle_score_card(self, file_name, json_object, output_path, val):
        self.progress.progress.print("42 ball reached generating scorecard insights!")
        await self.generate_and_save_insights(
            file_name, json_object, "score_card_insight", output_path, val
        )

    async def handle_game_status_change(self, file_name, json_object, output_path, val):
        self.progress.progress.print("Game status changed!")
        await self.generate_and_save_insights(
            file_name, json_object, "game_status_changed", output_path, val
        )

    async def generate_and_save_insights(self, file_name, json_object, event_type, output_path, val):
        thread_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        
        if self.make_llm_calls:
            chat_request = ChatRequest(
                thread_id=thread_id,
                user_prompt=jsonpickle.dumps(json_object, unpicklable=False),
                conversation_flow="ca_insights",
                event_type=event_type
            )

            response = await self.chat_service.get_chat_response(chat_request)
            response_content = json.loads(
                json.loads(response.agent_response)['response']['content']
            )
        else:
            response_content = [{"chat_response": "No LLM calls made"}]
            response = {}

        self.chat_response_object = response.agent_response
        await self.llm_response_to_markdown(file_name, response, event_type, output_path, val, response_content)

    async def handle_processing_error(self, file_name, error):
        self.progress.progress.print(f"Error processing {file_name}: {error}")
        raise

    def write_markdown_header(self, output_path):
        with open(output_path, 'w') as f:
            f.write("[TOC]\n\n## Responses\n\n")

    def write_markdown_footer(self, output_path):
        if 1 == 1:
            pass
        with open(output_path, 'a') as f:
            f.write("## Agent Prompts\n\n")
            template_path = Path("ingenious_extensions/templates/prompts")
            env = Environment(loader=FileSystemLoader(template_path), autoescape=True)
            for template in env.list_templates():
                if template.endswith('.jinja'):
                    content = env.get_template(template).render()
                    f.write(f"<details markdown='1'>\n<summary>{template}</summary>\n\n{content}\n</details>\n\n")

    async def llm_response_to_markdown(
        self,
        file_name,
        response,
        event_type,
        output_path,
        val,
        agent_response=None
    ):
        if self.make_llm_calls:
            await self.save_agent_response(output_path, agent_response[0]['chat_response'], event_type, "batsman")
            await self.save_agent_response(output_path, agent_response[1]['chat_response'], event_type, "bowler")
            await self.save_agent_response(output_path, agent_response[2]['chat_response'], event_type, "scorecard")
            await self.save_agent_response(output_path, agent_response[3]['chat_response'], event_type, "trivia")
            await self.save_agent_response(output_path, agent_response[4]['chat_response'], event_type, "summary")
        else:
            await self.save_agent_response(output_path, "Insight not yet generated", event_type, "batsman")
            await self.save_agent_response(output_path, "Insight not yet generated", event_type, "bowler")
            await self.save_agent_response(output_path, "Insight not yet generated", event_type, "scorecard")
            await self.save_agent_response(output_path, "Insight not yet generated", event_type, "trivia")
            await self.save_agent_response(output_path, "Insight not yet generated", event_type, "summary")


        #await self.save_agent_response(output_path, json.dumps(response.agent_response), event_type, "response_object")
        
        if self.make_llm_calls:
            response_overview = agent_response[-1]['chat_response']
        else:
            response_overview = "Insight not yet generated"

        event = Event(
            file_name=file_name,
            event_type=event_type,
            response_content=response_overview,
            ball_identifier=self.get_current_ball_identifier()
        )

        self.events.append(event.__dict__)

        await self.save_payload(output_path=output_path, val=val, event_type=event_type)   

    async def get_output_path(self, session_id, generate_new_id=True):
        if session_id:
            test_run_id = session_id
        else:
            test_run_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S") if generate_new_id else "20241221144853"
        
        output_path = f"./functional_test_outputs/{test_run_id}/responses.md"
        
        return output_path
    
    def get_current_ball_identifier(self):
        return "".join([ 
            f"{self.chat_service.service_class.message_data.Get_Current_Ball().InningsNumber:02}",
            "_",
            f"{self.chat_service.service_class.message_data.Get_Current_Ball().OverNumber:04}",
            "_",
            f"{self.chat_service.service_class.message_data.Get_Current_Ball().BallNumber:02}",
        ])
    
    async def save_agent_response(self, output_path, agent_response, event_type, agent_name):
        payload_file = f"agent_response_{event_type}_{agent_name}_{self.get_current_ball_identifier().strip()}.md"
        
        payload_output_path = Path(output_path).parent
        await self.fs.write_file(agent_response, payload_file,  payload_output_path)

    def render_button(self, icon, link_function, display_text, style):
        ret = """
            <button class="btn btn-@style@" onclick="@link_function@('@id@')">
                <i class="bi bi-@icon@ icon"></i> @display_text@
            </button>
        """
        ret = ret.replace("@id@", self.get_current_ball_identifier())
        ret = ret.replace("@link_function@", link_function)
        ret = ret.replace("@icon@", icon)
        ret = ret.replace("@display_text@", display_text)
        ret = ret.replace("@style@", style)

        return ret.strip()

    async def save_payload(self, output_path, val, event_type):
        payload_file = "".join([
            "payload_",
            event_type,
            "_",
            self.get_current_ball_identifier(),
            ".md"
        ]
        )
        
        payload_output_path = Path(output_path).parent
        await self.fs.write_file(val, payload_file,  payload_output_path)

    def convert_markdown_to_html(self, output_path):
        with open(output_path, 'r') as f:
            markdown_content = f.read()

        html_content = markdown.markdown(
            markdown_content,
            extensions=['extra', 'md_in_html', 'toc', 'fenced_code', 'codehilite']
        )

        template_path = Path("templates/html_pages")
        template_string = get_file_from_namespace_with_fallback(str(template_path), "responses_template.html")
        final_html = template_string.replace("{{content}}", html_content)

        html_output_path = output_path.replace(".md", ".html")
        with open(html_output_path, 'w') as f:
            f.write(final_html)

    async def rerun_single_event(self, event_type, ball_identifier, file_name, session_id):
        self.directory = "."

        innings = ball_identifier.split("_")[0]
        over = ball_identifier.split("_")[1]
        ball = ball_identifier.split("_")[2]
        output_path = await self.get_output_path(session_id=session_id, generate_new_id=False)
        file_contents = await self.fs.read_file(file_name=file_name, file_path=self.directory, container_name='matchfeed')


        json_object = json.loads(file_contents)
        file_data = gm.RootModel.model_validate_json(json.dumps(json_object, indent=4))
        file_data._progress = self.progress
        file_data.Revision = 'dfe19b62-07f1-4cb5-ae9a-561a253e4b04'

        self.chat_service = ChatService(
            chat_service_type="multi_agent",
            chat_history_repository=ingen_deps.get_chat_history_repository(),
            conversation_flow="ca_insights",
            config=self.config,
            revision = file_data.Revision
        )
        self.test_run_session_id = session_id

         #self.test_run_session_id
        self.chat_service.service_class.message_data = file_data

        # check if prompt folder is in local_files and if not copy the files from the template folder
        self.prompt_folder = f"prompts/{self.test_run_session_id}"
        file_check = await self.fs.list_files(file_path=f"prompts/{self.test_run_session_id}")
        if file_check is None:
            for file in os.listdir("ingenious_extensions/templates/prompts"):
                # read the file and write it to the local_files
                with open(f"ingenious_extensions/templates/prompts/{file}", "r") as f:
                    content = f.read()
                    await self.fs.write_file(content, file, self.prompt_folder)

        current_game_status = file_data.Fixture.GameStatus

        print(f"Processing {file_name} - Game Status: {current_game_status}\n")
        print(f"Processing {file_name}")
        print(f"Current Game Status: {current_game_status} - Pre Game Status: {self.past_game_status} - Ball Count: {self.ball_count}")

        balls = file_data.Get_All_Balls()
        file_data.Set_Current_Ball(balls[0])
        matched = False
        if balls:
            for b in balls:
                if b.InningsNumber == int(innings) and b.OverNumber == int(over) and b.BallNumber == int(ball):
                    self.chat_service.service_class.message_data.Set_Current_Ball(b)
                    matched = True
                    break

        if not matched:
            # Throw error
            print(f"Ball not found!. {innings}_{over}_{ball} in file {file_name}")
        val = await self.get_data_from_method_calls(file_data=file_data)

        if event_type == "is_wicket_ball":
            await self.handle_wicket_ball(
                file_name=file_name,
                json_object=file_data.model_dump(),
                output_path=output_path,
                val=val
            )

        if event_type == "score_card_insight":
            await self.handle_score_card(
                file_name=file_name,
                json_object=file_data.model_dump(),
                output_path=output_path,
                val=val
            )

        if event_type == "game_status_changed":
            await self.handle_game_status_change(
                file_name=file_name,
                json_object=file_data.model_dump(),
                output_path=output_path,
                val=val
            )

