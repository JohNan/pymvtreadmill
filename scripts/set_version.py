#!/usr/bin/env python3
"""
Script to set the version in pyproject.toml based on the provided argument.
Usage: python scripts/set_version.py <version>
Example: python scripts/set_version.py v1.2.3
"""

import sys
import re
import pathlib


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/set_version.py <version>")
        sys.exit(1)

    version = sys.argv[1]

    # Strip leading 'v' if present
    if version.startswith("v"):
        version = version[1:]

    # Validate version format (simple check)
    if not re.match(r"^\d+\.\d+\.\d+", version):
        print(f"Error: Invalid version format '{version}'. Expected X.Y.Z")
        sys.exit(1)

    pyproject_path = pathlib.Path(__file__).parent.parent / "pyproject.toml"

    if not pyproject_path.exists():
        print(f"Error: {pyproject_path} not found.")
        sys.exit(1)

    content = pyproject_path.read_text(encoding="utf-8")

    # Regex to find version = "..."
    # We look for version = "..." under [project] table context, but assuming standard format
    # simplistic regex: version = "..."

    # More robust: find `version = "..."` inside `[project]` section?
    # Or just replace the first occurrence of `version = "..."` which is usually the project version.

    pattern = r'version = "[^"]+"'
    replacement = f'version = "{version}"'

    if not re.search(pattern, content):
        print("Error: Could not find version string in pyproject.toml")
        sys.exit(1)

    new_content = re.sub(pattern, replacement, content, count=1)

    pyproject_path.write_text(new_content, encoding="utf-8")
    print(f"Updated pyproject.toml version to {version}")


if __name__ == "__main__":
    main()
