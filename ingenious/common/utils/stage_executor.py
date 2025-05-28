import time
from typing import List

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ingenious.common.utils.action_executor import ActionExecutor, IActionCallable
from ingenious.common.utils.log_levels import LogLevel
from ingenious.common.utils.progress_tracker import ProgressTracker


class stage_executor:
    """
    Executes stages with progress tracking and visual feedback.
    Each stage consists of a series of actions executed sequentially.
    """

    def __init__(self, log_level: LogLevel, console: Console):
        """
        Initialize the stage executor.

        Args:
            log_level: The minimum log level to display
            console: The rich console object
        """
        self.log_level = log_level
        self.console = console

    def _create_progress(self) -> Progress:
        """
        Create a rich Progress object.

        Returns:
            A new Progress object
        """
        return Progress(
            SpinnerColumn(
                spinner_name="dots", style="progress.spinner", finished_text="📦"
            ),
            TextColumn("[progress.description]{task.description}"),
            transient=False,
            console=self.console,
        )

    async def perform_stage(
        self,
        option: bool = True,
        action_callables: List[IActionCallable] = "",
        stage_name: str = "Stage - No Name Provided",
        **kwargs,
    ):
        """
        Perform a stage with progress tracking.

        Args:
            option: Whether to execute the stage or skip it
            action_callables: The list of actions to execute
            stage_name: The name of the stage
            **kwargs: Additional arguments for the actions
        """
        with self._create_progress() as progress:
            # Create a progress tracker
            progress_tracker = ProgressTracker(progress, self.log_level)

            # Create a task for this stage
            task_id = progress_tracker.create_task(f"[Initiated  ] Stage: {stage_name}")

            if option:
                # Execute the actions with timing
                await ActionExecutor.execute_with_timing(
                    actions=action_callables,
                    progress_tracker=progress_tracker,
                    task_id=task_id,
                    stage_name=stage_name,
                    **kwargs,
                )
            else:
                # Skip the stage
                progress_tracker.update_task_status(
                    task_id=task_id,
                    status="Skipped  -- ",
                    stage_name=stage_name,
                    completed=True,
                )

            # Add a short delay to ensure the progress bar is visible
            time.sleep(1)
