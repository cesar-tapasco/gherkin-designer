import time
from typing import List
from playwright.sync_api import Error as PlaywrightError
import pytest
from pathlib import Path
from allure import attach, attachment_type


class ComprehensiveErrorPlugin:
  def get_last_frames(self, tb) -> List[str]:
    """
    Get the last N frames from a traceback object.

    Args:
        tb: Traceback object

    Returns:
        List of formatted traceback strings
    """
    current_path = str(Path.cwd())
    frames = []
    current_tb = tb

    # Collect all frames
    while current_tb is not None:
      frames.append(current_tb)
      current_tb = current_tb.tb_next

    # Format each frame
    formatted_frames = []
    for frame in frames:
      line_number = frame.tb_lineno
      formatted_frame = f"{frame.tb_frame.f_code.co_filename}:{line_number}"

      if (
        f"{current_path}/src" in frame.tb_frame.f_code.co_filename
        or f"{current_path}/tests" in frame.tb_frame.f_code.co_filename
      ):
        ignoreFiles = ["validator.py", "capture_actions.py"]

        if all(ignoreFile not in frame.tb_frame.f_code.co_filename for ignoreFile in ignoreFiles):
          formatted_frames.append(formatted_frame)

    return formatted_frames

  @pytest.hookimpl(tryfirst=True, hookwrapper=True)
  def pytest_runtest_makereport(self, item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
      if call.excinfo is not None:
        error = call.excinfo.value
        if isinstance(
          error,
          (
            PlaywrightError,
            IndexError,
            ValueError,
            KeyError,
            TypeError,
            AttributeError,
            AssertionError,
            FileNotFoundError,
          ),
        ):
          report.outcome = "failed"

          # Get last frames of traceback
          frames = self.get_last_frames(call.excinfo.tb)

          # Get the traceback object
          tb = call.excinfo.tb

          # Extract file path and line number from the traceback
          while tb.tb_next is not None:
            tb = tb.tb_next  # Get to the last frame in traceback

          # file_path = os.path.relpath(tb.tb_frame.f_code.co_filename)
          line_number = tb.tb_lineno

          # Format the error message with file and line information
          if frames:
            main_error_message = frames[0]
          else:
            main_error_message = f"{tb.tb_frame.f_code.co_filename}:{line_number}"

          error_message = (
            f"Error Type: {type(error).__name__}\n"
            f"Error Message: {str(error)}\n"
            f"{main_error_message}\n"
            f"\nLast frames of traceback:\n"
            f"{'-' * 60}\n"
            f"{chr(10).join(frames)}\n"
            f"{'-' * 60}"
          )

          # Combine all information
          error_details = """
                       traceback:
                        {0}
                        {1}
                        {2}
                        """.replace(" ", "")
          separator = "#" * 60
          report.longrepr = error_details.format(separator, error_message, separator)
          attach(
            report.longrepr,
            name="Error details",
            attachment_type=attachment_type.TEXT,
          )
          time.sleep(0.25)
