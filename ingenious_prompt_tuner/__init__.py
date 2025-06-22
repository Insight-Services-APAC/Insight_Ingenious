import asyncio
import os
import sys

from ingenious.models.test_data import Events
from flask import Flask
from functools import wraps
from pathlib import Path
from ingenious.utils.namespace_utils import import_class_with_fallback, get_path_from_namespace_with_fallback
from ingenious.models.agent import Agent, AgentChats, Agents, IProjectAgents


# Get the current working directory
current_dir = os.path.abspath(os.getcwd())

# Add the current working directory to sys.path if it doesn't exist
if current_dir not in sys.path:
    print(f"Adding {current_dir} to sys.path")
    sys.path.append(current_dir)

import ingenious_prompt_tuner.utilities as uti
import ingenious.dependencies as ig_deps
from ingenious_prompt_tuner.templates.responses import responses
from ingenious_prompt_tuner.templates import home
from ingenious_prompt_tuner.templates.prompts import prompts
from ingenious_prompt_tuner import auth

config = ig_deps.get_config()


def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app = Flask(
        __name__,
        static_folder="static",
        static_url_path="/static",
        template_folder="templates",
    )

    app.secret_key = config.web_configuration.authentication.password
    app.config["username"] = config.web_configuration.authentication.username
    app.config["password"] = config.web_configuration.authentication.password
    app.config["revisions_folder"] = str(Path("revisions"))

    # Set utils so that downstream blueprints have access to the config
    app.utils = uti.utils_class(config)
    
    # Get the list of agents -- note this should preference the Agents class in the project level extensions dir
    # Note the Agents module and ProjectAgents class must be defined in the project level extensions dir
    agents_class: IProjectAgents = import_class_with_fallback('models.agent', "ProjectAgents")
    agents_instance = agents_class(config, ig_deps.get_chat_history_repository())
    agents_class: Agents = agents_instance.Get_Project_Agents(config)

    agents = agents_class.get_agents()
    app.config["agents"] = agents_class
    
    if config.file_storage.data.add_sub_folders:
        app.config["events_path"] = str(Path("functional_test_outputs"))
    else:
        app.config["events_path"] = str(Path("./"))
    
    app.config["test_output_path"] = str(Path("functional_test_outputs"))   

    app.config["response_agent_name"] = None
    for agent in agents:
        agent: Agent = agent  # type hinting
        if agent.return_in_response:
            app.config["response_agent_name"] = agent.agent_name
    
    if app.config["response_agent_name"] is None:
        raise ValueError("Response agent not found in agents list. You must set one agent to return in response.")
        
    # ensure the instance folder exists
    try:
        # os.makedirs(app.instance_path)
        print(app.instance_path)
    except OSError:
        pass

    app.register_blueprint(auth.bp)
    app.register_blueprint(home.bp)
    app.register_blueprint(prompts.bp)
    app.register_blueprint(responses.bp)

    return app
