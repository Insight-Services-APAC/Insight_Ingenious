from abc import ABC, abstractmethod
from typing import Optional


class IMessageFeedbackService(ABC):
    @abstractmethod
    async def update_message_feedback(
        self, message_id: str, thread_id: str, positive_feedback: Optional[bool]
    ) -> None:
        """Update feedback for a message"""
        pass
