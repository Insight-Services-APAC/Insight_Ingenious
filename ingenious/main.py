import importlib.resources as pkg_resources
import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

# Import controllers directly from bounded contexts
from ingenious.chat.interfaces.rest_controllers import router as chat_router
from ingenious.configuration.domain.models import MinimalConfig
from ingenious.configuration.interfaces.rest_controllers import (
    router as configuration_router,
)
from ingenious.diagnostics.interfaces.rest_controllers import (
    router as diagnostic_router,
)
from ingenious.external_integrations.interfaces.rest_controllers import (
    router as external_integrations_router,
)
from ingenious.file_management.interfaces.rest_controllers import (
    router as file_management_router,
)
from ingenious.prompt_management.interfaces.rest_controllers import (
    router as prompts_router,
)
from ingenious.security.interfaces.rest_controllers import router as security_router
from ingenious.shared.interfaces.rest_controllers import router as events_router

config = MinimalConfig()


# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class FastAgentAPI:
    def __init__(self, config: MinimalConfig):
        # Set the working directory
        os.chdir(os.environ["INGENIOUS_WORKING_DIR"])

        # Initialize FastAPI app
        self.app = FastAPI(title="FastAgent API", version="1.0.0")

        # Commented out for DDD migration - remove if not needed
        # import ingenious_prompt_tuner as prompt_tuner
        # self.flask_app = prompt_tuner.create_app()

        # TODO: Add CORS option to config.
        origins = [
            "http://localhost",
            "http://localhost:5173",
            "http://localhost:4173",
        ]

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Add DDD bounded context routes
        self.app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])
        self.app.include_router(
            diagnostic_router, prefix="/api/v1", tags=["Diagnostic"]
        )
        self.app.include_router(prompts_router, prefix="/api/v1", tags=["Prompts"])
        self.app.include_router(events_router, prefix="/api/v1", tags=["Events"])
        self.app.include_router(security_router, prefix="/api/v1", tags=["Security"])
        self.app.include_router(
            file_management_router, prefix="/api/v1", tags=["File Management"]
        )
        self.app.include_router(
            configuration_router, prefix="/api/v1", tags=["Configuration"]
        )
        self.app.include_router(
            external_integrations_router,
            prefix="/api/v1",
            tags=["External Integrations"],
        )

        # Add exception handler
        self.app.add_exception_handler(Exception, self.generic_exception_handler)

        # Mount ChainLit - commented out for DDD migration
        # if config.chainlit_configuration.enable:
        #     try:
        #         from chainlit.utils import mount_chainlit
        #         chainlit_path = pkg_resources.files("ingenious.chainlit") / "app.py"
        #         mount_chainlit(
        #             app=self.app, target=str(chainlit_path), path="/chainlit"
        #         )
        #     except ImportError:
        #         logger.warning("ChainLit not available, skipping mount")

        # Mount Flask App - commented out for DDD migration
        # self.app.mount("/prompt-tuner", WSGIMiddleware(self.flask_app))

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
            status_code=500, content={"detail": f"An error occurred: {str(exc)}"}
        )

    async def root(self):
        # Locate the HTML file in ingenious.api
        html_path = pkg_resources.files("ingenious.chainlit") / "index.html"
        with html_path.open("r") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
