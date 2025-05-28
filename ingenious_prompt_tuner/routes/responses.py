"""Routes for managing prompt responses and test results."""

import asyncio
import json
import os

from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    render_template,
    request,
    stream_with_context,
)

from ingenious_prompt_tuner.utilities import (
    get_selected_revision,
    requires_auth,
    requires_selected_revision,
)

bp = Blueprint("responses", __name__, url_prefix="/responses")


@bp.route("/view/<event_file>")
@requires_auth
@requires_selected_revision
def view_response(event_file):
    """View a specific test response."""
    selected_revision = get_selected_revision()
    file_service = current_app.file_service
    event_service = current_app.event_service

    # Get the test data folder for the selected revision
    test_folder = asyncio.run(file_service.ensure_test_data(selected_revision))

    # Load the event data
    event_data = asyncio.run(
        event_service.load_event_data(
            file_name=event_file,
            file_path=test_folder,
        )
    )

    return render_template(
        "responses/view.html",
        event_file=event_file,
        event_data=event_data,
        selected_revision=selected_revision,
    )


@bp.route("/test", methods=["POST"])
@requires_auth
@requires_selected_revision
def test_prompt():
    """Test a prompt with event data."""
    data = request.get_json()
    prompt_template = data.get("prompt_template")
    event_data = data.get("event_data", {})

    selected_revision = get_selected_revision()
    event_service = current_app.event_service

    # Create a chat request
    chat_request = event_service.prepare_chat_request(
        json_object=event_data,
        identifier=f"test-{selected_revision}",
        prompt_template_name=prompt_template,
    )

    # Process the request (in a real implementation, this would call the AI service)
    # For now, we'll just return a mock response
    def generate_response():
        yield json.dumps({"status": "processing", "message": "Processing request..."})
        import time

        time.sleep(1)  # Simulate processing time
        yield json.dumps(
            {
                "status": "complete",
                "message": "Response generated",
                "response": {
                    "text": f"This is a test response for prompt template: {prompt_template}",
                    "prompt": chat_request.prompt_template_input,
                },
            }
        )

    return Response(
        stream_with_context(generate_response()), content_type="application/json"
    )


@bp.route("/save", methods=["POST"])
@requires_auth
@requires_selected_revision
def save_response():
    """Save a test response."""
    data = request.get_json()
    response_data = data.get("response", {})
    file_name = data.get("file_name", f"response-{os.urandom(4).hex()}.json")

    # Ensure .json extension
    if not file_name.endswith(".json"):
        file_name += ".json"

    selected_revision = get_selected_revision()
    file_service = current_app.file_service

    # Get the test data folder for the selected revision
    test_folder = asyncio.run(file_service.ensure_test_data(selected_revision))

    # Save the response
    success = asyncio.run(
        file_service.write_file(
            file_name=file_name,
            file_path=test_folder,
            content=json.dumps(response_data, indent=2),
        )
    )

    return jsonify({"success": success, "file_name": file_name})
