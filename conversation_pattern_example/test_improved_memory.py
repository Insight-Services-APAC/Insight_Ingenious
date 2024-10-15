import os
import sys
import uuid

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), './../../'))
sys.path.append(parent_dir)

import ingenious.dependencies as deps
from ingenious.models.chat import ChatRequest, ChatResponse
import asyncio
import ingenious.config.config as config

#Classification agent with improved memory using RAG user proxy.
async def process_message(chat_request: ChatRequest) -> ChatResponse:

    user = await deps.get_chat_history_repository().get_user(chat_request.user_name)
    #chat_request.user_id = str(user.id)

    print("user_id:", chat_request.user_id)
    print("user:",user)

    cs = deps.get_chat_service(
            deps.get_chat_history_repository(),
            conversation_flow=chat_request.conversation_flow
    )

    res = await cs.get_chat_response(chat_request)
    return res


_config = config.get_config()
memory_path = _config.chat_history.memory_path
with open(f"{memory_path}/context.md", "w") as memory_file:
    memory_file.write("new conversation, please derive context from question")

new_guid = uuid.uuid4()
chat_request: ChatRequest = ChatRequest(
        thread_id=str(new_guid),
        user_id="elliot",
        user_prompt="",
        user_name="elliot",
        topic=None,
        conversation_flow="classification_agent"
    )


t = "tennis"
chat_request.user_prompt = f"What is grand slam in {t}?" #if I change this question to things other than grand slams it works.
res: ChatResponse = asyncio.run(process_message(chat_request=chat_request))

chat_request.user_prompt = f"Who are the most celebrated stars?"
res = asyncio.run(process_message(chat_request=chat_request))


print(res)
