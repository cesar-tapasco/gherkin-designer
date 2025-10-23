#!/bin/bash
set -e

echo "🚀 Installing Gherkin Designer..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv (Python package manager)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create virtual environment and install dependencies
echo "📥 Installing dependencies..."
UV_VENV_CLEAR=1 uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Install playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install

echo "✅ Installation complete!"
echo ""
echo "To start the Gherkin Designer web interface, run:"
echo "  ./run.sh"
