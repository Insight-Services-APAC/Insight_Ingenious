"""
Azure Blob Storage service implementation for storing ensemble conversations and results.

This module provides integration with Azure Blob Storage for persisting
prompt ensemble executions, results, and conversation histories.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.blob import BlobServiceClient

from ingenious.prompt_management.domain.ensemble import (
    EnsembleConfiguration,
    EnsembleExecution,
    EnsembleResult,
)

logger = logging.getLogger(__name__)


class AzureBlobStorageService:
    """Service for managing ensemble data in Azure Blob Storage."""

    def __init__(
        self,
        connection_string: Optional[str] = None,
        account_url: Optional[str] = None,
        credential: Optional[Any] = None,
    ):
        """Initialize Azure Blob Storage client."""
        if connection_string:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                connection_string
            )
        elif account_url:
            self.blob_service_client = BlobServiceClient(
                account_url=account_url, credential=credential
            )
        else:
            raise ValueError("Either connection_string or account_url must be provided")

        # Container names for different data types
        self.containers = {
            "configurations": "ensemble-configurations",
            "executions": "ensemble-executions",
            "results": "ensemble-results",
            "conversations": "conversations",
            "templates": "prompt-templates",
        }

        # Ensure containers exist
        asyncio.create_task(self._ensure_containers_exist())

    async def _ensure_containers_exist(self) -> None:
        """Ensure all required containers exist."""
        for container_name in self.containers.values():
            try:
                container_client = self.blob_service_client.get_container_client(
                    container_name
                )
                await container_client.create_container()
                logger.info(f"Created container: {container_name}")
            except ResourceExistsError:
                logger.debug(f"Container already exists: {container_name}")
            except Exception as e:
                logger.warning(f"Failed to create container {container_name}: {e}")

    async def store_configuration(self, config: EnsembleConfiguration) -> str:
        """Store an ensemble configuration."""
        try:
            blob_name = f"configs/{config.config_id}.json"
            container_client = self.blob_service_client.get_container_client(
                self.containers["configurations"]
            )

            # Convert to dict and serialize
            config_data = config.model_dump()
            config_data["stored_at"] = datetime.utcnow().isoformat()

            blob_client = container_client.get_blob_client(blob_name)
            await blob_client.upload_blob(
                json.dumps(config_data, indent=2),
                overwrite=True,
                metadata={
                    "config_name": config.name,
                    "strategy": config.strategy,
                    "created_at": config.created_at.isoformat(),
                },
            )

            logger.info(f"Stored configuration: {config.config_id}")
            return blob_name

        except Exception as e:
            logger.exception(f"Failed to store configuration {config.config_id}: {e}")
            raise

    async def load_configuration(
        self, config_id: str
    ) -> Optional[EnsembleConfiguration]:
        """Load an ensemble configuration by ID."""
        try:
            blob_name = f"configs/{config_id}.json"
            container_client = self.blob_service_client.get_container_client(
                self.containers["configurations"]
            )
            blob_client = container_client.get_blob_client(blob_name)

            blob_data = await blob_client.download_blob()
            config_data = json.loads(await blob_data.readall())

            # Remove storage metadata
            config_data.pop("stored_at", None)

            return EnsembleConfiguration(**config_data)

        except ResourceNotFoundError:
            logger.warning(f"Configuration not found: {config_id}")
            return None
        except Exception as e:
            logger.exception(f"Failed to load configuration {config_id}: {e}")
            raise

    async def store_execution(self, execution: EnsembleExecution) -> str:
        """Store an ensemble execution record."""
        try:
            blob_name = f"executions/{execution.execution_id}.json"
            container_client = self.blob_service_client.get_container_client(
                self.containers["executions"]
            )

            # Convert to dict and serialize
            execution_data = execution.model_dump()
            execution_data["stored_at"] = datetime.utcnow().isoformat()

            blob_client = container_client.get_blob_client(blob_name)
            await blob_client.upload_blob(
                json.dumps(execution_data, indent=2),
                overwrite=True,
                metadata={
                    "config_id": execution.config_id,
                    "status": execution.status,
                    "started_at": execution.started_at.isoformat(),
                    "agent_count": str(len(execution.agent_executions)),
                },
            )

            logger.info(f"Stored execution: {execution.execution_id}")
            return blob_name

        except Exception as e:
            logger.exception(f"Failed to store execution {execution.execution_id}: {e}")
            raise

    async def load_execution(self, execution_id: str) -> Optional[EnsembleExecution]:
        """Load an ensemble execution by ID."""
        try:
            blob_name = f"executions/{execution_id}.json"
            container_client = self.blob_service_client.get_container_client(
                self.containers["executions"]
            )
            blob_client = container_client.get_blob_client(blob_name)

            blob_data = await blob_client.download_blob()
            execution_data = json.loads(await blob_data.readall())

            # Remove storage metadata
            execution_data.pop("stored_at", None)

            return EnsembleExecution(**execution_data)

        except ResourceNotFoundError:
            logger.warning(f"Execution not found: {execution_id}")
            return None
        except Exception as e:
            logger.exception(f"Failed to load execution {execution_id}: {e}")
            raise

    async def store_result(self, result: EnsembleResult) -> str:
        """Store an ensemble result."""
        try:
            blob_name = f"results/{result.execution_id}.json"
            container_client = self.blob_service_client.get_container_client(
                self.containers["results"]
            )

            # Convert to dict and serialize
            result_data = result.model_dump()
            result_data["stored_at"] = datetime.utcnow().isoformat()

            blob_client = container_client.get_blob_client(blob_name)
            await blob_client.upload_blob(
                json.dumps(result_data, indent=2),
                overwrite=True,
                metadata={
                    "config_name": result.config_name,
                    "execution_id": result.execution_id,
                    "created_at": result.created_at.isoformat(),
                },
            )

            logger.info(f"Stored result: {result.execution_id}")
            return blob_name

        except Exception as e:
            logger.exception(f"Failed to store result {result.execution_id}: {e}")
            raise

    async def load_result(self, execution_id: str) -> Optional[EnsembleResult]:
        """Load an ensemble result by execution ID."""
        try:
            blob_name = f"results/{execution_id}.json"
            container_client = self.blob_service_client.get_container_client(
                self.containers["results"]
            )
            blob_client = container_client.get_blob_client(blob_name)

            blob_data = await blob_client.download_blob()
            result_data = json.loads(await blob_data.readall())

            # Remove storage metadata
            result_data.pop("stored_at", None)

            return EnsembleResult(**result_data)

        except ResourceNotFoundError:
            logger.warning(f"Result not found: {execution_id}")
            return None
        except Exception as e:
            logger.exception(f"Failed to load result {execution_id}: {e}")
            raise

    async def list_configurations(
        self,
        prefix: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """List stored configurations with metadata."""
        try:
            container_client = self.blob_service_client.get_container_client(
                self.containers["configurations"]
            )

            blob_prefix = f"configs/{prefix}" if prefix else "configs/"
            blobs = container_client.list_blobs(name_starts_with=blob_prefix)

            configurations = []
            count = 0

            async for blob in blobs:
                if limit and count >= limit:
                    break

                config_info = {
                    "config_id": blob.name.split("/")[-1].replace(".json", ""),
                    "name": blob.metadata.get("config_name", "Unknown"),
                    "strategy": blob.metadata.get("strategy", "Unknown"),
                    "created_at": blob.metadata.get("created_at"),
                    "last_modified": blob.last_modified.isoformat()
                    if blob.last_modified
                    else None,
                    "size": blob.size,
                }
                configurations.append(config_info)
                count += 1

            return configurations

        except Exception as e:
            logger.exception(f"Failed to list configurations: {e}")
            return []

    async def list_executions(
        self,
        config_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """List stored executions with optional filtering."""
        try:
            container_client = self.blob_service_client.get_container_client(
                self.containers["executions"]
            )

            blobs = container_client.list_blobs(name_starts_with="executions/")

            executions = []
            count = 0

            async for blob in blobs:
                if limit and count >= limit:
                    break

                # Apply filters
                if config_id and blob.metadata.get("config_id") != config_id:
                    continue
                if status and blob.metadata.get("status") != status:
                    continue

                execution_info = {
                    "execution_id": blob.name.split("/")[-1].replace(".json", ""),
                    "config_id": blob.metadata.get("config_id"),
                    "status": blob.metadata.get("status", "Unknown"),
                    "started_at": blob.metadata.get("started_at"),
                    "agent_count": blob.metadata.get("agent_count", "0"),
                    "last_modified": blob.last_modified.isoformat()
                    if blob.last_modified
                    else None,
                    "size": blob.size,
                }
                executions.append(execution_info)
                count += 1

            return executions

        except Exception as e:
            logger.exception(f"Failed to list executions: {e}")
            return []

    async def store_conversation(
        self,
        conversation_id: str,
        messages: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Store a conversation history."""
        try:
            blob_name = f"conversations/{conversation_id}.json"
            container_client = self.blob_service_client.get_container_client(
                self.containers["conversations"]
            )

            conversation_data = {
                "conversation_id": conversation_id,
                "messages": messages,
                "metadata": metadata or {},
                "stored_at": datetime.utcnow().isoformat(),
            }

            blob_client = container_client.get_blob_client(blob_name)
            await blob_client.upload_blob(
                json.dumps(conversation_data, indent=2),
                overwrite=True,
                metadata={
                    "conversation_id": conversation_id,
                    "message_count": str(len(messages)),
                    "stored_at": conversation_data["stored_at"],
                },
            )

            logger.info(f"Stored conversation: {conversation_id}")
            return blob_name

        except Exception as e:
            logger.exception(f"Failed to store conversation {conversation_id}: {e}")
            raise

    async def load_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Load a conversation history by ID."""
        try:
            blob_name = f"conversations/{conversation_id}.json"
            container_client = self.blob_service_client.get_container_client(
                self.containers["conversations"]
            )
            blob_client = container_client.get_blob_client(blob_name)

            blob_data = await blob_client.download_blob()
            conversation_data = json.loads(await blob_data.readall())

            return conversation_data

        except ResourceNotFoundError:
            logger.warning(f"Conversation not found: {conversation_id}")
            return None
        except Exception as e:
            logger.exception(f"Failed to load conversation {conversation_id}: {e}")
            raise

    async def delete_blob(self, container_type: str, blob_name: str) -> bool:
        """Delete a blob from the specified container."""
        try:
            if container_type not in self.containers:
                raise ValueError(f"Unknown container type: {container_type}")

            container_client = self.blob_service_client.get_container_client(
                self.containers[container_type]
            )
            blob_client = container_client.get_blob_client(blob_name)

            await blob_client.delete_blob()
            logger.info(f"Deleted blob: {blob_name} from {container_type}")
            return True

        except ResourceNotFoundError:
            logger.warning(f"Blob not found: {blob_name} in {container_type}")
            return False
        except Exception as e:
            logger.exception(f"Failed to delete blob {blob_name}: {e}")
            raise


# Fix import issue
import asyncio
