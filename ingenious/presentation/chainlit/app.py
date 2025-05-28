import uuid

import chainlit as cl
import chainlit.data as cl_data
import ingenious.presentation.api.dependencies as deps
import ingenious.presentation.chainlit.datalayer as cl_data_custom
from ingenious.domain.model.chat import ChatRequest

data_layer = cl_data_custom.DataLayer()
cl_data._data_layer = data_layer


@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="classification_agent",
            markdown_description="The underlying LLM model is optimised for topic classification and memory,"
            "you can ask me question like 'Can you tell me about basketball?'",
            icon="https://picsum.photos/200",
        ),
        cl.ChatProfile(
            name="sql_manipulation_agent",
            markdown_description="The underlying LLM model is optimised for sample sql database manipulation."
            "you can ask me question like 'what are the columns?', 'can you give me the count by gender?'",
            icon="https://picsum.photos/250",
        ),
        cl.ChatProfile(
            name="web_critic_agent",
            markdown_description="The underlying LLM model is optimised for sample sql database manipulation."
            "you can ask me question like 'Write me a short story in 100 words based on the following: "
            "The Australia men's national cricket team represents "
            "Australia in men's international cricket. "
            "It is the joint oldest team in Test cricket history,"
            " playing in the first ever Test match in 1999;"
            " the team current coach is Elliot Zhu.?'",
            icon="https://picsum.photos/300",
        ),
    ]


@cl.on_message
async def main(message: cl.Message):
    chat_profile = cl.user_session.get("chat_profile")
    new_guid = uuid.uuid4()
    chat_request: ChatRequest = ChatRequest(
        thread_id="demo_" + str(new_guid),
        user_id="Demo",
        user_prompt=message.content,
        user_name="Demo",
        topic="basketball, tennis" if chat_profile == "classification_agent" else "",
        memory_record=True,
        conversation_flow=chat_profile,
    )

    cs = deps.get_chat_service(
        deps.get_chat_history_repository(),
        conversation_flow=chat_request.conversation_flow,
    )

    ret = await cs.get_chat_response(chat_request)

    await cl.Message(content=ret.agent_response).send()


# Setting starters based on selected pattern
# @cl.set_starters
# async def set_starters():
#     chat_profile = cl.user_session.get("chat_profile")
#     if chat_profile == "classification_agent":
#         return [
#             cl.Starter(
#                 label="Let's do a test.",
#                 message="Can you tell me about basketball?",
#                 icon="/public/idea.png",
#             )
#         ]
#     elif chat_profile == "sql_manipulation_agent":
#         return [
#             cl.Starter(
#                 label="Let's do a test.",
#                 message="Can I have a count of all observations by gender?",
#                 icon="/public/idea.png",
#             )
#         ]


# cl.on_chat_resume
@cl.on_chat_start
async def on_chat_start():
    print("A new chat session has started!")
    print(f"Thread ID: {cl.user_session.get('id')}")
    user: cl.User = cl.user_session.get("user")
    await data_layer.set_user(user)
    if user:
        print(f"User ID: {user.identifier}")

    # value = settings["Pattern"]


@cl.on_stop
def on_stop():
    print("The user wants to stop the task!")


@cl.on_chat_end
def on_chat_end():
    print("The user disconnected!")
