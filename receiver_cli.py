import typer
from typing_extensions import Annotated
from rich.console import Console
from rich.theme import Theme
from rich import print
import uvicorn
from fastapi import FastAPI, Request
import json

# Initialize CLI app
app = typer.Typer(no_args_is_help=True)

# Define custom themes
custom_theme = Theme(
    {"info": "dim cyan", "warning": "dark_orange", "danger": "bold red", "error": "bold red", "debug": "khaki1"}
)
console = Console(theme=custom_theme)

# FastAPI app initialization
fast_api_app = FastAPI()

# Add a landing route
@fast_api_app.get("/")
async def landing():
    return {"message": "Welcome to the AI Response API! Visit /docs for API documentation."}

# Add a route to handle AI response publishing
@fast_api_app.post("/api/ai-response/publish")
async def publish_response(request: Request):
    try:
        payload = await request.json()  # Parse the incoming JSON payload
        # Log payload for debugging
        console.print(f"Payload received: {json.dumps(payload, indent=4)}", style="debug")
        return {"message": "Response received successfully", "data": payload}
    except Exception as e:
        console.print(f"Error processing request: {str(e)}", style="error")
        return {"message": "Failed to process the response", "error": str(e)}

# CLI command to run the FastAPI server
@app.command()
def run_all(
    host: Annotated[
        str,
        typer.Argument(
            help="The host to run the server on. Default is 0.0.0.0. For local development outside of Docker, use 127.0.0.1."
        ),
    ] = "0.0.0.0",
    port: Annotated[
        int,
        typer.Argument(help="The port to run the server on. Default is 88."),
    ] = 88,
):
    # Run FastAPI with Uvicorn
    console.print(f"Running FastAPI server on {host}:{port}", style="info")
    uvicorn.run(fast_api_app, host=host, port=port)


if __name__ == "__main__":
    app()
