import json
import time
import re
from playwright.sync_api import Page, Response
from typing import List, Any, Optional, Pattern, Callable, Union
from src.utils.core.query_jq import JSONQueryJQ


class ResponseMatcherWaiter:
  """Utility to wait for Playwright network responses using an event-listener strategy.

  This class attaches a temporary `response` listener to the provided `page`, collects
  matching responses according to filters, and then detaches the listener once done.
  """

  def __init__(self, response: Response, jq: JSONQueryJQ):
    self.response = response
    self.jq = jq


class RequestWaiter:
  """Utility to wait for Playwright network responses using an event-listener strategy.

  This class attaches a temporary `response` listener to the provided `page`, collects
  matching responses according to filters, and then detaches the listener once done.

  Examples:
    Instantiate and use directly:
    >>> waiter = RequestWaiter(page, logger)
    >>> responses = waiter.wait(url_regex=r"/api/items/\\d+", methods=["GET"], status_codes=200)

    Through `DomainBase` via convenience method:
    >>> self.wait_for_request(
    ...   url_regex="/api/patient-groups",
    ...   methods="POST",
    ...   response_body_predicate=lambda b: b and b.get("status") == "READY",
    ... )
  """

  def __init__(self, page: Page, logger=None):
    self.page = page
    self.logger = logger

  @staticmethod
  def _build_url_matcher(pattern: Optional[Union[str, Pattern]]) -> Callable[[str], bool]:
    """Build a URL matching function from pattern."""
    if pattern is None:
      return lambda _url: True
    if isinstance(pattern, re.Pattern):
      return lambda _url: bool(pattern.search(_url))
    if isinstance(pattern, str) and pattern:
      return RequestWaiter._compile_string_pattern(pattern)
    return lambda _url: False

  @staticmethod
  def _compile_string_pattern(pattern: str) -> Callable[[str], bool]:
    """Compile string pattern into a matcher function."""
    try:
      compiled_local = re.compile(pattern)
      return lambda _url: bool(compiled_local.search(_url))
    except re.error:
      return RequestWaiter._build_fnmatch_or_escaped(pattern)

  @staticmethod
  def _build_fnmatch_or_escaped(pattern: str) -> Callable[[str], bool]:
    """Build fnmatch or escaped pattern matcher."""
    import fnmatch

    if any(ch in pattern for ch in ("*", "?", "[", "]")):
      return lambda _url: fnmatch.fnmatch(_url, pattern)
    escaped = re.compile(re.escape(pattern))
    return lambda _url: bool(escaped.search(_url))

  @staticmethod
  def _normalize_methods(methods: Optional[Union[str, List[str]]]) -> Optional[set]:
    """Normalize methods parameter to a set of lowercase strings."""
    if methods is None:
      return None
    if isinstance(methods, str):
      return {methods.lower()}
    return {m.lower() for m in methods}

  @staticmethod
  def _normalize_status_codes(status_codes: Optional[Union[int, List[int]]]) -> Optional[set]:
    """Normalize status codes parameter to a set."""
    if status_codes is None:
      return None
    if isinstance(status_codes, int):
      return {status_codes}
    return set(status_codes)

  @staticmethod
  def _body_as_json_or_text(body_provider: Callable[[], Any]) -> Any:
    """Convert body data to JSON or text."""
    try:
      data = body_provider()
      if isinstance(data, (dict, list)):
        return data
      if data is None:
        return None
      if isinstance(data, (bytes, bytearray)):
        return RequestWaiter._decode_bytes_body(data)
      if isinstance(data, str):
        return RequestWaiter._parse_string_body(data)
      return data
    except Exception:
      return None

  @staticmethod
  def _decode_bytes_body(data: Union[bytes, bytearray]) -> Any:
    """Decode bytes/bytearray body to JSON or text."""
    try:
      return json.loads(data.decode("utf-8", errors="ignore"))
    except Exception:
      return data.decode("utf-8", errors="ignore")

  @staticmethod
  def _parse_string_body(data: str) -> Any:
    """Parse string body as JSON or return as-is."""
    try:
      return json.loads(data)
    except Exception:
      return data

  def _get_request_method(self, response: Response) -> str:
    """Extract request method from response."""
    if response.request and response.request.method:
      return response.request.method.lower()
    return ""

  def _get_request_body(self, response: Response) -> Any:
    """Extract and parse request body from response."""

    def req_body_provider():
      try:
        return response.request.post_data
      except Exception:
        return None

    return self._body_as_json_or_text(req_body_provider)

  def _get_response_body(self, response: Response) -> Any:
    """Extract and parse response body from response."""

    def resp_body_provider():
      try:
        return response.json()
      except Exception:
        try:
          return response.text()
        except Exception:
          return None

    return self._body_as_json_or_text(resp_body_provider)

  def _matches_url(self, response: Response, url_matches: Callable[[str], bool]) -> bool:
    """Check if response URL matches the pattern."""
    return url_matches(response.url)

  def _matches_method(self, response: Response, method_set: Optional[set]) -> bool:
    """Check if response method matches the filter."""
    if method_set is None:
      return True
    req_method = self._get_request_method(response)
    return req_method in method_set

  def _matches_status(self, response: Response, status_set: Optional[set]) -> bool:
    """Check if response status matches the filter."""
    if status_set is None:
      return True
    return response.status in status_set

  def _matches_request_body(
    self, response: Response, request_body_predicate: Optional[Callable[[Any], bool]]
  ) -> bool:
    """Check if request body matches the predicate."""
    if request_body_predicate is None:
      return True
    req_body = self._get_request_body(response)
    return request_body_predicate(req_body)

  def _matches_response_body(
    self, response: Response, response_body_predicate: Optional[Callable[[Any], bool]]
  ) -> bool:
    """Check if response body matches the predicate."""
    if response_body_predicate is None:
      return True
    resp_body = self._get_response_body(response)
    return response_body_predicate(resp_body)

  def _create_response_matcher(self, response: Response) -> ResponseMatcherWaiter:
    """Create a ResponseMatcherWaiter from a response."""
    try:
      return ResponseMatcherWaiter(response, JSONQueryJQ(response.json()))
    except Exception:
      return ResponseMatcherWaiter(response, None)

  def _response_matches_all_filters(
    self,
    response: Response,
    url_matches: Callable[[str], bool],
    method_set: Optional[set],
    status_set: Optional[set],
    request_body_predicate: Optional[Callable[[Any], bool]],
    response_body_predicate: Optional[Callable[[Any], bool]],
  ) -> bool:
    """Check if response matches all filters."""
    return (
      self._matches_url(response, url_matches)
      and self._matches_method(response, method_set)
      and self._matches_status(response, status_set)
      and self._matches_request_body(response, request_body_predicate)
      and self._matches_response_body(response, response_body_predicate)
    )

  def _detach_listener(self, listener: Callable):
    """Detach the response listener from the page."""
    if hasattr(self.page, "off"):
      self.page.off("response", listener)  # type: ignore[attr-defined]
    else:
      self.page.remove_listener("response", listener)  # type: ignore[attr-defined]

  def _wait_for_matches(
    self,
    matches: List[ResponseMatcherWaiter],
    expected_matches: int,
    timeout_ms: int,
    url_regex: Optional[Union[str, Pattern]],
  ) -> List[Any]:
    """Wait for the expected number of matches or timeout."""
    start = time.time()
    while (time.time() - start) * 1000 < timeout_ms:
      if len(matches) >= max(1, int(expected_matches)):
        return matches[:expected_matches]
      self.page.wait_for_timeout(50)
    raise AssertionError(
      f"Timed out after {timeout_ms}ms waiting for {expected_matches} matching request(s) - for url regex{url_regex}."
    )

  def wait(
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
    """Wait for network responses matching the specified filters."""
    url_matches = self._build_url_matcher(url_regex)
    method_set = self._normalize_methods(methods)
    status_set = self._normalize_status_codes(status_codes)
    matches: List[ResponseMatcherWaiter] = []

    def _on_response(response):
      try:
        if self._response_matches_all_filters(
          response,
          url_matches,
          method_set,
          status_set,
          request_body_predicate,
          response_body_predicate,
        ):
          response_match = self._create_response_matcher(response)
          matches.append(response_match)
      except Exception as e:
        if self.logger:
          self.logger.debug(f"RequestWaiter listener error: {e}")

    self.page.on("response", _on_response)

    try:
      return self._wait_for_matches(matches, expected_matches, timeout_ms, url_regex)
    finally:
      self._detach_listener(_on_response)
