from datetime import datetime, timezone
from typing import Dict, List, Optional

import chainlit as cl
import chainlit.data as cl_data
import ingenious.presentation.api.dependencies as deps
from chainlit.data import queue_until_user_message
from chainlit.element import Element, ElementDict
from chainlit.step import StepDict
from chainlit.types import (
    Feedback,
    PageInfo,
    PaginatedResponse,
    Pagination,
    ThreadDict,
    ThreadFilter,
)

now = datetime.now(timezone.utc)
now_str = now.strftime("%Y-%m-%d %H:%M:%S.%f%z")

thread_history = []  # type: List[ThreadDict]
deleted_thread_ids = []  # type: List[str]
user = None


class DataLayer(cl_data.BaseDataLayer):
    async def set_user(self, user):
        self.user = user

    async def get_user(self, identifier: str) -> Optional[cl.PersistedUser]:
        print("Searching for user with identifier: ", identifier)
        user = await deps.get_chat_history_repository().get_user(identifier)
        if user:
            print("Found Existing user with identifier: ", identifier)
            self.user = cl.PersistedUser(
                id=user.id, createdAt=user.createdAt, identifier=user.identifier
            )
            return self.user
        else:
            return None

    async def create_user(self, user: cl.User):
        print("Creating user with identifier: ", user.identifier)
        _user = await deps.get_chat_history_repository().add_user(
            identifier=user.identifier
        )
        self.user = cl.PersistedUser(
            id=user.identifier, createdAt=now_str, identifier=user.identifier
        )
        return self.user

    async def update_thread(
        self,
        thread_id: str,
        name: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
    ):
        print("Updating thread: ", thread_id)
        await deps.get_chat_history_repository().update_thread(
            thread_id, name, user_id, metadata, tags
        )

    @cl_data.queue_until_user_message()
    async def create_step(self, step_dict: StepDict):
        await deps.get_chat_history_repository().add_step(step_dict)

    async def get_thread_author(self, thread_id: str) -> str:
        print("Getting thread author for thread: ", thread_id)

        print("User ID: ", self.user.identifier)
        print("Thread ID: ", thread_id)
        threads = await deps.get_chat_history_repository().get_threads_for_user(
            identifier=self.user.identifier, thread_id=thread_id
        )
        # Get first user in the thread
        if threads:
            return threads[0]["userIdentifier"]
        else:
            return ""

    async def get_threads_for_user(self, user_id: str):
        threads = []
        tfu = await deps.get_chat_history_repository().get_threads_for_user(
            identifier=user_id, thread_id=None
        )
        if tfu:
            for t in tfu:
                thread = {
                    "id": t["id"],
                    "name": t["name"],
                    "createdAt": t["createdAt"],
                    "userId": t["userId"],
                    "userIdentifier": t["userIdentifier"],
                    "tags": t["tags"],
                    "metadata": t["metadata"],
                    "elements": t["elements"],
                    "steps": t["steps"],
                }
                threads.append(thread)
        return threads

    async def list_threads(
        self, pagination: Pagination, filters: ThreadFilter
    ) -> PaginatedResponse[ThreadDict]:
        thread_history = await self.get_threads_for_user(self.user.identifier)
        return PaginatedResponse(
            data=[t for t in thread_history if t["id"] not in deleted_thread_ids],
            pageInfo=PageInfo(hasNextPage=False, startCursor=None, endCursor=None),
        )

    async def get_thread(self, thread_id: str) -> Optional[ThreadDict]:
        print("Getting thread: ", thread_id)
        tfu = await deps.get_chat_history_repository().get_threads_for_user(
            identifier=self.user.identifier, thread_id=thread_id
        )
        thread = None
        if tfu:
            for t in tfu:
                thread = {
                    "id": t["id"],
                    "name": t["name"],
                    "createdAt": t["createdAt"],
                    "userId": t["userId"],
                    "userIdentifier": t["userIdentifier"],
                    "tags": t["tags"],
                    "metadata": t["metadata"],
                    "elements": t["elements"],
                    "steps": t["steps"],
                }
        if not thread:
            print("Thread not found")
            return None
        thread["steps"] = sorted(thread["steps"], key=lambda x: x["createdAt"])
        return ThreadDict(**thread)

    async def delete_thread(self, thread_id: str):
        deleted_thread_ids.append(thread_id)

    async def delete_feedback(
        self,
        feedback_id: str,
    ) -> bool:
        return True

    async def upsert_feedback(
        self,
        feedback: Feedback,
    ) -> str:
        return ""

    @queue_until_user_message()
    async def create_element(self, element: "Element"):
        print("Creating element: ", element)
        pass

    async def get_element(
        self, thread_id: str, element_id: str
    ) -> Optional["ElementDict"]:
        print("Getting element: ", element_id)
        pass

    @queue_until_user_message()
    async def delete_element(self, element_id: str, thread_id: Optional[str] = None):
        pass

    @queue_until_user_message()
    async def update_step(self, step_dict: "StepDict"):
        pass

    @queue_until_user_message()
    async def delete_step(self, step_id: str):
        pass

    async def build_debug_url(self) -> str:
        return ""
