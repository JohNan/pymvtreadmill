#!/bin/bash
set -e

# Ensure uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Please install it (e.g. curl -LsSf https://astral.sh/uv/install.sh | sh)"
    exit 1
fi

echo "Creating virtual environment..."
uv venv

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
uv pip install -e .[dev]

echo "Environment setup complete!"
