#!/bin/bash
set -e

VENV_DIR=".venv"
PYTHON="python3.13"

# spaCy and its dependencies (Pydantic V1, confection) are not compatible with Python 3.14+
if ! command -v "$PYTHON" &>/dev/null; then
    echo "Error: $PYTHON not found. Install it with: brew install python@3.13"
    exit 1
fi

# Create venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR (using $PYTHON)..."
    "$PYTHON" -m venv "$VENV_DIR"
fi

# Activate venv
source "$VENV_DIR/bin/activate"

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install presidio-analyzer presidio-anonymizer spacy anthropic

echo "Downloading spaCy language models..."

# English model (required)
python -m spacy download en_core_web_lg

# Czech spaCy model: not available in the official spaCy model registry (as of spaCy 3.8).
# The tool will fall back to regex-only mode for Czech NER if no model is loaded.

echo ""
echo "Installation complete. To use the tool, activate the virtual environment first:"
echo "  source $VENV_DIR/bin/activate"
