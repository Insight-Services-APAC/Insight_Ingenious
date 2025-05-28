"""Routes for managing prompt templates."""

import asyncio

from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request,
)

from ingenious_prompt_tuner.utilities import (
    get_selected_revision,
    requires_auth,
    requires_selected_revision,
)

bp = Blueprint("prompts", __name__, url_prefix="/prompts")


@bp.route("/<template_name>")
@requires_auth
@requires_selected_revision
def view_prompt(template_name):
    """View a specific prompt template."""
    selected_revision = get_selected_revision()
    file_service = current_app.file_service

    # Get the prompt template folder for the selected revision
    template_folder = asyncio.run(
        file_service.ensure_prompt_templates(selected_revision)
    )

    # Read the template file
    template_content = asyncio.run(
        file_service.read_file(
            file_name=template_name,
            file_path=template_folder,
        )
    )

    return render_template(
        "prompts/view.html",
        template_name=template_name,
        template_content=template_content,
        selected_revision=selected_revision,
    )


@bp.route("/create", methods=["GET", "POST"])
@requires_auth
@requires_selected_revision
def create_prompt():
    """Create a new prompt template."""
    selected_revision = get_selected_revision()
    file_service = current_app.file_service

    # Get the prompt template folder for the selected revision
    template_folder = asyncio.run(
        file_service.ensure_prompt_templates(selected_revision)
    )

    if request.method == "POST":
        # Create a new template
        template_name = request.form.get("template_name", "")
        template_content = request.form.get("template_content", "")

        # Ensure .jinja extension
        if not template_name.endswith(".jinja"):
            template_name += ".jinja"

        success = asyncio.run(
            file_service.write_file(
                file_name=template_name,
                file_path=template_folder,
                content=template_content,
            )
        )
        return jsonify({"success": success, "template_name": template_name})

    return render_template(
        "prompts/create.html",
        selected_revision=selected_revision,
    )
