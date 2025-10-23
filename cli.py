import re
import subprocess
import typer
import webbrowser
import time
import threading
from typing import List, Optional

app = typer.Typer()


def natural_sort_key(s):
  """
  Genera una clave para la ordenación natural.
  Divide la cadena en fragmentos de texto y números.
  Convierte los números a enteros para una comparación numérica correcta.
  """
  parts = [part for part in re.split(r"(\d+)", s) if part]
  key_parts = []
  for part in parts:
    if part.isdigit():
      key_parts.append(int(part))
    else:
      key_parts.append(part.lower())
  return key_parts


def collect_tests(tags=None):
  """Collect all test cases using pytest --collect-only."""
  command = ["pytest", "--collect-only"]
  if tags:
    command += ["-m", "and ".join(tags)]
  result = subprocess.run(command, capture_output=True, text=True)
  lines = result.stdout.splitlines()

  # Filter lines that contain test function names (these usually have "::")
  tests = [line.strip() for line in lines if "::" in line and not line.startswith(" ")]
  return tests


def process_specs(specs: Optional[List[str]]) -> List[str]:
  """Process specs input, splitting by comma and removing empty elements."""
  processed_specs = []

  if specs:
    for spec in specs:
      # Split the spec by commas, strip whitespace, and remove empty strings
      split_specs = [s.strip() for s in spec.split(",") if s.strip()]
      processed_specs.extend(split_specs)

  return processed_specs

def collect_and_find_specs(specs, tests):
  specs_found = []
  specs_to_search = process_specs(specs)
  if specs_to_search:
    typer.echo("Collected Test Cases:")
    for spec in specs_to_search:
      matched = [test for test in tests if spec in test]
      if matched:
        specs_found.extend(matched)
        typer.echo(f"Tests found matching the spec: {spec}")
        # typer.echo("\n".join([f"- {test}" for test in matched]))
      else:
        typer.echo(f"No tests found matching the spec: {spec}")
  return specs_found


@app.command()
def list_tests(
  specs: Optional[List[str]] = typer.Option(None),
  tags: Optional[List[str]] = typer.Option(None),
):
  """List all test cases using pytest --collect-only."""
  tests = collect_tests(tags)
  if specs:
    collect_and_find_specs(specs, tests)
  else:
    if tests:
      typer.echo("Collected Test Cases:")
    else:
      typer.echo("No test cases found.")


@app.command()
def start_web_runner(
  port: int = typer.Option(8765, "--port", "-p", help="Port to run the Gherkin Web Runner on."),
  no_browser: bool = typer.Option(False, "--no-browser", help="Do not automatically open browser."),
):
  """Start the Gherkin Web Runner FastAPI application."""
  try:
    typer.echo(f"Starting Gherkin Web Runner on http://localhost:{port}")

    # Open browser in background thread if requested
    if not no_browser:

      def open_browser():
        time.sleep(1)  # Give server time to start
        try:
          webbrowser.open(f"http://localhost:{port}")
        except Exception:
          pass  # Silently fail if browser can't be opened

      browser_thread = threading.Thread(target=open_browser, daemon=True)
      browser_thread.start()

    # Start uvicorn server
    subprocess.run(
      ["uvicorn", "src.webapp.backend.app:app", "--host", "0.0.0.0", "--port", str(port)],
      check=True,
    )

  except KeyboardInterrupt:
    typer.echo("\nShutting down Gherkin Web Runner...")
  except subprocess.CalledProcessError as e:
    typer.echo(f"Error starting Gherkin Web Runner: {e}", err=True)
    raise typer.Exit(code=1)
  except Exception as e:
    typer.echo(f"Unexpected error: {e}", err=True)
    raise typer.Exit(code=1)


if __name__ == "__main__":
  app()
