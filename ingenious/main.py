import os
from fastapi import FastAPI, Request, HTTPException, Header, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from chainlit.utils import mount_chainlit
from dotenv import load_dotenv
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
import logging
import ingenious.config.config as Config
import ingenious.api.routes.message_feedback as message_feedback
import importlib.resources as pkg_resources

# Import your routers
config = Config.get_config(os.getenv("INGENIOUS_PROJECT_PATH", ""))
print("config.web_configuration.asynchronous", config.web_configuration.asynchronous)
if config.web_configuration.asynchronous:
    import ingenious.api.routes.chat_async as chat
else:
    import ingenious.api.routes.chat as chat

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


# def verify_api_key(x_api_key: str = Header(...)):
#     expected_key = os.environ.get("CLI_API_KEY")
#     if not expected_key or x_api_key != expected_key:
#         raise HTTPException(status_code=403, detail="Invalid API Key")

class FastAgentAPI:
    def __init__(self, config: Config.Config):
        # Set the working directory
        os.chdir(os.environ["INGENIOUS_WORKING_DIR"])

        # Initialize FastAPI app
        self.app = FastAPI(title="FastAgent API", version="1.0.0")

        # Include routers
        self.app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
        self.app.include_router(message_feedback.router, prefix="/api/v1", tags=["Message Feedback"])

        # Instrument HTTPX - required for OpenAI SDK
        # https://github.com/open-telemetry/opentelemetry-python/issues/3693#issuecomment-2014923261
        HTTPXClientInstrumentor().instrument()

        # Add exception handler
        self.app.add_exception_handler(Exception, self.generic_exception_handler)

        # Add root endpoint
        self.app.get("/", tags=["Root"])(self.root)


    async def generic_exception_handler(self, request: Request, exc: Exception):
        if os.environ.get("LOADENV") == "True":
            load_dotenv()

        # Log the exception
        logger.exception(exc)

        return JSONResponse(
            status_code=500,
            content={"detail": f"An error occurred: {str(exc)}"}
        )

    async def root(self):
        # Locate the HTML file in ingenious.api
        html_path = pkg_resources.files("ingenious.api") / "index.html"
        with html_path.open("r") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
