from datetime import datetime, timedelta
import os
import time
import pytest
import hashlib
from typing import Any
from slugify import slugify
from allure import attach, attachment_type
from src.utils.logger import get_logger

logger = get_logger("hooks")


def attach_hook(pytestconfig, request):
  trace_path = _build_artifact_test_folder(pytestconfig, request, "trace.zip")
  if "URI_BUCKET" in os.environ:
    attach(
      f"<a href='{trace_path}' target='_blank'>Test trace</a>",
      name=trace_path,
      attachment_type=attachment_type.HTML,
    )
    time.sleep(0.25)


def _build_artifact_test_folder(
  pytestconfig: Any, request: pytest.FixtureRequest, folder_or_file_name: str
) -> str:
  output_dir = pytestconfig.getoption("--output").removeprefix(".temp/")

  return os.path.join(
    output_dir,
    _truncate_file_name(slugify(request.node.nodeid)),
    _truncate_file_name(folder_or_file_name),
  )


def _truncate_file_name(file_name: str) -> str:
  if len(file_name) < 256:
    return file_name
  return (
    f"{file_name[:100]}-{hashlib.sha256(file_name.encode()).hexdigest()[:7]}-{file_name[-100:]}"
  )
