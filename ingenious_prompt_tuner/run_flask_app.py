import asyncio
import io
import os
import sys
import uuid as guid
from functools import wraps
from pathlib import Path

import yaml
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

# Set up parent directory and import dependencies
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(parent_dir)

# import ingenious_extensions.tests.flask_app_render_payload as rp1
# import ingenious_extensions.tests.run_tests as rt
import rich.progress as rp

import ingenious.dependencies as ig_deps
from ingenious.files.files_repository import FileStorage
from ingenious.utils.stage_executor import ProgressConsoleWrapper
from ingenious_prompt_tuner.templates.responses.responses import bp as responses_bp
from ingenious_prompt_tuner.utilities import utils_class

app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/static",
    template_folder="templates",
)
app.secret_key = ig_deps.config.web_configuration.authentication.password

PROMPT_TEMPLATE_FOLDER = os.path.join(
    parent_dir, "ingenious_extensions", "templates", "prompts"
)

output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
functional_test_dir = os.path.join(output_dir, "functional_test_outputs")
os.makedirs(functional_test_dir, exist_ok=True)

USERNAME = ig_deps.config.web_configuration.authentication.username
PASSWORD = ig_deps.config.web_configuration.authentication.password
PORT = ig_deps.config.web_configuration.port
HOST = ig_deps.config.web_configuration.ip_address

fs = FileStorage(config=ig_deps.config)
fs_data = FileStorage(config=ig_deps.config, Category="data")
REVISIONS_FOLDER = Path("revisions")


progress = rp.Progress()
pcw = ProgressConsoleWrapper(progress=progress, log_level="INFO")
# run_tests = rt.RunBatches(progress=pcw, task_id=1)


# Initialize utils class for full functionality
utils = utils_class(config=ig_deps.config)

# Configure app with utils and other required components
app.config["utils"] = utils
app.config["test_output_path"] = functional_test_dir
app.config["agents"] = ig_deps.config.agents
app.config["response_agent_name"] = "summary"  # Default response agent

# Register the responses blueprint for full functionality
app.register_blueprint(responses_bp)

# Make utils available to templates
app.utils = utils


# Add a context processor to make utils available in templates
@app.context_processor
def inject_utils():
    return dict(utils=utils)


# Remove unused mock function
# def mock_render_dashboard(ball_identifier, fs, output_dir, event_type):
#     return (
#         f"<h1>Mock Dashboard</h1><p>Ball ID: {ball_identifier}, Event: {event_type}</p>"
#     )


# Authentication Helpers
def check_auth(username, password):
    return username == USERNAME and password == PASSWORD


def authenticate():
    return jsonify({"status": "error", "output": "Authentication required"}), 401


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "logged_in" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


def requires_selected_revision(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        selected_revision = request.cookies.get("selected_revision")
        if not selected_revision:
            return redirect(url_for("home"))
        return f(*args, **kwargs)

    return decorated_function


def get_selected_revision_direct_call():
    selected_revision = request.cookies.get("selected_revision")
    if selected_revision:
        return selected_revision


# Routes
@app.route("/debug")
def debug():
    """Debug route to check config values"""
    return jsonify(
        {
            "username": USERNAME,
            "password": PASSWORD,
            "auth_enabled": ig_deps.config.web_configuration.authentication.enable,
        }
    )


@app.route("/sync_prompts", methods=["POST"])
@requires_auth
def sync_prompts():
    """Stub route for sync prompts functionality"""
    return jsonify(
        {
            "status": "success",
            "message": "Sync prompts functionality not implemented yet",
        }
    )


@app.route("/sync_sample_data", methods=["POST"])
@requires_auth
def sync_sample_data():
    """Stub route for sync sample data functionality"""
    return jsonify(
        {
            "status": "success",
            "message": "Sync sample data functionality not implemented yet",
        }
    )


@app.route("/set_selected_revision", methods=["GET"])
@requires_auth
def set_selected_revision():
    """Set the selected revision using cookies"""
    revision_id = request.args.get("revision_id")
    if revision_id:
        response = jsonify(
            {"status": "success", "message": f"Selected revision: {revision_id}"}
        )
        response.set_cookie("selected_revision", revision_id)
        return response
    else:
        return jsonify({"status": "error", "message": "No revision ID provided"}), 400


@app.route("/health")
def health_check():
    """Simple health check route without any file operations"""
    return jsonify({"status": "healthy", "message": "Flask app is running"})


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if check_auth(username, password):
            session["logged_in"] = True
            return redirect(url_for("home"))
        else:
            return "Invalid credentials", 401
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))


@app.route("/")
@requires_auth
def home():
    # Simplified home route - avoid slow async operations for now
    try:
        revisions_path = REVISIONS_FOLDER / "revisions.yml"
        if revisions_path.exists():
            with open(revisions_path, "r") as f:
                revisions = yaml.safe_load(f) or []
        else:
            revisions = []
    except Exception:
        # If there are any file issues, just show empty revisions
        revisions = []

    return render_template("home.html", files=revisions)


@app.route("/create_revision", methods=["GET", "POST"])
@requires_auth
def create_revision():
    if request.method == "POST":
        revision_name = str(guid.uuid4())  # Auto-generate revision name
        revision_description = request.form["revision_description"]
        new_revision = {"name": revision_name, "description": revision_description}

        # Simplified file operations
        revisions_file = REVISIONS_FOLDER / "revisions.yml"

        try:
            if revisions_file.exists():
                with open(revisions_file, "r") as f:
                    revisions = yaml.safe_load(f) or []
            else:
                revisions = []

            revisions.append(new_revision)

            # Ensure the directory exists
            REVISIONS_FOLDER.mkdir(parents=True, exist_ok=True)

            with open(revisions_file, "w") as f:
                yaml.safe_dump(revisions, f)

        except Exception as e:
            print(f"Error saving revision: {e}")
            # Continue anyway for now

        return redirect(url_for("home"))
    return render_template("revisions/create_revision.html")


@app.route("/save_revision", methods=["POST"])
@requires_auth
def save_revision():
    revision_name = str(guid.uuid4())
    revision_description = request.form["revision_description"]
    new_revision = {"name": revision_name, "description": revision_description}

    if asyncio.run(
        fs.check_if_file_exists(
            file_name="revisions.yml", file_path=str(REVISIONS_FOLDER)
        )
    ):
        revisions_str = asyncio.run(
            fs.read_file(file_name="revisions.yml", file_path=str(REVISIONS_FOLDER))
        )
        revisions = yaml.safe_load(revisions_str)
    else:
        revisions = []

    revisions.append(new_revision)
    revisions_str = yaml.safe_dump(revisions)
    asyncio.run(
        fs.write_file(
            contents=revisions_str,
            file_name="revisions.yml",
            file_path=str(REVISIONS_FOLDER),
        )
    )
    prompts = asyncio.run(
        fs.list_files(f"prompts/{get_selected_revision_direct_call()}")
    )
    function_test_outputs = asyncio.run(
        fs.list_files(f"functional_test_outputs/{get_selected_revision_direct_call()}")
    )

    for prompt in prompts:
        content = asyncio.run(
            fs.read_file(
                file_name=prompt,
                file_path=f"prompts/{get_selected_revision_direct_call()}",
            )
        )
        asyncio.run(
            fs.write_file(
                file_name=prompt, file_path=f"prompts/{revision_name}", contents=content
            )
        )

    for function_test_output in function_test_outputs:
        content = asyncio.run(
            fs.read_file(
                file_name=function_test_output,
                file_path=f"functional_test_outputs/{get_selected_revision_direct_call()}",
            )
        )
        asyncio.run(
            fs.write_file(
                file_name=function_test_output,
                file_path=f"functional_test_outputs/{revision_name}",
                contents=content,
            )
        )

    return redirect(url_for("home"))


@app.route("/get_selected_revision", methods=["GET"])
@requires_auth
def get_selected_revision():
    selected_revision = request.cookies.get("selected_revision")
    return jsonify({"selected_revision": selected_revision})


@app.route("/edit_markdown")
@requires_auth
@requires_selected_revision
def edit_markdown():
    # Simplified - just return empty files list for now
    # In a real implementation, this would list files in the revision's prompt folder
    files = []
    return render_template("edit_markdown.html", files=files)


@app.route("/view_responses")
@requires_auth
@requires_selected_revision
def view_responses():
    # Use the full template with real functionality
    prompt_template_folder = asyncio.run(utils.get_prompt_template_folder())
    base_path = asyncio.run(utils.fs.get_base_path()) / Path(prompt_template_folder)
    data_folder = asyncio.run(utils.get_data_folder())
    data_base_path = asyncio.run(utils.fs_data.get_base_path()) / Path(data_folder)
    return render_template(
        "responses/view_responses.html",
        data_template_folder=data_base_path,
        prompt_template_folder=base_path,
    )


# Remove this route as it's now handled by the responses blueprint
# @app.route("/get_test_data_files", methods=["GET"])
# @requires_auth
# @requires_selected_revision
# def get_test_data_files():
#     # This functionality is now handled by the responses blueprint


# Remove this route as it's now handled by the responses blueprint
# @app.route("/get_payload", methods=["GET"])
# @requires_auth
# @requires_selected_revision
# def get_payload():
#     # This functionality is now handled by the responses blueprint


# Remove this route as it's now handled by the responses blueprint
# @app.route("/rerun_event", methods=["GET"])
# @requires_auth
# @requires_selected_revision
# def rerun_event():
#     # This functionality is now handled by the responses blueprint


# Remove this route as it's now handled by the responses blueprint
# @app.route("/get_agent_response", methods=["GET"])
# @requires_auth
# @requires_selected_revision
# def get_agent_response():
#     # This functionality is now handled by the responses blueprint


# Remove this route as it's now handled by the responses blueprint
# @app.route("/get_responses", methods=["GET"])
# @requires_auth
# @requires_selected_revision
# def get_responses():
#     # This functionality is now handled by the responses blueprint


# Remove this route as it's now handled by the responses blueprint
# @app.route("/get_agent_response_from_file", methods=["post"])
# @requires_auth
# @requires_selected_revision
# def get_agent_response_from_file():
#     # This functionality is now handled by the responses blueprint


# Remove this route as it's now handled by the responses blueprint
# @app.route("/get_responses1", methods=["GET"])
# @requires_auth
# @requires_selected_revision
# def get_responses1():
#     # This functionality is now handled by the responses blueprint


# Keep this route for backward compatibility
@app.route("/download_responses", methods=["GET"])
@requires_auth
@requires_selected_revision
def download_responses():
    try:
        latest_folder = max(
            [
                os.path.join(functional_test_dir, d)
                for d in os.listdir(functional_test_dir)
            ],
            key=os.path.getmtime,
        )
        RESPONSES_FILE = os.path.join(latest_folder, "responses.html")

        if os.path.exists(RESPONSES_FILE):
            with open(RESPONSES_FILE, "r", encoding="utf-8") as rf:
                file_contents = rf.read()
            return send_file(
                io.BytesIO(file_contents.encode("utf-8")),
                as_attachment=True,
                download_name="responses.html",
                mimetype="text/html",
            )
    except ValueError:
        pass
    return jsonify({"status": "error", "output": "Responses file not found"}), 404


# Remove this route as it's now handled by the responses blueprint
# @app.route("/run_live_progress", methods=["GET"])
# @requires_auth
# @requires_selected_revision
# def run_live_progress():
#     # This functionality is now handled by the responses blueprint


# Keep this route for backward compatibility
@app.route("/run_simple_tests", methods=["POST"])
@requires_auth
@requires_selected_revision
def run_simple_tests():
    try:
        import subprocess

        result = subprocess.run(
            ["ingen", "run-test-batch"], capture_output=True, text=True, check=False
        )
        status = "success" if result.returncode == 0 else "error"
        return jsonify({"status": status, "output": result.stdout or result.stderr})
    except Exception as e:
        return jsonify({"status": "error", "output": str(e)})


@app.route("/edit/<filename>", methods=["GET", "POST"])
@requires_auth
@requires_selected_revision
def edit_file(filename):
    # Simplified file editing - create files in a prompts directory per revision
    selected_revision = get_selected_revision_direct_call()
    if not selected_revision:
        return redirect(url_for("home"))

    # Create revision-specific prompts directory
    prompts_dir = Path("prompts") / selected_revision
    prompts_dir.mkdir(parents=True, exist_ok=True)
    file_path = prompts_dir / filename

    if request.method == "POST":
        new_content = request.form.get("file_content", "")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
        except Exception as e:
            print(f"Error saving file: {e}")
        return redirect(url_for("home"))
    else:
        # Read existing content or create empty file
        try:
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            else:
                content = "# New prompt file\n\n"
        except Exception as e:
            print(f"Error reading file: {e}")
            content = "# New prompt file\n\n"

        return render_template(
            "prompts/edit_prompt.html", filename=filename, content=content
        )


if __name__ == "__main__":
    app.run(debug=True, host=HOST, port=PORT)
