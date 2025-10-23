import asyncio
import json
import os
import shlex
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[3]
WORKSPACE_DIR = BASE_DIR
TESTS_DIR = WORKSPACE_DIR / "tests"
TEMP_FEATURE_ROOT = WORKSPACE_DIR / ".temp" / "webapp_features"
FRONTEND_DIR = WORKSPACE_DIR / "src" / "webapp" / "frontend"


app = FastAPI(title="Gherkin Web Runner")

# Track report server process
report_server_process = None


# Pydantic models for request/response
class EnvVarUpdate(BaseModel):
  key: str
  value: str
  file: str  # ".env" or ".users.env"


# Env file paths
ENV_FILE = WORKSPACE_DIR / ".env"
USERS_ENV_FILE = WORKSPACE_DIR / ".users.env"


def parse_env_file(file_path: Path) -> dict:
  """Parse .env file and return dict of key-value pairs."""
  env_vars = {}
  if not file_path.exists():
    return env_vars

  with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
      line = line.strip()
      # Skip comments and empty lines
      if not line or line.startswith("#"):
        continue
      # Parse KEY=VALUE
      if "=" in line:
        key, value = line.split("=", 1)
        env_vars[key.strip()] = value.strip()

  return env_vars


def write_env_file(file_path: Path, updates: dict):
  """Update .env file while preserving comments and structure."""
  if not file_path.exists():
    # Create new file with updates
    with open(file_path, "w", encoding="utf-8") as f:
      for key, value in updates.items():
        f.write(f"{key}={value}\n")
    return

  # Read all lines
  with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

  # Track which keys we've updated
  updated_keys = set()

  # Update existing keys
  new_lines = []
  for line in lines:
    stripped = line.strip()
    # Check if this line has a key we need to update
    if stripped and not stripped.startswith("#") and "=" in stripped:
      key = stripped.split("=", 1)[0].strip()
      if key in updates:
        new_lines.append(f"{key}={updates[key]}\n")
        updated_keys.add(key)
        continue
    new_lines.append(line)

  # Add new keys that weren't in the file
  for key, value in updates.items():
    if key not in updated_keys:
      new_lines.append(f"{key}={value}\n")

  # Write back
  with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)


def ensure_dirs():
  TEMP_FEATURE_ROOT.mkdir(parents=True, exist_ok=True)


def write_feature_file(feature_text: str, create_new_folder: bool = False) -> Path:
  ensure_dirs()
  # Use a fixed folder name by default, or generate unique ID if requested
  feature_id = uuid.uuid4().hex[:8] if create_new_folder else "current"
  feature_dir = TEMP_FEATURE_ROOT / feature_id
  feature_dir.mkdir(parents=True, exist_ok=True)
  feature_path = feature_dir / "scenario.feature"
  feature_path.write_text(feature_text, encoding="utf-8")

  # Create conftest.py with pytest hooks and fixtures
  conftest_py = feature_dir / "conftest.py"
  conftest_content = """import pytest
from config import Config
from src.utils.core.base_api_adapter import APIAdapterBase
from src.utils.logger import get_logger
from playwright.sync_api import BrowserContext
from src.utils.core.test.capture_actions import Capture, log_new_tab
import base64
from dotenv import load_dotenv

config = Config()
logger = get_logger("conftest")

pytest_plugins = [
  'tests.steps.common.common_api_steps',
  'tests.steps.common.common_ui_steps',
]

# =============================================================================
# Playwright Fixtures for UI Testing (Web Runner)
# =============================================================================
# These fixtures configure Playwright to run in HEADED mode for the web runner.
# This allows users to see the browser automation in action when running tests
# from the Gherkin Web Runner UI (http://localhost:8080).
#
# Configuration:
#   - headless=False: Browser window is visible
#   - slow_mo=300: Actions are slowed by 300ms for visibility
#   - viewport: 1920x1080 for consistent screenshots
#   - start-maximized: Browser opens in fullscreen
#
# To customize:
#   - Change slow_mo value (e.g., 100 for faster, 500 for slower)
#   - Set headless=True for background execution
#   - Adjust viewport dimensions for different screen sizes
# =============================================================================

def image_to_data_url(image_path):
  with open(image_path, "rb") as image_file:
    encoded = base64.b64encode(image_file.read()).decode()
    # Determine MIME type based on file extension
    if image_path.lower().endswith(".png"):
      mime_type = "image/png"
    elif image_path.lower().endswith(".jpg") or image_path.lower().endswith(".jpeg"):
      mime_type = "image/jpeg"
    elif image_path.lower().endswith(".gif"):
      mime_type = "image/gif"
    else:
      mime_type = "image/png"  # default

    return f"data:{mime_type};base64,{encoded}"


# @pytest.fixture
# def browser_context_args(ctx, browser_context_args):
#   return {
#       **browser_context_args,
#       "storage_state": ctx.get("storage_state", None),
#   }

@pytest.fixture
def page(context: BrowserContext, request):
  capture = Capture(request.node.name, logger)
  # Listen for new tabs at the context level
  context.on("page", lambda page: log_new_tab(page, capture))
  image_data_url = image_to_data_url("src/resources/images/gherkin-bot.gif")
  page = context.new_page()
  page.set_content(
    f"<div style='text-align: center; padding: 50px; font-family: Arial, sans-serif;'><img src='{image_data_url}'><h2>Loading...</h2></div>"
  )
  yield page
  page.close()


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
  \"\"\"Configure browser to launch in HEADED mode for web runner.\"\"\"
  return {
    **browser_type_launch_args,
    "headless": False,  # ✅ Always headed for web runner visibility
    "slow_mo": 300,     # ⏱️ Slow down actions for visibility (300ms)
    "args": [
      "--ignore-certificate-errors",
    ],
  }

@pytest.fixture(scope='session')
def shared_data():
  data = {}
  yield data
  data.clear()

@pytest.fixture(scope='class')
def ctx(request, shared_data):
  node = request.node
  ctx = {'config': config, 'nodeid': node.nodeid, 'global_vars': shared_data}
  yield ctx
  shared_data = ctx['global_vars']
  logger.debug(f'shared data: {shared_data}')


def pytest_sessionstart(session: pytest.Session):
  \"\"\"Hook that runs at the start of the pytest session.\"\"\"
  is_collect_tests = session.config.option.collectonly
  if is_collect_tests:
    return

  # Initialize a dictionary to store outcomes in the session
  session.test_outcomes = {}

@pytest.fixture
def api_context(ctx):
  adapter = APIAdapterBase(base_url=ctx['config'].BASE_URL, ctx=ctx)
  client = adapter.req
  return {
    'base_url': ctx['config'].BASE_URL,
    'client': client,
    'headers': {},
    'params': {},
    'request_body': None,
    'response': None,
    'response_json': None,
    'global_vars': {},
  }
"""
  conftest_py.write_text(conftest_content, encoding="utf-8")

  # Create minimal test file that just imports scenarios
  test_py = feature_dir / "test_webapp_feature.py"
  test_content = """from src.utils.bdd_extensions import scenarios

scenarios('scenario.feature')
"""
  test_py.write_text(test_content, encoding="utf-8")
  return feature_dir


@app.get("/designer")
def index():
  index_file = FRONTEND_DIR / "index.html"
  if index_file.exists():
    return FileResponse(index_file)
  return HTMLResponse("<h1>Gherkin Runner UI missing</h1>")


@app.get("/samples.js")
def samples_js():
  """Serve the samples.js file."""
  samples_path = FRONTEND_DIR / "samples.js"
  if samples_path.exists():
    return FileResponse(
      samples_path,
      media_type="application/javascript",
      headers={"Content-Type": "application/javascript; charset=utf-8"},
    )
  return HTMLResponse(content="// samples.js not found", status_code=404)


@app.get("/gherkin-steps.js")
def gherkin_steps_js():
  """Serve the gherkin-steps.js file for autocomplete."""
  steps_path = FRONTEND_DIR / "gherkin-steps.js"
  if steps_path.exists():
    return FileResponse(
      steps_path,
      media_type="application/javascript",
      headers={"Content-Type": "application/javascript; charset=utf-8"},
    )
  return HTMLResponse(content="// gherkin-steps.js not found", status_code=404)


@app.get("/api/env")
async def get_env_vars():
  """Get all environment variables from .env and .users.env files."""
  env_vars = parse_env_file(ENV_FILE)
  users_env_vars = parse_env_file(USERS_ENV_FILE)

  return {"files": {".env": env_vars, ".users.env": users_env_vars}}


@app.post("/api/env")
async def update_env_var(env_update: EnvVarUpdate):
  """Update a single environment variable in specified .env file."""
  file_path = ENV_FILE if env_update.file == ".env" else USERS_ENV_FILE

  # Read current values
  current_vars = parse_env_file(file_path)

  # Update the specific key
  current_vars[env_update.key] = env_update.value

  # Write back to file
  write_env_file(file_path, current_vars)

  # Immediately reload environment variables into the process
  load_dotenv(dotenv_path=ENV_FILE, override=True)
  load_dotenv(dotenv_path=USERS_ENV_FILE, override=True)

  return {
    "success": True,
    "key": env_update.key,
    "value": env_update.value,
    "file": env_update.file,
  }


@app.post("/api/env/reload")
async def reload_env_vars():
  """Reload environment variables from .env files into the process environment."""
  # Reload both .env files
  load_dotenv(dotenv_path=ENV_FILE, override=True)
  load_dotenv(dotenv_path=USERS_ENV_FILE, override=True)

  return {"success": True, "message": "Environment variables reloaded"}


@app.get("/api/report/status")
async def get_report_server_status():
  """Check if the report server is currently running."""
  global report_server_process
  is_running = report_server_process is not None and report_server_process.returncode is None
  return {"running": is_running}


@app.post("/api/report/start")
async def start_report_server():
  """Start the report server by running commands/serve.sh."""
  global report_server_process

  # Stop existing server if running
  if report_server_process and report_server_process.returncode is None:
    try:
      report_server_process.terminate()
      await asyncio.sleep(1)
      if report_server_process.returncode is None:
        report_server_process.kill()
    except ProcessLookupError:
      pass
    report_server_process = None

  # Start new server
  serve_script = WORKSPACE_DIR / "commands" / "serve.sh"
  if not serve_script.exists():
    return {"success": False, "message": "serve.sh script not found"}

  try:
    report_server_process = await asyncio.create_subprocess_exec(
      "sh",
      str(serve_script),
      cwd=str(WORKSPACE_DIR),
      stdout=asyncio.subprocess.PIPE,
      stderr=asyncio.subprocess.PIPE,
    )
    return {"success": True, "message": "Report server started", "pid": report_server_process.pid}
  except Exception as e:
    return {"success": False, "message": f"Failed to start server: {str(e)}"}


@app.post("/api/report/stop")
async def stop_report_server():
  """Stop the report server."""
  global report_server_process

  if not report_server_process or report_server_process.returncode is not None:
    return {"success": False, "message": "Report server is not running"}

  try:
    report_server_process.terminate()
    await asyncio.sleep(1)
    if report_server_process.returncode is None:
      report_server_process.kill()
    report_server_process = None
    return {"success": True, "message": "Report server stopped"}
  except ProcessLookupError:
    report_server_process = None
    return {"success": True, "message": "Report server stopped"}
  except Exception as e:
    return {"success": False, "message": f"Failed to stop server: {str(e)}"}


@app.post("/api/run")
async def run_gherkin(payload: dict):
  """
  Accepts JSON: { "feature": "...gherkin...", "tags": [..], "clear_allure_results": bool, "create_new_folder": bool }
  Returns { "run_id": str }
  Clients should connect to /ws/logs?run_id=... for live logs
  """
  feature_text = payload.get("feature", "").strip()
  if not feature_text:
    return {"error": "feature text required"}
  tags = payload.get("tags", [])
  clear_allure_results = payload.get("clear_allure_results", False)
  create_new_folder = payload.get("create_new_folder", False)
  feature_dir = write_feature_file(feature_text, create_new_folder=create_new_folder)
  run_id = feature_dir.name
  # Persist run metadata for WS
  meta = {"tags": tags, "clear_allure_results": clear_allure_results}
  (feature_dir / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
  return {"run_id": run_id}


@app.websocket("/ws/logs")
async def ws_logs(ws: WebSocket, run_id: Optional[str] = None):
  await ws.accept()
  if not run_id:
    await ws.send_text("ERR: run_id query param is required")
    await ws.close()
    return
  feature_dir = TEMP_FEATURE_ROOT / run_id
  if not feature_dir.exists():
    await ws.send_text(f"ERR: run_id {run_id} not found")
    await ws.close()
    return

  test_file = str(feature_dir / "test_webapp_feature.py")
  meta_path = feature_dir / "meta.json"
  tags = []
  clear_allure_results = False
  if meta_path.exists():
    meta = json.loads(meta_path.read_text())
    tags = meta.get("tags", [])
    clear_allure_results = meta.get("clear_allure_results", False)

  # Build pytest command with verbose logging to capture network data
  pytest_args = [
    "pytest",
    test_file,
    "-s",  # No output capture - needed to see print() statements
    "-vv",  # Very verbose to see all output
    "--tb=short",  # Short traceback format
    "-o",
    "addopts=",  # Override ini addopts to avoid forced -q from pytest.ini
    # Disable allure plugin for this ad-hoc run to avoid duplicate --alluredir option
    "-rA",
    "-q",
    "-p",
    "no:warnings",
    "--alluredir",
    ".temp/allure-results",
    "--headed",  # Force headed mode for browser tests
  ]
  # Pass tags as marker expressions
  for tag in tags:
    pytest_args.extend(["-m", tag])

  # Build shell command - conditionally clear allure results if option enabled
  # Use shlex to properly quote arguments with spaces
  cmd_parts = [shlex.quote(arg) for arg in pytest_args]

  if clear_allure_results:
    cmd = f"rm -rf .temp/allure-results && {' '.join(cmd_parts)}"
  else:
    cmd = " ".join(cmd_parts)

  env = os.environ.copy()
  # Ensure Allure and outputs go into an isolated folder
  output_dir = feature_dir / "allure-results"
  env["ALLURE_RESULTS_DIR"] = str(output_dir)
  # Ensure project imports (e.g., config, src.*) resolve during subprocess execution
  env["PYTHONPATH"] = str(WORKSPACE_DIR)
  # Enable webapp cURL emission in the API client
  env["WEBAPP_CURL"] = "1"
  # Enable logging to see debug output including WEBAPP_NET logs
  # env["PYTEST_ADDOPTS"] = env.get("PYTEST_ADDOPTS", "") + " -o log_cli=true -o log_cli_level=DEBUG"

  # Use shell=True to execute the command string
  # Set PYTHONUNBUFFERED to prevent output buffering issues
  env["PYTHONUNBUFFERED"] = "1"

  process = await asyncio.create_subprocess_shell(
    cmd,
    cwd=str(WORKSPACE_DIR),
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE,  # Keep separate to avoid BlockingIOError
    env=env,
  )

  async def stream_output(stream, prefix=""):
    """Stream output from a subprocess stream to WebSocket."""
    buffer = bytearray()
    while True:
      chunk = await stream.read(4096)
      if not chunk:
        # flush the last partial line
        if buffer:
          await ws.send_text(prefix + buffer.decode(errors="ignore"))
          buffer.clear()
        break
      buffer.extend(chunk)
      while True:
        try:
          idx = buffer.index(b"\n")
        except ValueError:
          break
        line = buffer[: idx + 1]
        del buffer[: idx + 1]
        await ws.send_text(prefix + line.decode(errors="ignore"))

  try:
    # Stream both stdout and stderr concurrently
    assert process.stdout is not None
    assert process.stderr is not None

    # Create tasks for streaming both outputs
    stdout_task = asyncio.create_task(stream_output(process.stdout, ""))
    stderr_task = asyncio.create_task(stream_output(process.stderr, ""))

    # Wait for both streams to complete
    await asyncio.gather(stdout_task, stderr_task)

  except WebSocketDisconnect:
    # Client disconnected; terminate subprocess
    try:
      process.terminate()
    except ProcessLookupError:
      pass
    return
  finally:
    rc = await process.wait()
    await ws.send_text(f"\n=== pytest exited with code {rc} ===\n")
    await ws.close()


# Mount the report directory for serving CSS, JS, and other static assets
report_dir = WORKSPACE_DIR / ".temp" / "report-sm"
if report_dir.exists():
  app.mount("/", StaticFiles(directory=str(report_dir), html=True), name="report")


# Serve static assets for the SPA
if FRONTEND_DIR.exists():
  app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
