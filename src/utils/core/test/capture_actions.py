import json
import allure


class Capture:
  def __init__(self, scenario, logger) -> None:
    self.scenario = scenario
    self.logger = logger

  def log_action(self, action_type, details):
    self.logger.debug(f"{self.scenario} ==== Action: {action_type}, Details: {details}")
    self._attach_action_to_allure(action_type, details)

  def _attach_action_to_allure(self, action_type, details):
    """
    Attach captured action details to Allure report.

    Args:
      action_type: Type of action performed (e.g., 'click', 'fill', 'goto')
      details: Dictionary containing action details (args, kwargs, locator info)
    """
    # Create sanitized details for Allure attachment
    sanitized_details = self._sanitize_details(details)

    action_data = {
      "scenario": self.scenario,
      "action": action_type,
      "timestamp": None,  # Could add timestamp if needed
      "details": sanitized_details,
    }

    # Format the attachment content
    attachment_content = json.dumps(action_data, indent=2, default=str)

    # Attach to Allure with descriptive name
    allure.attach(
      attachment_content,
      name=f"Action: {action_type}",
      attachment_type=allure.attachment_type.JSON,
    )

  def _sanitize_details(self, details):
    """
    Sanitize details to make them JSON-serializable and readable.

    Args:
      details: Dictionary containing action details

    Returns:
      Sanitized dictionary safe for JSON serialization
    """
    sanitized = {}

    for key, value in details.items():
      if key == "locator":
        # Extract locator selector string if available
        try:
          sanitized[key] = str(value)
        except Exception:
          sanitized[key] = "<locator object>"
      elif key == "args":
        # Convert args tuple to list and sanitize each item
        sanitized[key] = [self._sanitize_value(arg) for arg in value]
      elif key == "kwargs":
        # Sanitize each kwarg value
        sanitized[key] = {k: self._sanitize_value(v) for k, v in value.items()}
      else:
        sanitized[key] = self._sanitize_value(value)

    return sanitized

  def _sanitize_value(self, value):
    """
    Sanitize a single value for JSON serialization.

    Args:
      value: Value to sanitize

    Returns:
      JSON-serializable representation of the value
    """
    # Handle common Playwright objects
    if hasattr(value, "__class__") and "playwright" in str(value.__class__):
      return str(value)

    # Handle basic types
    if isinstance(value, (str, int, float, bool, type(None))):
      return value

    # Handle lists and tuples
    if isinstance(value, (list, tuple)):
      return [self._sanitize_value(item) for item in value]

    # Handle dictionaries
    if isinstance(value, dict):
      return {k: self._sanitize_value(v) for k, v in value.items()}

    # Fallback to string representation
    try:
      return str(value)
    except Exception:
      return "<non-serializable object>"


# Patch sync methods for Page and Locator
def patch_page(page, capture):
  def patch_method(method_name):
    original_method = getattr(page, method_name)

    def patched_method(*args, **kwargs):
      capture.log_action(method_name, {"args": args, "kwargs": kwargs})
      return original_method(*args, **kwargs)

    setattr(page, method_name, patched_method)

  # Patch the necessary Playwright methods
  methods_to_patch = ["goto", "click", "fill", "type", "hover", "check"]
  for method in methods_to_patch:
    patch_method(method)

  # Patch Locator interactions
  original_locator = page.locator

  def patched_locator(*args, **kwargs):
    locator = original_locator(*args, **kwargs)
    patch_locator(locator, capture)
    return locator

  page.locator = patched_locator


def patch_locator(locator, capture):
  def patch_method(method_name):
    original_method = getattr(locator, method_name)

    def patched_method(*args, **kwargs):
      capture.log_action(method_name, {"args": args, "kwargs": kwargs, "locator": locator})
      return original_method(*args, **kwargs)

    setattr(locator, method_name, patched_method)

  methods_to_patch = ["click", "fill", "type", "hover", "check", "select_option"]
  for method in methods_to_patch:
    patch_method(method)


# Function to log new tabs
def log_new_tab(popup_page, capture):
  capture.log_action("new_tab", {"new_tab_url": popup_page.url})
  # Patch the new tab's methods if you want to capture interactions in the new tab
  patch_page(popup_page, capture)
