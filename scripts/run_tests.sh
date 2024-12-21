#!/bin/bash

# Exit on error
set -e

VENV_DIR=".venv"

# Check if virtualenv exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Running setup..."
    ./scripts/setup_venv.sh
fi

# Activate virtual environment
source $VENV_DIR/bin/activate

# Run tests with coverage
pytest "$@" --cov=goat_sdk --cov-report=term-missing
