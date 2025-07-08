"""
Environment variable substitution utility for YAML configuration files.

This module provides functionality to replace environment variable placeholders
in YAML content with actual environment variable values using the syntax:
${VAR_NAME:default_value} or ${VAR_NAME}
"""

import os


def substitute_env_vars(content: str) -> str:
    """
    Substitute environment variables in a string using ${VAR_NAME:default} syntax.
    Handles nested variable expressions correctly.

    Args:
        content: String content containing environment variable placeholders

    Returns:
        String with environment variables substituted

    Examples:
        >>> os.environ['MY_VAR'] = 'test_value'
        >>> substitute_env_vars('${MY_VAR:default}')
        'test_value'
        >>> substitute_env_vars('${MISSING_VAR:default}')
        'default'
    """

    def find_variable_expressions(text):
        """Find all ${...} expressions, handling nested braces correctly."""
        expressions = []
        i = 0
        while i < len(text):
            if text[i : i + 2] == "${":
                # Found start of expression
                start = i
                i += 2
                brace_count = 1
                while i < len(text) and brace_count > 0:
                    if text[i] == "{":
                        brace_count += 1
                    elif text[i] == "}":
                        brace_count -= 1
                    i += 1
                if brace_count == 0:
                    # Found complete expression
                    var_expr = text[start + 2 : i - 1]
                    expressions.append((start, i, var_expr))
            else:
                i += 1
        return expressions

    def replace_expression(var_expr):
        """Replace a single variable expression."""
        if ":" in var_expr:
            var_name, default_value = var_expr.split(":", 1)
            return os.getenv(var_name, default_value)
        else:
            var_name = var_expr
            return os.getenv(var_name, "")

    # Keep substituting until no more changes occur (handles nested substitutions)
    max_iterations = 10  # Prevent infinite loops
    for _ in range(max_iterations):
        expressions = find_variable_expressions(content)
        if not expressions:
            break  # No more expressions to substitute

        # Replace expressions from right to left to avoid index issues
        new_content = content
        for start, end, var_expr in reversed(expressions):
            replacement = replace_expression(var_expr)
            new_content = new_content[:start] + replacement + new_content[end:]

        if new_content == content:
            break  # No more changes
        content = new_content

    return content


def load_yaml_with_env_substitution(file_path: str) -> str:
    """
    Load a YAML file and perform environment variable substitution.

    Args:
        file_path: Path to the YAML file

    Returns:
        YAML content with environment variables substituted
    """
    with open(file_path, "r") as file:
        content = file.read()

    return substitute_env_vars(content)
