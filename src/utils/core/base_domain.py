import json
import os
import tempfile
import string
from abc import ABC
from src.utils.logger import get_logger
from config import ConfigDict, Config
from playwright.sync_api import Page
from mimesis import Generic
from src.utils.core.query_jq import JSONQueryJQ
from datetime import datetime
from typing import Dict, Any, Optional, TypedDict


class TaskOptions(TypedDict, total=False):
  only_status: bool
  internal_req: bool


class DomainBase(ABC):
  def __init__(self, page: Page, ctx: ConfigDict = None):
    self.page = page
    self.ctx = ctx or {"config": Config()}
    self.config: Config = self.ctx["config"]
    self.gen = Generic("en")
    self.default_task_options: TaskOptions = {
      "only_status": True,
      "internal_req": False,
    }
    self.logger = get_logger(self.__class__.__name__)
    self.query_elements = """
    if .content!=null then
      .content[]
    elif ._embedded!=null then
      ._embedded[]
    else
      null
    end
    """

  def jq(self, data):
    return JSONQueryJQ(data)

  def get_resource(self, src_path, src_type="json"):
    with open(f"src/resources/{src_path}", "r") as f:
      if src_type == "json":
        return json.load(f)
    return f.read()

  def get_resource_path(self, src_path):
    relative_path = f"src/resources/{src_path}"
    return os.path.abspath(relative_path)

  def _generate_single_and_clause(self, clause_dict: Dict[str, Any]) -> Optional[str]:
    """
    Helper function to generate a single '(and ...)' clause string from a dictionary.
    Validates the input and handles creating the '(phrase ...)' parts.

    Args:
        clause_dict: The dictionary defining the AND clause.

    Returns:
        The '(and ...)' clause string if valid and non-empty,
        or None if the input dictionary is invalid or results in no phrases.
    """
    # Validate input dictionary (logic moved from the main loop)
    if not isinstance(clause_dict, dict) or not clause_dict:
      # print(f"Warning: Skipping invalid or empty clause definition: {clause_dict}")
      return None  # Indicates this definition doesn't yield a valid clause

    current_phrase_parts = []
    for field, value in clause_dict.items():
      # Skip if field or value is None
      if field is None or value is None:
        # print(f"Warning: Skipping field-value pair with None key/value in clause: {clause_dict}")
        continue

      # --- Basic Value Sanitization (IMPORTANT: adjust based on your query engine!) ---
      sanitized_value = str(value).replace("'", "\\'")
      sanitized_field = str(field)

      # Create the (phrase ...) part
      phrase_part = f"(phrase field={sanitized_field} '{sanitized_value}')"
      current_phrase_parts.append(phrase_part)

    # If valid phrase parts were created, combine them into an (and ...) clause
    if current_phrase_parts:
      return f"(and {' '.join(current_phrase_parts)})"
    else:
      # Dictionary was valid but resulted in no phrases (e.g., all values were None)
      return None

  def get_current_state(self, statuses, current_status):
    return next(
      (status for status in statuses if status["state"] == current_status),
      None,
    )

  def pick_random_element(self, elements_list):
    return self.gen.random.choice(elements_list.jq.all(self.query_elements))

  def pick_random_elements(self, elements_list, k=1):
    elements = elements_list.jq.all(self.query_elements)
    return self.gen.random.choices(elements, k=k)

  def random_num(self, num_from=0, num_to=10):
    "Get a random number and exclude limits"
    return self.gen.random.randrange(num_from, num_to)

  # Generate a random float with the specified number of digits
  def generate_random_float(self, digits):
    # The number of digits before the decimal point
    integer_digits = digits - 1  # At least 1 digit for the integer part
    min_value = 10 ** (integer_digits - 1)  # Minimum value for the integer part
    max_value = 10**integer_digits - 1  # Maximum value for the integer part

    # Generate the integer part of the number
    integer_part = self.gen.random.randint(min_value, max_value)

    # Generate the decimal part based on the remaining digits
    decimal_part = self.gen.random.randint(0, 10 ** (digits - integer_digits) - 1)

    # Combine integer and decimal parts
    float_number = float(f"{integer_part}.{decimal_part:0{digits - integer_digits}}")

    return float_number

  def generate_random_string(self, string_len=2):
    # Generate a random string of the specified length
    if string_len <= 0:
      raise ValueError("string_len must be greater than 0")
    return "".join(self.gen.random.choice(string.ascii_letters) for _ in range(string_len))

  def get_current_date(self, format="%Y-%m-%d"):
    return datetime.now().strftime(format)

  def get_temp_file_path(self, file_name, file_extension="csv"):
    temp_dir = tempfile.mkdtemp()
    csv_file_path = os.path.join(
      temp_dir, f"{file_name or self.generate_random_string()}.{file_extension}"
    )
    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)
    return csv_file_path

  def create_temp_file(self, file_name, file_extension="csv", file_content=None):
    file_path = self.get_temp_file_path(file_name, file_extension)
    with open(file_path, "w") as f:
      f.write(file_content or "")
    return file_path

  def get_locator(self, locator_name):
    return self.page.locator(locator_name)

  def manage_handle_request(self, url_route, ctx, key):
    def handle_request(route):
      response = route.fetch()
      try:
        json_data = response.json()
      except json.JSONDecodeError:
        json_data = response.text()
        self.logger.warning(f"Response is not JSON, storing as text for key: {key}")
      ctx[key] = json_data
      route.continue_()
      self.page.unroute(url_route)

    self.page.route(url_route, handle_request)
