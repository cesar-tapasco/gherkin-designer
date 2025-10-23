// Gherkin step definitions for autocomplete
// Based on common_api_steps.py

export const gherkinSteps = [
  // Basic HTTP requests
  {
    caption: 'I send "METHOD" req to "URL"',
    snippet: 'I send "${1:GET}" req to "${2:/api/endpoint}"',
    meta: 'HTTP Request',
    docHTML: 'Send an HTTP request with authentication. Methods: GET, POST, PUT, DELETE, PATCH'
  },
  {
    caption: 'I send "METHOD" req without user id to "URL"',
    snippet: 'I send "${1:GET}" req without user id to "${2:/api/endpoint}"',
    meta: 'HTTP Request',
    docHTML: 'Send an HTTP request without user ID in query params'
  },
  // Response validation
  {
    caption: 'the res code should be NUMBER',
    snippet: 'the res code should be ${1:200}',
    meta: 'Validation',
    docHTML: 'Validate response status code is exactly the specified number'
  },
  {
    caption: 'the res code should be ok',
    snippet: 'the res code should be ok',
    meta: 'Validation',
    docHTML: 'Validate response status code is 2xx (success)'
  },
  {
    caption: 'the res code should be "CODE"',
    snippet: 'the res code should be "${1:2xx}"',
    meta: 'Validation',
    docHTML: 'Validate response status code matches pattern (e.g., "2xx", "4xx")'
  },

  // JSON path validation
  {
    caption: 'the res jq "PATH" should be "VALUE"',
    snippet: 'the res jq "${1:$.id}" should be "${2:{{variable}}}"',
    meta: 'JSON Validation',
    docHTML: 'Validate JSON response using jq filter. Example: $.data[0].name'
  },
  {
    caption: 'I store the value from JSON path "PATH" of the last response as "VAR"',
    snippet: 'I store the value from JSON path "${1:$.id}" of the last response as "${2:myVar}"',
    meta: 'Variable',
    docHTML: 'Extract value from JSON response and store in variable'
  },

  // Request body
  {
    caption: 'I set the request body to:',
    snippet: 'I set the request body to:\n  """\n  ${1:{\n    "key": "value"\n  }}\n  """',
    meta: 'Request Body',
    docHTML: 'Set request body with inline JSON (docstring)'
  },
  {
    caption: 'I set the request body from "FILE"',
    snippet: 'I set the request body from "${1:payloads/data.json}"',
    meta: 'Request Body',
    docHTML: 'Load request body from JSON file'
  },

  // Variables
  {
    caption: 'I set var "NAME" as "VALUE"',
    snippet: 'I set var "${1:varName}" as "${2:value}"',
    meta: 'Variable',
    docHTML: 'Set a variable with a literal value or template'
  },
  {
    caption: 'I set var "NAME" as responseBody',
    snippet: 'I set var "${1:varName}" as responseBody',
    meta: 'Variable',
    docHTML: 'Store entire response body in variable'
  },
  {
    caption: 'I set var "NAME" as responseCode',
    snippet: 'I set var "${1:varName}" as responseCode',
    meta: 'Variable',
    docHTML: 'Store response status code in variable'
  },
  {
    caption: 'I set var "NAME" as Time',
    snippet: 'I set var "${1:varName}" as Time',
    meta: 'Variable',
    docHTML: 'Store current timestamp in variable'
  },
  {
    caption: 'I set var "NAME" as userId from session',
    snippet: 'I set var "${1:varName}" as userId from session',
    meta: 'Variable',
    docHTML: 'Get user ID from current session'
  },
  {
    caption: 'I set var "NAME" as envvar "ENV"',
    snippet: 'I set var "${1:varName}" as envvar "${2:ENV_VAR_NAME}"',
    meta: 'Variable',
    docHTML: 'Set variable from environment variable'
  },
  {
    caption: 'I set var list "NAME" as "VALUE"',
    snippet: 'I set var list "${1:listVar}" as "${2:[1,2,3]}"',
    meta: 'Variable',
    docHTML: 'Set a list variable from JSON array'
  },

  // Query parameters
  {
    caption: 'I set query params',
    snippet: 'I set query params\n  | name | value |\n  | ${1:param} | ${2:value} |',
    meta: 'Query Params',
    docHTML: 'Set query parameters using data table'
  },
  {
    caption: 'I set query params from "FILE"',
    snippet: 'I set query params from "${1:payloads/params.json}"',
    meta: 'Query Params',
    docHTML: 'Load query parameters from JSON file'
  },
  {
    caption: 'I set query param "NAME" from global var "VAR"',
    snippet: 'I set query param "${1:paramName}" from global var "${2:varName}"',
    meta: 'Query Params',
    docHTML: 'Set single query param from a variable'
  },
  {
    caption: 'I clear all params',
    snippet: 'I clear all params',
    meta: 'Query Params',
    docHTML: 'Clear all query parameters'
  },

  // Headers
  {
    caption: 'I set headers',
    snippet: 'I set headers\n  | name | value |\n  | ${1:Content-Type} | ${2:application/json} |',
    meta: 'Headers',
    docHTML: 'Set HTTP headers using data table'
  },
  {
    caption: 'I clear all headers',
    snippet: 'I clear all headers',
    meta: 'Headers',
    docHTML: 'Clear all custom headers'
  },
  {
    caption: 'I clear all headers for external request',
    snippet: 'I clear all headers for external request',
    meta: 'Headers',
    docHTML: 'Clear headers for external/unauthenticated request'
  },
  {
    caption: 'I restore normal headers behavior',
    snippet: 'I restore normal headers behavior',
    meta: 'Headers',
    docHTML: 'Restore default header behavior after external request'
  },

  // Base URL
  {
    caption: 'the base URL is "URL"',
    snippet: 'the base URL is "${1:https://api.example.com}"',
    meta: 'Configuration',
    docHTML: 'Set the base URL for all requests'
  },

  // Wait/Sleep
  {
    caption: 'the user waits Ns',
    snippet: 'the user waits ${1:2}s',
    meta: 'Wait',
    docHTML: 'Wait for specified seconds'
  },
  {
    caption: 'sleep N',
    snippet: 'sleep ${1:1}',
    meta: 'Wait',
    docHTML: 'Sleep for N seconds'
  },

  // Polling
  {
    caption: 'the system waits "URL" until contains "VALUES"',
    snippet: 'the system waits "${1:/api/task/{{taskId}}}" until contains "${2:COMPLETED,FAILED}"',
    meta: 'Polling',
    docHTML: 'Poll endpoint until response contains one of the specified values'
  },
  {
    caption: 'the system waits without userId "URL" until contains "VALUES"',
    snippet: 'the system waits without userId "${1:/api/task/{{taskId}}}" until contains "${2:COMPLETED,FAILED}"',
    meta: 'Polling',
    docHTML: 'Poll endpoint without user ID until response contains specified values'
  },

  // Schema validation
  {
    caption: 'the response JSON should conform to the schema defined in "FILE"',
    snippet: 'the response JSON should conform to the schema defined in "${1:schemas/resource.json}"',
    meta: 'Schema Validation',
    docHTML: 'Validate response against JSON schema file'
  },
  {
    caption: 'the res JSON should match with schema:',
    snippet: 'the res JSON should match with schema:\n  ${1:{\n    "type": "object"\n  }}',
    meta: 'Schema Validation',
    docHTML: 'Validate response against inline JSON schema'
  },
  {
    caption: 'the response JSON should match:',
    snippet: 'the response JSON should match:\n  ${1:{\n    "key": "value"\n  }}',
    meta: 'JSON Validation',
    docHTML: 'Compare entire response with expected JSON'
  },

  // Custom logic
  {
    caption: 'I execute custom logic:',
    snippet: 'I execute custom logic:\n  """\n  ${1:# Python code here}\n  """',
    meta: 'Advanced',
    docHTML: 'Execute custom Python code (access api_context, api_domain)'
  },

  // File operations
  {
    caption: 'I set file named "FIELD" with content:',
    snippet: 'I set file named "${1:file}" with content:\n  ${2:content}',
    meta: 'File Upload',
    docHTML: 'Set file upload with inline content'
  },
  {
    caption: 'I set file named "FIELD" from path "PATH"',
    snippet: 'I set file named "${1:file}" from path "${2:path/to/file.csv}"',
    meta: 'File Upload',
    docHTML: 'Set file upload from file path'
  },
  {
    caption: 'I set binary file from path "PATH"',
    snippet: 'I set binary file from path "${1:path/to/file.bin}"',
    meta: 'File Upload',
    docHTML: 'Upload binary file'
  },
  {
    caption: 'I set multipart field "FIELD" to "VALUE"',
    snippet: 'I set multipart field "${1:fieldName}" to "${2:value}"',
    meta: 'File Upload',
    docHTML: 'Set multipart form field'
  },
  {
    caption: 'I attach file "PATH" to multipart field "FIELD"',
    snippet: 'I attach file "${1:path/to/file}" to multipart field "${2:fieldName}"',
    meta: 'File Upload',
    docHTML: 'Attach file to multipart form'
  },

  // Response header validation
  {
    caption: 'the res header "NAME" should be "VALUE"',
    snippet: 'the res header "${1:Content-Type}" should be "${2:application/json}"',
    meta: 'Header Validation',
    docHTML: 'Validate response header value'
  },

  // Element validation
  {
    caption: 'the "ELEMENT" should contain the value "VALUE"',
    snippet: 'the "${1:$.data}" should contain the value "${2:expected}"',
    meta: 'Validation',
    docHTML: 'Check if element contains specified value'
  },
  {
    caption: 'the "ELEMENT" should not contain the value "VALUE"',
    snippet: 'the "${1:$.data}" should not contain the value "${2:unwanted}"',
    meta: 'Validation',
    docHTML: 'Check if element does not contain specified value'
  },
  {
    caption: 'the response should contain the value "VALUE"',
    snippet: 'the response should contain the value "${1:expected}"',
    meta: 'Validation',
    docHTML: 'Check if response body contains specified value'
  },

  // Performance validation
  {
    caption: 'the "DURATION" duration should not exceed Nx of "INITIAL"',
    snippet: 'the "${1:final_time}" duration should not exceed ${2:2.0}x of "${3:initial_time}"',
    meta: 'Performance',
    docHTML: 'Validate execution time does not exceed threshold'
  },

  // Variable matching
  {
    caption: 'the "VAR1" should match with "VAR2"',
    snippet: 'the "${1:actual}" should match with "${2:expected}"',
    meta: 'Validation',
    docHTML: 'Deep compare two variables'
  },
  {
    caption: 'the order "VAR1" should match with "VAR2"',
    snippet: 'the order "${1:actualList}" should match with "${2:expectedList}"',
    meta: 'Validation',
    docHTML: 'Compare two lists preserving order'
  },

  // Schema validation for elements
  {
    caption: 'the "ELEMENT" should have the schema "SCHEMA"',
    snippet: 'the "${1:$.data}" should have the schema "${2:schemaName}"',
    meta: 'Schema Validation',
    docHTML: 'Validate element against named schema'
  },

  // List operations
  {
    caption: 'I set list "NAME" from string "VALUE"',
    snippet: 'I set list "${1:listName}" from string "${2:item1,item2,item3}"',
    meta: 'Variable',
    docHTML: 'Create list from comma-separated string'
  },
  {
    caption: 'all elements of "LIST1" should be in "LIST2"',
    snippet: 'all elements of "${1:sublist}" should be in "${2:mainlist}"',
    meta: 'Validation',
    docHTML: 'Validate all elements of list1 exist in list2'
  },

  // Data table variables
  {
    caption: 'I define vars',
    snippet: 'I define vars\n  | name | value |\n  | ${1:varName} | ${2:varValue} |',
    meta: 'Variable',
    docHTML: 'Define multiple variables using data table'
  },

  // Debug
  {
    caption: 'breakpoint',
    snippet: 'breakpoint',
    meta: 'Debug',
    docHTML: 'Set breakpoint for debugging (drops into pdb)'
  },
  {
    caption: 'I like to debug',
    snippet: 'I like to debug',
    meta: 'Debug',
    docHTML: 'Alternative breakpoint syntax'
  },

  // Variable templates
  {
    caption: '{{variableName}}',
    snippet: '{{${1:variableName}}}',
    meta: 'Template',
    docHTML: 'Reference a variable using template syntax'
  },

  // JQ expressions
  {
    caption: '$.jsonPath',
    snippet: '$.${1:field}',
    meta: 'JQ Filter',
    docHTML: 'JQ filter to access JSON field'
  },
  {
    caption: '$._embedded',
    snippet: '$._embedded',
    meta: 'JQ Filter',
    docHTML: 'Access _embedded field (common in HAL responses)'
  },
  {
    caption: '$.content[0]',
    snippet: '$.content[${1:0}]',
    meta: 'JQ Filter',
    docHTML: 'Access array element in content field'
  },

  // ==================== UI STEPS (Playwright) ====================

  // Navigation
  {
    caption: 'the user navigates to "URL"',
    snippet: 'the user navigates to "${1:/page}"',
    meta: 'UI Navigation',
    docHTML: 'Navigate to the specified URL (supports variable templates)'
  },
  {
    caption: 'the user reloads the page',
    snippet: 'the user reloads the page',
    meta: 'UI Navigation',
    docHTML: 'Reload the current page'
  },
  {
    caption: 'the user goes back',
    snippet: 'the user goes back',
    meta: 'UI Navigation',
    docHTML: 'Navigate back in browser history'
  },
  {
    caption: 'the user goes forward',
    snippet: 'the user goes forward',
    meta: 'UI Navigation',
    docHTML: 'Navigate forward in browser history'
  },

  // Click actions (selector-based)
  {
    caption: 'the user clicks on "SELECTOR"',
    snippet: 'the user clicks on "${1:#element}"',
    meta: 'UI Click',
    docHTML: 'Click on an element by CSS selector'
  },
  {
    caption: 'the user clicks on "SELECTOR" with timeout Ns',
    snippet: 'the user clicks on "${1:#element}" with timeout ${2:5}s',
    meta: 'UI Click',
    docHTML: 'Click on an element with custom timeout'
  },
  {
    caption: 'the user double clicks on "SELECTOR"',
    snippet: 'the user double clicks on "${1:#element}"',
    meta: 'UI Click',
    docHTML: 'Double click on an element'
  },
  {
    caption: 'the user right clicks on "SELECTOR"',
    snippet: 'the user right clicks on "${1:#element}"',
    meta: 'UI Click',
    docHTML: 'Right click on an element'
  },
  {
    caption: 'the user clicks on text "TEXT"',
    snippet: 'the user clicks on text "${1:Button Text}"',
    meta: 'UI Click',
    docHTML: 'Click on element containing specific text'
  },

  // Click actions (role-based) - Accessibility
  {
    caption: 'the user clicks on role "ROLE" with name "NAME"',
    snippet: 'the user clicks on role "${1:button}" with name "${2:Submit}"',
    meta: 'UI Click (Role)',
    docHTML: 'Click element by ARIA role and name. Roles: button, textbox, checkbox, link, heading, etc.'
  },
  {
    caption: 'the user double clicks on role "ROLE" with name "NAME"',
    snippet: 'the user double clicks on role "${1:button}" with name "${2:Submit}"',
    meta: 'UI Click (Role)',
    docHTML: 'Double click element by ARIA role and name'
  },

  // Hover actions
  {
    caption: 'the user hovers over "SELECTOR"',
    snippet: 'the user hovers over "${1:#element}"',
    meta: 'UI Hover',
    docHTML: 'Hover over an element by selector'
  },
  {
    caption: 'the user hovers over role "ROLE" with name "NAME"',
    snippet: 'the user hovers over role "${1:button}" with name "${2:Submit}"',
    meta: 'UI Hover (Role)',
    docHTML: 'Hover over element by ARIA role and name'
  },

  // Input actions (selector-based)
  {
    caption: 'the user types "TEXT" into "SELECTOR"',
    snippet: 'the user types "${1:text}" into "${2:#input}"',
    meta: 'UI Input',
    docHTML: 'Type text into an input element by selector'
  },
  {
    caption: 'the user types "TEXT" into "SELECTOR" slowly',
    snippet: 'the user types "${1:text}" into "${2:#input}" slowly',
    meta: 'UI Input',
    docHTML: 'Type text slowly (100ms delay between characters)'
  },
  {
    caption: 'the user fills "SELECTOR" with "TEXT"',
    snippet: 'the user fills "${1:#input}" with "${2:value}"',
    meta: 'UI Input',
    docHTML: 'Fill input element (clears first, then types)'
  },
  {
    caption: 'the user clears "SELECTOR"',
    snippet: 'the user clears "${1:#input}"',
    meta: 'UI Input',
    docHTML: 'Clear an input element'
  },

  // Input actions (role-based)
  {
    caption: 'the user types "TEXT" into role "ROLE" with name "NAME"',
    snippet: 'the user types "${1:text}" into role "${2:textbox}" with name "${3:Name *}"',
    meta: 'UI Input (Role)',
    docHTML: 'Type text into input by ARIA role and name'
  },
  {
    caption: 'the user types "TEXT" into role "ROLE" with name "NAME" slowly',
    snippet: 'the user types "${1:text}" into role "${2:textbox}" with name "${3:Name *}" slowly',
    meta: 'UI Input (Role)',
    docHTML: 'Type text slowly into input by ARIA role and name'
  },
  {
    caption: 'the user fills role "ROLE" with name "NAME" with "TEXT"',
    snippet: 'the user fills role "${1:textbox}" with name "${2:Email}" with "${3:value}"',
    meta: 'UI Input (Role)',
    docHTML: 'Fill input element by ARIA role and name'
  },
  {
    caption: 'the user clears role "ROLE" with name "NAME"',
    snippet: 'the user clears role "${1:textbox}" with name "${2:Search}"',
    meta: 'UI Input (Role)',
    docHTML: 'Clear input element by ARIA role and name'
  },

  // Keyboard actions
  {
    caption: 'the user presses "KEY"',
    snippet: 'the user presses "${1:Enter}"',
    meta: 'UI Keyboard',
    docHTML: 'Press a keyboard key (Enter, Escape, Tab, etc.)'
  },
  {
    caption: 'the user presses "KEY" on "SELECTOR"',
    snippet: 'the user presses "${1:Enter}" on "${2:#input}"',
    meta: 'UI Keyboard',
    docHTML: 'Press a key on specific element'
  },
  {
    caption: 'the user presses "KEY" on role "ROLE" with name "NAME"',
    snippet: 'the user presses "${1:Enter}" on role "${2:textbox}" with name "${3:Search}"',
    meta: 'UI Keyboard (Role)',
    docHTML: 'Press a key on element by ARIA role and name'
  },

  // Select/Dropdown
  {
    caption: 'the user selects "OPTION" from "SELECTOR"',
    snippet: 'the user selects "${1:option1}" from "${2:#dropdown}"',
    meta: 'UI Select',
    docHTML: 'Select option from dropdown'
  },

  // Checkbox/Radio
  {
    caption: 'the user checks "SELECTOR"',
    snippet: 'the user checks "${1:#checkbox}"',
    meta: 'UI Checkbox',
    docHTML: 'Check a checkbox or radio button'
  },
  {
    caption: 'the user unchecks "SELECTOR"',
    snippet: 'the user unchecks "${1:#checkbox}"',
    meta: 'UI Checkbox',
    docHTML: 'Uncheck a checkbox'
  },
  {
    caption: 'the user checks role "ROLE" with name "NAME"',
    snippet: 'the user checks role "${1:checkbox}" with name "${2:I agree}"',
    meta: 'UI Checkbox (Role)',
    docHTML: 'Check checkbox by ARIA role and name'
  },
  {
    caption: 'the user unchecks role "ROLE" with name "NAME"',
    snippet: 'the user unchecks role "${1:checkbox}" with name "${2:I agree}"',
    meta: 'UI Checkbox (Role)',
    docHTML: 'Uncheck checkbox by ARIA role and name'
  },

  // File upload
  {
    caption: 'the user uploads file "PATH" to "SELECTOR"',
    snippet: 'the user uploads file "${1:test-data/file.csv}" to "${2:#file-input}"',
    meta: 'UI File Upload',
    docHTML: 'Upload file to file input (path relative to src/resources/)'
  },

  // Focus & Scroll
  {
    caption: 'the user focuses on "SELECTOR"',
    snippet: 'the user focuses on "${1:#element}"',
    meta: 'UI Focus',
    docHTML: 'Focus on an element'
  },
  {
    caption: 'the user focuses on role "ROLE" with name "NAME"',
    snippet: 'the user focuses on role "${1:textbox}" with name "${2:Search}"',
    meta: 'UI Focus (Role)',
    docHTML: 'Focus on element by ARIA role and name'
  },
  {
    caption: 'the user scrolls to "SELECTOR"',
    snippet: 'the user scrolls to "${1:#element}"',
    meta: 'UI Scroll',
    docHTML: 'Scroll to an element'
  },
  {
    caption: 'the user scrolls to role "ROLE" with name "NAME"',
    snippet: 'the user scrolls to role "${1:button}" with name "${2:Submit}"',
    meta: 'UI Scroll (Role)',
    docHTML: 'Scroll to element by ARIA role and name'
  },

  // Drag & Drop
  {
    caption: 'the user drags "SOURCE" to "TARGET"',
    snippet: 'the user drags "${1:#source}" to "${2:#target}"',
    meta: 'UI Drag & Drop',
    docHTML: 'Drag an element to another element'
  },

  // Wait actions (selector-based)
  {
    caption: 'the user waits for "SELECTOR" to be visible',
    snippet: 'the user waits for "${1:#element}" to be visible',
    meta: 'UI Wait',
    docHTML: 'Wait for element to become visible'
  },
  {
    caption: 'the user waits for "SELECTOR" to be hidden',
    snippet: 'the user waits for "${1:#element}" to be hidden',
    meta: 'UI Wait',
    docHTML: 'Wait for element to become hidden'
  },
  {
    caption: 'the user waits for "SELECTOR" to be enabled',
    snippet: 'the user waits for "${1:#button}" to be enabled',
    meta: 'UI Wait',
    docHTML: 'Wait for element to become enabled'
  },
  {
    caption: 'the user waits for selector "SELECTOR" with timeout Ns',
    snippet: 'the user waits for selector "${1:#element}" with timeout ${2:10}s',
    meta: 'UI Wait',
    docHTML: 'Wait for selector with custom timeout'
  },
  {
    caption: 'the user waits for page load',
    snippet: 'the user waits for page load',
    meta: 'UI Wait',
    docHTML: 'Wait for page to fully load'
  },
  {
    caption: 'the user waits for network idle',
    snippet: 'the user waits for network idle',
    meta: 'UI Wait',
    docHTML: 'Wait for network to be idle'
  },

  // Wait actions (role-based)
  {
    caption: 'the user waits for role "ROLE" with name "NAME" to be visible',
    snippet: 'the user waits for role "${1:button}" with name "${2:Submit}" to be visible',
    meta: 'UI Wait (Role)',
    docHTML: 'Wait for element by role to become visible'
  },
  {
    caption: 'the user waits for role "ROLE" with name "NAME" to be hidden',
    snippet: 'the user waits for role "${1:dialog}" with name "${2:Modal}" to be hidden',
    meta: 'UI Wait (Role)',
    docHTML: 'Wait for element by role to become hidden'
  },

  // Assertions - Visibility (selector-based)
  {
    caption: 'the element "SELECTOR" should be visible',
    snippet: 'the element "${1:#element}" should be visible',
    meta: 'UI Assert Visibility',
    docHTML: 'Assert element is visible'
  },
  {
    caption: 'the element "SELECTOR" should be hidden',
    snippet: 'the element "${1:#element}" should be hidden',
    meta: 'UI Assert Visibility',
    docHTML: 'Assert element is hidden'
  },

  // Assertions - Visibility (role-based)
  {
    caption: 'the role "ROLE" with name "NAME" should be visible',
    snippet: 'the role "${1:button}" with name "${2:Submit}" should be visible',
    meta: 'UI Assert Visibility (Role)',
    docHTML: 'Assert element by role is visible'
  },
  {
    caption: 'the role "ROLE" with name "NAME" should be hidden',
    snippet: 'the role "${1:alert}" with name "${2:Error}" should be hidden',
    meta: 'UI Assert Visibility (Role)',
    docHTML: 'Assert element by role is hidden'
  },

  // Assertions - Text content (selector-based)
  {
    caption: 'the element "SELECTOR" should contain text "TEXT"',
    snippet: 'the element "${1:#element}" should contain text "${2:Expected Text}"',
    meta: 'UI Assert Text',
    docHTML: 'Assert element contains specific text'
  },
  {
    caption: 'the element "SELECTOR" should have text "TEXT"',
    snippet: 'the element "${1:#element}" should have text "${2:Exact Text}"',
    meta: 'UI Assert Text',
    docHTML: 'Assert element has exact text'
  },

  // Assertions - Text content (role-based)
  {
    caption: 'the role "ROLE" with name "NAME" should contain text "TEXT"',
    snippet: 'the role "${1:heading}" with name "${2:Title}" should contain text "${3:Welcome}"',
    meta: 'UI Assert Text (Role)',
    docHTML: 'Assert element by role contains text'
  },
  {
    caption: 'the role "ROLE" with name "NAME" should have text "TEXT"',
    snippet: 'the role "${1:button}" with name "${2:Submit}" should have text "${3:Submit}"',
    meta: 'UI Assert Text (Role)',
    docHTML: 'Assert element by role has exact text'
  },

  // Assertions - Input values (selector-based)
  {
    caption: 'the element "SELECTOR" should have value "VALUE"',
    snippet: 'the element "${1:#input}" should have value "${2:expected}"',
    meta: 'UI Assert Value',
    docHTML: 'Assert input element has specific value'
  },

  // Assertions - Input values (role-based)
  {
    caption: 'the role "ROLE" with name "NAME" should have value "VALUE"',
    snippet: 'the role "${1:textbox}" with name "${2:Email}" should have value "${3:test@example.com}"',
    meta: 'UI Assert Value (Role)',
    docHTML: 'Assert input by role has specific value'
  },

  // Assertions - Enabled/Disabled (selector-based)
  {
    caption: 'the element "SELECTOR" should be enabled',
    snippet: 'the element "${1:#button}" should be enabled',
    meta: 'UI Assert State',
    docHTML: 'Assert element is enabled'
  },
  {
    caption: 'the element "SELECTOR" should be disabled',
    snippet: 'the element "${1:#button}" should be disabled',
    meta: 'UI Assert State',
    docHTML: 'Assert element is disabled'
  },

  // Assertions - Enabled/Disabled (role-based)
  {
    caption: 'the role "ROLE" with name "NAME" should be enabled',
    snippet: 'the role "${1:button}" with name "${2:Submit}" should be enabled',
    meta: 'UI Assert State (Role)',
    docHTML: 'Assert element by role is enabled'
  },
  {
    caption: 'the role "ROLE" with name "NAME" should be disabled',
    snippet: 'the role "${1:button}" with name "${2:Submit}" should be disabled',
    meta: 'UI Assert State (Role)',
    docHTML: 'Assert element by role is disabled'
  },

  // Assertions - Checked state (selector-based)
  {
    caption: 'the element "SELECTOR" should be checked',
    snippet: 'the element "${1:#checkbox}" should be checked',
    meta: 'UI Assert Checkbox',
    docHTML: 'Assert checkbox is checked'
  },
  {
    caption: 'the element "SELECTOR" should not be checked',
    snippet: 'the element "${1:#checkbox}" should not be checked',
    meta: 'UI Assert Checkbox',
    docHTML: 'Assert checkbox is not checked'
  },

  // Assertions - Checked state (role-based)
  {
    caption: 'the role "ROLE" with name "NAME" should be checked',
    snippet: 'the role "${1:checkbox}" with name "${2:I agree}" should be checked',
    meta: 'UI Assert Checkbox (Role)',
    docHTML: 'Assert checkbox by role is checked'
  },
  {
    caption: 'the role "ROLE" with name "NAME" should not be checked',
    snippet: 'the role "${1:checkbox}" with name "${2:I agree}" should not be checked',
    meta: 'UI Assert Checkbox (Role)',
    docHTML: 'Assert checkbox by role is not checked'
  },

  // Assertions - Count
  {
    caption: 'the element "SELECTOR" should have count N',
    snippet: 'the element "${1:.item}" should have count ${2:5}',
    meta: 'UI Assert Count',
    docHTML: 'Assert number of matching elements'
  },

  // Assertions - Attributes
  {
    caption: 'the element "SELECTOR" should have attribute "ATTR" with value "VALUE"',
    snippet: 'the element "${1:#element}" should have attribute "${2:data-id}" with value "${3:123}"',
    meta: 'UI Assert Attribute',
    docHTML: 'Assert element has specific attribute value'
  },
  {
    caption: 'the element "SELECTOR" should have class "CLASS"',
    snippet: 'the element "${1:#element}" should have class "${2:active}"',
    meta: 'UI Assert Class',
    docHTML: 'Assert element has specific CSS class'
  },

  // Assertions - Page
  {
    caption: 'the page title should be "TITLE"',
    snippet: 'the page title should be "${1:Expected Title}"',
    meta: 'UI Assert Page',
    docHTML: 'Assert page title'
  },
  {
    caption: 'the page URL should contain "TEXT"',
    snippet: 'the page URL should contain "${1:/dashboard}"',
    meta: 'UI Assert Page',
    docHTML: 'Assert URL contains specific text'
  },

  // Variable storage from UI (selector-based)
  {
    caption: 'I store text from "SELECTOR" as "VAR"',
    snippet: 'I store text from "${1:#element}" as "${2:varName}"',
    meta: 'UI Variable',
    docHTML: 'Store text content from element into variable'
  },
  {
    caption: 'I store attribute "ATTR" from "SELECTOR" as "VAR"',
    snippet: 'I store attribute "${1:data-id}" from "${2:#element}" as "${3:varName}"',
    meta: 'UI Variable',
    docHTML: 'Store attribute value from element into variable'
  },
  {
    caption: 'I store value from "SELECTOR" as "VAR"',
    snippet: 'I store value from "${1:#input}" as "${2:varName}"',
    meta: 'UI Variable',
    docHTML: 'Store input value from element into variable'
  },

  // Variable storage from UI (role-based)
  {
    caption: 'I store text from role "ROLE" with name "NAME" as "VAR"',
    snippet: 'I store text from role "${1:heading}" with name "${2:Title}" as "${3:varName}"',
    meta: 'UI Variable (Role)',
    docHTML: 'Store text from element by role into variable'
  },
  {
    caption: 'I store value from role "ROLE" with name "NAME" as "VAR"',
    snippet: 'I store value from role "${1:textbox}" with name "${2:Email}" as "${3:varName}"',
    meta: 'UI Variable (Role)',
    docHTML: 'Store input value from element by role into variable'
  },

  // Dialog handling
  {
    caption: 'the user accepts the dialog',
    snippet: 'the user accepts the dialog',
    meta: 'UI Dialog',
    docHTML: 'Accept the next browser dialog (alert/confirm)'
  },
  {
    caption: 'the user dismisses the dialog',
    snippet: 'the user dismisses the dialog',
    meta: 'UI Dialog',
    docHTML: 'Dismiss the next browser dialog'
  },

  // Screenshot
  {
    caption: 'the user takes a screenshot as "FILENAME"',
    snippet: 'the user takes a screenshot as "${1:screenshot.png}"',
    meta: 'UI Screenshot',
    docHTML: 'Take a screenshot and save to .temp/screenshots/'
  },

  // JavaScript execution
  {
    caption: 'the user executes javascript:',
    snippet: 'the user executes javascript:\n  """\n  ${1:// JavaScript code}\n  """',
    meta: 'UI JavaScript',
    docHTML: 'Execute custom JavaScript in page context (result stored in js_result variable)'
  },

  // Debug
  {
    caption: 'pause',
    snippet: 'pause',
    meta: 'UI Debug',
    docHTML: 'Pause execution and open Playwright Inspector'
  },

  // ==================== get_by_label Steps ====================

  // Click actions (label-based)
  {
    caption: 'the user clicks on label "LABEL"',
    snippet: 'the user clicks on label "${1:Email}"',
    meta: 'UI Click (Label)',
    docHTML: 'Click element by label text (finds input associated with <label>)'
  },
  {
    caption: 'the user double clicks on label "LABEL"',
    snippet: 'the user double clicks on label "${1:Email}"',
    meta: 'UI Click (Label)',
    docHTML: 'Double click element by label text'
  },

  // Hover actions (label-based)
  {
    caption: 'the user hovers over label "LABEL"',
    snippet: 'the user hovers over label "${1:Username}"',
    meta: 'UI Hover (Label)',
    docHTML: 'Hover over element by label text'
  },

  // Input actions (label-based)
  {
    caption: 'the user types "TEXT" into label "LABEL"',
    snippet: 'the user types "${1:text}" into label "${2:Email}"',
    meta: 'UI Input (Label)',
    docHTML: 'Type text into input by label text'
  },
  {
    caption: 'the user types "TEXT" into label "LABEL" slowly',
    snippet: 'the user types "${1:text}" into label "${2:Email}" slowly',
    meta: 'UI Input (Label)',
    docHTML: 'Type text slowly into input by label text'
  },
  {
    caption: 'the user fills label "LABEL" with "TEXT"',
    snippet: 'the user fills label "${1:Email}" with "${2:value}"',
    meta: 'UI Input (Label)',
    docHTML: 'Fill input element by label text'
  },
  {
    caption: 'the user clears label "LABEL"',
    snippet: 'the user clears label "${1:Search}"',
    meta: 'UI Input (Label)',
    docHTML: 'Clear input element by label text'
  },

  // Keyboard actions (label-based)
  {
    caption: 'the user presses "KEY" on label "LABEL"',
    snippet: 'the user presses "${1:Enter}" on label "${2:Email}"',
    meta: 'UI Keyboard (Label)',
    docHTML: 'Press a key on element by label text'
  },

  // Checkbox/Radio (label-based)
  {
    caption: 'the user checks label "LABEL"',
    snippet: 'the user checks label "${1:I agree to terms}"',
    meta: 'UI Checkbox (Label)',
    docHTML: 'Check checkbox by label text'
  },
  {
    caption: 'the user unchecks label "LABEL"',
    snippet: 'the user unchecks label "${1:I agree to terms}"',
    meta: 'UI Checkbox (Label)',
    docHTML: 'Uncheck checkbox by label text'
  },

  // Focus & Scroll (label-based)
  {
    caption: 'the user focuses on label "LABEL"',
    snippet: 'the user focuses on label "${1:Email}"',
    meta: 'UI Focus (Label)',
    docHTML: 'Focus on element by label text'
  },
  {
    caption: 'the user scrolls to label "LABEL"',
    snippet: 'the user scrolls to label "${1:Email}"',
    meta: 'UI Scroll (Label)',
    docHTML: 'Scroll to element by label text'
  },

  // Wait actions (label-based)
  {
    caption: 'the user waits for label "LABEL" to be visible',
    snippet: 'the user waits for label "${1:Email}" to be visible',
    meta: 'UI Wait (Label)',
    docHTML: 'Wait for element by label to become visible'
  },
  {
    caption: 'the user waits for label "LABEL" to be hidden',
    snippet: 'the user waits for label "${1:Email}" to be hidden',
    meta: 'UI Wait (Label)',
    docHTML: 'Wait for element by label to become hidden'
  },

  // Assertions - Visibility (label-based)
  {
    caption: 'the label "LABEL" should be visible',
    snippet: 'the label "${1:Email}" should be visible',
    meta: 'UI Assert Visibility (Label)',
    docHTML: 'Assert element by label is visible'
  },
  {
    caption: 'the label "LABEL" should be hidden',
    snippet: 'the label "${1:Email}" should be hidden',
    meta: 'UI Assert Visibility (Label)',
    docHTML: 'Assert element by label is hidden'
  },

  // Assertions - Text content (label-based)
  {
    caption: 'the label "LABEL" should contain text "TEXT"',
    snippet: 'the label "${1:Email}" should contain text "${2:Expected Text}"',
    meta: 'UI Assert Text (Label)',
    docHTML: 'Assert element by label contains text'
  },
  {
    caption: 'the label "LABEL" should have text "TEXT"',
    snippet: 'the label "${1:Email}" should have text "${2:Exact Text}"',
    meta: 'UI Assert Text (Label)',
    docHTML: 'Assert element by label has exact text'
  },

  // Assertions - Input values (label-based)
  {
    caption: 'the label "LABEL" should have value "VALUE"',
    snippet: 'the label "${1:Email}" should have value "${2:test@example.com}"',
    meta: 'UI Assert Value (Label)',
    docHTML: 'Assert input by label has specific value'
  },

  // Assertions - Enabled/Disabled (label-based)
  {
    caption: 'the label "LABEL" should be enabled',
    snippet: 'the label "${1:Email}" should be enabled',
    meta: 'UI Assert State (Label)',
    docHTML: 'Assert element by label is enabled'
  },
  {
    caption: 'the label "LABEL" should be disabled',
    snippet: 'the label "${1:Email}" should be disabled',
    meta: 'UI Assert State (Label)',
    docHTML: 'Assert element by label is disabled'
  },

  // Assertions - Checked state (label-based)
  {
    caption: 'the label "LABEL" should be checked',
    snippet: 'the label "${1:I agree}" should be checked',
    meta: 'UI Assert Checkbox (Label)',
    docHTML: 'Assert checkbox by label is checked'
  },
  {
    caption: 'the label "LABEL" should not be checked',
    snippet: 'the label "${1:I agree}" should not be checked',
    meta: 'UI Assert Checkbox (Label)',
    docHTML: 'Assert checkbox by label is not checked'
  },

  // Variable storage from UI (label-based)
  {
    caption: 'I store text from label "LABEL" as "VAR"',
    snippet: 'I store text from label "${1:Email}" as "${2:varName}"',
    meta: 'UI Variable (Label)',
    docHTML: 'Store text from element by label into variable'
  },
  {
    caption: 'I store value from label "LABEL" as "VAR"',
    snippet: 'I store value from label "${1:Email}" as "${2:varName}"',
    meta: 'UI Variable (Label)',
    docHTML: 'Store input value from element by label into variable'
  }
];

export function getStepCompletions() {
  return gherkinSteps.map((step, index) => ({
    ...step,
    value: step.snippet,
    score: 1000 - index, // Higher score for earlier items
    completer: {
      insertMatch: function(editor, data) {
        const pos = editor.getCursorPosition();
        const line = editor.session.getLine(pos.row);
        const beforeCursor = line.substring(0, pos.column);
        const afterCursor = line.substring(pos.column);

        // Check if we're in a step context (after Given/When/Then/And/*)
        const stepMatch = /^\s*(Given|When|Then|And|\*)\s+(.*)$/i.exec(beforeCursor);

        if (stepMatch) {
          const keyword = stepMatch[1];
          const partialText = stepMatch[2];

          // Calculate the range to replace
          // We need to replace from after the keyword to the cursor position
          const startColumn = stepMatch[0].length - partialText.length;
          const endColumn = pos.column;

          const Range = ace.require("ace/range").Range;
          const range = new Range(pos.row, startColumn, pos.row, endColumn);

          // Replace the range with the snippet
          editor.session.replace(range, data.snippet || data.value);
        } else {
          // Default behavior - just insert
          editor.execCommand("insertstring", data.value);
        }
      }
    }
  }));
}
