"""
Dependency Injection Bindings for Ingenious.

This module defines the bindings between interfaces and their implementations
for the dependency injection container.
"""

from ingenious.application.repository.chat_history_repository import (
    ChatHistoryRepository,
)
from ingenious.application.repository.file_repository import FileRepository
from ingenious.application.service.chat_service import ChatService
from ingenious.application.service.message_feedback_service import (
    MessageFeedbackService,
)
from ingenious.common.di.container import get_container
from ingenious.domain.interfaces.repository.chat_history_repository import (
    IChatHistoryRepository,
)
from ingenious.domain.interfaces.repository.file_repository import IFileRepository
from ingenious.domain.interfaces.service.chat_service import IChatService
from ingenious.domain.interfaces.service.message_feedback_service import (
    IMessageFeedbackService,
)
from ingenious.domain.model.config import Config
from ingenious.domain.model.database.database_client import DatabaseClientType
from ingenious.presentation.api.managers.app_configuration_manager import (
    AppConfigurationManager,
)
from ingenious.presentation.api.managers.mountable_component_manager import (
    MountableComponentManager,
)
from ingenious.presentation.api.managers.router_manager import RouterManager


def register_bindings(config: Config) -> None:
    """
    Register all bindings with the DI container.

    Args:
        config: The application configuration
    """
    container = get_container()

    # Bind configuration
    container.bind_instance(Config, config)

    # Bind factories for repositories and services
    container.bind_factory(
        IChatHistoryRepository,
        lambda: ChatHistoryRepository(
            db_type=DatabaseClientType(config.chat_history.database_type.lower()),
            config=config,
        ),
    )

    container.bind_factory(
        IFileRepository,
        lambda Category="revisions": FileRepository(config=config, Category=Category),
    )

    container.bind_factory(
        IChatService,
        lambda conversation_flow="": ChatService(
            chat_service_type=config.chat_service.type,
            chat_history_repository=container.resolve(IChatHistoryRepository),
            conversation_flow=conversation_flow,
            config=config,
        ),
    )

    container.bind_factory(
        IMessageFeedbackService,
        lambda: MessageFeedbackService(
            chat_history_repository=container.resolve(IChatHistoryRepository)
        ),
    )

    # Bind API managers
    container.bind_factory(
        AppConfigurationManager, lambda app: AppConfigurationManager(app, config)
    )

    container.bind_factory(RouterManager, lambda app: RouterManager(app, config))

    container.bind_factory(
        MountableComponentManager, lambda app: MountableComponentManager(app, config)
    )
