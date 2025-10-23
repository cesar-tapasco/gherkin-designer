#!/bin/bash
set -e

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv (Python package manager)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create virtual environment and install dependencies
echo "📥 Installing dependencies..."
UV_VENV_CLEAR=1 uv venv


# Extract the ZIP file into a subdirectory
echo "📦 Extracting files..."
mkdir -p extracted
cd extracted
# unzip -q -o ../gherkin-designer.zip
echo '
import os
import zipfile
import urllib.request

# ============================================================
# CONFIGURATION: Set your zip file URL here (or leave empty to upload manually)
# ============================================================
ZIP_URL = "https://github.com/cesar-tapasco/gherkin-designer/releases/download/1.0/gherkin-designer.zip"

# ============================================================

def download_and_extract_from_url(url):
    """Download zip from URL and extract it."""
    print(f"Downloading from URL: {url}")
    zip_filename = "project.zip"

    try:
        urllib.request.urlretrieve(url, zip_filename)
        print(f"✓ Downloaded successfully: {zip_filename}")
        return zip_filename
    except Exception as e:
        print(f"✗ Error downloading file: {e}")
        return None

def extract_project(zip_filename):
    """Extract the zip file and navigate to project directory."""
    print("\\nExtracting files...")
    with zipfile.ZipFile(zip_filename, "r") as zip_ref:
        zip_ref.extractall(".")
    print("✓ Extraction complete!")

    # Find the extracted directory
    extracted_dirs = [d for d in os.listdir(".") if os.path.isdir(d) and not d.startswith(".")]
    if extracted_dirs:
        project_dir = extracted_dirs[0] if "gherkin" in extracted_dirs[0].lower() else extracted_dirs[0]
        print(f"\\nProject directory: {project_dir}")
    else:
        project_dir = "."
        print("\\nUsing current directory as project directory")

    # Change to project directory
    os.chdir(project_dir)
    print(f"Current working directory: {os.getcwd()}")
    return project_dir

# Main logic
print("="*60)
print("Gherkin Designer - Project Setup")
print("="*60 + "\\n")

zip_filename = None


print("📦 Using URL method...")
zip_filename = download_and_extract_from_url(ZIP_URL)

if zip_filename:
    project_dir = extract_project(zip_filename)
    print("\\n" + "="*60)
    print("✓ Project setup complete!")
    print("="*60)
    print("\\nProject contents:")
else:
    print("\\n✗ Failed to get project files. Please check the URL or try manual upload.")

' > extract_and_navigate.py

uv run python extract_and_navigate.py

export PATH="$PWD/.venv/bin:$PATH"
uv pip install -r requirements.txt


# Install playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium
playwright install-deps chromium

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 Starting Gherkin Designer..."
echo ""

uv run cli.py start-web-runner --port 9000