import secrets
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing_extensions import Annotated
from ingenious.dependencies import get_chat_service
from ingenious.errors.content_filter_error import ContentFilterError
from ingenious.errors.token_limit_exceeded_error import TokenLimitExceededError
from ingenious.models.chat import ChatRequest
from ingenious.models.http_error import HTTPError
from ingenious.services.chat_service import ChatService
import ingenious.dependencies as igen_deps
import asyncio
import requests
import json

logger = logging.getLogger(__name__)
router = APIRouter()


def send_response(response, thread_id, api_key=None):
    """
    Sends the response to the FastAPI API endpoint with optional API key.

    Parameters:
    - response: An object containing the agent's response details.
    - thread_id: The thread ID associated with the response.
    - api_key: (Optional) API key for authentication.
    """
    # Define the API endpoint
    api_url = "http://127.0.0.1:88/api/ai-response/publish"

    try:
        agent_response = json.loads(response.agent_response)

        payload = {
            "responseId": str(thread_id),  # Use thread_id as responseId
            "response": {
                "content": agent_response.content,
                "feedId":  agent_response.feedId,
                "feedTimestamp": agent_response.feedTimestamp,
                "overBall": agent_response.overBall,
            },
            "metadata": {
                "matchId": agent_response.match_id,
                "entities": {
                    "players": agent_response.entities.players,
                    "teams": agent_response.entities.teams,
                },
            },
        }
        print("=======================================================")
        print(payload)
        print("=======================================================")
    except:
        payload = {
            "responseId": str(thread_id),  # Use thread_id as responseId
            "response": {
                "content": 'failed AI response',
                "feedId": "",
                "feedTimestamp": "",
                "overBall": "",
            },
            "metadata": {
                "matchId": "",
                "entities": {
                    "players": "",
                    "teams": "",
                },
            },
        }

    # Prepare headers
    headers = {
        "Content-Type": "application/json"
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        # Send the POST request
        response = requests.post(api_url, json=payload, headers=headers)

        # Check for successful response
        if response.status_code == 200:
            logger.info(f"Response successfully sent to API: {response.json()}")
        else:
            logger.error(
                f"Failed to send response to API. Status code: {response.status_code}, Response: {response.text}"
            )
    except Exception as e:
        logger.exception(f"Error while sending response to API: {e}")




@router.post(
    "/chat",
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
        chat_request: ChatRequest,
        chat_service: Annotated[ChatService, Depends(get_chat_service)],
        credentials: Annotated[HTTPBasicCredentials, Depends(igen_deps.get_security_service)],
):
    """
    Handles chat requests and acknowledges receipt.
    """
    try:
        # Log acknowledgment
        logger.info(f"Request received for conversation_flow: {chat_request.conversation_flow}")

        if not chat_request.conversation_flow:
            raise ValueError(f"conversation_flow not set {chat_request}")

        # Perform asynchronous processing
        async def process_chat():
            try:
                response = await chat_service.get_chat_response(chat_request)
                # Save response (placeholder logic for Cosmos DB saving)
                send_response(response, chat_request.thread_id)
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
