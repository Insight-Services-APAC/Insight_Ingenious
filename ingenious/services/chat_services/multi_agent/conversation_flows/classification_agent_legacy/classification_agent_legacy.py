import autogen.retrieve_utils
import autogen.runtime_logging
import autogen
import ingenious.config.config as config
import ingenious.dependencies as deps
from ingenious.services.chat_services.multi_agent.agent_factory_legacy import AgentFactory
from ingenious.models.chat import Action, ChatRequest, ChatResponse, KnowledgeBaseLink, Product
from ingenious.services.chat_services.multi_agent.agent_factory_legacy import ToolFunctions
import json


class ConversationFlow:
    @staticmethod
    async def get_conversation_response(message: str, topics: list = [], thread_memory: str='', memory_record_switch=True, thread_chat_history: list[str, str] = []):
        _config = config.get_config()
               
        llm_config = _config.models[0].__dict__

        chat_history_json = json.dumps(thread_chat_history)

        agent_fac = AgentFactory()

        agent_fac.add_agent(agent=autogen.ConversableAgent(
            name="Reporter",
            system_message="""
            You are responsible for generating the final summary based on the user's preference. 
            If the user requests a diagram, you **must** use Mermaid syntax and return it in a code block. Plain text should **not** be used for diagrams under any circumstances.

            Key Guidelines:
            1. When diagrams, graphs, or charts are requested, return them as Mermaid diagrams inside a code block.
            2. Ensure the Mermaid syntax is correct and that the diagram accurately represents the requested data.
            3. Default to Markdown for tables, lists, and text unless the user explicitly requests a visual representation that requires a Mermaid diagram.
            4. **Do not use plain text** for diagramming. Always use Mermaid syntax for visual elements.

            Attached is the chat history context: {chat_history_json}.
         """,
            llm_config=llm_config,
        ))

        agent_fac.add_agent(agent=autogen.ConversableAgent(
            name="Summarizer",
            system_message="""
            Your role is to provide succinct summaries while respecting the user's preferred format for the final output.
            If the user requires a diagram or chart, you **must** use Mermaid syntax to create it, enclosed in a code block. Plain text should **not** be used for diagrams.

            Instructions:
            1. Use Mermaid diagrams when diagrams are required and enclose them in a code block.
            2. Ensure tables, lists, and text are returned as regular Markdown unless the user specifies otherwise.
            3. **Avoid using plain text for diagrams.** Always use Mermaid syntax.
            4. Always validate if the final output matches the user's preference before submitting.

            Attached is the chat history context: {chat_history_json}.
            """,
            llm_config=llm_config
        ))

        agent_fac.add_agent(agent=autogen.ConversableAgent(
            name="DocumentAgent",
            system_message="""
            You talk about unstructured document data for Client A. 
            index_name parameter for tool searchtool is always 'document-search'. 
            result_attribute parameter for tool searchtool is always 'chunk'.
            If there are no results, or the results aren't relevant to the question (i.e asking about a specific, event, incident, etc), return 'No relating documents found'.
            Chat history context: """
              + chat_history_json,
            llm_config=llm_config
        ))

        agent_fac.add_agent(agent=autogen.ConversableAgent(
            name="IncidentAgent",
            system_message="You talk about incident related data for Client A. index_name parameter for tool searchtool is always 'nested-json-index'. result_attribute parameter for tool searchtool is always 'content'. Chat history context : " + chat_history_json,
            llm_config=llm_config
        ))

        agent_fac.add_agent(agent=autogen.ConversableAgent(
            name="ControlManagementAgent",
            system_message="You talk about control management related data for Client A. index_name parameter for tool searchtool is always 'nested-json-cma-index'. result_attribute parameter for tool searchtool is always 'content'. Chat history context : " + chat_history_json,
            llm_config=llm_config

        ))

        agent_fac.add_agent(agent=autogen.ConversableAgent(
            name="Classifier",
            system_message="You analyse a message and chat history to determine if there is a topic about incidents or control management. If it is about incidents you simply return the word 'incidents' as a single word else if it is about control management you simply return the word 'controlmanagement' as a single word else return 'neither'. Take the chat history context into account if there is any: " + chat_history_json,
            llm_config=llm_config
        ))

        agent_fac.get_agent_by_name("DocumentAgent").register_for_llm(name="searchtool", description="A simple tool to search for additional content")(ToolFunctions.aisearch)
        agent_fac.get_agent_by_name("IncidentAgent").register_for_llm(name="searchtool", description="A simple tool to search for additional content")(ToolFunctions.aisearch)
        agent_fac.get_agent_by_name("ControlManagementAgent").register_for_llm(name="searchtool", description="A simple tool to search for additional content")(ToolFunctions.aisearch)
        agent_fac.get_agent_by_name("Reporter").register_for_execution(name="searchtool")(ToolFunctions.aisearch)
        agent_fac.get_agent_by_name("Summarizer").register_for_execution(name="searchtool")(ToolFunctions.aisearch)


        # always start by running the DocumentAgent
        chat_responses: list[ChatResponse] = []

        doc_res = agent_fac.get_agent_by_name("Reporter").initiate_chat(
                                                    agent_fac.get_agent_by_name("DocumentAgent"), 
                                                        clear_history=False, 
                                                        message=message, 
                                                        max_turns=2, 
                                                        summary_method="last_msg"
                                                    )
        chat_responses.append(doc_res)


        # run the classification step
        msg = "Classify this message:"
        msg = msg + str(message)
        msg = msg + "\nTake the chat history into context if there is any: " + chat_history_json
        class_res = agent_fac.get_agent_by_name("Reporter").initiate_chat(
                                                        agent_fac.get_agent_by_name("Classifier"), 
                                                        clear_history=False, 
                                                        message=msg, 
                                                        max_turns=1, 
                                                        summary_method="last_msg"
                                                        )
        
        topic = str(class_res.chat_history[1]["content"]).lower()

        if topic != "neither":
                # return "The message is not related to the topics of the agents."
            question_agent = agent_fac.get_agent_by_name("Summarizer")
            answer_agent =  agent_fac.get_agent_by_name("IncidentAgent") if topic == "incidents" else agent_fac.get_agent_by_name("ControlManagementAgent")

            chat_response = await question_agent.a_initiate_chat(
                answer_agent,
                max_turns=2,
                clear_history=False,
                message=message,
                summary_method="last_msg"
            )

            chat_responses.append(chat_response)

        # Summarize the final results using the Reporter agent
        msg = "Summarize this conversation to be displayed to the user:"
        for r in chat_responses:
            msg = msg + "\n" + r.summary

        # Summarize the final conversation using the Summarizer and Reporter agents
        res = agent_fac.get_agent_by_name("Reporter").initiate_chat(
                                                            agent_fac.get_agent_by_name("Summarizer"), 
                                                            clear_history=False, 
                                                            message=msg, 
                                                            max_turns=1, 
                                                            summary_method="last_msg"
                                                        )

        # Send a response back to the user
        return res.summary


