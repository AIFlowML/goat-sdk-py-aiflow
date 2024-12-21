#!/bin/bash

# Exit on error
set -e

VENV_DIR=".venv"
REQUIREMENTS_FILE="requirements.txt"
PYTHON_VERSION_FILE=".python-version"

# Check if pyenv is installed
if ! command -v pyenv &> /dev/null; then
    echo "Installing pyenv..."
    brew install pyenv
fi

# Read Python version from .python-version
PYTHON_VERSION=$(cat $PYTHON_VERSION_FILE)

# Install Python version if not already installed
if ! pyenv versions | grep -q $PYTHON_VERSION; then
    echo "Installing Python $PYTHON_VERSION..."
    pyenv install $PYTHON_VERSION
fi

# Set local Python version
pyenv local $PYTHON_VERSION

# Get path to Python executable
PYTHON_PATH=$(pyenv which python)

# Check if virtualenv is installed
if ! $PYTHON_PATH -m pip list | grep -q virtualenv; then
    echo "Installing virtualenv..."
    $PYTHON_PATH -m pip install virtualenv
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    $PYTHON_PATH -m venv $VENV_DIR
fi

# Activate virtual environment
source $VENV_DIR/bin/activate

# Install/upgrade pip
python -m pip install --upgrade pip

# Install requirements if requirements.txt exists
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing requirements..."
    pip install -r $REQUIREMENTS_FILE
else
    echo "No requirements.txt found. Installing base packages..."
    pip install pytest pytest-asyncio pytest-cov black isort mypy
fi

# Print activation command for user reference
echo ""
echo "Virtual environment is ready!"
echo "To activate it in a new terminal, run:"
echo "source $VENV_DIR/bin/activate"
