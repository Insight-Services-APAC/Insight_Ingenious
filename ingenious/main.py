import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from chainlit.utils import mount_chainlit
from dotenv import load_dotenv
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
import logging
import ingenious.config.config as ingen_config
import importlib.resources as pkg_resources

# Import your routers
import ingenious.api.routes.chat as chat
import ingenious.api.routes.message_feedback as message_feedback

config = ingen_config.get_config(os.getenv("INGENIOUS_PROJECT_PATH", ""))
print("config.web_configuration.asynchronous", config.web_configuration.asynchronous)

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

if config.web_configuration.asynchronous:
    import ingenious_extensions.api.routes.chat_async_ca as chat_async
else:
    pass



class FastAgentAPI:
    def __init__(self, config: ingen_config.Config):
        # Set the working directory
        os.chdir(os.environ["INGENIOUS_WORKING_DIR"])

        # Initialize FastAPI app
        self.app = FastAPI(title="FastAgent API", version="1.0.0")

        # Include routers
        try:
            self.app.include_router(chat_async.router, prefix="/api/v1", tags=["ChatAsync"])
        except:
            pass
        self.app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
        self.app.include_router(message_feedback.router, prefix="/api/v1", tags=["Message Feedback"])

        # Instrument HTTPX - required for OpenAI SDK
        HTTPXClientInstrumentor().instrument()

        # Add exception handler
        self.app.add_exception_handler(Exception, self.generic_exception_handler)

        # Mount ChainLit
        if config.chainlit_configuration.enable:
            chainlit_path = pkg_resources.files("ingenious.chainlit") / "app.py"
            mount_chainlit(app=self.app, target=str(chainlit_path), path="/chainlit")

        # Redirect `/` to `/docs`
        self.app.get("/", tags=["Root"])(self.redirect_to_docs)


    async def redirect_to_docs(self):
        """Redirect the root endpoint to /docs."""
        return RedirectResponse(url="/docs")


    async def generic_exception_handler(self, request: Request, exc: Exception):
        if os.environ.get("LOADENV") == "True":
            load_dotenv()

        # Log the exception
        logger.exception(exc)

        return JSONResponse(
            status_code=500,
            content={"detail": f"An error occurred: {str(exc)}"}
        )

