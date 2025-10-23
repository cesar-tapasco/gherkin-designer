import json
import os
import allure
import functools
from assertpy.assertpy import AssertionBuilder
from src.utils.logger import get_logger
from playwright.sync_api import expect, LocatorAssertions
from jsonschema import validate, ValidationError, Draft202012Validator
from genson import SchemaBuilder
from config import Config


class Validator(AssertionBuilder):
  # Assertion methods from assertpy that should be auto-wrapped with Allure attachments
  _ASSERTPY_METHODS = {
    "is_true",
    "is_false",
    "is_none",
    "is_not_none",
    "is_empty",
    "is_not_empty",
    "is_equal_to",
    "is_not_equal_to",
    "is_same_as",
    "is_not_same_as",
    "is_greater_than",
    "is_greater_than_or_equal_to",
    "is_less_than",
    "is_less_than_or_equal_to",
    "is_between",
    "is_close_to",
    "is_zero",
    "is_not_zero",
    "is_positive",
    "is_negative",
    "is_type_of",
    "is_instance_of",
    "is_length",
    "is_alpha",
    "is_digit",
    "is_lower",
    "is_upper",
    "contains",
    "does_not_contain",
    "contains_only",
    "contains_sequence",
    "contains_duplicates",
    "does_not_contain_duplicates",
    "is_in",
    "is_not_in",
    "starts_with",
    "ends_with",
    "matches",
    "does_not_match",
  }

  def __init__(self, val, description=""):
    self.logger = get_logger(self.__class__.__name__)
    self.config: Config = Config()
    self._skip_allure = False  # Flag to prevent recursive Allure attachments
    super().__init__(val, description)

  def __getattribute__(self, name):
    """
    Intercept method calls to automatically wrap assertpy assertion methods with Allure attachments.
    """
    attr = object.__getattribute__(self, name)

    # Skip internal methods, private methods, and non-callable attributes
    if name.startswith("_") or not callable(attr):
      return attr

    # Skip if we're already in an Allure attachment to prevent recursion
    skip_allure = object.__getattribute__(self, "_skip_allure")
    if skip_allure:
      return attr

    # Check if this is an assertpy assertion method that should be auto-wrapped
    assertpy_methods = object.__getattribute__(self, "_ASSERTPY_METHODS")
    if name in assertpy_methods:
      return self._wrap_assertion_with_allure(name, attr)

    return attr

  def _wrap_assertion_with_allure(self, method_name, method):
    """
    Wrap an assertion method with Allure attachment logic.

    Args:
      method_name: Name of the assertion method
      method: The actual method to wrap

    Returns:
      Wrapped method that adds Allure attachments
    """

    @functools.wraps(method)
    def wrapper(*args, **kwargs):
      # Format validation name based on method name and arguments
      validation_name = self._format_validation_name(method_name, args, kwargs)

      try:
        # Temporarily set flag to prevent recursive Allure attachments
        self._skip_allure = True
        result = method(*args, **kwargs)
        self._skip_allure = False

        # Attach success result
        details = self._extract_validation_details(method_name, args, kwargs, None)
        self._attach_validation_result(
          validation_name=validation_name, status="PASSED", details=details
        )
        return result
      except AssertionError as e:
        self._skip_allure = False
        # Attach failure result
        details = self._extract_validation_details(method_name, args, kwargs, e)
        self._attach_validation_result(
          validation_name=validation_name, status="FAILED", details=details
        )
        raise

    return wrapper

  def _format_validation_name(self, method_name, args, kwargs):
    """
    Format a readable validation name based on the method and its arguments.
    """
    # Convert method name to readable format (e.g., is_equal_to -> Equal To)
    readable_name = (
      method_name.replace("_", " ").replace("is ", "").replace("does not ", "not ").title()
    )

    # Add first argument if present (typically the expected value)
    if args and len(args) > 0:
      first_arg = args[0]
      if isinstance(first_arg, str) and len(first_arg) > 50:
        first_arg = first_arg[:47] + "..."
      return f"{readable_name}: {first_arg}"

    return readable_name

  def _extract_validation_details(self, method_name, args, kwargs, error=None):
    """
    Extract relevant details from the validation for the Allure attachment.
    """
    details = {"actual": self.val}

    # Add expected value if present in arguments
    if args and len(args) > 0:
      details["expected"] = args[0]

    # Add any keyword arguments
    if kwargs:
      details.update(kwargs)

    # Add error message if validation failed
    if error:
      details["error"] = str(error)

    return details

  def _truncate_string(self, input_str, max_length):
    # Check if the input string is longer than the maximum allowed length
    if len(input_str) > max_length:
      # Return the truncated string with an ellipsis at the end
      return input_str[: max_length - 3] + "..."
    else:
      # Return the original string if it's within the limit
      return input_str

  def _attach_validation_result(self, validation_name: str, status: str, details: dict = None):
    """
    Attach validation results to Allure report.

    Args:
      validation_name: Name of the validation being performed
      status: "PASSED" or "FAILED"
      details: Additional details to include in the attachment
    """
    result = {
      "validation": validation_name,
      "status": status,
      "description": self.description if self.description else "No description provided",
    }

    if details:
      result.update(details)

    # Format the attachment content
    attachment_content = json.dumps(result, indent=2)

    # Attach to Allure with appropriate name
    allure.attach(
      attachment_content,
      name=f"Validation: {validation_name} - {status}",
      attachment_type=allure.attachment_type.JSON,
    )

  def generate_json_schema(self, json_data, file_path=None):
    builder = SchemaBuilder()
    if isinstance(json_data, str):
      json_data = json.loads(json_data)
    builder.add_object(json_data)
    schema = builder.to_schema()
    if file_path is None:
      print(json.dumps(schema, indent=self.config.INDENT))
      return
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
      json.dump(schema, f, indent=self.config.INDENT)

  def to_has_schema(self, schema, replace=False):
    schema_name = schema if isinstance(schema, str) else "inline_schema"
    if isinstance(schema, str):
      file_name = f"src/resources/schemas/{schema}_schema.json"
      if replace:
        os.remove(file_name)
      if not os.path.isfile(file_name):
        self.generate_json_schema(self.val, file_path=file_name)
      with open(file_name, "r") as f:
        schema = json.load(f)
    v = Draft202012Validator(schema)
    errors = sorted(v.iter_errors(self.val), key=lambda e: e.path)
    error_list = []
    for error in errors:
      in_sub_error = False
      for suberror in sorted(error.context, key=lambda e: e.schema_path):
        in_sub_error = True
        error_list.append(f"{list(suberror.schema_path)} {suberror.message}")
      if not in_sub_error:
        error_list.append(f"{error.json_path} {self._truncate_string(error.message, 50)}")
    if len(error_list) > 0:
      self._attach_validation_result(
        validation_name="Schema Validation",
        status="FAILED",
        details={"schema": schema_name, "errors": error_list, "error_count": len(error_list)},
      )
      raise AssertionError("\n ".join(error_list))
    else:
      self._attach_validation_result(
        validation_name="Schema Validation",
        status="PASSED",
        details={"schema": schema_name},
      )
      self.is_true()
    return self

  def to_not_has_schema(self, schema):
    try:
      validate(instance=self.val, schema=schema)
      self.is_false()
    except ValidationError as e:
      self.logger.info(f"Schema validation error: {e}")
      self.is_true()
    return self

  def has_code_status(self, expected_code):
    if self.val.status == expected_code:
      self._attach_validation_result(
        validation_name="Status Code Validation",
        status="PASSED",
        details={"expected": expected_code, "actual": self.val.status},
      )
      self.is_true()
    else:
      self.logger.info(f"Expected status code '{expected_code}', but got '{self.val.status}'")
      self._attach_validation_result(
        validation_name="Status Code Validation",
        status="FAILED",
        details={"expected": expected_code, "actual": self.val.status},
      )
      raise AssertionError(f"Expected status code '{expected_code}', but got '{self.val.status}'")
    return self

  def has_ok_status(self):
    if self.val.res.is_success:
      self._attach_validation_result(
        validation_name="Success Status Validation",
        status="PASSED",
        details={"expected": "200-226", "actual": self.val.status},
      )
      self.is_true()
    else:
      message = f"Expected status code should be between 200 and 226, but got '{self.val.status}'"
      self._attach_validation_result(
        validation_name="Success Status Validation",
        status="FAILED",
        details={"expected": "200-226", "actual": self.val.status},
      )
      raise AssertionError(message)
    return self

  def has_error_status(self):
    if self.val.res.is_error:
      self._attach_validation_result(
        validation_name="Error Status Validation",
        status="PASSED",
        details={"expected": "400-599", "actual": self.val.status},
      )
      self.is_true()
    else:
      message = f"Expected status code should be between 400 and 599, but got '{self.val.status}'"
      self._attach_validation_result(
        validation_name="Error Status Validation",
        status="FAILED",
        details={"expected": "400-599", "actual": self.val.status},
      )
      raise AssertionError(message)
    return self

  def has_response_text(self, expected_text):
    if self.val.status_text == expected_text:
      self._attach_validation_result(
        validation_name="Response Text Validation",
        status="PASSED",
        details={"expected": expected_text, "actual": self.val.status_text},
      )
      self.is_true()
    else:
      self._attach_validation_result(
        validation_name="Response Text Validation",
        status="FAILED",
        details={"expected": expected_text, "actual": self.val.status_text},
      )
      raise AssertionError(f"Expected status text '{expected_text}', but got '{self.val.status}'")
    return self

  def locator(self) -> LocatorAssertions:
    return expect(self.val)
