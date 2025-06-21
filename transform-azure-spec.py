#!/usr/bin/env python3
"""
Transform Azure OpenAPI specs to work with Prism mock server.

Azure specs often use 'x-ms-paths' instead of 'paths', which Prism doesn't recognize.
This script downloads Azure specs and transforms them to standard OpenAPI format.
"""

import json
import sys
import urllib.request
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required to handle YAML specs.")
    print("Install it with: uv add pyyaml")
    sys.exit(1)


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle date/datetime objects."""

    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


def download_spec(url: str) -> Dict[str, Any]:
    """Download OpenAPI spec from URL."""
    print(f"Downloading spec from: {url}")
    with urllib.request.urlopen(url) as response:
        content = response.read().decode("utf-8")

        if url.endswith(".yaml") or url.endswith(".yml"):
            # Parse as YAML
            try:
                return yaml.safe_load(content)
            except yaml.YAMLError as e:
                print(f"Error parsing YAML: {e}")
                sys.exit(1)
        else:
            # Parse as JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
                sys.exit(1)


def transform_azure_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Transform Azure spec to work with Prism by moving x-ms-paths to paths."""
    if "x-ms-paths" in spec:
        print("Found x-ms-paths, transforming to paths...")

        # Initialize paths if it doesn't exist
        if "paths" not in spec:
            spec["paths"] = {}

        # Move operations from x-ms-paths to paths
        x_ms_paths = spec.pop("x-ms-paths")

        for path, operations in x_ms_paths.items():
            # Azure paths sometimes have query parameters in the path template
            # We need to clean these for Prism compatibility
            clean_path = path.split("?")[0]  # Remove query parameters

            if clean_path in spec["paths"]:
                # Merge operations if path already exists
                spec["paths"][clean_path].update(operations)
            else:
                spec["paths"][clean_path] = operations

        print(f"Moved {len(x_ms_paths)} paths from x-ms-paths to paths")

    # Also handle any x-ms-* extensions that might cause issues
    # Remove problematic extensions that Prism might not handle
    if "x-ms-parameterized-host" in spec:
        print("Removing x-ms-parameterized-host...")
        spec.pop("x-ms-parameterized-host")

    # Ensure we have a proper host and basePath for Prism
    if "host" not in spec:
        spec["host"] = "localhost"

    if "schemes" not in spec:
        spec["schemes"] = ["http", "https"]

    # Count total operations for verification
    total_ops = 0
    if "paths" in spec:
        for path_ops in spec["paths"].values():
            total_ops += len(
                [
                    k
                    for k in path_ops.keys()
                    if k in ["get", "post", "put", "delete", "patch", "head", "options"]
                ]
            )

    print(
        f"Spec now contains {total_ops} operations across {len(spec.get('paths', {}))} paths"
    )

    return spec


def save_spec(spec: Dict[str, Any], filepath: Path) -> None:
    """Save transformed spec to file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(spec, f, indent=2, cls=CustomJSONEncoder)
    print(f"Saved transformed spec to: {filepath}")


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 transform-azure-spec.py <source_url> <output_file>")
        sys.exit(1)

    source_url = sys.argv[1]
    output_file = Path(sys.argv[2])

    try:
        # Download and transform spec
        spec = download_spec(source_url)
        transformed_spec = transform_azure_spec(spec)

        # Save transformed spec
        save_spec(transformed_spec, output_file)

        print(f"\nSuccess! Transformed spec saved to {output_file}")
        print("You can now use this file with Prism:")
        print(f"  prism mock {output_file} --port <port>")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
