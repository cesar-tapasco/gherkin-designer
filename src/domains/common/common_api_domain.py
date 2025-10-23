import datetime
import difflib
import json
import mimetypes
import os
import re
import sys
from typing import IO, Any, Dict, List, Optional, Tuple, Union
import uuid
from curlify2 import Curlify
from deepdiff import DeepDiff
import httpx
from dotenv import load_dotenv
from faker import Faker
from src.utils.core.api import APIX
from src.utils.core.base_domain import DomainBase
from config import ConfigDict
from src.utils.core.magic_response import MagicResponse
from src.utils.core.base_api_adapter import APIAdapterBase


class CommonApiDomain(DomainBase):
  # --- Constants ---
  VISUAL_DIFF_THRESHOLD = 60  # String length threshold for visual diff
  VISUAL_DIFF_CONTEXT = 3  # Lines of context in unified diff

  def __init__(self, ctx: ConfigDict = None, api_context: dict = None):
    self.api_context = api_context
    self.api_adapter = APIAdapterBase(ctx=ctx)
    self.faker = Faker()
    super().__init__(None, ctx)

  def _resolve_jq_expression(self, jq_filter: str, is_list=False) -> str:
    """Evaluates a jq filter against the last response JSON."""
    if not jq_filter:
      raise AssertionError("$ prefix found but no filter provided.")

    response_json = self._get_response_json()

    # Handle custom functions (random, faker)
    jq_filter = self.resolve_variable(jq_filter)
    if self._is_random_function(jq_filter):
      return self._handle_random_function(jq_filter, response_json)
    elif self._is_faker_function(jq_filter):
      return self._handle_faker_function(jq_filter)

    # Handle regular jq expressions
    return self._execute_jq_filter(jq_filter, response_json, is_list)

  def _get_response_json(self):
    """Gets the response JSON from the API context."""
    response_json = self.api_context.get("response_json")
    if response_json is None:
      response_json = self.api_context.get("response")._text
    return response_json

  def _is_random_function(self, jq_filter: str) -> bool:
    """Checks if the jq filter is a custom random() function."""
    return jq_filter.startswith("random(") and jq_filter.endswith(")")

  def _is_faker_function(self, jq_filter: str) -> bool:
    """Checks if the jq filter is a custom faker() function."""
    return jq_filter.startswith("faker(") and jq_filter.endswith(")")

  def _handle_random_function(self, jq_filter: str, response_json) -> str:
    """Handles the custom random() function processing."""
    try:
      inner_expression = jq_filter[7:-1]  # Remove "random(" and ")"
      array_result = self.jq(response_json).all(inner_expression)

      self._validate_random_array(array_result)

      random_element = self.gen.random.choice(array_result)
      return random_element if random_element is not None else "null"

    except ValueError as e:
      return self._raise_random_error(jq_filter, e, response_json)
    except Exception as e:
      raise AssertionError(
        f"An unexpected error occurred while processing random() expression '{jq_filter}': {e}"
      )

  def _handle_faker_function(self, jq_filter: str) -> str:
    """Handles the custom faker() function processing."""
    try:
      inner_expression = jq_filter[6:-1]  # Remove "faker(" and ")"
      faker_method = inner_expression.strip()

      fake_value = self._generate_faker_value(faker_method)
      return fake_value

    except Exception as e:
      raise AssertionError(
        f"An unexpected error occurred while processing faker() expression '{jq_filter}': {e}"
      )

  def _validate_random_array(self, array_result):
    """Validates that the random() function result is a non-empty array."""
    if not isinstance(array_result, list) or len(array_result) == 0:
      raise AssertionError(
        f"random() requires a non-empty array, but got: {type(array_result)} with {len(array_result) if isinstance(array_result, list) else 'non-list'} elements"
      )

  def _raise_random_error(self, jq_filter: str, error: ValueError, response_json):
    """Raises a detailed error for random() function processing failures."""
    response_preview = json.dumps(response_json, indent=2)[:500]
    raise AssertionError(
      f"Error processing random() expression '{jq_filter}': {error}\n"
      f"Response JSON (preview):\n{response_preview}"
    )

  def _execute_jq_filter(self, jq_filter: str, response_json, is_list: bool) -> str:
    """Executes a regular jq filter against the response JSON."""
    try:
      jq_result = self._apply_jq_filter(jq_filter, response_json, is_list)
      resolved_value = jq_result if jq_result is not None else "null"
      return resolved_value
    except ValueError as e:
      return self._raise_jq_error(jq_filter, e, response_json)
    except Exception as e:
      raise AssertionError(f"An unexpected error occurred applying jq filter '{jq_filter}': {e}")

  def _apply_jq_filter(self, jq_filter: str, response_json, is_list: bool):
    """Applies the jq filter to the response JSON."""
    if not is_list:
      return self.jq(response_json).one(jq_filter)
    else:
      return self.jq(response_json).all(jq_filter)

  def _raise_jq_error(self, jq_filter: str, error: ValueError, response_json):
    """Raises a detailed error for jq filter processing failures."""
    response_preview = json.dumps(response_json, indent=2)[:500]
    raise AssertionError(
      f"Error processing jq filter '{jq_filter}': {error}\n"
      f"Response JSON (preview):\n{response_preview}"
    )

  def _find_variable_value(self, var_name: str) -> Tuple[bool, Optional[str]]:
    """
    Looks up a variable name in global_vars and then config attributes.

    Returns:
        A tuple (found: bool, value: Optional[str]). Value is stringified if found.
    """
    global_vars = self.ctx.get("global_vars", {})
    config = self.ctx.get("config")

    # 1. Check context variables (highest priority)
    if var_name in global_vars:
      return True, str(global_vars[var_name])

    # 2. Check Config instance attributes
    if config and hasattr(config, var_name):
      config_val = getattr(config, var_name)
      return True, str(config_val)

    # 3. Not found in either source
    return False, None

  def _get_value_for_placeholder(
    self,
    var_name: str,
    placeholder: str,
    replacements: Dict[str, str],
    not_found_placeholders: List[str],
  ) -> None:
    """
    Resolves a single variable by its name and updates tracking collections.

    It first checks for special dynamic variables (newUuid, newDate, faker).
    If not a special variable, it attempts to find it using `_find_variable_value`.
    Updates `replacements` if found, or `not_found_placeholders` if not.
    Skips if the placeholder has already been processed.

    Args:
        var_name (str): The name of the variable (e.g., "BASE_URL").
        placeholder (str): The full placeholder string (e.g., "{{BASE_URL}}").
        replacements (Dict[str, str]): Dictionary to store resolved placeholders.
        not_found_placeholders (List[str]): List to track unresolved placeholders.
    """
    # Skip if this exact placeholder was already processed in this run
    if placeholder in replacements or placeholder in not_found_placeholders:
      return

    # Handle special dynamic variables
    if var_name == "newUuid":
      replacements[placeholder] = str(uuid.uuid4())
      return
    if var_name == "newDate":
      replacements[placeholder] = self.get_current_utc_isoformat_z()
      return

    # Handle faker variables (e.g., {{faker.name}}, {{faker.word}}, {{faker.company}})
    if var_name.startswith("faker."):
      faker_method = var_name[6:]  # Remove "faker." prefix
      try:
        fake_value = self._generate_faker_value(faker_method)
        replacements[placeholder] = fake_value
        return
      except AttributeError:
        not_found_placeholders.append(placeholder)
        return

    # Handle other variables from context (scenario, global, config)
    found, var_value = self._find_variable_value(var_name)
    if found:
      replacements[placeholder] = str(var_value)  # Ensure value is string
    else:
      not_found_placeholders.append(placeholder)

  def _generate_faker_value(self, faker_method: str) -> str:
    """
    Generates a fake value using Faker library based on the method name.

    Args:
        faker_method (str): The faker method to call (e.g., "name", "word", "company")

    Returns:
        str: The generated fake value

    Raises:
        AttributeError: If the faker method doesn't exist
    """
    # Mapping of faker methods to their generation functions
    FAKER_METHODS = {
      "word": lambda: self.faker.word(),
      "words": lambda: " ".join(self.faker.words(nb=3)),
      "sentence": lambda: self.faker.sentence(),
      "company": lambda: self.faker.company(),
      "name": lambda: self.faker.name(),
      "email": lambda: self.faker.email(),
      "address": lambda: self.faker.address(),
      "phone_number": lambda: self.faker.phone_number(),
      "uuid": lambda: str(self.faker.uuid4()),
    }

    try:
      # First try to find the method in our mapping
      if faker_method in FAKER_METHODS:
        return str(FAKER_METHODS[faker_method]())

      # If not in mapping, try dynamic method calling
      if hasattr(self.faker, faker_method):
        method = getattr(self.faker, faker_method)
        if not callable(method):
          raise AttributeError(f"Faker attribute '{faker_method}' is not callable")

        # Use introspection to determine how to call the method
        fake_value = self._call_faker_method_safely(method, faker_method)
        return str(fake_value)

      # Method not found
      raise AttributeError(f"Faker method '{faker_method}' not found")

    except Exception as e:
      if isinstance(e, AttributeError):
        raise  # Re-raise AttributeError as-is
      raise AttributeError(f"Error generating faker value for method '{faker_method}': {e}")

  def _call_faker_method_safely(self, method, faker_method: str):
    """
    Safely calls a faker method, handling methods that require parameters.

    Args:
        method: The faker method to call
        faker_method (str): The method name for error reporting

    Returns:
        The result of calling the faker method
    """
    try:
      import inspect

      sig = inspect.signature(method)
      params = sig.parameters

      # If method has no parameters, call it directly
      if len(params) == 0:
        return method()

      # Parameter handling strategies for different faker methods
      PARAM_STRATEGIES = {
        "random_int": lambda: method(min=1, max=100),
        "random_digit": lambda: method(min=1, max=100),
        "random_element": lambda: method(["option1", "option2", "option3"]),
        "text": lambda: method(max_nb_chars=50),
        "paragraph": lambda: method(nb_sentences=3),
        "date": lambda: method(),
        "time": lambda: method(),
        "datetime": lambda: method(),
        "word_list": lambda: method(),
        "sentence_list": lambda: method(),
      }

      # Try to find a strategy for this method
      if faker_method in PARAM_STRATEGIES:
        return PARAM_STRATEGIES[faker_method]()

      # For unknown parameterized methods, try calling without arguments first
      # This works for many faker methods that have optional parameters
      try:
        return method()
      except TypeError:
        # If that fails, provide helpful error with parameter info
        param_names = list(params.keys())
        raise AttributeError(
          f"Faker method '{faker_method}' requires parameters that aren't handled yet. "
          f"Parameters: {param_names}"
        )

    except ImportError:
      # Fallback if inspect isn't available (shouldn't happen in normal Python)
      return method()

  def _apply_all_replacements(self, text: str, replacements: Dict[str, str]) -> str:
    """
    Applies all resolved variable replacements to the input text.

    Args:
        text (str): The original text template.
        replacements (Dict[str, str]): A dictionary of placeholders and their resolved values.

    Returns:
        str: The text with all placeholders replaced.
    """
    for placeholder, final_value in replacements.items():
      text = text.replace(placeholder, final_value)
    return text

  def _resolve_placeholder_variables(self, value_template: str) -> str:
    """
    Resolves {{VAR_NAME}} placeholders in a string using dynamic values,
    scenario/global variables, and Config attributes.

    Args:
        value_template (str): The string template containing placeholders.

    Returns:
        str: The string with placeholders resolved.

    Raises:
        AssertionError: If one or more variables could not be resolved.
    """
    # Find all occurrences of the {{VAR_NAME}} pattern
    # Using list() to consume the iterator immediately
    matches = list(re.finditer(r"\{\{(\w+)\}\}", value_template))

    if not matches:
      return value_template  # No variables to resolve, return original template

    replacements: Dict[str, str] = {}  # Stores {placeholder: resolved_value}
    not_found_placeholders: List[str] = []  # Stores unresolved placeholders

    # Iterate through each found placeholder match
    for match in matches:
      placeholder = match.group(0)  # The full placeholder, e.g., "{{BASE_URL}}"
      var_name = match.group(1)  # The variable name, e.g., "BASE_URL"

      # Delegate the resolution of this specific variable
      self._get_value_for_placeholder(var_name, placeholder, replacements, not_found_placeholders)

    # If any variables were not found, raise an error listing all of them
    if not_found_placeholders:
      # Use set to get unique placeholders, then sort for consistent error messages
      unique_missing_vars = sorted(set(not_found_placeholders))
      missing_vars_str = ", ".join(unique_missing_vars)
      raise AssertionError(
        f"Variable(s) {missing_vars_str} could not be resolved. "
        f"Checked scenario/global variables and Config attributes."
      )

    # Apply all successfully resolved replacements to the original template
    return self._apply_all_replacements(value_template, replacements)

  def get_current_utc_isoformat_z(self):
    """
    Gets the current time in UTC and formats it as an ISO 8601 string
    with 'Z' indicating UTC and microsecond precision.
    """
    # Get the current time, explicitly setting the timezone to UTC
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    # Format the datetime object into ISO 8601 format
    # timespec='microseconds' ensures the full precision is included
    iso_format_string = now_utc.isoformat(timespec="microseconds")
    # The default isoformat for UTC includes '+00:00'. Replace it with 'Z'.
    if iso_format_string.endswith("+00:00"):
      iso_format_string = iso_format_string[:-6] + "Z"
    return iso_format_string

  def resolve_variable(self, value_template: Any, is_list=False) -> Any:
    """
    Resolves variables like {{VAR_NAME}} or jq expressions like $.filter within a string.

    Resolution order:
    1. Check for '$' prefix. If found, evaluate the filter against the last response JSON.
    2. If no '$' prefix, resolve {{VAR_NAME}} placeholders using context and config.

    Args:
        value_template: The value to process. If it's a string, it may contain
                        {{VAR_NAME}} placeholders or start with $.

    Returns:
        The resolved value. If the input was not a string, it's returned unchanged.
        If it was a string, returns the resolved string.

    Raises:
        AssertionError: If a variable or jq filter cannot be resolved/evaluated,
                        or if the input format is invalid (e.g., '$' with no filter).
    """
    # 1. Handle non-string input directly
    if not isinstance(value_template, str):
      return value_template

    # 2. Handle jq expressions
    if value_template.startswith("$"):
      value_template = value_template.replace("'", '"')  # Remove the $ prefix
      jq_filter = value_template[1:]
      return self._resolve_jq_expression(jq_filter, is_list)

    # 3. Handle placeholder variables (only if {{ is present)
    # Optimization: avoid regex if no {{ is present
    if "{{" in value_template and "}}" in value_template:
      return self._resolve_placeholder_variables(value_template)
    else:
      # If not jq and no placeholders detected, return original string
      return value_template

  def resolve_variables_recursive(self, data):
    """Recursively resolves {{VAR}} in strings within complex data structures (dicts, lists)."""
    if isinstance(data, dict):
      return {k: self.resolve_variables_recursive(v) for k, v in data.items()}
    elif isinstance(data, list):
      return [self.resolve_variables_recursive(item) for item in data]
    elif isinstance(data, str):
      return self.resolve_variable(data)
    else:
      return data

  def _resolve_request_path(self, path_template: str) -> str:
    """Resolves {{variables}} and then {path_params} in the path."""
    # 1. Resolve template variables like {{DOMAIN}}
    try:
      resolved_template = self.resolve_variable(path_template)
    except AssertionError as e:
      raise AssertionError(f"Failed to resolve variables in path template '{path_template}': {e}")

    # 2. Resolve path parameters like {user_id} using global_vars
    def replace_param(match):
      param_name = match.group(1)
      value = self.ctx.get("global_vars", {}).get(param_name)
      if value is None:
        raise AssertionError(f"Path parameter '{{{param_name}}}' not found in global variables.")
      return str(value)

    try:
      resolved_path = re.sub(r"\{(\w+)\}", replace_param, resolved_template)
      return resolved_path
    except AssertionError as e:
      # Catch the error from replace_param if needed, or let it propagate
      raise AssertionError(f"Path parameter resolution failed for '{resolved_template}': {e}")
    except Exception as e:  # Catch potential regex errors
      raise AssertionError(f"Regex error during path param substitution: {e}")

  def _prepare_file_part(
    self,
    field_name: str,
    file_info: Tuple[str, Union[bytes, str], str],
    file_objects_to_close: List[IO[bytes]],
  ) -> Tuple[str, Union[bytes, IO[bytes]], str]:
    """
    Prepares a single file part for a multipart request.
    Opens file if a path is provided and adds it to a list of files to close.
    Returns a tuple in the format expected by httpx for multipart file uploads.
    """
    filename, content_or_path, mime_type = file_info
    if isinstance(content_or_path, bytes):  # Inline content
      self.logger.info(f"  Adding inline file part: field='{field_name}', filename='{filename}'")
      return (filename, content_or_path, mime_type)
    else:  # File path
      file_path_str = str(content_or_path)  # Ensure it's a string for os.path.abspath
      try:
        abs_file_path = os.path.abspath(file_path_str)
        self.logger.info(f"  Opening file for upload: field='{field_name}', path='{abs_file_path}'")
        file_object = open(abs_file_path, "rb")
        file_objects_to_close.append(file_object)  # Add to list for later cleanup
        # Return tuple in format (filename, file_object, mime_type) for httpx multipart
        return (filename, file_object, mime_type)
      except IOError as e:
        self.logger.error(f"Could not open file for upload: {abs_file_path} - {e}")
        raise ValueError(f"Could not open file for upload: {abs_file_path} - {e}")

  def _prepare_all_files(
    self, upload_files_info: Dict[str, Tuple[str, Union[bytes, str], str]]
  ) -> Tuple[Optional[Dict[str, Any]], List[IO[bytes]]]:
    """
    Prepares all file parts for the request and collects file objects that need closing.
    Returns a dictionary of files to send and a list of file objects to close.
    """
    if not upload_files_info:
      return None, []

    files_to_send: Dict[str, Any] = {}
    file_objects_to_close: List[IO[bytes]] = []

    try:
      for field_name, file_info_tuple in upload_files_info.items():
        files_to_send[field_name] = self._prepare_file_part(
          field_name, file_info_tuple, file_objects_to_close
        )
    except Exception as e:  # Catch exceptions during file preparation
      self.logger.error(f"Error preparing file parts for upload: {e}")
      for f_obj in file_objects_to_close:  # Attempt to close any already opened files
        try:
          f_obj.close()
        except IOError as close_err:
          self.logger.error(f"Error closing file during cleanup: {close_err}")
      raise AssertionError(
        f"Error preparing file parts for upload: {e}"
      )  # Re-raise as AssertionError like original

    return files_to_send, file_objects_to_close

  def _handle_multipart_request(
    self,
    upload_files_info: Optional[Dict[str, Tuple[str, Union[bytes, str], str]]],
    multipart_fields: Optional[Dict[str, Any]],
  ) -> Tuple[Dict[str, Any], List[IO[bytes]]]:
    """
    Prepares data for a multipart/form-data request.
    This includes both file parts and regular form data fields.
    """
    data_kwarg: Dict[str, Any] = {}
    all_file_objects_to_close: List[IO[bytes]] = []

    self.logger.info("Preparing multipart/form-data request...")

    # Prepare the files dictionary for httpx
    files: Dict[str, Any] = {}
    data: Dict[str, Any] = {}

    # 1. Add regular form fields to files dict
    if multipart_fields:
      self.logger.info(f"  Adding data fields: {list(multipart_fields.keys())}")
      for field_name, field_value in multipart_fields.items():
        data[field_name] = (None, str(field_value))

    # 2. Add file parts
    if upload_files_info:
      prepared_files, file_objects_to_close = self._prepare_all_files(upload_files_info)
      if prepared_files:
        files.update(prepared_files)
      all_file_objects_to_close.extend(file_objects_to_close)

    # Set the files in data_kwarg if we have any
    if files:
      data_kwarg["files"] = files

    if data:
      data_kwarg["data"] = data

    return data_kwarg, all_file_objects_to_close

  def _handle_standard_request_body(
    self, request_body: Any, headers: Dict[str, Any]
  ) -> Dict[str, Any]:
    """
    Prepares data for a standard request body (not multipart).
    Determines whether to use 'json' or 'data' keyword.
    """
    data_kwarg: Dict[str, Any] = {}
    content_type = headers.get("Content-Type", "").lower()

    if isinstance(request_body, (dict, list)) and "application/json" in content_type:
      self.logger.info("Preparing JSON request body.")
      data_kwarg["json"] = request_body
    else:
      self.logger.info("Preparing non-JSON data request body.")
      data_kwarg["data"] = request_body
    return data_kwarg

  def _prepare_request_data(self, api_context: Dict, headers: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determines the keyword argument ('json', 'data', or 'content') for the request body.
    Manages file resources if uploads are involved.
    """
    request_body = api_context.get("request_body")
    raw_content = api_context.get("raw_content")  # Raw binary content for presigned URLs
    upload_files_info = api_context.get("upload_files")  # File parts (inline or path)
    multipart_fields = api_context.get("multipart_fields")  # Regular form data fields

    is_explicit_multipart = bool(multipart_fields)
    has_files_to_upload = bool(upload_files_info and len(upload_files_info) > 0)

    data_kwarg: Dict[str, Any] = {}

    # Handle raw content for presigned URL uploads
    if raw_content is not None:
      self.logger.info("Preparing raw content for presigned URL upload.")
      data_kwarg["content"] = raw_content
    elif is_explicit_multipart or has_files_to_upload:
      # Handle multipart/form-data request
      request_params, _ = self._handle_multipart_request(upload_files_info, multipart_fields)
      data_kwarg = request_params
      # Set the Content-Type header for multipart/form-data
      if "Content-Type" not in headers:
        headers["Content-Type"] = "multipart/form-data"
    elif request_body is not None:
      data_kwarg = self._handle_standard_request_body(request_body, headers)

    return data_kwarg

  def _execute_http_request(
    self,
    client: APIX,  # Use specific type if possible
    method: str,
    url: str,
    headers: Dict,
    params: Optional[Dict],
    data_kwarg: Dict,
    api_context: Dict,
  ) -> Any:  # Return the raw httpx response object
    """Executes the HTTP request using the provided client and arguments."""
    print(f"\nMaking {method.upper()} request to: {url}")
    if params:
      print(f"  Query Params: {params}")
    # Avoid printing sensitive headers in real scenarios
    if headers:
      print(f"  Headers: {headers}")
    if data_kwarg:
      body_preview = str(data_kwarg)[:200]  # Limit preview size
      print(f"  Body Args: {body_preview}...")

    try:
      # Ensure proper handling of multipart/form-data
      if "Content-Type" in headers and "multipart/form-data" in headers["Content-Type"]:
        # For multipart/form-data, we need to let httpx handle the Content-Type header
        headers.pop("Content-Type", None)
      # Handle external requests that need clean headers
      if api_context.get("external_request", False):
        # For external requests, clear client's persistent headers and cookies
        client.client.headers.clear()
        client.client.cookies.clear()
        # Don't add default auth headers
        options = {"add_headers": False}
        print("Cleared persistent client headers and cookies for external request")
      else:
        options = {"add_headers": True}

      response = client.request(
        method.upper(),
        url,
        headers=headers,
        params=params,
        options=options,
        follow_redirects=True,  # Good default, adjust if needed
        **data_kwarg,
      )
      res = response.res  # Raise HTTPStatusError for 4xx/5xx responses
      print(f"Response Status: {res.status_code}")
      return response
    except httpx.RequestError as e:
      # Handle connection errors, timeouts, etc.
      raise AssertionError(f"HTTP Request failed: {e}")
    except Exception as e:
      # Handle unexpected errors during request processing
      raise AssertionError(f"An unexpected error occurred during the request: {e}")

  def _process_response(self, response: MagicResponse, api_context: Dict = None) -> None:
    """Stores response details and attempts to parse JSON body."""
    api_context = self.api_context or api_context
    # Store raw response
    api_context["response"] = response.res
    api_context["response_debug"] = response

    # Reset and attempt to parse JSON
    api_context["response_json"] = None
    content_type = api_context["response"].headers.get("content-type", "").lower()

    if not api_context["response"].content:  # Check if content is empty
      print("Response body is empty.")
      return

    if "application/json" in content_type or api_context["response"].text:
      try:
        api_context["response_json"] = api_context["response"].json()
        # print(f"Response JSON: {json.dumps(api_context['response_json'], indent=2)}") # Optional: verbose
      except json.JSONDecodeError:
        # Only warn if header *claimed* it was JSON
        if "application/json" in content_type:
          print(
            f"Warning: Content-Type is JSON but body is not valid JSON: {api_context["response"].text[:200]}..."
          )
        else:
          # Just print text snippet if not declared as JSON but parsing failed
          print(
            f"Response Text (non-JSON or failed parse): {api_context["response"].text[:200]}..."
          )
      except Exception as e:  # Catch other potential errors during .json() call
        print(f"Error processing response body: {e}")
        print(f"Response Text: {api_context["response"].text[:200]}...")

    elif response.text:  # If not JSON-like, print text snippet
      print(f"Response Text: {response.text[:200]}...")


  def _extract_url_params(self, url: str) -> Tuple[str, Optional[Dict]]:
    """
    Extracts query parameters from a URL and returns clean URL and params dict.

    Args:
      url: Full URL that may contain query parameters

    Returns:
      Tuple of (clean_url_without_params, params_dict)
    """
    from urllib.parse import urlparse, parse_qs

    parsed = urlparse(url)

    # Reconstruct URL without query parameters
    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    # Extract parameters from query string
    if parsed.query:
      params_dict = {}
      parsed_params = parse_qs(parsed.query, keep_blank_values=True)
      # parse_qs returns lists, but we want single values for most cases
      for key, values in parsed_params.items():
        if len(values) == 1:
          params_dict[key] = values[0]
        else:
          # Keep as list if multiple values
          params_dict[key] = values
      return clean_url, params_dict

    return clean_url, None

  def _merge_params(
    self, context_params: Optional[Dict], url_params: Optional[Dict]
  ) -> Optional[Dict]:
    """
    Merges context parameters with URL parameters, giving precedence to URL parameters.

    Args:
      context_params: Parameters from api_context
      url_params: Parameters extracted from URL

    Returns:
      Merged parameters dict or None if both are None/empty
    """
    if not context_params and not url_params:
      return None

    if not context_params:
      return url_params

    if not url_params:
      return context_params

    # Merge dictionaries, URL params take precedence
    merged = context_params.copy()
    merged.update(url_params)
    return merged

  def make_request(self, path_template: str, api_context: Dict, method: str) -> None:
    """
    Resolves path, prepares data, executes HTTP request, and processes the response.
    Updates api_context with response details.
    """
    # 1. Get context data
    base_url = api_context.get("base_url", "")
    client = api_context.get("client")
    headers = api_context.get("headers", {}).copy()  # Make a copy to avoid modifying original
    params = api_context.get("params")

    assert client is not None, "HTTP client not found in api_context"
    assert base_url, "Base URL not found in api_context"

    # Debug: Log final headers being used (without exposing tokens completely)
    headers_debug = {}
    for key, value in headers.items():
      if key == "internal-authorization":
        headers_debug[key] = f"{value[:20]}..." if value else "None"
      else:
        headers_debug[key] = value
    self.logger.info(f"Final headers for request: {headers_debug}")

    # 3. Resolve Path
    resolved_path = self._resolve_request_path(path_template)
    if resolved_path.startswith("https://"):
      url, url_params = self._extract_url_params(resolved_path)
      params = self._merge_params(params, url_params)
    else:
      url = f"{base_url.rstrip('/')}/{resolved_path.lstrip('/')}"

    # 4. Prepare Data Payload
    data_kwarg = self._prepare_request_data(api_context, headers)

    # 5. Execute Request (includes logging within the helper)
    response = self._execute_http_request(
      client, method, url, headers, params, data_kwarg, api_context
    )

    # 6. Process Response (updates api_context)
    self._process_response(response, api_context)

  def resolve_actual_expected_value(self, api_context, expected_value_template, jq_filter):
    """Checks if the result of a jq filter on the response JSON matches the expected value."""
    actual_json = api_context.get("response_json")
    assert actual_json is not None, "Response body is not valid JSON or was not parsed"

    # --- Resolve expected value (resolving variables) ---
    try:
      resolved_expected_value_str = self.resolve_variable(str(expected_value_template))
    except AssertionError as e:
      raise AssertionError(f"Failed to resolve variables in step's expected value: {e}")

    # --- Determine type of resolved expected value ---
    try:
      # Attempt to load the resolved string as JSON (handles numbers, bools, null, quoted strings)
      expected_value = json.loads(resolved_expected_value_str)
    except json.JSONDecodeError:
      # If it fails, treat it as a plain string (remove outer quotes if they exist from parsing)
      expected_value = resolved_expected_value_str.strip('"')
    # --- End of resolving expected value ---

    # --- Apply jq filter to actual JSON ---
    try:
      # Use jq.first to get the value from the JSON using the filter
      # It returns the first result or None if no results.
      actual_value = self.jq(actual_json).one(jq_filter)
    except ValueError as e:  # Handle errors in jq filter syntax or application
      raise AssertionError(
        f"Error processing jq filter '{jq_filter}': {e}\nResponse JSON:\n{json.dumps(actual_json, indent=2)}"
      )
    except Exception as e:  # Catch other potential jq errors
      raise AssertionError(
        f"An unexpected error occurred while applying jq filter '{jq_filter}': {e}"
      )

    # jq returns native Python types, so direct comparison usually works well.
    return (
      actual_value == expected_value,
      f"jq filter '{jq_filter}': Expected '{expected_value}' (type {type(expected_value)}), "
      f"but got '{actual_value}' (type {type(actual_value)})."
      f"\n(Resolved expected value template was: '{resolved_expected_value_str}')"
      f"\nResponse JSON:\n{json.dumps(actual_json, indent=2)}",
    )

  def _prepare_expected_json(self, expected_json_template: str) -> Dict[str, Any]:
    """
    Resolves variables in the template string, loads it as JSON,
    and resolves variables within the resulting structure.
    """
    try:
      resolved_expected_str = self.resolve_variable(expected_json_template)
      expected_json_loaded = json.loads(resolved_expected_str)
      expected_json_final = self.resolve_variables_recursive(expected_json_loaded)
      return expected_json_final
    except json.JSONDecodeError as e:
      raise AssertionError(
        f"Invalid expected JSON after variable substitution: {e}\n"
        f"Expected JSON template: {expected_json_template}\n"
        f"Resolved string: {resolved_expected_str}"
      )
    except Exception as e:  # Catch potential variable resolution errors too
      raise AssertionError(f"Failed to prepare expected JSON: {e}")

  def _is_notnull_match(self, expected_value: Any, actual_value: Any) -> bool:
    """Checks if the condition for a '#notnull' match is met."""
    return expected_value == "#notnull" and actual_value is not None

  def _generate_visual_diff(self, change_path: str, old_val: str, new_val: str) -> Optional[str]:
    """Generates a unified diff string if strings are long."""
    if (
      isinstance(old_val, str)
      and isinstance(new_val, str)
      and (len(old_val) > self.VISUAL_DIFF_THRESHOLD or len(new_val) > self.VISUAL_DIFF_THRESHOLD)
    ):
      diff_lines = difflib.unified_diff(
        old_val.splitlines(keepends=True),
        new_val.splitlines(keepends=True),
        fromfile=f"{change_path} (Expected)",
        tofile=f"{change_path} (Actual)",
        n=self.VISUAL_DIFF_CONTEXT,
      )
      return f"Visual Diff for '{change_path}':\n" + "".join(diff_lines)
    return None

  def _process_values_changed(
    self, changes: Dict[str, Dict], visual_diffs: List[str]
  ) -> Dict[str, Dict]:
    """Processes 'values_changed' diffs, handling #notnull and visual diffs."""
    processed = {}
    for change_path, details in changes.items():
      old_val = details["old_value"]
      new_val = details["new_value"]

      if self._is_notnull_match(old_val, new_val):
        continue  # Skip #notnull matches

      # Generate visual diff for long strings
      visual_diff = self._generate_visual_diff(change_path, old_val, new_val)
      if visual_diff:
        visual_diffs.append(visual_diff)

      # Keep the change if it wasn't handled by #notnull
      processed[change_path] = details
    return processed

  def _process_type_changes(self, changes: Dict[str, Dict]) -> Dict[str, Dict]:
    """Processes 'type_changes' diffs, handling #notnull."""
    processed = {}
    for change_path, details in changes.items():
      # Check if the type change is acceptable due to #notnull expectation
      # We check old_type was string because '#notnull' is always a string
      if details["old_type"] == str and self._is_notnull_match(
        details["old_value"], details["new_value"]
      ):
        continue  # Skip #notnull matches even if type differs
      processed[change_path] = details
    return processed

  def _filter_diff_results(self, diff: DeepDiff) -> Tuple[Dict[str, Any], List[str]]:
    """
    Filters the raw DeepDiff results, handling special markers like #notnull
    and generating visual diffs for long string mismatches.
    """
    filtered_diff = {}
    visual_diffs = []

    for diff_type, changes in diff.items():
      processed_changes: Any = None  # Initialize as None

      if diff_type == "values_changed":
        processed_changes = self._process_values_changed(changes, visual_diffs)
      elif diff_type == "type_changes":
        processed_changes = self._process_type_changes(changes)
      else:
        # Keep other diff types as is for now
        # Convert sets to sorted lists for consistent reporting
        if isinstance(changes, set):
          processed_changes = sorted(changes)
        else:
          processed_changes = changes  # Keep dicts or other types

      # Only add to filtered_diff if there are actual changes remaining
      if processed_changes:
        filtered_diff[diff_type] = processed_changes

    return filtered_diff, visual_diffs

  def _format_assertion_error(
    self,
    filtered_diff: Dict[str, Any],
    visual_diffs: List[str],
    expected_json: Dict[str, Any],
    actual_json: Dict[str, Any],
  ) -> str:
    """Formats the detailed assertion error message."""
    try:
      diff_report = json.dumps(filtered_diff, indent=2)
    except TypeError:
      diff_report = str(filtered_diff)  # Fallback for non-serializable items

    error_message = f"JSON mismatch (after handling #notnull):\n{diff_report}"

    if visual_diffs:
      error_message += "\n\n--- Visual Diffs for Long Strings ---\n"
      error_message += "\n\n".join(visual_diffs)

    # Use try-except for JSON dumps as a safety measure
    try:
      expected_json_str = json.dumps(expected_json, indent=2)
    except TypeError:
      expected_json_str = str(expected_json)

    try:
      actual_json_str = json.dumps(actual_json, indent=2)
    except TypeError:
      actual_json_str = str(actual_json)

    error_message += f"\n\n--- Expected JSON (after resolving vars) ---\n{expected_json_str}"
    error_message += f"\n\n--- Actual JSON ---\n{actual_json_str}"
    return error_message

  def compare_response(self, api_context, expected_json_template: str):
    """
    Performs a DeepDiff comparison between the response JSON and an expected JSON structure.
    Handles variable resolution, #notnull markers, and provides visual diffs.
    """
    actual_json = api_context.get("response_json")
    assert actual_json is not None, "Response body is not valid JSON or was not parsed"

    # 1. Prepare the expected JSON (handles variable resolution and loading)
    expected_json_final = self._prepare_expected_json(expected_json_template)

    # 2. Perform the core comparison
    diff = DeepDiff(
      expected_json_final,
      actual_json,
      ignore_order=True,
      report_repetition=True,
    )

    # 3. Filter and process the diff results (#notnull, visual diffs)
    filtered_diff, visual_diffs = self._filter_diff_results(diff)

    # 4. Assert based on filtered results
    if filtered_diff:
      error_message = self._format_assertion_error(
        filtered_diff, visual_diffs, expected_json_final, actual_json
      )
      raise AssertionError(error_message)
    else:
      print("JSON matching passed.")  # Or use logging

  def extract_save_from_last_response(self, api_context, jq_filter, variable_name):
    """Extracts a value using a jq filter from the last response and stores it in global_vars."""
    response_json = api_context.get("response_json")
    assert response_json is not None, "Cannot store value: Last response had no valid JSON."
    try:
      # Use jq.first to get the first result matching the filter
      stored_value = self.jq(response_json).one(jq_filter)

      assert (
        stored_value is not None
      ), f"jq filter '{jq_filter}' produced no results (or null) in last response:\n{json.dumps(response_json, indent=2)}"

      self.ctx.setdefault("global_vars", {})[variable_name] = stored_value
      print(
        f"Stored global var '{variable_name}' = {repr(stored_value)}"
      )  # Use repr for clarity on types
    except ValueError as e:  # Catches errors in the jq filter syntax or application
      raise AssertionError(
        f"Error processing jq filter '{jq_filter}': {e}\nResponse JSON:\n{json.dumps(response_json, indent=2)}"
      )
    except Exception as e:  # Catch other potential jq errors
      raise AssertionError(
        f"An unexpected error occurred while applying jq filter '{jq_filter}': {e}"
      )

  def debug(self, api_context):
    IS_DEBUG_MODE = os.getenv("DEBUG") == "1"
    IS_PYTHON_DEBUG_FLAG_SET = bool(sys.flags.debug)
    IS_DEBUGPY = "debugpy" in sys.modules
    if IS_DEBUG_MODE or IS_PYTHON_DEBUG_FLAG_SET or IS_DEBUGPY:
      if api_context["response"]:
        url = api_context["response"].request.url.path
        print(f"++++++++++URL+++++++++\n{url}\n")
        status_code = api_context["response"].status_code
        print(f"++++++++++STATUS CODE+++++++++\n{status_code}\n")
        status_text = api_context["response"].reason_phrase
        if status_text:
          print(f"++++++++++STATUS TEXT+++++++++\n{status_text}\n")
        env_vars = self.ctx.get("global_vars", "")
        print(f"++++++++++VARS+++++++++\n{env_vars}\n")
        headers = dict(api_context["response"].request.headers)
        print(f"++++++++++HEADERS+++++++++\n{headers}\n")
        api_context["response"].request.read()
        body = api_context["response"].request.content.decode("utf-8")
        print(f"=============BODY============\n{body}\n")

        curl = Curlify(api_context["response"].request).to_curl()
        print(f"============CURL============\n{curl}\n")
        response_headers = dict(api_context["response"].headers)
        print(f"============RESPONSE_HEADERS============\n{response_headers}\n")
        if api_context["response_json"]:
          response = api_context["response_json"]
          print(f"=============RESPONSE JSON============\n{response}\n")
          if "error" in response:
            status_text = api_context["response_json"]["error"]
            print(f"++++++++++STATUS TEXT+++++++++\n{status_text}\n")
        else:
          response = api_context["response"]._text
          print(f"=============RESPONSE=============\n{response}\n")
        breakpoint()
        print(api_context["response_debug"].jq.all("."))

  def compare_dict_structures(self, dict1, dict2, path="root"):
    """Recursively compares keys and order of nested dictionaries."""
    errors = []
    keys1 = list(dict1.keys())
    keys2 = list(dict2.keys())

    if keys1 != keys2:
      errors.append(
        f"Key mismatch/order difference at '{path}':\n  Expected: {keys1}\n  Actual:   {keys2}"
      )
      # If keys don't match, further deep comparison is likely meaningless/error-prone
      return errors

    # Keys match at this level, check nested dictionaries
    for key in keys1:
      val1 = dict1[key]
      val2 = dict2[key]

      # If both values are dictionaries, recurse
      if isinstance(val1, dict) and isinstance(val2, dict):
        nested_errors = self.compare_dict_structures(val1, val2, path=f"{path}.{key}")
        errors.extend(nested_errors)

    return errors

  def _clear_conflicting_request_data(self, source_step_type):
    """Internal helper to clear data that conflicts with multipart/file uploads."""
    cleared = False
    if "request_body" in self.api_context and self.api_context["request_body"] is not None:
      print(f"Clearing previously set request body due to setting {source_step_type}.")
      self.api_context["request_body"] = None
      cleared = True
    # Multipart/files usually require httpx to set the Content-Type
    if "Content-Type" in self.api_context.get("headers", {}):
      print(f"Clearing Content-Type header due to setting {source_step_type}.")
      self.api_context["headers"].pop("Content-Type", None)
      cleared = True
    return cleared

  def attach_multipart_file_with_mime(self, path_template, mime_template, field_name_template):
    """Attaches a file (from path) to a multipart/form-data request with optional MIME type."""
    self._clear_conflicting_request_data("multipart file attachment")
    self.api_context.setdefault("upload_files", {})  # Files stored here for make_request logic
    try:
      field_name = self.resolve_variable(field_name_template)
      file_path = self.resolve_variable(path_template)
      mime_type = self.resolve_variable(mime_template) if mime_template else None

      file_path = f"src/resources/{file_path}"

      if not os.path.exists(file_path):
        raise AssertionError(f"File not found at path: {file_path} (or relative to features dir)")
      filename = os.path.basename(file_path)
      if not mime_type:
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
          mime_type = "application/octet-stream"
        print(f"Guessed MIME type for '{filename}': {mime_type}")

      # Store using the same structure as single file uploads
      self.api_context["upload_files"][field_name] = (filename, file_path, mime_type)
      print(
        f"Attached multipart file: field='{field_name}', path='{file_path}', mime='{mime_type}'"
      )
    except AssertionError as e:
      raise AssertionError(
        f"Failed to resolve variables/jq# for multipart file attachment '{field_name_template}': {e}"
      )
    except Exception as e:
      raise AssertionError(f"An unexpected error occurred attaching multipart file: {e}")

  def set_multipart_field(self, field_name_template, field_value_template):
    """Sets a regular form-data field for multipart/form-data requests."""
    try:
      self.api_context["multipart_fields"] = {}
      field_name = self.resolve_variable(field_name_template)
      field_value = self.resolve_variable(field_value_template)
      self.api_context["multipart_fields"][field_name] = field_value
      print(f"Set multipart field: {field_name} = {field_value}")
    except AssertionError as e:
      raise AssertionError(
        f"Failed to resolve variables/jq# for multipart field '{field_name_template}': {e}"
      )
    except Exception as e:
      raise AssertionError(f"An unexpected error occurred setting multipart field: {e}")

  def resolve_json_variables(self, data, resolver):
    if isinstance(data, dict):
      return {k: self.resolve_json_variables(v, resolver) for k, v in data.items()}
    elif isinstance(data, list):
      return [self.resolve_json_variables(item, resolver) for item in data]
    elif isinstance(data, str):
      resolved = resolver(data)
      try:
        parsed = json.loads(resolved)
        if isinstance(parsed, list):
          return parsed
        return resolved
      except (ValueError, SyntaxError):
        return resolved
    else:
      return data

  def ensure_directory(self, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

  def load_json_list(self, path):
    if os.path.exists(path):
      with open(path, "r") as f:
        try:
          return json.load(f)
        except json.JSONDecodeError:
          return []
    return []

  def save_json_list(self, path, data):
    self.ensure_directory(path)
    with open(path, "w") as f:
      json.dump(data, f, indent=2)

  def move_random_item_to_deleted(
    self, name, history_path: str, delete=False, property_name="id", unique=False
  ) -> dict | None:
    """
    Selects a random item from history and moves it to the deleted folder structure.
    If delete=True, removes it from the original file.
    If delete=False, keeps it in both original and deleted folders.

    Returns the selected item.
    """
    # Load original data
    original_path = f"src/resources/kotlin/history/{history_path}_history.json"
    data = self.load_json_list(original_path)

    if not data:
      return None

    # Select random item
    if unique:
      filtered_data = [
        item
        for item in data
        if self.get_property_value(item, property_name) != self.ctx.get("global_vars", {}).get(name)
      ]
    else:
      filtered_data = data
    if len(filtered_data) > 0:
      selected_item = self.gen.random.choice(filtered_data)
    else:
      raise AssertionError(f"No elements in history {history_path} with property {property_name}")

    # Only remove from original if delete=True
    if delete:
      data.remove(selected_item)
      # Save updated original data
      self.save_json_list(original_path, data)
      print(f"Removed item from history: {original_path}")

    # Move/Copy to deleted folder
    deleted_path = f"src/resources/kotlin/deleted/{history_path}_history.json"
    deleted_data = self.load_json_list(deleted_path)
    deleted_data.append(selected_item)
    self.save_json_list(deleted_path, deleted_data)

    action = "Moved" if delete else "Copied"
    print(f"{action} item to deleted folder: {deleted_path}")
    return selected_item

  def get_property_value(self, item: dict, property_name: str):
    """
    Extracts a property value from an item, handling array indexing syntax.

    Examples:
    - property_name = "name" -> returns item["name"]
    - property_name = "tags[0]" -> returns item["tags"][0]
    """
    match = re.match(r"^(.+)\[(\d+)\]$", property_name)
    if match and item:
      base_property, index = match.groups()
      index = int(index)
      if base_property in item:
        return item[base_property][index]
    elif item and property_name in item:
      return item[property_name]
    return None

  def download_file(self, file_path_template: str, history_path_template: str):
    """
    Downloads a file from the specified endpoint/URL and saves it to the history folder.

    Args:
      file_path_template: The endpoint or URL to download the file from, can contain variables
      history_path_template: The path where to save the file in the history, can contain variables
    """
    try:
      # Resolve variables in both parameters
      resolved_file_path = self.resolve_variable(file_path_template)
      resolved_history_path = self.resolve_variable(history_path_template)

      print(f"Starting file download from: {resolved_file_path}")
      print(f"Will save to history path: {resolved_history_path}")

      # Check if it's a full URL or a relative endpoint
      if resolved_file_path.startswith(("https://")):
        # It's a full URL, use the download_presigned_url method
        response = self.api_adapter.download_presigned_url(resolved_file_path)
      else:
        # It's a relative endpoint, make a regular API request
        # First ensure we have a base URL set in the API context
        if not self.api_context or not self.api_context.get("base_url"):
          raise AssertionError(
            "Base URL must be set before downloading files from relative endpoints"
          )

        # Make a GET request to download the file
        self.make_request(resolved_file_path, self.api_context, "GET")
        response = self.api_context.get("response")

        if response is None:
          raise AssertionError("No response received from download endpoint")

      # Check if the download was successful
      if response.res.is_error:
        raise AssertionError(
          f"File download failed: HTTP {response.status} - {response.res.text[:500]}"
        )

      # Determine the file extension and content type
      content_type = response.res.headers.get("content-type", "application/octet-stream")
      file_extension = self._get_file_extension_from_content_type(content_type)

      # Create the full history file path
      history_file_path = f"src/resources/kotlin/history/{resolved_history_path}{file_extension}"

      # Ensure the directory exists
      self.ensure_directory(history_file_path)

      # Save the file content
      with open(history_file_path, "wb") as f:
        f.write(response.res.content)

      print(f"File successfully downloaded and saved to: {history_file_path}")
      print(f"File size: {len(response.res.content)} bytes")
      print(f"Content type: {content_type}")

      # Store the download information in global variables for potential later use
      self.ctx["global_vars"]["last_downloaded_file_path"] = history_file_path
      self.ctx["global_vars"]["last_downloaded_file_size"] = len(response.res.content)
      self.ctx["global_vars"]["last_downloaded_content_type"] = content_type

    except Exception as e:
      raise AssertionError(f"Error downloading file from '{resolved_file_path}': {str(e)}")

  def _get_file_extension_from_content_type(self, content_type: str) -> str:
    """
    Determines file extension based on content type.

    Args:
      content_type: The HTTP content-type header value

    Returns:
      File extension with leading dot (e.g., '.csv', '.json', '.txt')
    """
    content_type_lower = content_type.lower().split(";")[0].strip()  # Remove charset info

    extension_mapping = {
      "text/csv": ".csv",
      "application/csv": ".csv",
      "application/json": ".json",
      "text/json": ".json",
      "text/plain": ".txt",
      "application/xml": ".xml",
      "text/xml": ".xml",
      "application/pdf": ".pdf",
      "application/zip": ".zip",
      "application/octet-stream": ".bin",
      "text/html": ".html",
      "application/vnd.ms-excel": ".xls",
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    }

    return extension_mapping.get(content_type_lower, ".txt")  # Default to .txt if unknown

  def load_env_variable(self, var_name: str) -> str:
    """
    Load a variable from .env files and ENV_PATH files using dotenv.

    Args:
      var_name: The variable name to look up

    Returns:
      The resolved variable value

    Raises:
      AssertionError: If the variable is not found
    """
    # Load .env file using dotenv
    load_dotenv()

    # Check environment variables (includes .env)
    value = os.getenv(var_name)
    if value:
      print(f"Found {var_name} in environment/.env")
      return value

    # Check ENV_PATH file if specified
    env_path = os.getenv("ENV_PATH") or self.config.get("ENV_PATH")
    if env_path:
      load_dotenv(env_path)
      value = os.getenv(var_name)
      if value:
        print(f"Found {var_name} in ENV_PATH file: {env_path}")
        return value

    # Fallback to config
    value = self.config.get(var_name)
    if value:
      print(f"Found {var_name} in config")
      return value

    raise AssertionError(f"Variable '{var_name}' not found in .env, ENV_PATH, or config")
