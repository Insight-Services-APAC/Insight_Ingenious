import time
from typing import Any, Dict, Optional

from rich.progress import Progress

from ingenious.common.utils.log_levels import LogLevel


class ProgressTracker:
    """
    A class to track progress of operations with visual feedback.
    Handles the rich Progress object and provides additional functionality.
    """

    def __init__(self, progress: Progress, log_level: LogLevel):
        """
        Initialize the ProgressTracker.

        Args:
            progress: The rich Progress object
            log_level: The minimum log level to display
        """
        self.progress = progress
        self.log_level = log_level
        self._completed_items = 0
        self._failed_items = 0

    def print(self, message: str, level: LogLevel = LogLevel.INFO, *args, **kwargs):
        """
        Print a message to the console with the specified log level.

        Args:
            message: The message to print
            level: The log level of the message
            *args: Additional arguments for rich.console.print
            **kwargs: Additional keyword arguments for rich.console.print
        """
        if level >= self.log_level:
            # Set the style based on the log level if not provided
            style = kwargs.get("style", None)
            if style is None:
                style = LogLevel.to_string(level).lower()
            kwargs["style"] = style

            # Print the message
            self.progress.console.print(message, *args, **kwargs)

    @property
    def completed_items(self) -> int:
        """Get the number of completed items."""
        return self._completed_items

    @completed_items.setter
    def completed_items(self, value: int):
        """Set the number of completed items."""
        self._completed_items = value

    @property
    def failed_items(self) -> int:
        """Get the number of failed items."""
        return self._failed_items

    @failed_items.setter
    def failed_items(self, value: int):
        """Set the number of failed items."""
        self._failed_items = value

    def __getattr__(self, attr: str) -> Any:
        """
        Forward attribute access to the Progress object if not found in this class.

        Args:
            attr: The attribute name

        Returns:
            The attribute value from the Progress object
        """
        return getattr(self.progress, attr)

    def create_task(self, description: str) -> int:
        """
        Create a new progress task.

        Args:
            description: The task description

        Returns:
            The task ID
        """
        return self.progress.add_task(description=description)

    def update_task_status(
        self,
        task_id: int,
        status: str,
        stage_name: str,
        completed: bool = False,
        runtime: Optional[float] = None,
    ):
        """
        Update the status and description of a task.

        Args:
            task_id: The task ID
            status: The status text (e.g., "Running", "Completed")
            stage_name: The name of the stage
            completed: Whether the task is completed
            runtime: The runtime in seconds (if completed)
        """
        description = f"[{status}] Stage: {stage_name}"

        if runtime is not None:
            milliseconds = int((runtime % 1) * 1000)
            runtime_str = (
                time.strftime("%H:%M:%S", time.gmtime(runtime)) + f".{milliseconds:03d}"
            )
            description += f"[info] | Runtime: {runtime_str}[/info]"

        update_args: Dict[str, Any] = {"description": description}

        if completed:
            update_args["total"] = 1
            update_args["completed"] = 1

        self.progress.update(task_id=task_id, **update_args)
