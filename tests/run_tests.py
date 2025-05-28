"""
Module for running test batches.
This module provides functionality for running batches of tests.
"""

import os

import pytest


class RunBatches:
    """
    Class for running test batches.
    This class handles running batches of tests using pytest.
    """

    def __init__(self, progress=None, task_id=None):
        """
        Initialize the RunBatches class.

        Args:
            progress: Progress tracker (optional)
            task_id: Task ID (optional)
        """
        self.progress = progress
        self.task_id = task_id

    async def run(self, progress=None, task_id=None, **kwargs):
        """
        Run a batch of tests.

        Args:
            progress: Progress tracker (optional)
            task_id: Task ID (optional)
            **kwargs: Additional arguments

        Returns:
            A dictionary containing the test results
        """
        # Build the pytest arguments
        pytest_args = []

        # Add specific test filter if provided
        test_name = kwargs.get("test_name")
        if test_name:
            pytest_args.append(test_name)

        # Add test type filter if provided
        test_type = kwargs.get("test_type")
        if test_type:
            pytest_args.append(f"-m={test_type}")

        # Add verbose flag if specified
        verbose = kwargs.get("verbose", "true").lower() == "true"
        if verbose:
            pytest_args.append("-v")

        # Get current directory as the test directory if not specified
        test_dir = kwargs.get("test_dir", os.path.join(os.getcwd(), "tests"))
        pytest_args.append(test_dir)

        # Log the test execution
        if progress:
            progress.update(
                task_id, description=f"Running tests with args: {' '.join(pytest_args)}"
            )

        # Run the tests using pytest
        result = pytest.main(pytest_args)

        # Map the pytest exit code to a result message
        result_messages = {
            0: "All tests passed successfully",
            1: "Tests failed",
            2: "Test execution was interrupted",
            3: "Internal error occurred",
            4: "pytest command line usage error",
            5: "No tests were collected",
        }

        # Return the results
        test_results = {
            "exit_code": result,
            "result_message": result_messages.get(
                result, f"Unknown result code: {result}"
            ),
            "args": pytest_args,
        }

        # Update progress if available
        if progress:
            progress.update(
                task_id, description=f"Test Results: {test_results['result_message']}"
            )

        return test_results
