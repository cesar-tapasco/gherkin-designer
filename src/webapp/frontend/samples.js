// Sample Gherkin scenarios for the Web Runner
// Based on actual test scenarios from the project
// All variables are properly defined

export const samples = [
  {
    id: 'api',
    name: 'Pokemon API',
    category: 'Basic',
    description: 'Many examples of pokemon API requests',
    content: `@api @pokemon
Feature: Pokemon API Testing
  As a QA Engineer
  I want to test the PokeAPI
  So that I can ensure the API endpoints work correctly

  Background:
    Given the base URL is "https://pokeapi.co/api/v2"
    And I set headers
      | name   | value            |
      | Accept | application/json |

  @pokemon @smoke
  Scenario: Get all Pokemon with pagination
    Given I set query params
      | name   | value |
      | limit  | 10    |
      | offset | 0     |
    When I send "GET" req to "/pokemon"
    Then the res code should be 200
    And the res jq ".results | length" should be "10"
    And the res jq ".count" should not be "0"

  @pokemon @positive
  Scenario: Get a specific Pokemon by ID - Pikachu
    Given I send "GET" req to "/pokemon/25"
    Then the res code should be 200
    And the res jq ".name" should be "pikachu"
    And the res jq ".id" should be "25"
    And I store the value from JSON path ".name" of the last response as "pokemon_name"
    And the "pokemon_name" should contain the value "pikachu"

  @pokemon @positive
  Scenario: Get a specific Pokemon by name - Charizard
    Given I send "GET" req to "/pokemon/charizard"
    Then the res code should be 200
    And the res jq ".name" should be "charizard"
    And the res jq ".id" should be "6"
    And I store the value from JSON path ".types | length" of the last response as "type_count"

  @pokemon @pagination
  Scenario: Get Pokemon with custom pagination
    Given I set query params
      | name   | value |
      | limit  | 5     |
      | offset | 20    |
    When I send "GET" req to "/pokemon"
    Then the res code should be 200
    And the res jq ".results | length" should be "5"
    And I store the value from JSON path ".next" of the last response as "next_page"
    And the "next_page" should contain the value "offset=25"

  @pokemon @data-validation
  Scenario: Verify Pokemon data structure
    Given I send "GET" req to "/pokemon/1"
    Then the res code should be 200
    And the res jq ".name" should be "bulbasaur"
    And I store the value from JSON path ".name" of the last response as "poke_name"
    And I store the value from JSON path ".height" of the last response as "poke_height"
    And I store the value from JSON path ".weight" of the last response as "poke_weight"
    And I store the value from JSON path ".base_experience" of the last response as "poke_exp"
    And the "poke_name" should contain the value "bulbasaur"

  @abilities @smoke
  Scenario: Get all Pokemon abilities
    Given I set query params
      | name   | value |
      | limit  | 10    |
      | offset | 0     |
    When I send "GET" req to "/ability"
    Then the res code should be 200
    And the res jq ".results | length" should be "10"

  @abilities @positive
  Scenario: Get a specific ability by ID
    Given I send "GET" req to "/ability/1"
    Then the res code should be 200
    And the res jq ".name" should be "stench"
    And I store the value from JSON path ".name" of the last response as "ability_name"
    And the "ability_name" should contain the value "stench"

  @types @smoke
  Scenario: Get all Pokemon types
    Given I set query params
      | name  | value |
      | limit | 20    |
    When I send "GET" req to "/type"
    Then the res code should be 200
    And the res jq ".results | length" should be "20"

  @types @positive
  Scenario: Get a specific type - Fire
    Given I send "GET" req to "/type/10"
    Then the res code should be 200
    And the res jq ".name" should be "fire"
    And I store the value from JSON path ".name" of the last response as "type_name"
    And the "type_name" should contain the value "fire"

  @moves @smoke
  Scenario: Get all Pokemon moves
    Given I set query params
      | name   | value |
      | limit  | 10    |
      | offset | 0     |
    When I send "GET" req to "/move"
    Then the res code should be 200
    And the res jq ".results | length" should be "10"

  @moves @positive
  Scenario: Get a specific move - Thunderbolt
    Given I send "GET" req to "/move/85"
    Then the res code should be 200
    And the res jq ".name" should be "thunderbolt"
    And the res jq ".power" should be "90"
    And I store the value from JSON path ".name" of the last response as "move_name"
    And the "move_name" should contain the value "thunderbolt"

  @generations @smoke
  Scenario: Get all Pokemon generations
    Given I send "GET" req to "/generation"
    Then the res code should be 200
    And the res jq ".count" should not be "0"

  @generations @positive
  Scenario: Get a specific generation - Generation I
    Given I send "GET" req to "/generation/1"
    Then the res code should be 200
    And the res jq ".name" should be "generation-i"
    And I store the value from JSON path ".main_region.name" of the last response as "region_name"
    And the "region_name" should contain the value "kanto"

  @berries @smoke
  Scenario: Get all berries
    Given I set query params
      | name   | value |
      | limit  | 10    |
      | offset | 0     |
    When I send "GET" req to "/berry"
    Then the res code should be 200
    And the res jq ".results | length" should be "10"

  @berries @positive
  Scenario: Get a specific berry - Cheri Berry
    Given I send "GET" req to "/berry/1"
    Then the res code should be 200
    And the res jq ".name" should be "cheri"
    And I store the value from JSON path ".name" of the last response as "berry_name"

  @items @smoke
  Scenario: Get all items
    Given I set query params
      | name   | value |
      | limit  | 10    |
      | offset | 0     |
    When I send "GET" req to "/item"
    Then the res code should be 200
    And the res jq ".results | length" should be "10"

  @negative @validation
  Scenario: Attempt to get Pokemon with invalid ID
    Given I send "GET" req to "/pokemon/999999"
    Then the res code should be 404

  @negative @validation
  Scenario: Attempt to get Pokemon with invalid name
    Given I send "GET" req to "/pokemon/invalidpokemonname123"
    Then the res code should be 404

  @pokemon @multiple-requests
  Scenario: Get multiple specific Pokemon and verify names
    Given I send "GET" req to "/pokemon/1"
    Then the res code should be 200
    And I store the value from JSON path ".name" of the last response as "first_pokemon"
    When I send "GET" req to "/pokemon/4"
    Then the res code should be 200
    And I store the value from JSON path ".name" of the last response as "second_pokemon"
    And the "first_pokemon" should contain the value "bulbasaur"
    And the "second_pokemon" should contain the value "charmander"

  @pokemon @stats
  Scenario: Verify Pokemon stats structure
    Given I send "GET" req to "/pokemon/25"
    Then the res code should be 200
    And the res jq ".stats | length" should be "6"
    And I store the value from JSON path ".stats[0].stat.name" of the last response as "first_stat"

  @wait-test @performance
  Scenario: Test API with wait between requests
    Given I set query params
      | name  | value |
      | limit | 5     |
    When I send "GET" req to "/pokemon"
    Then the res code should be 200
    And the user waits 1s
    When I send "GET" req to "/type"
    Then the res code should be 200


  @variable-resolution @advanced
  Scenario: Store and compare response values
    Given I send "GET" req to "/pokemon/1"
    Then the res code should be 200
    And I set var "status_code_1" as responseCode
    And I set var "body_1" as responseBody
    When I send "GET" req to "/pokemon/1"
    Then the res code should be 200
    And I set var "status_code_2" as responseCode
    And I set var "body_2" as responseBody
    And the "status_code_1" should match with "status_code_2"

  @pokemon @forms
  Scenario: Get Pokemon forms for a specific Pokemon
    Given I send "GET" req to "/pokemon/25"
    Then the res code should be 200
    And I store the value from JSON path ".forms[0].name" of the last response as "form_name"
    And the "form_name" should contain the value "pikachu"

  @custom-logic @advanced
  Scenario: Use custom logic to validate Pokemon data
    Given I set query params
      | name  | value |
      | limit | 5     |
    When I send "GET" req to "/pokemon"
    Then the res code should be 200
    And I execute custom logic:
      """
      response_json = api_context.get('response_json')
      results = response_json['results']
      print(f"Found {len(results)} Pokemon")
      assert len(results) == 5, f"Expected 5 Pokemon but got {len(results)}"
      for pokemon in results:
          assert 'name' in pokemon, "Pokemon missing 'name' field"
          assert 'url' in pokemon, "Pokemon missing 'url' field"
      """

  @clear-params @parameter-management
  Scenario: Clear query parameters between requests
    Given I set query params
      | name   | value |
      | limit  | 5     |
      | offset | 10    |
    When I send "GET" req to "/pokemon"
    Then the res code should be 200
    And I clear all query params
    Given I set query params
      | name  | value |
      | limit | 3     |
    When I send "GET" req to "/type"
    Then the res code should be 200
    And the res jq ".results | length" should be "3"

  @performance @response-time
  Scenario: Test Pokemon endpoint performance
    Given I send "GET" req to "/pokemon/1"
    Then the res code should be 200
    And I set var "request_time" as Time
    And the "request_time" should contain the value "."

  @locations @smoke
  Scenario: Get all locations
    Given I set query params
      | name   | value |
      | limit  | 10    |
      | offset | 0     |
    When I send "GET" req to "/location"
    Then the res code should be 200
    And the res jq ".results | length" should be "10"

  @evolution @smoke
  Scenario: Get evolution chains
    Given I send "GET" req to "/evolution-chain/1"
    Then the res code should be 200
    And I store the value from JSON path ".chain.species.name" of the last response as "base_species"

  @pokemon @species
  Scenario: Get Pokemon species information
    Given I send "GET" req to "/pokemon-species/25"
    Then the res code should be 200
    And the res jq ".name" should be "pikachu"
    And I store the value from JSON path ".name" of the last response as "species_name"
    And the "species_name" should contain the value "pikachu"
`
  },
  {
    id: 'ui',
    name: 'Sauce Labs Demo',
    category: 'Basic',
    description: 'A simple demo for Sauce Labs Browser Automation',
    content: `Feature: Sauce Demo Login and Purchase Flow
  
  Background:
    Given the user waits for 4 seconds
  
  Scenario: As a standard user complete a purchase
    Given I set var "base_url" as "https://www.saucedemo.com"
    And I set var "username" as "standard_user"
    And I set var "password" as "secret_sauce"
    And I set var "inventory_title" as "span:has-text('Products')"
    
    When the user navigates to "{{base_url}}"
    And the user waits for page load
    Then the element "input[data-test='username']" should be visible
    And the element "input[data-test='password']" should be visible
    
    When the user fills "input[data-test='username']" with "{{username}}"
    And the user fills "input[data-test='password']" with "{{password}}"
    And the user clicks on "input[data-test='login-button']"
    
    Then the user waits for "{{inventory_title}}" to be visible
    And the element "{{inventory_title}}" should be visible
    And the element "div.inventory_list" should be visible
    
    When the user clicks on "button[data-test='add-to-cart-sauce-labs-backpack']"
    And the user clicks on "a.shopping_cart_link"
    
    Then the element "div.cart_list" should be visible
    
    And the element "[data-test='inventory-item-name']:has-text('Sauce Labs Backpack')" should be visible
    
    When the user clicks on "button[data-test='checkout']"
    Then the element "input[data-test='firstName']" should be visible
    
    When the user fills "input[data-test='firstName']" with "John"
    And the user fills "input[data-test='lastName']" with "Doe"
    And the user fills "input[data-test='postalCode']" with "12345"
    And the user clicks on "input[data-test='continue']"
    Then the element "[data-test='secondary-header']:has-text('Checkout: Overview')" should be visible
    And the element "div.summary_info" should be visible
    
    When the user clicks on "button[data-test='finish']"
    Then the element "h2:has-text('Thank you for your order!')" should be visible
    And the element "button[data-test='back-to-products']" should be visible
  

  Scenario: As a user sort products by price
    Given I set var "base_url" as "https://www.saucedemo.com"
    And I set var "username" as "standard_user"
    And I set var "password" as "secret_sauce"
    And I set var "sort_dropdown" as "select.product_sort_container"
    
    When the user navigates to "{{base_url}}"
    And the user waits for page load
    And the user fills "input[data-test='username']" with "{{username}}"
    And the user fills "input[data-test='password']" with "{{password}}"
    And the user clicks on "input[data-test='login-button']"
    
    Then the element "{{sort_dropdown}}" should be visible
    
    When the user clicks on "{{sort_dropdown}}"
    And the user selects "lohi" from "{{sort_dropdown}}"
    
    # Then the first product price should be "$7.99"
    
    When the user clicks on "{{sort_dropdown}}"
    And the user selects "hilo" from "{{sort_dropdown}}"
    
    # Then the first product price should be "$49.99"

  Scenario: As a locked out user attempt to login
    Given I set var "base_url" as "https://www.saucedemo.com"
    And I set var "locked_user" as "locked_out_user"
    And I set var "password" as "secret_sauce"
    And I set var "error_message" as "h3[data-test='error']"
    
    When the user navigates to "{{base_url}}"
    And the user waits for page load
    
    When the user fills "input[data-test='username']" with "{{locked_user}}"
    And the user fills "input[data-test='password']" with "{{password}}"
    And the user clicks on "input[data-test='login-button']"
    
    Then the element "{{error_message}}" should be visible
    And the element "{{error_message}}" should contain text "Epic sadface: Sorry, this user has been locked out"

  Scenario: As a user navigate through menu options
    Given I set var "base_url" as "https://www.saucedemo.com"
    And I set var "username" as "standard_user"
    And I set var "password" as "secret_sauce"
    And I set var "menu_button" as "button#react-burger-menu-btn"
    And I set var "menu_wrap" as "div.bm-menu-wrap"
    
    When the user navigates to "{{base_url}}"
    And the user waits for page load
    And the user fills "input[data-test='username']" with "{{username}}"
    And the user fills "input[data-test='password']" with "{{password}}"
    And the user clicks on "input[data-test='login-button']"
    
    Then the element "{{menu_button}}" should be visible
    
    When the user clicks on "{{menu_button}}"
    Then the user waits for "{{menu_wrap}}" to be visible
    And the element "a#inventory_sidebar_link" should be visible
    And the element "a#about_sidebar_link" should be visible
    And the element "a#logout_sidebar_link" should be visible
    And the element "a#reset_sidebar_link" should be visible
    
    When the user clicks on "a#logout_sidebar_link"
    Then the element "input[data-test='username']" should be visible
    And the user should be on "{{base_url}}/"

  Scenario: As a user remove items from cart
    Given I set var "base_url" as "https://www.saucedemo.com"
    And I set var "username" as "standard_user"
    And I set var "password" as "secret_sauce"
    And I set var "cart_badge" as "span.shopping_cart_badge"
    
    When the user navigates to "{{base_url}}"
    And the user waits for page load
    And the user fills "input[data-test='username']" with "{{username}}"
    And the user fills "input[data-test='password']" with "{{password}}"
    And the user clicks on "input[data-test='login-button']"
    
    When the user clicks on "button[data-test='add-to-cart-sauce-labs-backpack']"
    And the user clicks on "button[data-test='add-to-cart-sauce-labs-bike-light']"
    
    Then the element "{{cart_badge}}" should be visible
    And the element "{{cart_badge}}" should contain text "2"
    
    When the user clicks on "a.shopping_cart_link"
    Then the element "button[data-test='remove-sauce-labs-backpack']" should be visible
    
    When the user clicks on "button[data-test='remove-sauce-labs-backpack']"
    Then the element "{{cart_badge}}" should contain text "1"
    
    When the user clicks on "button[data-test='remove-sauce-labs-bike-light']"
    Then the element "{{cart_badge}}" should not be visible`
  },
];

// Category grouping
export const categories = [
  'Basic',
  'CRUD',
  'Advanced',
  'Validation',
  'Workflows',
  'UI - Basic',
  'UI - Navigation',
  'UI - Forms',
  'UI - Grid Operations',
  'UI - Interactive',
  'UI - Validation',
  'UI - Workflows'
];

export function getSampleById(id) {
  return samples.find(s => s.id === id);
}

export function getSamplesByCategory(category) {
  return samples.filter(s => s.category === category);
}

export function getAllSamples() {
  return samples;
}

export function getCategories() {
  return [...new Set(samples.map(s => s.category))];
}
