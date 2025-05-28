# Sample Extension Module
"""
Sample extension module for Ingenious.
"""


def initialize():
    """
    Initialize the extension.
    """
    print("Initializing sample extension")
    return True


def get_capabilities():
    """
    Return the capabilities of this extension.
    """
    return {
        "name": "sample_extension",
        "version": "0.1.0",
        "description": "A sample extension for Ingenious",
        "functions": [
            {
                "name": "sample_function",
                "description": "A sample function",
                "parameters": {},
            }
        ],
    }


def sample_function():
    """
    A sample function.
    """
    return "Hello from the sample extension!"
