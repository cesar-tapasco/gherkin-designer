from playwright.sync_api import Page, expect
from config import ConfigDict, Config
from src.utils.logger import get_logger
from datetime import datetime
from src.utils.core.request_waiter import RequestWaiter
from typing import List, Any, Optional, Pattern, Callable, Union


class PageBase:
  ctx = {}
  url = ""

  def __init__(self, page: Page, ctx: ConfigDict = None):
    self.page = page
    self.ctx = ctx or {"config": Config()}
    self.config: Config = self.ctx["config"]
    self.logger = get_logger(self.__class__.__name__)
    self.loading_time = 1200000
    self.dismiss_notification = page.locator('[data-testid="notification-dismiss-button"]').or_(
      page.locator('[data-qa="dismiss-button"]')
    )
    self.loading = page.locator(
      '[data-testid="loading"], .mui-style-bpicqv, .loading-overlay, .spinerAnimation, .css-bpicqv'
    )
    self.user_menu_icon = (
      page.locator(".main-menu-icon-color")
      .or_(page.locator('[data-qa="menu-icon"]'))
      .or_(page.locator('[data-qa="user-menu-icon"]'))
      .or_(page.get_by_role(role="button", name="Menu and apps"))
    )
    self.view_as_admin_button = page.get_by_role("button", name="View as an Administrator")
    self.view_as_regular_user_button = page.get_by_role("button", name="View as a Regular User")

  def navigate(self):
    if self.url.strip() == "":
      raise ValueError("url variable is not set")
    self.page.goto(self.url)

  def wait_for_page_load(self):
    """Wait for the page to load completely"""
    self.page.wait_for_load_state("load")

  def is_title_contains(self, text):
    title = self.page.title()
    if title.find(text) == -1:
      return False
    else:
      return True

  def is_url_contains(self, text):
    if self.page.url.find(text) == -1:
      return False
    else:
      return True

  def validate_list_names(self, target_list_options, names_expect):
    count = 0
    for li in target_list_options.all():
      expect(li).to_contain_text(names_expect[count])
      count += 1
      if count == len(names_expect):
        break

  def wait_init_url(self):
    expect(self.loading.first).to_be_hidden(timeout=self.loading_time)
    self.page.wait_for_load_state(state="load")
    if self.is_url_contains("/UpdatesAndNewFeatures"):
      expect(self.dismiss_notification).to_be_visible()
      self.dismiss_notification.click()
      expect(self.loading.first).to_be_hidden(timeout=self.loading_time)
    expect(self.user_menu_icon.first).to_be_visible(timeout=30000)

  def wait_until_element_to_disappears(self, element):
    expect(element).to_have_count(0, timeout=30000)

  def wait_element_change_color(self, element, color, css_property="background-color"):
    expect(element).to_have_css(css_property, color, timeout=30000)

  def validate_current_page(self, timeout=100000):
    if self.page_title:
      expect(self.page_title).to_be_visible(timeout=timeout)
    else:
      raise ValueError("page_title locator is not set")

  def sort_column(self, column_header, sort="asc", sort_attribute="aria-sort"):
    if not column_header.is_visible():
      raise AssertionError("The column does not exist or is not visible on the page")
    sort_map = {"asc": "ascending", "desc": "descending"}
    if sort not in sort_map:
      raise AssertionError("Invalid sort order. Use 'asc' or 'desc'.")
    while column_header.get_attribute(sort_attribute) != "none":
      column_header.click()
    for _ in range(1 if sort == "asc" else 2):
      column_header.click()
    sort_status = column_header.get_attribute(sort_attribute)
    if sort_status != sort_map[sort]:
      raise ValueError(f"Expected '{sort_map[sort]}', but got '{sort_status}'")

  def is_date_format(self, text):
    # Check if elements are dates (MM-DD-YYYY format)
    try:
      datetime.strptime(text, "%m-%d-%Y")
      return True
    except ValueError:
      return False

  def _collect_element_texts(self, elements_locator) -> List[str]:
    """Collect all inner texts from elements."""
    all_elements = []
    for element in elements_locator:
      all_elements += element.all_inner_texts()
    return all_elements

  def _validate_date_sort(self, date_strings: List[str], sort: str) -> None:
    """Validate that date elements are sorted correctly."""
    date_objects = [datetime.strptime(date_str, "%m-%d-%Y") for date_str in date_strings]
    sorted_dates = sorted(date_objects, reverse=(sort == "desc"))

    if date_objects != sorted_dates:
      order = "ascending" if sort == "asc" else "descending"
      raise AssertionError(f"The date elements are not sorted in {order} order")

  def _validate_string_sort(self, elements: List[str], sort: str) -> None:
    """Validate that string elements are sorted correctly."""
    if sort == "asc":
      sorted_elements = sorted(elements)
      if elements != sorted_elements:
        raise AssertionError(f"The elements: {elements} are not sorted in ascending order")
    elif sort == "desc":
      reversed_elements = elements[::-1]
      sorted_reversed = sorted(reversed_elements, reverse=True)
      if reversed_elements != sorted_reversed:
        raise AssertionError(
          f"The elements: {reversed_elements} are not sorted in descending order"
        )

  def validate_sort_column(self, elements_locator, sort):
    """Validate that column elements are sorted in the specified order."""
    if sort not in ["asc", "desc"]:
      raise ValueError("Invalid sort order. Use 'asc' or 'desc'")

    all_elements = self._collect_element_texts(elements_locator)

    if all_elements and self.is_date_format(all_elements[0]):
      self._validate_date_sort(all_elements, sort)
    else:
      self._validate_string_sort(all_elements, sort)

  def validate_current_url(self, expected_url):
    expect(self.page).to_have_url(expected_url)

  def wait_until_loading_indicator_disappear(self):
    expect(self.loading.first).to_be_hidden(timeout=self.loading_time)

  def reload_page(self):
    self.page.reload()

  def get_background_color(self, element):
    return element.evaluate("el => getComputedStyle(el).backgroundColor")

  def get_color(self, element):
    return element.evaluate("el => getComputedStyle(el).color")

  def wait_for_request(
    self,
    url_regex: Optional[Union[str, Pattern]] = None,
    *,
    methods: Optional[Union[str, List[str]]] = None,
    status_codes: Optional[Union[int, List[int]]] = None,
    request_body_predicate: Optional[Callable[[Any], bool]] = None,
    response_body_predicate: Optional[Callable[[Any], bool]] = None,
    expected_matches: int = 1,
    timeout_ms: int = 30000,
  ) -> List[Any]:
    """
    Waits for one or more network responses that match the provided filters using a
    page.on listener strategy, and detaches the listener when finished.

    Args:
      url_regex: String or compiled regex to match the request/response URL.
      methods: HTTP method(s) to match (e.g., "GET", "POST"). Case-insensitive.
      status_codes: HTTP status code or list of codes to match (e.g., 200 or [200, 204]).
      request_body_predicate: Callable that receives the request body (parsed JSON if possible,
        otherwise raw string) and returns True if acceptable.
      response_body_predicate: Callable that receives the response body (parsed JSON if possible,
        otherwise raw string) and returns True if acceptable.
      expected_matches: Number of matching responses to wait for before resolving.
      timeout_ms: Maximum time to wait in milliseconds.

    Returns:
      List of matching playwright Response objects.

    Raises:
      TimeoutError: If the expected matches are not collected before the timeout.

    Examples:
      Basic 200 match by URL substring:
      >>> self.wait_for_request(url_regex="/api/patient-groups", methods="GET", status_codes=200)

      Regex URL and JSON body validation:
      >>> self.wait_for_request(
      ...   url_regex=r"/api/patient-groups/\\d+",
      ...   status_codes=[200, 201],
      ...   response_body_predicate=lambda body: body and body.get("status") == "READY",
      ... )

      Wait for multiple matches (e.g., two requests):
      >>> self.wait_for_request(url_regex="/batch", expected_matches=2, timeout_ms=60000)
    """

    waiter = RequestWaiter(self.page, logger=self.logger)
    return waiter.wait(
      url_regex=url_regex,
      methods=methods,
      status_codes=status_codes,
      request_body_predicate=request_body_predicate,
      response_body_predicate=response_body_predicate,
      expected_matches=expected_matches,
      timeout_ms=timeout_ms,
    )
