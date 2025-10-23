import pytest
from pytest_bdd import step, parsers
from playwright.sync_api import Page

from src.utils.core.validator import Validator as v


@pytest.fixture
def ui_context(ctx, page):
  """Provides UI context for Playwright operations."""
  ctx.setdefault("ui_vars", {})
  return ctx


@step("pause")
def _(page: Page):
  page.pause()


@step("the user navigates to {string}")
@step(parsers.parse('the user navigates to "{url_template}"'))
def navigate_to_url(page: Page, ctx, url_template):
  """Navigates to the specified URL, resolving variables."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_url = domain.resolve_variable(url_template)
  print(f"Navigating to: {resolved_url}")
  page.goto(resolved_url)
  page.wait_for_load_state("domcontentloaded")


@step("the user clicks on {string}")
@step(parsers.parse('the user clicks on "{selector_template}"'))
def click_element(page: Page, ctx, selector_template):
  """Clicks on an element identified by selector."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Clicking on: {resolved_selector}")
  page.locator(resolved_selector).click()


@step("the user clicks on {string} with timeout {int}s")
@step(parsers.parse('the user clicks on "{selector_template}" with timeout {timeout}s'))
def click_element_with_timeout(page: Page, ctx, selector_template, timeout):
  """Clicks on an element with a custom timeout."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Clicking on: {resolved_selector} with timeout {timeout}s")
  page.locator(resolved_selector).click(timeout=timeout * 1000)


@step("the user double clicks on {string}")
@step(parsers.parse('the user double clicks on "{selector_template}"'))
def double_click_element(page: Page, ctx, selector_template):
  """Double clicks on an element identified by selector."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Double clicking on: {resolved_selector}")
  page.locator(resolved_selector).dblclick()


@step("the user right clicks on {string}")
@step(parsers.parse('the user right clicks on "{selector_template}"'))
def right_click_element(page: Page, ctx, selector_template):
  """Right clicks on an element identified by selector."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Right clicking on: {resolved_selector}")
  page.locator(resolved_selector).click(button="right")


@step("the user hovers over {string}")
@step(parsers.parse('the user hovers over "{selector_template}"'))
def hover_element(page: Page, ctx, selector_template):
  """Hovers over an element identified by selector."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Hovering over: {resolved_selector}")
  page.locator(resolved_selector).hover()


@step("the user types {string} into {string}")
@step(parsers.parse('the user types "{text_template}" into "{selector_template}"'))
def type_into_element(page: Page, ctx, text_template, selector_template):
  """Types text into an input element."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_text = domain.resolve_variable(text_template)
  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Typing '{resolved_text}' into: {resolved_selector}")
  page.locator(resolved_selector).fill(resolved_text)


@step("the user types {string} into {string} slowly")
@step(parsers.parse('the user types "{text_template}" into "{selector_template}" slowly'))
def type_into_element_slowly(page: Page, ctx, text_template, selector_template):
  """Types text into an input element character by character (slow typing)."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_text = domain.resolve_variable(text_template)
  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Typing '{resolved_text}' slowly into: {resolved_selector}")
  page.locator(resolved_selector).type(resolved_text, delay=100)


@step("the user clears {string}")
@step(parsers.parse('the user clears "{selector_template}"'))
def clear_element(page: Page, ctx, selector_template):
  """Clears an input element."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Clearing: {resolved_selector}")
  page.locator(resolved_selector).clear()


@step("the user fills {string} with {string}")
@step(parsers.parse('the user fills "{selector_template}" with "{text_template}"'))
def fill_element(page: Page, ctx, selector_template, text_template):
  """Fills an input element (clears first, then types)."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_text = domain.resolve_variable(text_template)
  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Filling '{resolved_selector}' with: {resolved_text}")
  page.locator(resolved_selector).fill(resolved_text)


@step("the user presses {string}")
@step(parsers.parse('the user presses "{key}"'))
def press_key(page: Page, key):
  """Presses a keyboard key."""
  print(f"Pressing key: {key}")
  page.keyboard.press(key)


@step("the user presses {string} on {string}")
@step(parsers.parse('the user presses "{key}" on "{selector_template}"'))
def press_key_on_element(page: Page, ctx, key, selector_template):
  """Presses a keyboard key on a specific element."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Pressing '{key}' on: {resolved_selector}")
  page.locator(resolved_selector).press(key)


@step("the user selects {string} from {string}")
@step(parsers.parse('the user selects "{option_template}" from "{selector_template}"'))
def select_option(page: Page, ctx, option_template, selector_template):
  """Selects an option from a dropdown."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_option = domain.resolve_variable(option_template)
  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Selecting '{resolved_option}' from: {resolved_selector}")
  page.locator(resolved_selector).select_option(resolved_option)


@step("the user checks {string}")
@step(parsers.parse('the user checks "{selector_template}"'))
def check_element(page: Page, ctx, selector_template):
  """Checks a checkbox or radio button."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Checking: {resolved_selector}")
  page.locator(resolved_selector).check()


@step("the user unchecks {string}")
@step(parsers.parse('the user unchecks "{selector_template}"'))
def uncheck_element(page: Page, ctx, selector_template):
  """Unchecks a checkbox."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Unchecking: {resolved_selector}")
  page.locator(resolved_selector).uncheck()


@step("the user uploads file {string} to {string}")
@step(parsers.parse('the user uploads file "{file_path_template}" to "{selector_template}"'))
def upload_file(page: Page, ctx, file_path_template, selector_template):
  """Uploads a file to a file input element."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_file_path = domain.resolve_variable(file_path_template)
  resolved_selector = domain.resolve_variable(selector_template)
  full_file_path = f"src/resources/{resolved_file_path}"

  print(f"Uploading file '{full_file_path}' to: {resolved_selector}")
  page.locator(resolved_selector).set_input_files(full_file_path)


@step("the user waits for {string} to be visible")
@step(parsers.parse('the user waits for "{selector_template}" to be visible'))
def wait_for_visible(page: Page, ctx, selector_template):
  """Waits for an element to be visible."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Waiting for visibility: {resolved_selector}")
  page.locator(resolved_selector).wait_for(state="visible")


@step("the user waits for {string} to be hidden")
@step(parsers.parse('the user waits for "{selector_template}" to be hidden'))
def wait_for_hidden(page: Page, ctx, selector_template):
  """Waits for an element to be hidden."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Waiting for hidden: {resolved_selector}")
  page.locator(resolved_selector).wait_for(state="hidden")


@step("the user waits for {string} to be enabled")
@step(parsers.parse('the user waits for "{selector_template}" to be enabled'))
def wait_for_enabled(page: Page, ctx, selector_template):
  """Waits for an element to be enabled."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Waiting for enabled: {resolved_selector}")
  page.locator(resolved_selector).wait_for(state="attached")
  v(page.locator(resolved_selector)).locator().to_be_enabled()


@step("the user waits for page load")
def wait_for_page_load(page: Page):
  """Waits for page to fully load."""
  print("Waiting for page load")
  page.wait_for_load_state("load")


@step("the user waits for network idle")
def wait_for_network_idle(page: Page):
  """Waits for network to be idle."""
  print("Waiting for network idle")
  page.wait_for_load_state("networkidle")


@step("the user waits for {int} seconds")
@step(parsers.parse("the user waits for {timeout:d} seconds"))
def wait_for_timeout_seconds(page: Page, timeout):
  """Waits for a specified number of seconds."""
  print(f"Waiting for {timeout} seconds")
  page.wait_for_timeout(timeout * 1000)


@step("the element {string} should be visible")
@step(parsers.parse('the element "{selector_template}" should be visible'))
def assert_element_visible(page: Page, ctx, selector_template):
  """Asserts that an element is visible."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Asserting visibility: {resolved_selector}")
  v(page.locator(resolved_selector)).locator().to_be_visible()


@step("the element {string} should be hidden")
@step(parsers.parse('the element "{selector_template}" should be hidden'))
def assert_element_hidden(page: Page, ctx, selector_template):
  """Asserts that an element is hidden."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Asserting hidden: {resolved_selector}")
  v(page.locator(resolved_selector)).locator().to_be_hidden()


@step("the element {string} should not be visible")
@step(parsers.parse('the element "{selector_template}" should not be visible'))
def assert_element_not_visible(page: Page, ctx, selector_template):
  """Asserts that an element is not visible."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Asserting not visible: {resolved_selector}")
  v(page.locator(resolved_selector)).locator().not_to_be_visible()


@step("the element {string} should contain text {string}")
@step(parsers.parse('the element "{selector_template}" should contain text "{text_template}"'))
def assert_element_contains_text(page: Page, ctx, selector_template, text_template):
  """Asserts that an element contains specific text."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  resolved_text = domain.resolve_variable(text_template)
  print(f"Asserting '{resolved_selector}' contains text: {resolved_text}")
  v(page.locator(resolved_selector)).locator().to_contain_text(resolved_text)


@step("the element {string} should have text {string}")
@step(parsers.parse('the element "{selector_template}" should have text "{text_template}"'))
def assert_element_has_text(page: Page, ctx, selector_template, text_template):
  """Asserts that an element has exact text."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  resolved_text = domain.resolve_variable(text_template)
  print(f"Asserting '{resolved_selector}' has text: {resolved_text}")
  v(page.locator(resolved_selector)).locator().to_have_text(resolved_text)


@step("the element {string} should have value {string}")
@step(parsers.parse('the element "{selector_template}" should have value "{value_template}"'))
def assert_element_has_value(page: Page, ctx, selector_template, value_template):
  """Asserts that an input element has a specific value."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  resolved_value = domain.resolve_variable(value_template)
  print(f"Asserting '{resolved_selector}' has value: {resolved_value}")
  v(page.locator(resolved_selector)).locator().to_have_value(resolved_value)


@step("the element {string} should be enabled")
@step(parsers.parse('the element "{selector_template}" should be enabled'))
def assert_element_enabled(page: Page, ctx, selector_template):
  """Asserts that an element is enabled."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Asserting enabled: {resolved_selector}")
  v(page.locator(resolved_selector)).locator().to_be_enabled()


@step("the element {string} should be disabled")
@step(parsers.parse('the element "{selector_template}" should be disabled'))
def assert_element_disabled(page: Page, ctx, selector_template):
  """Asserts that an element is disabled."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Asserting disabled: {resolved_selector}")
  v(page.locator(resolved_selector)).locator().to_be_disabled()


@step("the element {string} should be checked")
@step(parsers.parse('the element "{selector_template}" should be checked'))
def assert_element_checked(page: Page, ctx, selector_template):
  """Asserts that a checkbox/radio is checked."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Asserting checked: {resolved_selector}")
  v(page.locator(resolved_selector)).locator().to_be_checked()


@step("the element {string} should not be checked")
@step(parsers.parse('the element "{selector_template}" should not be checked'))
def assert_element_not_checked(page: Page, ctx, selector_template):
  """Asserts that a checkbox/radio is not checked."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Asserting not checked: {resolved_selector}")
  v(page.locator(resolved_selector)).locator().not_to_be_checked()


@step("the element {string} should have count {int}")
@step(parsers.parse('the element "{selector_template}" should have count {count:d}'))
def assert_element_count(page: Page, ctx, selector_template, count):
  """Asserts the count of elements matching selector."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Asserting '{resolved_selector}' has count: {count}")
  v(page.locator(resolved_selector)).locator().to_have_count(count)


@step("the page title should be {string}")
@step(parsers.parse('the page title should be "{title_template}"'))
def assert_page_title(page: Page, ctx, title_template):
  """Asserts the page title."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_title = domain.resolve_variable(title_template)
  print(f"Asserting page title: {resolved_title}")
  v(page).locator().to_have_title(resolved_title)


@step("the page URL should contain {string}")
@step(parsers.parse('the page URL should contain "{url_part_template}"'))
def assert_url_contains(page: Page, ctx, url_part_template):
  """Asserts the page URL contains specific text."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_url_part = domain.resolve_variable(url_part_template)
  print(f"Asserting URL contains: {resolved_url_part}")
  v(page).locator().to_have_url(lambda url: resolved_url_part in url)


@step("the user should be on {string}")
@step(parsers.parse('the user should be on "{url_template}"'))
def assert_current_url(page: Page, ctx, url_template):
  """Asserts that the current page URL matches the expected URL."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_url = domain.resolve_variable(url_template)
  print(f"Asserting current URL is: {resolved_url}")
  v(page).locator().to_have_url(resolved_url)


@step("the user scrolls to {string}")
@step(parsers.parse('the user scrolls to "{selector_template}"'))
def scroll_to_element(page: Page, ctx, selector_template):
  """Scrolls to an element."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Scrolling to: {resolved_selector}")
  page.locator(resolved_selector).scroll_into_view_if_needed()


@step("the user takes a screenshot as {string}")
@step(parsers.parse('the user takes a screenshot as "{filename_template}"'))
def take_screenshot(page: Page, ctx, filename_template):
  """Takes a screenshot and saves it."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_filename = domain.resolve_variable(filename_template)
  screenshot_path = f".temp/screenshots/{resolved_filename}"
  print(f"Taking screenshot: {screenshot_path}")
  page.screenshot(path=screenshot_path)


@step("the user reloads the page")
def reload_page(page: Page):
  """Reloads the current page."""
  print("Reloading page")
  page.reload()


@step("the user goes back")
def go_back(page: Page):
  """Navigates back in browser history."""
  print("Navigating back")
  page.go_back()


@step("the user goes forward")
def go_forward(page: Page):
  """Navigates forward in browser history."""
  print("Navigating forward")
  page.go_forward()


@step("the user focuses on {string}")
@step(parsers.parse('the user focuses on "{selector_template}"'))
def focus_element(page: Page, ctx, selector_template):
  """Focuses on an element."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Focusing on: {resolved_selector}")
  page.locator(resolved_selector).focus()


@step("the user drags {string} to {string}")
@step(parsers.parse('the user drags "{source_selector}" to "{target_selector}"'))
def drag_and_drop(page: Page, ctx, source_selector, target_selector):
  """Drags an element to another element."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_source = domain.resolve_variable(source_selector)
  resolved_target = domain.resolve_variable(target_selector)
  print(f"Dragging '{resolved_source}' to '{resolved_target}'")
  page.locator(resolved_source).drag_to(page.locator(resolved_target))


@step("I store text from {string} as {string}")
@step(parsers.parse('I store text from "{selector_template}" as "{variable_name}"'))
def store_text_from_element(page: Page, ctx, selector_template, variable_name):
  """Stores text from an element into a variable."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  text_content = page.locator(resolved_selector).text_content()
  ctx["global_vars"][variable_name] = text_content
  print(f"Stored text from '{resolved_selector}' as '{variable_name}': {text_content}")


@step("I store attribute {string} from {string} as {string}")
@step(
  parsers.parse('I store attribute "{attribute}" from "{selector_template}" as "{variable_name}"')
)
def store_attribute_from_element(page: Page, ctx, attribute, selector_template, variable_name):
  """Stores an attribute value from an element into a variable."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  attribute_value = page.locator(resolved_selector).get_attribute(attribute)
  ctx["global_vars"][variable_name] = attribute_value
  print(
    f"Stored attribute '{attribute}' from '{resolved_selector}' as '{variable_name}': {attribute_value}"
  )


@step("I store value from {string} as {string}")
@step(parsers.parse('I store value from "{selector_template}" as "{variable_name}"'))
def store_value_from_element(page: Page, ctx, selector_template, variable_name):
  """Stores the value from an input element into a variable."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  input_value = page.locator(resolved_selector).input_value()
  ctx["global_vars"][variable_name] = input_value
  print(f"Stored value from '{resolved_selector}' as '{variable_name}': {input_value}")


@step("the user executes javascript:")
@step(parsers.parse("the user executes javascript:"))
def execute_javascript(page: Page, ctx, docstring):
  """Executes custom JavaScript code in the page context."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_script = domain.resolve_variable(docstring)
  print(f"Executing JavaScript: {resolved_script[:100]}...")
  result = page.evaluate(resolved_script)
  if result is not None:
    ctx["global_vars"]["js_result"] = result
    print(f"JavaScript result: {result}")


@step("the user waits for selector {string} with timeout {int}s")
@step(parsers.parse('the user waits for selector "{selector_template}" with timeout {timeout}s'))
def wait_for_selector_with_timeout(page: Page, ctx, selector_template, timeout):
  """Waits for a selector to appear with custom timeout."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  print(f"Waiting for selector '{resolved_selector}' with timeout {timeout}s")
  page.wait_for_selector(resolved_selector, timeout=timeout * 1000)


@step("the user clicks on text {string}")
@step(parsers.parse('the user clicks on text "{text_template}"'))
def click_by_text(page: Page, ctx, text_template):
  """Clicks on an element containing specific text."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_text = domain.resolve_variable(text_template)
  print(f"Clicking on element with text: {resolved_text}")
  page.get_by_text(resolved_text).click()


@step("the user clicks on role {string} with name {string}")
@step(parsers.parse('the user clicks on role "{role}" with name "{name_template}"'))
def click_by_role(page: Page, ctx, role, name_template):
  """Clicks on an element by role and accessible name."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_name = domain.resolve_variable(name_template)
  print(f"Clicking on {role} with name: {resolved_name}")
  page.get_by_role(role, name=resolved_name).click()


@step("the user double clicks on role {string} with name {string}")
@step(parsers.parse('the user double clicks on role "{role}" with name "{name_template}"'))
def double_click_by_role(page: Page, ctx, role, name_template):
  """Double clicks on an element by role and accessible name."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_name = domain.resolve_variable(name_template)
  print(f"Double clicking on {role} with name: {resolved_name}")
  page.get_by_role(role, name=resolved_name).dblclick()


@step("the user hovers over role {string} with name {string}")
@step(parsers.parse('the user hovers over role "{role}" with name "{name_template}"'))
def hover_by_role(page: Page, ctx, role, name_template):
  """Hovers over an element by role and accessible name."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_name = domain.resolve_variable(name_template)
  print(f"Hovering over {role} with name: {resolved_name}")
  page.get_by_role(role, name=resolved_name).hover()


@step("the user types {string} into role {string} with name {string}")
@step(
  parsers.parse('the user types "{text_template}" into role "{role}" with name "{name_template}"')
)
def type_into_role(page: Page, ctx, text_template, role, name_template):
  """Types text into an element by role and accessible name."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_text = domain.resolve_variable(text_template)
  resolved_name = domain.resolve_variable(name_template)
  print(f"Typing '{resolved_text}' into {role} with name: {resolved_name}")
  page.get_by_role(role, name=resolved_name).fill(resolved_text)


@step("the user types {string} into role {string} with name {string} slowly")
@step(
  parsers.parse(
    'the user types "{text_template}" into role "{role}" with name "{name_template}" slowly'
  )
)
def type_into_role_slowly(page: Page, ctx, text_template, role, name_template):
  """Types text slowly into an element by role and accessible name."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_text = domain.resolve_variable(text_template)
  resolved_name = domain.resolve_variable(name_template)
  print(f"Typing '{resolved_text}' slowly into {role} with name: {resolved_name}")
  page.get_by_role(role, name=resolved_name).type(resolved_text, delay=100)


@step("the user fills role {string} with name {string} with {string}")
@step(
  parsers.parse('the user fills role "{role}" with name "{name_template}" with "{text_template}"')
)
def fill_role(page: Page, ctx, role, name_template, text_template):
  """Fills an element by role and accessible name."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_text = domain.resolve_variable(text_template)
  resolved_name = domain.resolve_variable(name_template)
  print(f"Filling {role} '{resolved_name}' with: {resolved_text}")
  page.get_by_role(role, name=resolved_name).fill(resolved_text)


@step("the user clears role {string} with name {string}")
@step(parsers.parse('the user clears role "{role}" with name "{name_template}"'))
def clear_role(page: Page, ctx, role, name_template):
  """Clears an input element by role and accessible name."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_name = domain.resolve_variable(name_template)
  print(f"Clearing {role} with name: {resolved_name}")
  page.get_by_role(role, name=resolved_name).clear()


@step("the user presses {string} on role {string} with name {string}")
@step(parsers.parse('the user presses "{key}" on role "{role}" with name "{name_template}"'))
def press_key_on_role(page: Page, ctx, key, role, name_template):
  """Presses a key on an element by role and accessible name."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_name = domain.resolve_variable(name_template)
  print(f"Pressing '{key}' on {role} with name: {resolved_name}")
  page.get_by_role(role, name=resolved_name).press(key)


@step("the user checks role {string} with name {string}")
@step(parsers.parse('the user checks role "{role}" with name "{name_template}"'))
def check_role(page: Page, ctx, role, name_template):
  """Checks a checkbox/radio by role and accessible name."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_name = domain.resolve_variable(name_template)
  print(f"Checking {role} with name: {resolved_name}")
  page.get_by_role(role, name=resolved_name).check()


@step("the user unchecks role {string} with name {string}")
@step(parsers.parse('the user unchecks role "{role}" with name "{name_template}"'))
def uncheck_role(page: Page, ctx, role, name_template):
  """Unchecks a checkbox by role and accessible name."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_name = domain.resolve_variable(name_template)
  print(f"Unchecking {role} with name: {resolved_name}")
  page.get_by_role(role, name=resolved_name).uncheck()


@step("the user focuses on role {string} with name {string}")
@step(parsers.parse('the user focuses on role "{role}" with name "{name_template}"'))
def focus_role(page: Page, ctx, role, name_template):
  """Focuses on an element by role and accessible name."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_name = domain.resolve_variable(name_template)
  print(f"Focusing on {role} with name: {resolved_name}")
  page.get_by_role(role, name=resolved_name).focus()


@step("the user scrolls to role {string} with name {string}")
@step(parsers.parse('the user scrolls to role "{role}" with name "{name_template}"'))
def scroll_to_role(page: Page, ctx, role, name_template):
  """Scrolls to an element by role and accessible name."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_name = domain.resolve_variable(name_template)
  print(f"Scrolling to {role} with name: {resolved_name}")
  page.get_by_role(role, name=resolved_name).scroll_into_view_if_needed()


@step("the user waits for role {string} with name {string} to be visible")
@step(parsers.parse('the user waits for role "{role}" with name "{name_template}" to be visible'))
def wait_for_role_visible(page: Page, ctx, role, name_template):
  """Waits for an element by role to be visible."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_name = domain.resolve_variable(name_template)
  print(f"Waiting for {role} with name '{resolved_name}' to be visible")
  page.get_by_role(role, name=resolved_name).wait_for(state="visible")


@step("the user waits for role {string} with name {string} to be hidden")
@step(parsers.parse('the user waits for role "{role}" with name "{name_template}" to be hidden'))
def wait_for_role_hidden(page: Page, ctx, role, name_template):
  """Waits for an element by role to be hidden."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_name = domain.resolve_variable(name_template)
  print(f"Waiting for {role} with name '{resolved_name}' to be hidden")
  page.get_by_role(role, name=resolved_name).wait_for(state="hidden")


@step("the role {string} with name {string} should be visible")
@step(parsers.parse('the role "{role}" with name "{name_template}" should be visible'))
def assert_role_visible(page: Page, ctx, role, name_template):
  """Asserts that an element by role is visible."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_name = domain.resolve_variable(name_template)
  print(f"Asserting {role} '{resolved_name}' is visible")
  v(page.get_by_role(role, name=resolved_name)).locator().to_be_visible()


@step("the role {string} with name {string} should be hidden")
@step(parsers.parse('the role "{role}" with name "{name_template}" should be hidden'))
def assert_role_hidden(page: Page, ctx, role, name_template):
  """Asserts that an element by role is hidden."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_name = domain.resolve_variable(name_template)
  print(f"Asserting {role} '{resolved_name}' is hidden")
  v(page.get_by_role(role, name=resolved_name)).locator().to_be_hidden()


@step("the role {string} with name {string} should contain text {string}")
@step(
  parsers.parse(
    'the role "{role}" with name "{name_template}" should contain text "{text_template}"'
  )
)
def assert_role_contains_text(page: Page, ctx, role, name_template, text_template):
  """Asserts that an element by role contains specific text."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_name = domain.resolve_variable(name_template)
  resolved_text = domain.resolve_variable(text_template)
  print(f"Asserting {role} '{resolved_name}' contains text: {resolved_text}")
  v(page.get_by_role(role, name=resolved_name)).locator().to_contain_text(resolved_text)


@step("the role {string} with name {string} should have text {string}")
@step(
  parsers.parse('the role "{role}" with name "{name_template}" should have text "{text_template}"')
)
def assert_role_has_text(page: Page, ctx, role, name_template, text_template):
  """Asserts that an element by role has exact text."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_name = domain.resolve_variable(name_template)
  resolved_text = domain.resolve_variable(text_template)
  print(f"Asserting {role} '{resolved_name}' has text: {resolved_text}")
  v(page.get_by_role(role, name=resolved_name)).locator().to_have_text(resolved_text)


@step("the role {string} with name {string} should have value {string}")
@step(
  parsers.parse(
    'the role "{role}" with name "{name_template}" should have value "{value_template}"'
  )
)
def assert_role_has_value(page: Page, ctx, role, name_template, value_template):
  """Asserts that an input element by role has a specific value."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_name = domain.resolve_variable(name_template)
  resolved_value = domain.resolve_variable(value_template)
  print(f"Asserting {role} '{resolved_name}' has value: {resolved_value}")
  v(page.get_by_role(role, name=resolved_name)).locator().to_have_value(resolved_value)


@step("the role {string} with name {string} should be enabled")
@step(parsers.parse('the role "{role}" with name "{name_template}" should be enabled'))
def assert_role_enabled(page: Page, ctx, role, name_template):
  """Asserts that an element by role is enabled."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_name = domain.resolve_variable(name_template)
  print(f"Asserting {role} '{resolved_name}' is enabled")
  v(page.get_by_role(role, name=resolved_name)).locator().to_be_enabled()


@step("the role {string} with name {string} should be disabled")
@step(parsers.parse('the role "{role}" with name "{name_template}" should be disabled'))
def assert_role_disabled(page: Page, ctx, role, name_template):
  """Asserts that an element by role is disabled."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_name = domain.resolve_variable(name_template)
  print(f"Asserting {role} '{resolved_name}' is disabled")
  v(page.get_by_role(role, name=resolved_name)).locator().to_be_disabled()


@step("the role {string} with name {string} should be checked")
@step(parsers.parse('the role "{role}" with name "{name_template}" should be checked'))
def assert_role_checked(page: Page, ctx, role, name_template):
  """Asserts that a checkbox/radio by role is checked."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_name = domain.resolve_variable(name_template)
  print(f"Asserting {role} '{resolved_name}' is checked")
  v(page.get_by_role(role, name=resolved_name)).locator().to_be_checked()


@step("the role {string} with name {string} should not be checked")
@step(parsers.parse('the role "{role}" with name "{name_template}" should not be checked'))
def assert_role_not_checked(page: Page, ctx, role, name_template):
  """Asserts that a checkbox/radio by role is not checked."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_name = domain.resolve_variable(name_template)
  print(f"Asserting {role} '{resolved_name}' is not checked")
  v(page.get_by_role(role, name=resolved_name)).locator().not_to_be_checked()


@step("I store text from role {string} with name {string} as {string}")
@step(
  parsers.parse('I store text from role "{role}" with name "{name_template}" as "{variable_name}"')
)
def store_text_from_role(page: Page, ctx, role, name_template, variable_name):
  """Stores text from an element by role into a variable."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_name = domain.resolve_variable(name_template)
  text_content = page.get_by_role(role, name=resolved_name).text_content()
  ctx["global_vars"][variable_name] = text_content
  print(f"Stored text from {role} '{resolved_name}' as '{variable_name}': {text_content}")


@step("I store value from role {string} with name {string} as {string}")
@step(
  parsers.parse('I store value from role "{role}" with name "{name_template}" as "{variable_name}"')
)
def store_value_from_role(page: Page, ctx, role, name_template, variable_name):
  """Stores the value from an input element by role into a variable."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_name = domain.resolve_variable(name_template)
  input_value = page.get_by_role(role, name=resolved_name).input_value()
  ctx["global_vars"][variable_name] = input_value
  print(f"Stored value from {role} '{resolved_name}' as '{variable_name}': {input_value}")


# ==================== get_by_label Steps ====================


@step("the user clicks on label {string}")
@step(parsers.parse('the user clicks on label "{label_template}"'))
def click_by_label(page: Page, ctx, label_template):
  """Clicks on an element by label text."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_label = domain.resolve_variable(label_template)
  print(f"Clicking on element with label: {resolved_label}")
  page.get_by_label(resolved_label).click()


@step("the user double clicks on label {string}")
@step(parsers.parse('the user double clicks on label "{label_template}"'))
def double_click_by_label(page: Page, ctx, label_template):
  """Double clicks on an element by label text."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_label = domain.resolve_variable(label_template)
  print(f"Double clicking on element with label: {resolved_label}")
  page.get_by_label(resolved_label).dblclick()


@step("the user hovers over label {string}")
@step(parsers.parse('the user hovers over label "{label_template}"'))
def hover_by_label(page: Page, ctx, label_template):
  """Hovers over an element by label text."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_label = domain.resolve_variable(label_template)
  print(f"Hovering over element with label: {resolved_label}")
  page.get_by_label(resolved_label).hover()


@step("the user types {string} into label {string}")
@step(parsers.parse('the user types "{text_template}" into label "{label_template}"'))
def type_into_label(page: Page, ctx, text_template, label_template):
  """Types text into an element by label text."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_text = domain.resolve_variable(text_template)
  resolved_label = domain.resolve_variable(label_template)
  print(f"Typing '{resolved_text}' into element with label: {resolved_label}")
  page.get_by_label(resolved_label).fill(resolved_text)


@step("the user types {string} into label {string} slowly")
@step(parsers.parse('the user types "{text_template}" into label "{label_template}" slowly'))
def type_into_label_slowly(page: Page, ctx, text_template, label_template):
  """Types text slowly into an element by label text."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_text = domain.resolve_variable(text_template)
  resolved_label = domain.resolve_variable(label_template)
  print(f"Typing '{resolved_text}' slowly into element with label: {resolved_label}")
  page.get_by_label(resolved_label).type(resolved_text, delay=100)


@step("the user fills label {string} with {string}")
@step(parsers.parse('the user fills label "{label_template}" with "{text_template}"'))
def fill_label(page: Page, ctx, label_template, text_template):
  """Fills an element by label text."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_text = domain.resolve_variable(text_template)
  resolved_label = domain.resolve_variable(label_template)
  print(f"Filling element with label '{resolved_label}' with: {resolved_text}")
  page.get_by_label(resolved_label).fill(resolved_text)


@step("the user clears label {string}")
@step(parsers.parse('the user clears label "{label_template}"'))
def clear_label(page: Page, ctx, label_template):
  """Clears an input element by label text."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_label = domain.resolve_variable(label_template)
  print(f"Clearing element with label: {resolved_label}")
  page.get_by_label(resolved_label).clear()


@step("the user presses {string} on label {string}")
@step(parsers.parse('the user presses "{key}" on label "{label_template}"'))
def press_key_on_label(page: Page, ctx, key, label_template):
  """Presses a key on an element by label text."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_label = domain.resolve_variable(label_template)
  print(f"Pressing '{key}' on element with label: {resolved_label}")
  page.get_by_label(resolved_label).press(key)


@step("the user checks label {string}")
@step(parsers.parse('the user checks label "{label_template}"'))
def check_label(page: Page, ctx, label_template):
  """Checks a checkbox/radio by label text."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_label = domain.resolve_variable(label_template)
  print(f"Checking element with label: {resolved_label}")
  page.get_by_label(resolved_label).check()


@step("the user unchecks label {string}")
@step(parsers.parse('the user unchecks label "{label_template}"'))
def uncheck_label(page: Page, ctx, label_template):
  """Unchecks a checkbox by label text."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_label = domain.resolve_variable(label_template)
  print(f"Unchecking element with label: {resolved_label}")
  page.get_by_label(resolved_label).uncheck()


@step("the user focuses on label {string}")
@step(parsers.parse('the user focuses on label "{label_template}"'))
def focus_label(page: Page, ctx, label_template):
  """Focuses on an element by label text."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_label = domain.resolve_variable(label_template)
  print(f"Focusing on element with label: {resolved_label}")
  page.get_by_label(resolved_label).focus()


@step("the user scrolls to label {string}")
@step(parsers.parse('the user scrolls to label "{label_template}"'))
def scroll_to_label(page: Page, ctx, label_template):
  """Scrolls to an element by label text."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_label = domain.resolve_variable(label_template)
  print(f"Scrolling to element with label: {resolved_label}")
  page.get_by_label(resolved_label).scroll_into_view_if_needed()


@step("the user waits for label {string} to be visible")
@step(parsers.parse('the user waits for label "{label_template}" to be visible'))
def wait_for_label_visible(page: Page, ctx, label_template):
  """Waits for an element by label to be visible."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_label = domain.resolve_variable(label_template)
  print(f"Waiting for element with label '{resolved_label}' to be visible")
  page.get_by_label(resolved_label).wait_for(state="visible")


@step("the user waits for label {string} to be hidden")
@step(parsers.parse('the user waits for label "{label_template}" to be hidden'))
def wait_for_label_hidden(page: Page, ctx, label_template):
  """Waits for an element by label to be hidden."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_label = domain.resolve_variable(label_template)
  print(f"Waiting for element with label '{resolved_label}' to be hidden")
  page.get_by_label(resolved_label).wait_for(state="hidden")


@step("the label {string} should be visible")
@step(parsers.parse('the label "{label_template}" should be visible'))
def assert_label_visible(page: Page, ctx, label_template):
  """Asserts that an element by label is visible."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_label = domain.resolve_variable(label_template)
  print(f"Asserting element with label '{resolved_label}' is visible")
  v(page.get_by_label(resolved_label)).locator().to_be_visible()


@step("the label {string} should be hidden")
@step(parsers.parse('the label "{label_template}" should be hidden'))
def assert_label_hidden(page: Page, ctx, label_template):
  """Asserts that an element by label is hidden."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_label = domain.resolve_variable(label_template)
  print(f"Asserting element with label '{resolved_label}' is hidden")
  v(page.get_by_label(resolved_label)).locator().to_be_hidden()


@step("the label {string} should contain text {string}")
@step(parsers.parse('the label "{label_template}" should contain text "{text_template}"'))
def assert_label_contains_text(page: Page, ctx, label_template, text_template):
  """Asserts that an element by label contains specific text."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_label = domain.resolve_variable(label_template)
  resolved_text = domain.resolve_variable(text_template)
  print(f"Asserting element with label '{resolved_label}' contains text: {resolved_text}")
  v(page.get_by_label(resolved_label)).locator().to_contain_text(resolved_text)


@step("the label {string} should have text {string}")
@step(parsers.parse('the label "{label_template}" should have text "{text_template}"'))
def assert_label_has_text(page: Page, ctx, label_template, text_template):
  """Asserts that an element by label has exact text."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_label = domain.resolve_variable(label_template)
  resolved_text = domain.resolve_variable(text_template)
  print(f"Asserting element with label '{resolved_label}' has text: {resolved_text}")
  v(page.get_by_label(resolved_label)).locator().to_have_text(resolved_text)


@step("the label {string} should have value {string}")
@step(parsers.parse('the label "{label_template}" should have value "{value_template}"'))
def assert_label_has_value(page: Page, ctx, label_template, value_template):
  """Asserts that an input element by label has a specific value."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_label = domain.resolve_variable(label_template)
  resolved_value = domain.resolve_variable(value_template)
  print(f"Asserting element with label '{resolved_label}' has value: {resolved_value}")
  v(page.get_by_label(resolved_label)).locator().to_have_value(resolved_value)


@step("the label {string} should be enabled")
@step(parsers.parse('the label "{label_template}" should be enabled'))
def assert_label_enabled(page: Page, ctx, label_template):
  """Asserts that an element by label is enabled."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_label = domain.resolve_variable(label_template)
  print(f"Asserting element with label '{resolved_label}' is enabled")
  v(page.get_by_label(resolved_label)).locator().to_be_enabled()


@step("the label {string} should be disabled")
@step(parsers.parse('the label "{label_template}" should be disabled'))
def assert_label_disabled(page: Page, ctx, label_template):
  """Asserts that an element by label is disabled."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_label = domain.resolve_variable(label_template)
  print(f"Asserting element with label '{resolved_label}' is disabled")
  v(page.get_by_label(resolved_label)).locator().to_be_disabled()


@step("the label {string} should be checked")
@step(parsers.parse('the label "{label_template}" should be checked'))
def assert_label_checked(page: Page, ctx, label_template):
  """Asserts that a checkbox/radio by label is checked."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_label = domain.resolve_variable(label_template)
  print(f"Asserting element with label '{resolved_label}' is checked")
  v(page.get_by_label(resolved_label)).locator().to_be_checked()


@step("the label {string} should not be checked")
@step(parsers.parse('the label "{label_template}" should not be checked'))
def assert_label_not_checked(page: Page, ctx, label_template):
  """Asserts that a checkbox/radio by label is not checked."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_label = domain.resolve_variable(label_template)
  print(f"Asserting element with label '{resolved_label}' is not checked")
  v(page.get_by_label(resolved_label)).locator().not_to_be_checked()


@step("I store text from label {string} as {string}")
@step(parsers.parse('I store text from label "{label_template}" as "{variable_name}"'))
def store_text_from_label(page: Page, ctx, label_template, variable_name):
  """Stores text from an element by label into a variable."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_label = domain.resolve_variable(label_template)
  text_content = page.get_by_label(resolved_label).text_content()
  ctx["global_vars"][variable_name] = text_content
  print(
    f"Stored text from element with label '{resolved_label}' as '{variable_name}': {text_content}"
  )


@step("I store value from label {string} as {string}")
@step(parsers.parse('I store value from label "{label_template}" as "{variable_name}"'))
def store_value_from_label(page: Page, ctx, label_template, variable_name):
  """Stores the value from an input element by label into a variable."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_label = domain.resolve_variable(label_template)
  input_value = page.get_by_label(resolved_label).input_value()
  ctx["global_vars"][variable_name] = input_value
  print(
    f"Stored value from element with label '{resolved_label}' as '{variable_name}': {input_value}"
  )


@step("the user accepts the dialog")
def accept_dialog(page: Page):
  """Sets up handler to accept the next dialog."""
  print("Setting up dialog accept handler")
  page.once("dialog", lambda dialog: dialog.accept())


@step("the user dismisses the dialog")
def dismiss_dialog(page: Page):
  """Sets up handler to dismiss the next dialog."""
  print("Setting up dialog dismiss handler")
  page.once("dialog", lambda dialog: dialog.dismiss())


@step("the element {string} should have attribute {string} with value {string}")
@step(
  parsers.parse(
    'the element "{selector_template}" should have attribute "{attribute}" with value "{value_template}"'
  )
)
def assert_element_has_attribute(page: Page, ctx, selector_template, attribute, value_template):
  """Asserts that an element has a specific attribute value."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  resolved_value = domain.resolve_variable(value_template)
  print(f"Asserting '{resolved_selector}' has attribute '{attribute}' with value: {resolved_value}")
  v(page.locator(resolved_selector)).locator().to_have_attribute(attribute, resolved_value)


@step("the element {string} should have class {string}")
@step(parsers.parse('the element "{selector_template}" should have class "{class_name}"'))
def assert_element_has_class(page: Page, ctx, selector_template, class_name):
  """Asserts that an element has a specific CSS class."""
  from src.domains.common.common_api_domain import CommonApiDomain

  domain = CommonApiDomain(ctx, {})

  resolved_selector = domain.resolve_variable(selector_template)
  resolved_class = domain.resolve_variable(class_name)
  print(f"Asserting '{resolved_selector}' has class: {resolved_class}")
  v(page.locator(resolved_selector)).locator().to_have_class(
    lambda classes: resolved_class in classes
  )
