#!/bin/bash

# Function to check if virtual environment is activated
check_venv() {
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        echo "Virtual environment is already activated: $VIRTUAL_ENV"
        return 0
    else
        return 1
    fi
}

# Check if .venv directory exists and activate it (checking in parent directory)
if [ -d "../.venv" ]; then
    if ! check_venv; then
        echo "Activating virtual environment (../.venv)..."
        source ../.venv/bin/activate
        if check_venv; then
            echo "✓ Virtual environment activated successfully"
        else
            echo "✗ Failed to activate virtual environment"
            exit 1
        fi
    fi
else
    echo "✗ ERROR: No .venv directory found in parent directory!"
    echo "A virtual environment is required to run this application."
    echo "Please create one in the root directory with: python -m venv .venv"
    echo "Then install dependencies with: pip install -r requirements.txt"
    exit 1
fi

echo "Starting AWS Workshop API server (Demo 1) on port 8001..."
echo "Health endpoint: http://localhost:8001/health"
echo "Chat endpoint: http://localhost:8001/chat"


uvicorn main:app \
    --host 0.0.0.0 \
    --port 8001 \
    --reload \
    --log-level info 