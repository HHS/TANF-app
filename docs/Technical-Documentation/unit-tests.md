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

```
$ tdrs-run-pytest
```

## Frontend Unit Tests
* Uses Jest
* Tests exist alongside their associated action, component or reducer

```bash
$ tdrs-run-jest
```

## Frontend Accessibility Tests
* Uses Pa11y
* Bypasses authentication through use of the `REACT_APP_PA11Y_TEST` environment variable on app build.
* Navigates to several pages in the app and confirms presence of expected private template container before taking a screenshot and running automated accessibility checks.
* Stores the screenshots as artifacts in Circle CI.

```bash
$ tdrs-run-pa11y
```

## Frontend Integration / E2E Tests
* None currently (as of 12/1/2021), the plan is to use Pa11y to accomplish this or add another integration testing framework.
* Some examples of UI functionality that needs to be tested:
    * Profile page as an authenticated user - viewing and editing.
    * Data Files page as Data Analyst - searching for files by year and quarter for current STT.
    * Data Files page as OFA Admin - searching for files by STT, year and quarter
    * Data Files upload as both user types
    * Welcome page shows expected permissions.

## Notes

See **[Commands.sh](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/commands.sh)** for a list and description of standardized commands for running these tests as part of local development. The code sections above are aliases or functions from `commands.sh`.
