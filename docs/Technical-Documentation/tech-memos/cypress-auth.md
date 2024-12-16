# Cypress E2E

**Audience**: TDP Software Engineers <br>
**Subject**:  Cypress Refactor <br>
**Date**:     October 16th, 2024 <br>

## Summary
Digging into our pipeline failures associated in ticket #3141, it was found that our cypress authentication was not persisting for the admin user within a single routine that also used the STT user. Further investigation showed our cypress code is not easily extensible and has not only issues with CSRF compliance but scenario-specific authentication as opposed to abstracted and compartmented sessions. While splitting the scenario and/or using `cypress.wait()` might temporarily solve one problem, we have uncovered technical debt requiring refactoring of this code.

### Background
Debugging the failures within the pipeline had 3 recurring issues:
1. Referer not found as in [this post](https://github.com/cypress-io/cypress/issues/16975)
2. `adminApiRequest` failed to update status, resulting in next step failure.
3. Errors regarding Django's 'csrf_middleware_token`.

By addressing authentication in a standard way and storing all session cookies and tokens, we should be able to resolve these 3 issues.

## Out of Scope
* Any changes to frontend ReactJS and Nginx apps
* Significant changes to backend authentication
* New Cypress workflows beyond our end-to-end test against deployed develop branch

## Method/Design

### Abstracted Gherkin Steps
Presently, many of the defined Javascript functions for a given Gherkin step are bespoke or single-use instead of abstracted and should be adapted. Additionally, it was found that sessions were lingering between Gherkin scenarios as we did not have generic `setup` and `teardown` implementations ahead of these. Sufficient utilization of abstraction within the scenarios which are now doing setup/teardown between scenarios and proper session management should result in a cleaner Cypress execution and make future additions simpler.

Before:
```
    Scenario: A new user is put in the pending state
        Given The admin logs in
        And 'new-cypress@teamraft.com' is in begin state
        When 'new-cypress@teamraft.com' visits the home page
        And 'new-cypress@teamraft.com' logs in
        Then 'new-cypress@teamraft.com' requests access
        And The admin sets the approval status of 'new-cypress@teamraft.com' to 'Pending'
        Then 'new-cypress@teamraft.com' sees the request still submitted
```

There are specific functions for each of the Gherkin Steps and they might rely on the setup steps such as "user is in begin state" which could be handled if we utilized Cypress setup steps:

After:
```
    Scenario: A new user is put in the pending state
        Given 'new-cypress@teamraft.com' logs in
        And 'new-cypress@teamraft.com' requests access
        When The admin sets the approval status of 'new-cypress@teamraft.com' to 'Pending'
        Then 'new-cypress@teamraft.com' sees the request still submitted
```

Setup/Teardown hook psuedo-code:
```JavaScript
describe('E2E User Approval Flow', ()=> {
  beforeEach(() => {
    cy.AdminLogsIn(kwargs)
    cy.UserIsInBeginState(user)
  }))

  afterEach(() => {
    cy.get(@testTeardownId).then(id => {
       cy.resetUser(user)
       cy.resetFilesUploaded(user)
    })
  }
})

When('The admin sets the approval status of {string} to {string}',
  (username, status) => {
    // proceed with your test steps
  }
```

- [Cypress Teardown Hook Blog Post](https://medium.com/@joydeep56053/how-to-implement-test-teardown-hook-in-cypress-671fc9667e07)

### Abstracted utility authentication functions
Our current Cypress implementation has Gherkin scenarios `accounts.feature` which relies on definitions in `accounts.js`, `common-steps.js`, and finally `commands.js` which handle authentication in different ways for different scenarios (e.g., `login()`, `adminLogin()`, and `adminApiRequest()`)

These current functions do not handle the new django `crsf_middleware_token` which may be required for smooth operation. We will move to a standardized authentication function with wrappers which will make the Gherkin scenarios uniform in their approach to authentication and session management.  

### Session Management 
These new implementations will need to leverage newer Cypress commands `session` and `intercept` for managing our two-user scenarios.

```Javascript
const login = (name) => {
  cy.session(name, () => {
    cy.request({
      method: 'POST',
      url: '/login',
      body: { name, password: 's3cr3t' },
    }).then(({ body }) => {
      window.localStorage.setItem('authToken', body.token)
    })
  })
}

it('should transfer money between users', () => {
  login('user')
  cy.visit('/transfer')
  cy.get('#amount').type('100.00')
  cy.get('#send-money').click()

  login('other-user')
  cy.visit('/account_balance')
  cy.get('#balance').should('eq', '100.00')
})
```
[Session Documentation](https://docs.cypress.io/api/commands/session#Switching-sessions-inside-tests)

```Javascript
// spying
cy.intercept('/users/**')
cy.intercept('GET', '/users*')
cy.intercept({
  method: 'GET',
  url: '/users*',
  hostname: 'localhost',
})

// spying and response stubbing
cy.intercept('POST', '/users*', {
  statusCode: 201,
  body: {
    name: 'Peter Pan',
  },
})

// spying, dynamic stubbing, request modification, etc.
cy.intercept('/users*', { hostname: 'localhost' }, (req) => {
  /* do something with request and/or response */
})
```
[Intercept Documentation](https://docs.cypress.io/api/commands/intercept)

## Affected Systems
Existing Django CypressAuth class, django middleware, and existing Nginx implementation.

## Use and Test cases to consider
Test E2E Deployment pipelines and future Cypress integration tests.