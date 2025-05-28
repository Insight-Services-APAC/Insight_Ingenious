import time
from abc import ABC, abstractmethod
from typing import List

from ingenious.common.utils.progress_tracker import ProgressTracker


class IActionCallable(ABC):
    """Interface for callable actions that can be executed in a stage."""

    @abstractmethod
    async def __call__(self, progress, task_id, **kwargs):
        """
        Execute the action.

        Args:
            progress: The progress tracker
            task_id: The task ID
            **kwargs: Additional arguments for the action
        """
        pass


class ActionExecutor:
    """Executes actions with progress tracking."""

    @staticmethod
    async def execute_actions(
        actions: List[IActionCallable],
        progress_tracker: ProgressTracker,
        task_id: int,
        **kwargs,
    ):
        """
        Execute a list of actions sequentially.

        Args:
            actions: The list of actions to execute
            progress_tracker: The progress tracker
            task_id: The task ID
            **kwargs: Additional arguments for the actions
        """
        for action in actions:
            await action(progress=progress_tracker, task_id=task_id, **kwargs)

    @staticmethod
    async def execute_with_timing(
        actions: List[IActionCallable],
        progress_tracker: ProgressTracker,
        task_id: int,
        stage_name: str,
        **kwargs,
    ) -> float:
        """
        Execute a list of actions with timing and status updates.

        Args:
            actions: The list of actions to execute
            progress_tracker: The progress tracker
            task_id: The task ID
            stage_name: The name of the stage
            **kwargs: Additional arguments for the actions

        Returns:
            The runtime in seconds
        """
        # Update status to running
        progress_tracker.update_task_status(
            task_id=task_id, status="Running  🏃‍♂️", stage_name=stage_name
        )

        # Start timing
        start_time = time.time()

        # Execute actions
        await ActionExecutor.execute_actions(
            actions=actions,
            progress_tracker=progress_tracker,
            task_id=task_id,
            **kwargs,
        )

        # Calculate runtime
        runtime = time.time() - start_time

        # Update status to completed
        progress_tracker.update_task_status(
            task_id=task_id,
            status="Completed ✅ ",
            stage_name=stage_name,
            completed=True,
            runtime=runtime,
        )

        return runtime
