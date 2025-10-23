import mimetypes
import pytest
import time
import json
import os
import allure
from jsonschema import validate as validate_schema
from jsonschema.exceptions import ValidationError as SchemaValidationError
from pytest_bdd import step, parsers
from src.utils.core.validator import Validator as v
from src.domains.common.common_api_domain import CommonApiDomain
from src.utils.decorators import parse_datatable
from src.utils.logger import get_logger

logger = get_logger(__name__)


def attach_validation_context(step_name: str, context: dict, status: str = "FAILED"):
  """
  Attach validation context to Allure report for better traceability.

  Usage pattern for non-Validator exceptions:
  ```python
  try:
    with open(file_path, "r") as f:
      data = json.load(f)
  except FileNotFoundError:
    attach_validation_context("File Loading", {"path": file_path, "error": "not found"})
    raise ValueError(...)
  except json.JSONDecodeError as e:
    attach_validation_context("JSON Parsing", {"path": file_path, "error": str(e)})
    raise ValueError(...)
  ```

  Args:
    step_name: Name of the step/validation being performed
    context: Dictionary with relevant context information
    status: Status of the validation (PASSED/FAILED)
  """
  result = {
    "step": step_name,
    "status": status,
    "context": context,
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
  }

  attachment_content = json.dumps(result, indent=2, default=str)

  allure.attach(
    attachment_content,
    name=f"Step Context: {step_name} - {status}",
    attachment_type=allure.attachment_type.JSON,
  )


@pytest.fixture
def api_domain(ctx, api_context):
  return CommonApiDomain(ctx, api_context)


@step("the base URL is {string}")
@step(parsers.parse('the base URL is "{url_template}"'))
def set_base_url(api_context, api_domain: CommonApiDomain, url_template):
  """Sets the base URL for subsequent requests, resolving variables."""
  resolved_url = api_domain.resolve_variable(url_template)
  api_context["base_url"] = resolved_url.rstrip("/")  # Ensure no trailing slash
  print(f"Set base URL to: {api_context['base_url']}")


@step("the user waits {int}s")
@step(parsers.parse("the user waits {seconds}s"))
@step("sleep {int}")
@step(parsers.parse("sleep {seconds}"))
def wait_seconds(seconds):
  time.sleep(float(seconds))


@step("the {string} duration should not exceed {float}x of {string}")
@step(parsers.parse('the "{final_lapse}" duration should not exceed {times}x of "{initial_lapse}"'))
def check_duration_performance(
  api_context, api_domain: CommonApiDomain, initial_lapse, final_lapse, times
):
  if api_domain.config.VALIDATE_PERFORMANCE:
    initial_lapse_value = float(api_domain.resolve_variable(initial_lapse))
    final_lapse_value = float(api_domain.resolve_variable(final_lapse))
    v(
      final_lapse_value <= initial_lapse_value * float(times),
      f"{final_lapse} lapse ({final_lapse_value:.2f}) exceeded {initial_lapse} lapse ({initial_lapse_value:.2f}) by more than {times} times.",
    ).is_true()


@step("I set the request body to:")
@step(parsers.parse("I set the request body to:"))
def set_request_body_inline(api_context, api_domain: CommonApiDomain, docstring):
  """Sets the request body, resolving variables before parsing."""
  try:
    resolved_body_str = api_domain.resolve_variable(docstring)
    # Try parsing as JSON *after* variable substitution
    if resolved_body_str.strip().startswith(("{", "[")):
      api_context["request_body"] = json.loads(resolved_body_str)
      # Default Content-Type to JSON if not set explicitly and body looks like JSON
      api_context["headers"].setdefault("Content-Type", "application/json")
    else:
      # Treat as raw string if not JSON
      api_context["request_body"] = resolved_body_str
  except json.JSONDecodeError as e:
    raise ValueError(
      f"Request body is not valid JSON after variable substitution: {e}\nBody: {resolved_body_str}"
    )


@step("I set the request body from {string}")
@step(parsers.parse('I set the request body from "{payload}"'))
def set_request_body_from_file(api_context, api_domain: CommonApiDomain, payload):
  """Sets the request body, resolving variables before parsing."""
  if "void" not in payload:
    payload_data = api_domain.load_json_list(f"src/resources/{payload}.json")
    api_context["request_body"] = api_domain.resolve_json_variables(
      payload_data, api_domain.resolve_variable
    )
    api_context["headers"].setdefault("Content-Type", "application/json")


@step("I set var {string} as {string}")
@step(parsers.parse('I set var "{name}" as "{value_template}"'))
def set_var_as_value(api_domain: CommonApiDomain, name, value_template):
  """Defines a variable within the scenario's context (global_vars)."""
  try:
    resolved_value = api_domain.resolve_variable(value_template)
    api_domain.ctx["global_vars"][name] = resolved_value
    print(f"Defined global var: {name} = {resolved_value}")
  except Exception as e:
    raise AssertionError(f"Failed to define global variable '{name}': {e}")


@step("I set var {string} as envvar {string}")
@step(parsers.parse('I set var "{name}" as envvar "{value_template}"'))
def set_var_as_envvar(api_domain: CommonApiDomain, name, value_template):
  """Defines a variable within the scenario's context (global_vars) by loading from .env and ENV_PATH files."""
  try:
    resolved_value = api_domain.load_env_variable(value_template)
    api_domain.ctx["global_vars"][name] = resolved_value
    print(f"Defined global var: {name} = {resolved_value}")
  except Exception as e:
    raise AssertionError(f"Failed to define global variable '{name}': {e}")


@step("I set var list {string} as {string}")
@step(parsers.parse('I set var list "{name}" as "{value_template}"'))
def set_var_list_as_value(api_domain: CommonApiDomain, name, value_template):
  """Defines a variable within the scenario's context (global_vars)."""
  try:
    resolved_value = api_domain.resolve_variable(value_template, is_list=True)
    api_domain.ctx["global_vars"][name] = resolved_value
    print(f"Defined global var: {name} = {resolved_value}")
  except Exception as e:
    raise AssertionError(f"Failed to define global variable '{name}': {e}")


@step("I set list {string} from string {string}")
@step(parsers.parse('I set list "{name}" from string "{value_template}"'))
def set_list_from_string(api_domain: CommonApiDomain, name, value_template):
  """Defines a variable within the scenario's context (global_vars)."""
  try:
    resolved_value = json.loads(value_template)
    api_domain.ctx["global_vars"][name] = resolved_value
    print(f"Defined global var: {name} = {resolved_value}")
  except Exception as e:
    raise AssertionError(f"Failed to define global variable '{name}': {e}")


@step("I set var {string} as responseBody")
@step(parsers.parse('I set var "{name}" as responseBody'))
def set_var_as_response_body(api_domain: CommonApiDomain, name):
  """Defines a responseBody variable within the scenario's context (global_vars)."""
  try:
    resolved_value = api_domain.resolve_variable("$.")
    api_domain.ctx["global_vars"][name] = resolved_value
    print(f"Defined global var: {name} = {resolved_value}")
  except Exception as e:
    raise AssertionError(f"Failed to define global variable '{name}': {e}")


@step("I set var {string} as responseCode")
@step(parsers.parse('I set var "{name}" as responseCode'))
def set_var_as_response_code(api_domain: CommonApiDomain, api_context, name):
  """Defines a responseCode variable within the scenario's context (global_vars)."""
  try:
    resolved_value = api_context["response"].status_code
    api_domain.ctx["global_vars"][name] = resolved_value
    print(f"Defined global var: {name} = {resolved_value}")
  except Exception as e:
    raise AssertionError(f"Failed to define global variable '{name}': {e}")


@step("I set var {string} as Time")
@step(parsers.parse('I set var "{name}" as Time'))
def set_var_as_time(api_domain: CommonApiDomain, api_context, name):
  try:
    resolved_value = api_context["response"].elapsed.total_seconds()
    api_domain.ctx["global_vars"][name] = resolved_value
    print(f"Defined global var: {name} = {resolved_value}")
  except Exception as e:
    raise AssertionError(f"Failed to define global variable '{name}': {e}")


@step(
  parsers.parse(
    'I store the value from JSON path "{jq_filter}" of the last response as "{variable_name}"'
  )
)
def store_value_from_response_json(
  api_domain: CommonApiDomain, api_context, jq_filter, variable_name
):
  api_domain.extract_save_from_last_response(api_context, jq_filter, variable_name)


@step("I send {string} req to {string}")
@step(parsers.parse('I send "{method}" req to "{path_template}"'))
def make_request(ctx, api_context, api_domain: CommonApiDomain, method, path_template):
  """Makes an HTTP request using the current context (URL, headers, body, etc.)."""
  initial_time = time.time()
  v(api_context.get("base_url"), "Base URL must be set before making a request").is_not_empty()
  api_domain.make_request(path_template, api_context, method)
  api_domain.ctx["global_vars"]["elapsed_time"] = time.time() - initial_time


@step("I send {string} req without user id to {string}")
@step(parsers.parse('I send "{method}" req without user id to "{path_template}"'))
def make_request_without_user_id(
  ctx, api_context, api_domain: CommonApiDomain, method, path_template
):
  """Makes an HTTP request without userId in headers using the current context (URL, headers, body, etc.)."""
  initial_time = time.time()
  v(api_context.get("base_url"), "Base URL must be set before making a request").is_not_empty()

  # Store the original client and use one without userId
  original_client = api_context.get("client")

  try:
    # Use the API adapter's client configured without userId
    api_context["client"] = api_domain.api_adapter.req_without_user_id

    # Make the request using the existing make_request method
    api_domain.make_request(path_template, api_context, method)

  finally:
    # Restore the original client
    if original_client is not None:
      api_context["client"] = original_client

  api_domain.ctx["global_vars"]["elapsed_time"] = time.time() - initial_time


@step("breakpoint")
@step("I like to debug")
def debug_breakpoint(api_context, api_domain: CommonApiDomain):
  api_domain.debug(api_context)


@step("the res code should be {string}")
@step(parsers.parse('the res code should be "{code}"'))
def check_response_code_string(api_domain, api_context, code):
  """Checks if the response status code matches the expected value."""
  # Resolve expected header name and value using variables
  resolved_name = api_domain.resolve_variable(code)
  check_status_code(api_context, int(resolved_name))


@step("the res code should be ok")
def check_response_code_ok(api_context):
  """Checks if the response status code matches the expected value."""
  status_code = api_context["response"].status_code
  v(
    200 <= status_code < 300,
    f"Expected status should be 2xx, but got {status_code}. \n{api_context['response'].text}",
  ).is_true()


@step("the res code should be {int}")
@step(parsers.parse("the res code should be {code:d}"))
def check_status_code(api_context, code):
  """Checks if the response status code matches the expected value."""
  response = api_context.get("response")
  v(response, "No request was made (response is None)").is_not_empty()
  v(
    response.status_code == code,
    f"Expected status {code}, but got {response.status_code}. Response: {response.text[:500]}",
  ).is_true()


@step(parsers.parse('the res header "{name_template}" should be "{expected_value_template}"'))
def check_response_header(
  api_context, api_domain: CommonApiDomain, name_template, expected_value_template
):
  """Checks if a specific response header matches the expected value, resolving variables."""
  response = api_context.get("response")

  # Resolve expected header name and value using variables
  resolved_name = api_domain.resolve_variable(name_template)
  resolved_expected_value = api_domain.resolve_variable(expected_value_template)

  v(response, "No request was made").is_not_empty()

  # Header names are case-insensitive according to HTTP spec
  actual_value = response.headers.get(resolved_name)

  v(
    actual_value,
    f"Header '{resolved_name}' not found in response headers: {list(response.headers.keys())}",
  ).is_not_empty()
  v(
    actual_value,
    f"Expected header '{resolved_name}' to be '{resolved_expected_value}', but got '{actual_value}'",
  ).equals(resolved_expected_value)


@step("the res jq {string} should be {string}")
@step(parsers.parse('the res jq "{jq_filter}" should be "{expected_value_template}"'))
def check_response_json_path(
  api_context, api_domain: CommonApiDomain, jq_filter, expected_value_template
):
  assertion_result, message = api_domain.resolve_actual_expected_value(
    api_context, expected_value_template, jq_filter
  )
  v(assertion_result, message).is_true()


@step(
  parsers.parse(
    'the response JSON should conform to the schema defined in "{schema_file_template}"'
  )
)
def check_response_schema_file(api_context, api_domain: CommonApiDomain, schema_file_template):
  """Validates response JSON against a schema loaded from a file (path resolved)."""
  actual_json = api_context.get("response_json")

  v(actual_json, "Response body is not valid JSON or was not parsed").is_not_empty()

  # Resolve variables in the schema file path
  schema_file = api_domain.resolve_variable(schema_file_template)
  # Assume schema file path is relative to the features directory for simplicity
  # A more robust solution might involve a base schema path configuration.
  schema_path = os.path.join(os.path.dirname(__file__), "..", "features", schema_file)
  print(f"Loading schema from: {schema_path}")  # Debug info

  # Load the schema file
  try:
    with open(schema_path, "r") as f:
      schema = json.load(f)
  except FileNotFoundError:
    attach_validation_context(
      "Schema File Validation",
      {
        "schema_file_template": schema_file_template,
        "resolved_path": schema_path,
        "error": "Schema file not found",
      },
    )
    raise ValueError(
      f"JSON schema file not found at resolved path: {schema_path} (original template: '{schema_file_template}')"
    )
  except json.JSONDecodeError as e:
    attach_validation_context(
      "Schema File Validation",
      {"schema_path": schema_path, "error": str(e)},
    )
    raise ValueError(f"Invalid JSON in schema file '{schema_path}': {e}")
  except Exception as e:  # Catch variable resolution errors
    attach_validation_context(
      "Schema File Validation",
      {"schema_file_template": schema_file_template, "error": str(e)},
    )
    raise ValueError(f"Failed to resolve variables in schema file path: {e}")

  # Perform validation
  try:
    validate_schema(instance=actual_json, schema=schema)
    attach_validation_context(
      "JSON Schema Validation",
      {"schema_file": schema_file, "validation_result": "Schema validation passed"},
      "PASSED",
    )
    print("JSON Schema validation passed.")  # Debug info
  except SchemaValidationError as e:
    # Attach detailed validation context for schema validation errors (NOT using Validator)
    attach_validation_context(
      "JSON Schema Validation",
      {
        "schema_file": schema_file,
        "error_message": e.message,
        "error_path": " -> ".join(map(str, e.path)),
        "instance_snippet": str(e.instance)[:500],
        "response_json_preview": str(actual_json)[:1000],
      },
    )
    # Provide detailed error message on failure
    raise AssertionError(
      f"JSON Schema validation failed (schema file: {schema_file}):\n"
      f"Error: {e.message}\n"
      f"Path: {' -> '.join(map(str, e.path))}\n"
      f"Instance Snippet: {str(e.instance)[:200]}...\n"
    )


@step(parsers.parse("the res JSON should match with schema:\n{schema_json_str}"))
def check_response_schema_inline(api_context, api_domain: CommonApiDomain, schema_json_str):
  """Validates response JSON against an inline schema provided in the step."""
  actual_json = api_context.get("response_json")
  v(actual_json, "Response body is not valid JSON or was not parsed").is_not_empty()

  # Resolve variables within the inline schema string
  try:
    resolved_schema_str = api_domain.resolve_variable(schema_json_str)
    schema = json.loads(resolved_schema_str)
  except json.JSONDecodeError as e:
    raise AssertionError(
      f"Invalid JSON schema provided in step definition: {e}\nSchema: {schema_json_str}"
    )
  except Exception as e:  # Catch variable resolution errors
    raise AssertionError(f"Failed to resolve variables in inline schema: {e}")

  # Perform validation
  try:
    validate_schema(instance=actual_json, schema=schema)
    attach_validation_context(
      "JSON Schema Validation",
      {"schema_file": "inline_schema", "validation_result": "Schema validation passed"},
      "PASSED",
    )
    print("Inline JSON Schema validation passed.")  # Debug info
  except SchemaValidationError as e:
    raise AssertionError(
      f"Inline JSON Schema validation failed:\n"
      f"Error: {e.message}\n"
      f"Path: {' -> '.join(map(str, e.path))}\n"
      f"Instance Snippet: {str(e.instance)[:200]}...\n"
    )


@step(parsers.parse("the response JSON should match:\n{expected_json_template}"))
def check_response_json_matches(api_context, api_domain: CommonApiDomain, expected_json_template):
  api_domain.compare_response(api_context, expected_json_template)


@step("I set query params")
@parse_datatable()
def set_query_params_from_table(
  api_domain: CommonApiDomain, api_context, datatable
):  # 'context' gives access to the table
  """Parses a Gherkin DataTable and sets multiple query parameters."""
  v(datatable, "DataTable provided to step is empty.").is_not_empty()
  try:
    # Iterate through the rows of the DataTable
    api_context["params"] = {}
    for row in datatable:
      key_template = row["name"]
      value_template = row["value"]
      try:
        # Resolve variables in both the parameter name (key) and value
        resolved_key = api_domain.resolve_variable(str(key_template))
        resolved_value = api_domain.resolve_variable(str(value_template))
        api_context["params"][resolved_key] = resolved_value
        attach_validation_context(
          "Query Parameter Validation",
          {"param_name": resolved_key, "param_value": resolved_value},
          "PASSED",
        )
        print(f"Set query parameter from table: {resolved_key} = {resolved_value}")  # Debug info
      except Exception as e:
        attach_validation_context(
          "Query Parameter Validation",
          {"param_name": key_template, "param_value": value_template, "error": str(e)},
          "FAILED",
        )
        raise AssertionError(
          f"Failed to resolve variables for parameter '{key_template}' in table row: {e}"
        )

  except Exception as e:
    raise AssertionError(f"An unexpected error occurred setting parameters from table: {e}")


@step("I set query param {string} from global var {string}")
@step(parsers.parse('I set query param "{param_name}" from global var "{var_name}"'))
def set_query_param_from_global_var(api_domain: CommonApiDomain, api_context, param_name, var_name):
  """Sets a single query parameter using a value from global variables."""
  try:
    # Get the value from global variables
    if var_name in api_domain.ctx.get("global_vars", {}):
      param_value = api_domain.ctx["global_vars"][var_name]
      api_context.setdefault("params", {})
      api_context["params"][param_name] = param_value
      attach_validation_context(
        "Query Parameter Validation",
        {
          "param_name": param_name,
          "param_value": param_value,
          "validation_result": "Query parameter set from global var",
        },
        "PASSED",
      )
      print(f"Set query parameter from global var: {param_name} = {param_value} (from {var_name})")
    else:
      attach_validation_context(
        "Query Parameter Validation",
        {
          "param_name": param_name,
          "param_value": param_value,
          "error": f"Global variable '{var_name}' not found in context",
        },
        "FAILED",
      )
      raise AssertionError(f"Global variable '{var_name}' not found in context")
  except Exception as e:
    raise AssertionError(
      f"Failed to set query parameter '{param_name}' from global var '{var_name}': {e}"
    )


@step("I set query params from global vars")
@parse_datatable()
def set_query_params_from_global_vars(api_domain: CommonApiDomain, api_context, datatable):
  """Sets multiple query parameters using values from global variables."""
  v(datatable, "DataTable provided to step is empty.").is_not_empty()
  try:
    api_context.setdefault("params", {})
    for row in datatable:
      param_name = row["name"]
      var_name = row["value"]
      try:
        # Get the value from global variables
        if var_name in api_domain.ctx.get("global_vars", {}):
          param_value = api_domain.ctx["global_vars"][var_name]
          api_context["params"][param_name] = param_value
          attach_validation_context(
            "Query Parameter Validation",
            {
              "param_name": param_name,
              "param_value": param_value,
              "validation_result": "Query parameter set from global var",
            },
            "PASSED",
          )
          print(
            f"Set query parameter from global var: {param_name} = {param_value} (from {var_name})"
          )
        else:
          attach_validation_context(
            "Query Parameter Validation",
            {
              "param_name": param_name,
              "param_value": param_value,
              "error": f"Global variable '{var_name}' not found in context",
            },
            "FAILED",
          )
          raise AssertionError(f"Global variable '{var_name}' not found in context")
      except Exception as e:
        raise AssertionError(
          f"Failed to set query parameter '{param_name}' from global var '{var_name}': {e}"
        )
  except Exception as e:
    raise AssertionError(f"An unexpected error occurred setting parameters from global vars: {e}")


@step("I execute custom logic:")
@step(parsers.parse("I execute custom logic:"))
def execute_custom_logic(api_context, api_domain: CommonApiDomain, docstring):
  """Executes custom Python code with access to api_context and global variables."""
  try:
    # Create a safe execution environment with access to necessary objects
    exec_globals = {
      "api_context": api_context,
      "global_vars": api_domain.ctx.get("global_vars", {}),
      "ctx": api_domain.ctx,
      "api_domain": api_domain,
      "print": print,
      "len": len,
      "str": str,
      "int": int,
      "float": float,
      "bool": bool,
      "list": list,
      "dict": dict,
      "set": set,
      "tuple": tuple,
      "type": type,
      "isinstance": isinstance,
      "hasattr": hasattr,
      "getattr": getattr,
      "setattr": setattr,
      "json": __import__("json"),
      "re": __import__("re"),
      "datetime": __import__("datetime"),
      "time": __import__("time"),
      "random": __import__("random"),
      "math": __import__("math"),
      "os": __import__("os"),
      "pathlib": __import__("pathlib"),
    }

    # Execute the custom code
    exec(docstring, exec_globals)
    attach_validation_context(
      "Custom Logic Execution",
      {"docstring": docstring, "validation_result": "Custom logic executed successfully"},
      "PASSED",
    )
    print("Custom logic executed successfully")

  except Exception as e:
    attach_validation_context(
      "Custom Logic Execution", {"docstring": docstring, "error": str(e)}, "FAILED"
    )
    raise AssertionError(f"Failed to execute custom logic: {e}")


@step("I set query params from {string}")
@step(parsers.parse('I set query params from "{payload}"'))
def set_query_params_from_file(api_domain: CommonApiDomain, api_context, payload):
  try:
    if "void" not in payload:
      with open(f"src/resources/{payload}.json", "r") as f:
        data = json.load(f)
      api_context["params"] = {}
      api_context["params"].update(
        api_domain.resolve_json_variables(data, api_domain.resolve_variable)
      )
    else:
      api_context["params"] = {}
    attach_validation_context(
      "Query Parameter Validation",
      {"payload": payload, "validation_result": "Query parameters set from file"},
      "PASSED",
    )
  except json.JSONDecodeError as e:
    attach_validation_context(
      "Query Parameter Validation", {"payload": payload, "error": str(e)}, "FAILED"
    )
    print("Error al cargar JSON:", e)


@step("I remove userid from headers")
def _(api_context):
  api_context["headers"]["userid"] = ""


@step("I set headers")
@parse_datatable()
def set_headers_from_table(
  api_domain: CommonApiDomain, api_context, datatable
):  # 'context' gives access to the table
  """Parses a Gherkin DataTable and sets multiple request headers."""
  v(datatable, "DataTable provided to step is empty.").is_not_empty()
  try:
    # Iterate through the rows of the DataTable
    for row in datatable:
      key_template = row["name"]
      value_template = row["value"]
      try:
        # Resolve variables in both the header name (key) and value
        resolved_key = api_domain.resolve_variable(str(key_template))
        resolved_value = api_domain.resolve_variable(str(value_template))
        api_context["headers"][resolved_key] = resolved_value
        attach_validation_context(
          "Header Validation",
          {
            "header_name": resolved_key,
            "header_value": resolved_value,
            "validation_result": "Header set from table",
          },
          "PASSED",
        )
        print(f"Set header from table: {resolved_key} = {resolved_value}")  # Debug info
      except Exception as e:
        attach_validation_context(
          "Header Validation",
          {"header_name": key_template, "header_value": value_template, "error": str(e)},
          "FAILED",
        )
        raise AssertionError(
          f"Failed to resolve variables for header '{key_template}' in table row: {e}"
        )

  except Exception as e:
    raise AssertionError(f"An unexpected error occurred setting headers from table: {e}")


@step("I clear all headers")
@step("I clean all headers")
def clear_all_headers(api_context):
  """Clears all request headers."""
  try:
    # Clear all headers by resetting the headers dictionary
    api_context["headers"].clear()
    attach_validation_context(
      "Header Validation", {"validation_result": "All headers have been cleared"}, "PASSED"
    )
    print("All headers have been cleared")
  except Exception as e:
    attach_validation_context("Header Validation", {"error": str(e)}, "FAILED")
    raise AssertionError(f"An unexpected error occurred clearing headers: {e}")


@step("I clear all headers for external request")
@step("I clean all headers for external request")
def clear_headers_for_external_request(api_context):
  """Clears all headers and enables external request mode to bypass all automatic header injection."""
  try:
    # Clear all headers by resetting the headers dictionary
    api_context["headers"].clear()
    # Enable external request mode to bypass all automatic header addition in APIX client
    api_context["external_request"] = True
    attach_validation_context(
      "Header Validation",
      {"validation_result": "All headers have been cleared for external request"},
      "PASSED",
    )
    print(
      "All headers cleared and external request mode enabled - no automatic headers will be added"
    )
  except Exception as e:
    attach_validation_context("Header Validation", {"error": str(e)}, "FAILED")
    raise AssertionError(f"An unexpected error occurred clearing headers for external request: {e}")


@step("I clear all params")
@step("I clear all query params")
def clear_all_params(api_context):
  """Clears all query parameters."""
  try:
    # Clear all params by resetting the params dictionary
    if "params" in api_context:
      api_context["params"].clear()
      print("All query parameters cleared")
    else:
      # Initialize empty params if it doesn't exist
      api_context["params"] = {}
      print("Query parameters initialized as empty")
    attach_validation_context(
      "Query Parameter Validation",
      {"validation_result": "All query parameters have been cleared"},
      "PASSED",
    )
  except Exception as e:
    attach_validation_context("Query Parameter Validation", {"error": str(e)}, "FAILED")
    raise AssertionError(f"An unexpected error occurred clearing params: {e}")


@step("I set file as raw content")
def set_file_as_raw_content(api_context, api_domain: CommonApiDomain):
  """Alternative way to set file for presigned URL uploads using content parameter."""
  try:
    file_path = "src/resources/advertising/aq_test.csv"

    # Read file as binary
    with open(file_path, "rb") as f:
      file_content = f.read()

    # Clear any existing request body or upload files
    api_context["request_body"] = None
    api_context["upload_files"] = {}
    api_context["multipart_fields"] = {}

    # Set as raw content for httpx
    api_context["raw_content"] = file_content
    attach_validation_context(
      "File as Raw Content", {"validation_result": "File as raw content set"}, "PASSED"
    )
    print(f"Set file as raw content: {len(file_content)} bytes")
  except Exception as e:
    attach_validation_context("File as Raw Content", {"error": str(e)}, "FAILED")
    raise AssertionError(f"Failed to set file as raw content: {e}")


@step("I define vars")
@parse_datatable()
def define_global_vars_from_table(api_domain: CommonApiDomain, api_context, datatable):
  """Parses a Gherkin DataTable and defines multiple global variables."""
  v(datatable, "DataTable provided to step is empty.").is_not_empty()
  api_context.setdefault("global_vars", {})
  try:
    # Iterate through the rows of the DataTable
    for row in datatable:
      var_name = row["name"]
      value_template = row["value"]
      try:
        # Resolve variables in the value before storing
        resolved_value = api_domain.resolve_variable(str(value_template))
        api_context["global_vars"][var_name] = resolved_value
        attach_validation_context(
          "Global Variable Definition",
          {
            "var_name": var_name,
            "var_value": resolved_value,
            "validation_result": "Global variable defined from table",
          },
          "PASSED",
        )
        print(f"Defined global var from table: {var_name} = {resolved_value}")  # Debug info
      except Exception as e:
        attach_validation_context(
          "Global Variable Definition",
          {"var_name": var_name, "var_value": value_template, "error": str(e)},
          "FAILED",
        )
        raise AssertionError(
          f"Failed to resolve variables for variable '{var_name}' in table row: {e}"
        )

  except Exception as e:
    raise AssertionError(f"An unexpected error occurred defining variables from table: {e}")


@step(parsers.parse('I set file named "{field_name_template}" with content:\n{content_template}'))
def set_file_upload_content(
  api_domain: CommonApiDomain, api_context, field_name_template, content_template
):
  """Sets a file for upload using inline content."""
  # File uploads conflict with raw request body, clear it if set.
  if "request_body" in api_context and api_context["request_body"] is not None:
    print("Clearing previously set request body due to setting file upload.")
    api_context["request_body"] = None
  # Also clear potentially conflicting Content-Type header
  api_context["headers"].pop("Content-Type", None)

  api_context.setdefault("upload_files", {})
  try:
    field_name = api_domain.resolve_variable(field_name_template)
    content = api_domain.resolve_variable(content_template)  # Resolve vars in content too
    # For inline content, we need a dummy filename. Use the field name as default.
    filename = f"{field_name}.txt"  # Default filename, maybe make configurable later
    # Store as tuple: (filename, content_bytes, mime_type)
    # Encode content to bytes, assuming UTF-8 for text.
    # Default MIME type to text/plain for inline content.
    api_context["upload_files"][field_name] = (filename, content.encode("utf-8"), "text/plain")
    attach_validation_context(
      "File Upload",
      {
        "field_name": field_name,
        "filename": filename,
        "mime": "text/plain",
        "validation_result": "File upload set from inline content",
      },
      "PASSED",
    )
    print(
      f"Set file upload (inline): field='{field_name}', filename='{filename}', mime='text/plain'"
    )
  except Exception as e:
    attach_validation_context(
      "File Upload",
      {"field_name": field_name, "filename": filename, "mime": "text/plain", "error": str(e)},
      "FAILED",
    )
    raise AssertionError(
      f"Failed to resolve variables/$ for inline file upload '{field_name_template}': {e}"
    )


@step("I set file named {string} from path {string}")
@step(parsers.parse('I set file named "{field_name_template}" from path "{path_template}"'))
def set_file_upload_path(
  api_domain: CommonApiDomain,
  api_context,
  field_name_template,
  path_template,
):
  """Sets a file for upload using a local file path."""
  # File uploads conflict with raw request body, clear it if set.
  if "request_body" in api_context and api_context["request_body"] is not None:
    print("Clearing previously set request body due to setting file upload.")
    api_context["request_body"] = None
  # Also clear potentially conflicting Content-Type header
  api_context["headers"].pop("Content-Type", None)

  api_context.setdefault("upload_files", {})
  try:
    field_name = api_domain.resolve_variable(field_name_template)
    file_path = api_domain.resolve_variable(path_template)
    file_path = f"src/resources/{file_path}"
    # Basic check if file exists
    if not os.path.exists(file_path):
      raise AssertionError(f"File not found at path: {file_path} (or relative to features dir)")

    filename = os.path.basename(file_path)

    # Guess MIME type if not provided or empty
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
      mime_type = "application/octet-stream"  # Default if guess fails
    print(f"Guessed MIME type for '{filename}': {mime_type}")

    # Store as tuple: (filename, file_object, mime_type)
    # We will open the file object in the 'make_request' step to ensure it's handled correctly.
    # Store the path for now, and resolve to file object later.
    api_context["upload_files"][field_name] = (
      filename,
      file_path,
      mime_type,
    )  # Store path initially
    attach_validation_context(
      "File Upload",
      {
        "field_name": field_name,
        "filename": filename,
        "mime": mime_type,
        "validation_result": "File upload set from path",
      },
      "PASSED",
    )
    print(f"Set file upload (path): field='{field_name}', path='{file_path}', mime='{mime_type}'")

  except Exception as e:
    attach_validation_context(
      "File Upload",
      {"field_name": field_name, "filename": filename, "mime": mime_type, "error": str(e)},
      "FAILED",
    )
    raise AssertionError(
      f"Failed to resolve variables/$ for file path upload '{field_name_template}': {e}"
    )


@step("I set binary file from path {string}")
@step(parsers.parse('I set binary file from path "{path_template}"'))
def set_binary_file_upload(
  api_domain: CommonApiDomain,
  api_context,
  path_template,
):
  """Sets binary file content as request body for presigned URL uploads (e.g., GCS)."""
  # Binary file uploads conflict with multipart form data, clear it if set.
  if "upload_files" in api_context and api_context["upload_files"]:
    print("Clearing previously set file uploads due to setting binary file upload.")
    api_context["upload_files"] = {}

  try:
    file_path = api_domain.resolve_variable(path_template)
    full_file_path = f"src/resources/{file_path}"

    # Basic check if file exists
    if not os.path.exists(full_file_path):
      raise AssertionError(f"File not found at path: {full_file_path}")

    # Read file content as binary
    with open(full_file_path, "rb") as file:
      file_content = file.read()

    # Set as request body for binary upload
    api_context["request_body"] = file_content
    attach_validation_context(
      "Binary File Upload",
      {"path": full_file_path, "validation_result": "Binary file content set as request body"},
      "PASSED",
    )
    print(
      f"Set binary file content as request body from path: {full_file_path} ({len(file_content)} bytes)"
    )

  except Exception as e:
    attach_validation_context(
      "Binary File Upload", {"path": full_file_path, "error": str(e)}, "FAILED"
    )
    raise AssertionError(
      f"Failed to resolve variables/$ for binary file upload '{path_template}': {e}"
    )


@step("the order {string} should match with {string}")
@step(parsers.parse('the order "{var1_name}" should match with "{var2_name}"'))
def check_variable_structure_match(api_domain, var1_name, var2_name):
  """
  Checks if two variables stored in global_vars are dictionaries and have the
  exact same keys in the same order. Values are ignored.
  """
  global_vars = api_domain.ctx.get("global_vars", {})

  # Check if variables exist
  v(var1_name in global_vars, f"Variable '{var1_name}' not found in global variables.").is_true()
  v(var2_name in global_vars, f"Variable '{var2_name}' not found in global variables.").is_true()

  var1_value = global_vars[var1_name]
  var2_value = global_vars[var2_name]

  if isinstance(var1_value, dict):
    # Check if both are dictionaries
    v(
      isinstance(var1_value, dict),
      f"Variable '{var1_name}' is not a dictionary (type: {type(var1_value)}).",
    ).is_true()
    v(
      isinstance(var2_value, dict),
      f"Variable '{var2_name}' is not a dictionary (type: {type(var2_value)}).",
    ).is_true()

    # Compare keys (order matters)
    var1_keys = list(var1_value.keys())
    var2_keys = list(var2_value.keys())

    v(
      var1_keys == var2_keys,
      f"Structure mismatch between variable '{var1_name}' and '{var2_name}'.\n"
      f"Keys for '{var1_name}': {var1_keys}\n"
      f"Keys for '{var2_name}': {var2_keys}",
    ).is_true()

  print(f"Structure match the order validated for variables '{var1_name}' and '{var2_name}'.")


@step("the {string} should match with {string}")
@step(parsers.parse('the "{var1_name}" should match with "{var2_name}"'))
def check_variable_match(api_domain, var1_name, var2_name):
  """
  Checks if two variables stored in global_vars are dictionaries and have the
  exact same keys in the same values.
  """
  global_vars = api_domain.ctx.get("global_vars", {})

  # Check if variables exist
  v(var1_name in global_vars, f"Variable '{var1_name}' not found in global variables.").is_true()
  v(var2_name in global_vars, f"Variable '{var2_name}' not found in global variables.").is_true()

  var1_value = global_vars[var1_name]
  var2_value = global_vars[var2_name]

  v(
    var1_value == var2_value,
    f"Structure match validated for variables '{var1_value}' {'\n ==================== \n'*3} '{var2_value}'.",
  ).is_true()


@step("I set multipart field {string} to {string}")
@step(parsers.parse('I set multipart field "{field_name_template}" to "{field_value_template}"'))
def set_multipart_field(api_domain: CommonApiDomain, field_name_template, field_value_template):
  """Sets a regular data field for a multipart/form-data request."""
  api_domain._clear_conflicting_request_data("multipart field")
  api_domain.api_context.setdefault("multipart_fields", {})
  api_domain.set_multipart_field(field_name_template, field_value_template)


@step("I attach file {string} to multipart field {string}")
@step(parsers.parse('I attach file "{path_template}" to multipart field "{field_name_template}"'))
def attach_multipart_file_simple(api_domain: CommonApiDomain, path_template, field_name_template):
  """Attaches a file to a multipart/form-data request, guessing MIME type."""
  # Delegate to the more specific step with mime_type=None
  api_domain.attach_multipart_file_with_mime(path_template, None, field_name_template)


@step("the {string} should have the schema {string}")
@step(parsers.parse('the "{element_name}" should have the schema "{element_schema}"'))
def check_element_schema(ctx, api_domain: CommonApiDomain, element_name, element_schema):
  if "void" not in element_schema:
    if element_name == "responseBody":
      response_json = api_domain.api_context.get("response_json")
      v(response_json, "Response body is not valid JSON or was not parsed").is_not_empty()
      element = response_json
    else:
      global_vars = api_domain.ctx.get("global_vars", {})
      v(
        element_name in global_vars, f"Variable '{element_name}' not found in global variables."
      ).is_true()
      element = global_vars[element_name]

    v(element, "Validate schema").to_has_schema(element_schema)


@step("the {string} should contain the value {string}")
@step(parsers.parse('the "{element_name}" should contain the value "{element_value}"'))
def check_element_contains_value(ctx, api_domain: CommonApiDomain, element_name, element_value):
  global_vars = api_domain.ctx.get("global_vars", {})
  element_name = api_domain.resolve_variable(element_name)
  v(
    element_name in global_vars, f"Variable '{element_name}' not found in global variables."
  ).is_true()
  element = global_vars[element_name]
  element_instance = api_domain.resolve_variable(element_value)
  v(str(element), "Validate contains").contains(element_instance)


@step("the response should contain the value {string}")
@step(parsers.parse('the response should contain the value "{element_value}"'))
def check_response_contains_value(api_context, api_domain: CommonApiDomain, element_value):
  response = api_context.get("response")
  v(response, "No response found in API context").is_not_empty()
  resolved_value = api_domain.resolve_variable(element_value)
  v(response.text, "Response").contains(resolved_value)


@step("the {string} should not contain the value {string}")
@step(parsers.parse('the "{element_name}" should not contain the value "{element_value}"'))
def check_does_not_contain(ctx, api_domain: CommonApiDomain, element_name, element_value):
  global_vars = api_domain.ctx.get("global_vars", {})
  element_name = api_domain.resolve_variable(element_name)
  v(
    element_name in global_vars, f"Variable '{element_name}' not found in global variables."
  ).is_true()
  element = global_vars[element_name]
  element_instance = api_domain.resolve_variable(element_value)
  v(str(element), f"Response message for {element_name}").contains(element_instance)


@step("all elements of {string} should be in {string}")
@step(parsers.parse('all elements of "{list_a_name}" should be in "{list_b_name}"'))
def check_all_elements_contained(api_domain, list_a_name, list_b_name):
  """
  Checks if all elements of list_a are contained in list_b
  """
  global_vars = api_domain.ctx.get("global_vars", {})

  v(
    list_a_name in global_vars, f"Variable '{list_a_name}' not found in global variables."
  ).is_true()
  v(
    list_b_name in global_vars, f"Variable '{list_b_name}' not found in global variables."
  ).is_true()

  list_a = global_vars[list_a_name]
  list_b = global_vars[list_b_name]

  # Ensure both are lists
  v(isinstance(list_a, list), f"'{list_a_name}' is not a list").is_true()
  v(isinstance(list_b, list), f"'{list_b_name}' is not a list").is_true()

  # Check if all elements of list_a are in list_b
  missing_elements = [elem for elem in list_a if elem not in list_b]

  v(
    not missing_elements,
    f"Not all elements of '{list_a_name}' are in '{list_b_name}'. "
    f"Missing elements: {missing_elements}",
  ).is_true()

  print(f":white_check_mark: All elements of '{list_a_name}' are contained in '{list_b_name}'")
