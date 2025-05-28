"""Home routes for the prompt tuner application."""

import asyncio
import uuid as guid

import yaml
from flask import (
    Blueprint,
    current_app,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)

from ingenious_prompt_tuner.utilities import (
    get_selected_revision,
    requires_auth,
)

bp = Blueprint("index", __name__)


@bp.route("/")
@requires_auth
def home():
    """Home page route that displays revisions."""
    file_service = current_app.file_service
    revisions = {}

    # Load revisions from file if it exists
    revisions_path = current_app.config["REVISIONS_FOLDER"]
    try:
        if asyncio.run(
            file_service.check_if_file_exists(
                file_name="revisions.yml",
                file_path=str(revisions_path),
            )
        ):
            revisions_str = asyncio.run(
                file_service.read_file(
                    file_name="revisions.yml",
                    file_path=str(revisions_path),
                )
            )
            revisions = yaml.safe_load(revisions_str)
    except Exception as e:
        print(f"Error loading revisions: {e}")

    selected_revision = get_selected_revision()
    return render_template(
        "home.html", revisions=revisions or {}, selected_revision=selected_revision
    )


@bp.route("/create_revision", methods=["POST"])
@requires_auth
def create_revision():
    """Create a new revision."""
    if request.method == "POST":
        revision_id = str(guid.uuid4())
        revision_description = request.form.get("revision_description", "")

        file_service = current_app.file_service
        revisions_path = current_app.config["REVISIONS_FOLDER"]

        # Load existing revisions or create empty dict
        revisions = {}
        try:
            if asyncio.run(
                file_service.check_if_file_exists(
                    file_name="revisions.yml",
                    file_path=str(revisions_path),
                )
            ):
                revisions_str = asyncio.run(
                    file_service.read_file(
                        file_name="revisions.yml",
                        file_path=str(revisions_path),
                    )
                )
                revisions = yaml.safe_load(revisions_str) or {}
        except Exception as e:
            print(f"Error loading revisions: {e}")

        # Add new revision
        revisions[revision_id] = revision_description

        # Save updated revisions
        try:
            asyncio.run(
                file_service.write_file(
                    file_name="revisions.yml",
                    file_path=str(revisions_path),
                    content=yaml.dump(revisions),
                )
            )
        except Exception as e:
            print(f"Error saving revisions: {e}")
            return jsonify({"error": str(e)}), 500

        # Set the new revision as selected
        response = make_response(redirect(url_for("index.home")))
        response.set_cookie("selected_revision", revision_id)
        return response

    return redirect(url_for("index.home"))


@bp.route("/select_revision/<revision_id>")
@requires_auth
def select_revision(revision_id):
    """Select a revision to work with."""
    response = make_response(redirect(url_for("index.home")))
    response.set_cookie("selected_revision", revision_id)
    return response
