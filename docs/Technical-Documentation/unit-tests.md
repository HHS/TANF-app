# TDP Tech Deep Dive - Unit Tests

## Backend Unit Tests
* Uses Pytest
* Most tests are located in their relevant Django app under the `tdpservice` module
* Tests rely heavily on Factories and Fixtures using pytest-factoryboy
* Most fixtures are defined in the `conftest.py` at the root of the `tdpservice` directory
* Tests that could use the most refactoring are under the `users` app - that was among the first Django code for the project and is not very DRY.
* 2 test modules are located in the main `tests` subdirectory:
    * test_admin: Tests that customizations to the admin site work correctly
    * test_clients: Tests a now-unused S3 client. This could be removed along with the `clients.py:get_s3_client` function. 

## Frontend Unit Tests
* Uses Jest
* Tests exist alongside their associated action, component or reducer

## Frontend Integration Tests
* Uses Cypress
* Two test modules under cypress/integration:
    * login.spec.js - Tests that the login page shows a Sign In button
    * welcome_page_greeting.spec.js - Tests that the correct elements are shown on the welcome page for unauthenticated users
* Needs to either be replaced or updated to test much more of the site
