import asyncio
import json
import logging
import os

import requests
from fastapi import APIRouter, HTTPException

import ingenious.config.config as ingen_config
from ingenious.errors.content_filter_error import ContentFilterError
from ingenious.errors.token_limit_exceeded_error import TokenLimitExceededError
from ingenious.models.http_error import HTTPError


import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../..'))
sys.path.append(parent_dir)
print("parent_dir:", parent_dir)


config = ingen_config.get_config(os.getenv("INGENIOUS_PROJECT_PATH", ""))
logger = logging.getLogger(__name__)
router = APIRouter()

import ingenious.run_tests as rt
import rich.progress as rp
from ingenious.utils.stage_executor import ProgressConsoleWrapper



def send_response(response, thread_id):
    """
    Sends the response to the FastAPI API endpoint with optional API key.

    Parameters:
    - response: An object containing the agent's response details.
    - thread_id: The thread ID associated with the response.
    - api_key: (Optional) API key for authentication.
    """
    api_url = config.receiver_configuration.api_url
    headers = {
        "X-API-Key": config.receiver_configuration.api_key,
        "Content-Type": "application/json",
    }

    try:
        payload = json.loads(response)
        payload["response_id"] = thread_id
        res = json.loads(payload["response"]["content"])
        if 'Summarizer' in res[-1]['chat_title']:
            payload["response"]["content"] = res[-1]['chat_response']
        else:
            payload = {
                "response_id": thread_id,
                "error_flag": True,
                "error_detail": "Error when processing request, AI does not return a summary."
            }

        if not payload["response"]["content"]:
            payload = {
                "response_id":thread_id,
                "error_flag": True,
                "error_detail": "Error when processing request, AI cannot identify event type."
            }
    except Exception as e:
        logger.exception(f"Error while sending response to API: {e}")
        payload = {
            "response_id": thread_id,
            "error_flag": True,
            "error_detail": f"Error while sending response to API: {e}"
        }

    response = requests.post(api_url, json = payload, headers=headers)

    if response.status_code == 200:
        logger.info("Response successfully sent to API.")
    else:
        logger.error(
            f"Failed to send response to API. Status code: {response.status_code}"
        )


@router.post(
    "/chat_async",
    responses={
        200: {"description": "Request Received"},
        400: {"model": HTTPError, "description": "Bad Request"},
        406: {"model": HTTPError, "description": "Not Acceptable"},
        413: {"model": HTTPError, "description": "Payload Too Large"},
        500: {"model": HTTPError, "description": "Internal Server Error"},
    },
    status_code=200,  # Default response status for acknowledgment
)
async def chat(
    pay_load_dict: dict,
    #chat_request: ChatRequest,
    #credentials: Annotated[HTTPBasicCredentials, Depends(igen_deps.get_security_service)],
):
    """
    Handles chat requests and acknowledges receipt.
    """
    try:
        # Log acknowledgment
        # pay_load_dict = json.loads(pay_load)
        if not pay_load_dict.get("File_Name", None):
            raise ValueError(f"No File Name provided in request.")
        else:
            logger.info(f"Request received for conversation_flow: {pay_load_dict.get('Thread_Id', 'no_thread_id')}.")


        # Perform asynchronous processing
        async def process_chat():
            try:
                progress = rp.Progress()
                pcw = ProgressConsoleWrapper(progress=progress, log_level='INFO')
                run_tests = rt.RunBatches(progress=pcw, task_id=1)

                event_type = pay_load_dict.get('Event_Type')
                ball_identifier = pay_load_dict.get('Ball_Identifier')
                file_name = pay_load_dict.get('File_Name')
                session_id = pay_load_dict.get('Thread_Id')
                #Blob_Url = pay_load_dict.get('Blob_Url')
                #file_contents = await run_tests.fs.read_file(file_name=file_name, file_path=run_tests.directory)

                await run_tests.rerun_single_event(event_type, ball_identifier, file_name, session_id)


                send_response(run_tests.chat_response_object, session_id)

            except Exception as e:
                logger.exception(f"Error processing chat: {e}")

        # Schedule the processing task
        asyncio.create_task(process_chat())

        # Return acknowledgment immediately
        return {"message": "Request received and processing"}

    except ValueError as e:
        logger.exception(e)
        raise HTTPException(status_code=400, detail=str(e))
    except ContentFilterError as cfe:
        logger.exception(cfe)
        raise HTTPException(status_code=406, detail=ContentFilterError.DEFAULT_MESSAGE)
    except TokenLimitExceededError as tle:
        logger.exception(tle)
        raise HTTPException(status_code=413, detail=TokenLimitExceededError.DEFAULT_MESSAGE)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))
