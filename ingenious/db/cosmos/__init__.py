from datetime import datetime
from typing import Dict, List, Optional
import uuid
import os
from azure.cosmos import DatabaseProxy, PartitionKey, exceptions, CosmosClient, DatabaseProxy
from ingenious.models.message import Message
from ingenious.db.chat_history_repository import IChatHistoryRepository
import ingenious.config.config as Config


class cosmos_ChatHistoryRepository(IChatHistoryRepository):
    def __init__(self, config: Config.Config):
        connection_string = config.chat_history.database_connection_string
        print(f"Connection string: {connection_string}")
        database_name = config.chat_history.database_name
        print(f"Database name: {database_name}")
        cosmos_client = CosmosClient.from_connection_string(connection_string)
        database_client = cosmos_client.get_database_client(database_name)
        self.container = database_client.create_container_if_not_exists(
            id="chat_history",
            partition_key=PartitionKey(path="/thread_id")
        )

        self.container_memory = database_client.create_container_if_not_exists(
            id="chat_history_memory",
            partition_key=PartitionKey(path="/thread_id")
        )

    async def add_message(self, message: Message) -> str:
        message.message_id = str(uuid.uuid4())
        message.timestamp = datetime.now()
        message_dict = message.model_dump(mode="json")
        message_dict['id'] = message.message_id
        self.container.create_item(body=message_dict)

        return message.message_id

    async def get_message(self, message_id: str, thread_id: str) -> Message | None:
        try:
            item = self.container.read_item(item=message_id, partition_key=thread_id)
            return Message(**item)
        except exceptions.CosmosHttpResponseError as e:
            if e.status_code == 404:
                return None
            raise

    async def get_thread_messages(self, thread_id: str) -> list[Message]:
        query = "SELECT * FROM c WHERE c.thread_id = @thread_id ORDER BY c.timestamp"
        parameters: list[dict[str, object]] = [{"name": "@thread_id", "value": thread_id}]
        items = list(self.container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
        return [Message(**item) for item in items]

    async def update_message_feedback(self, message_id: str, thread_id: str, positive_feedback: bool | None) -> None:
        item = self.container.read_item(item=message_id, partition_key=thread_id)
        item['positive_feedback'] = positive_feedback
        self.container.replace_item(item=item, body=item)

    async def update_message_content_filter_results(
            self, message_id: str, thread_id: str, content_filter_results: dict[str, object]) -> None:
        item = self.container.read_item(item=message_id, partition_key=thread_id)
        item['content_filter_results'] = content_filter_results
        self.container.replace_item(item=item, body=item)

    async def delete_thread(self, thread_id: str) -> None:
        query = "SELECT * FROM c WHERE c.thread_id = @thread_id"
        parameters: list[dict[str, object]] = [{"name": "@thread_id", "value": thread_id}]
        items = list(self.container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
        for item in items:
            self.container.delete_item(item=item['id'], partition_key=item['id'])

    async def update_thread(
        self,
        thread_id: str,
        name: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        pass
    
    async def add_user(self, identifier: str) -> IChatHistoryRepository.User:
        user_id = uuid.uuid4()
        user_data = {
            "id": user_id,
            "identifier": identifier,
            "createdAt": datetime.now().isoformat(),
            "metadata": {}
        }
        self.container.create_item(body=user_data)
        return IChatHistoryRepository.User(
            id=user_id,
            identifier=identifier,
            createdAt=user_data["createdAt"],
            metadata=user_data["metadata"]
        )

    async def get_user(self, identifier: str) -> IChatHistoryRepository.User | None:
        query = "SELECT * FROM c WHERE c.identifier = @identifier"
        parameters = [{"name": "@identifier", "value": identifier}]
        results = list(self.container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
        if results:
            user_data = results[0]
            return IChatHistoryRepository.User(
                id=user_data["id"],
                identifier=user_data["identifier"],
                createdAt=user_data["createdAt"],
                metadata=user_data.get("metadata", {})
            )
        return None


    async def get_threads_for_user(self, identifier: str, thread_id: Optional[str]) -> Optional[List[Dict]]:
        """Retrieve threads associated with a specific user."""
        query = "SELECT * FROM c WHERE c.user_id = @user_id"
        parameters = [{"name": "@user_id", "value": identifier}]
        if thread_id:
            query += " AND c.thread_id = @thread_id"
            parameters.append({"name": "@thread_id", "value": thread_id})

        results = list(self.container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))
        return results if results else None

    async def add_memory(self, message: Message) -> str:
        message.message_id = str(uuid.uuid4())
        message.timestamp = datetime.now()

        # Prepare message dictionary for insertion
        message_dict = {
            "id": message.message_id,
            "user_id": message.user_id,
            "thread_id": message.thread_id,
            "message_id": message.message_id,
            "positive_feedback": message.positive_feedback,
            "timestamp": message.timestamp.isoformat(),
            "role": message.role,
            "content": message.content,
            "content_filter_results": message.content_filter_results,
            "tool_calls": message.tool_calls,
            "tool_call_id": message.tool_call_id,
            "tool_call_function": message.tool_call_function,
            "is_memory": True  # Flag to indicate that this is a memory entry
        }

        # Insert the memory record into CosmosDB
        try:
            self.container_memory.create_item(body=message_dict)
        except exceptions.CosmosHttpResponseError as e:
            raise RuntimeError(f"Failed to add memory to CosmosDB: {e}")

        return message.message_id

    async def get_memory(self, message_id: str, thread_id: str) -> Message | None:
        try:
            query = """
                SELECT * FROM c WHERE c.thread_id = @thread_id 
                AND c.message_id = @message_id AND c.is_memory = true
                ORDER BY c.timestamp DESC
                OFFSET 0 LIMIT 1
            """
            parameters = [
                {"name": "@thread_id", "value": thread_id},
                {"name": "@message_id", "value": message_id}
            ]
            items = list(self.container_memory.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
            if items:
                return Message(**items[0])
        except exceptions.CosmosHttpResponseError as e:
            if e.status_code == 404:
                return None
            raise


    async def update_memory(self) -> None:
        # Query to find the latest record for each thread
        query = """
            SELECT c.user_id, c.thread_id, c.message_id, c.positive_feedback, c.timestamp, 
                   c.role, c.content, c.content_filter_results, c.tool_calls, 
                   c.tool_call_id, c.tool_call_function
            FROM c
            WHERE c.is_memory = true
            ORDER BY c.thread_id, c.timestamp DESC
        """

        # Retrieve the latest memory records from CosmosDB
        items = list(self.container_memory.query_items(query=query, enable_cross_partition_query=True))
        latest_records = {}

        # Deduplicate by thread_id, keeping only the latest record
        for item in items:
            thread_id = item["thread_id"]
            if thread_id not in latest_records:
                latest_records[thread_id] = item

        # Delete all memory records
        delete_query = "SELECT c.id FROM c WHERE c.is_memory = true"
        delete_items = list(self.container_memory.query_items(query=delete_query, enable_cross_partition_query=True))
        for item in delete_items:
            self.container_memory.delete_item(item=item['id'], partition_key=item['thread_id'])

        # Insert the latest memory records back into CosmosDB
        for record in latest_records.values():
            try:
                self.container_memory.create_item(body=record)
            except exceptions.CosmosHttpResponseError as e:
                raise RuntimeError(f"Failed to update memory in CosmosDB: {e}")


    async def get_thread_memory(self, thread_id: str) -> list[Message]:
        query = """
            SELECT * FROM c WHERE c.thread_id = @thread_id 
            AND c.is_memory = true ORDER BY c.timestamp DESC
        """
        parameters = [{"name": "@thread_id", "value": thread_id}]
        items = list(self.container_memory.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
        return [Message(**item) for item in items] if items else []


    async def update_memory_feedback(self, message_id: str, thread_id: str, positive_feedback: bool | None) -> None:
        try:
            # Retrieve the memory record
            item = self.container_memory.read_item(item=message_id, partition_key=thread_id)
            if item.get('is_memory'):
                # Update the positive_feedback field
                item['positive_feedback'] = positive_feedback
                self.container_memory.replace_item(item=item, body=item)
        except exceptions.CosmosHttpResponseError as e:
            if e.status_code == 404:
                raise ValueError("Memory not found")
            raise

    async def update_memory_content_filter_results(self, message_id: str, thread_id: str, content_filter_results: dict[str, object]) -> None:
        try:
            # Retrieve the memory record
            item = self.container_memory.read_item(item=message_id, partition_key=thread_id)
            if item.get('is_memory'):
                # Update the content_filter_results field
                item['content_filter_results'] = content_filter_results
                self.container_memory.replace_item(item=item, body=item)
        except exceptions.CosmosHttpResponseError as e:
            if e.status_code == 404:
                raise ValueError("Memory not found")
            raise

    async def delete_thread_memory(self, thread_id: str) -> None:
        # Query to find all memory records for the thread
        query = "SELECT c.id FROM c WHERE c.thread_id = @thread_id AND c.is_memory = true"
        parameters = [{"name": "@thread_id", "value": thread_id}]
        items = list(self.container_memory.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))

        # Delete each memory record found
        for item in items:
            self.container_memory.delete_item(item=item['id'], partition_key=thread_id)


    async def delete_user_memory(self, user_id: str) -> None:
        # Query to find all memory records for the user
        query = "SELECT c.id FROM c WHERE c.user_id = @user_id AND c.is_memory = true"
        parameters = [{"name": "@thread_id", "value": user_id}]
        items = list(self.container_memory.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))

        # Delete each memory record found
        for item in items:
            self.container_memory.delete_item(item=item['id'], partition_key=user_id)