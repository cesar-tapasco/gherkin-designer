#!/bin/bash
sh install.sh
set -e

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run ./install.sh first"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Start the web runner
echo "🚀 Starting Gherkin Designer..."
python cli.py start-web-runner --port 9000
