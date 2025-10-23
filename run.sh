#!/bin/bash
set -e

# Configuration
REPO_URL="https://github.com/cesar-tapasco/gherkin-designer/releases/download/1.0/gherkin-designer.zip"
DOWNLOAD_DIR="/tmp/gherkin-designer-download"
INSTALL_DIR="$HOME/gherkin-designer"

echo "🚀 Gherkin Designer Installer"
echo ""

# Check if unzip is installed
# if ! command -v unzip &> /dev/null; then
#     echo "❌ Error: unzip is not installed"
#     echo "Please install unzip and try again"
#     exit 1
# fi

# Create temporary download directory
echo "📁 Creating temporary directory..."
mkdir -p "$DOWNLOAD_DIR"
cd "$DOWNLOAD_DIR"

# Download the ZIP file
echo "📥 Downloading Gherkin Designer..."
if curl -LsSf "$REPO_URL" -o gherkin-designer.zip; then
    echo "✅ Download successful"
else
    echo "❌ Failed to download. Please check your internet connection"
    exit 1
fi

# Extract the ZIP file into a subdirectory
echo "📦 Extracting files..."
mkdir -p extracted
cd extracted
unzip -q -o ../gherkin-designer.zip

# Move to installation directory
echo "📂 Installing to $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
# Copy all files except __MACOSX metadata
find . -maxdepth 1 ! -name "." ! -name "__MACOSX" -exec cp -r {} "$INSTALL_DIR/" \;
cd "$INSTALL_DIR"

# Clean up temporary files
echo "🧹 Cleaning up..."
rm -rf "$DOWNLOAD_DIR"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv (Python package manager)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create virtual environment and install dependencies
echo "📥 Installing dependencies..."
UV_VENV_CLEAR=1 uv venv
# source .venv/bin/activate
export PATH="$PWD/.venv/bin:$PATH"
uv pip install -r requirements.txt

# Install playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 Starting Gherkin Designer..."
echo ""

# Start the web runner
python cli.py start-web-runner --port 9000
