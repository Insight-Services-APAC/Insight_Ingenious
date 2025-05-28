"""Authentication routes and utilities for the prompt tuner."""

from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check credentials against configuration
        if (
            username == current_app.config["USERNAME"]
            and password == current_app.config["PASSWORD"]
        ):
            session["logged_in"] = True
            return redirect(url_for("index.home"))
        else:
            return "Invalid credentials", 401

    return render_template("login.html")


@bp.route("/logout")
def logout():
    """Handle user logout."""
    session.pop("logged_in", None)
    return redirect(url_for("auth.login"))
