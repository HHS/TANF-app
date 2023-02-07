# 19. Integration tests

Date: 2022-12-05

## Status

Accepted

## Context

Deployments are slow and require a lot of manual testing; this can cause quite a backup during PR reviews and releases. Unit tests are valuable for fast feedback close to the code, but we are lacking broader-scale automated testing of features.

### Agile testing quadrants

Resources
* [Testing Quadrants](http://www.exampler.com/old-blog/2003/08/22/#agile-testing-project-2)
* [Using the Agile Testing Quadrants](https://lisacrispin.com/2011/11/08/using-the-agile-testing-quadrants/)

The Agile Testing Quadrants is a useful way to explore how different types of tests can be used to help achieve different testing goals. In Brian Marick's original post, tests are described as being either **business facing** or **technology facing**.

* _Business-facing_ tests describe functionality in user's own terms, as a set of actions taken in the system to achieve a broader goal for the person or business.
   * Example: Account holders have to verify their PIN before they're able to submit a transaction.
* _Technology-facing_ tests describe technical aspects of the system that are relevant to the team that owns it.
   * Example: Transactions submitted without PIN verification should fail with "Error Code 4".

Both tests can be for the same functionality, but the buiness-facing example implicitly covers more rules (frontend-validation, integration between different system parts) and approaches validation from the perspective of helping the user achieve their end-goal. The technology-facing example, however, is useful in its exact-ness: a test like this can be isolated to a single part of the codebase and provide fast-feedback to developers about potential breaking changes. There's some fuzziness here, of course, as many technical decisions are partly business decisions and vice-versa.


Both business-facing and technology-facing tests can be described as having one of two goals: **support programming** or **critique the product**.

* Tests that _support programming_ are used by developers to safeguard their development of the system; they are written and run often during development and help developers identify any unintended side-effects of changes they've made. We can also use these tests to prepare ourselves and test assumptions prior to starting development.
* Tests that _critique the product_ are used by developers and stakeholders alike to uncover issues that already exist; whether they are issues in planning, technology, design, or development. These tests find bugs and help identify other ways the system can be made better for the end-user.


We can consider these ideas as a matrix. The following example from Lisa Crispin shows the quadrants and examples of types of tests applying to each

![Quadrants and test types](http://www.exampler.com/testing-com/blog/agile/test-matrix.jpg)

Tests in the left half of the quadrant are generally valuable to automate - they consider "known" paths for the system and expected behaviors/results. We can codify these and run them every time a change is made to the system in order to give us confidence in releases.

Tests in the right half of the quadrants generally try to seek answers to unknowns about the behavior of the system or expectations of the people using it. We're trying to uncover issues and test our assumptions rather than our implementations, therefore these tests need the power of human subjectivity to be wholly effective. They can be supported by tools, but ultimately are manual tests.

### Types of automated tests

To simplify the above quadrants, we can categorize the "Automated" tests (Q1 and Q2) as

* Unit tests (Q1) - tests that are technology-facing and support programming. For these tests, fast-feedback is key. They should cover isolated cases in individual parts of the system, and mock as much as is reasonable to do so.
* Integrations Tests (Q2) - tests that are business-facing and support programming. These tests should be automated to provide the fastest feedback possible, but more emphasis should be placed on accurately modeling the user's experience and workflow. Mock as little of the system as possible and perform steps in the system as the user would actually do them, also using indicators within the system to provide results.

As stated before, there's a grey area in this type of testing and tests can be both business- _and_ technology-facing, so consider the quadrants to be starting points and extremes in a spectrum. Ultimately, the most valuable test is the test that verifies as much of the system as possible for the functionality being tested. Also be sure to consider the tradeoff with reliability and speed.

### Tools

* [Selenium](https://www.selenium.dev/) is a browser-automation tool that has been a cornerstone of the automated testing industry for quite some time.
   * Pro: extensive language support, documentation, and community support.
   * Con: requires a lot of setup for common tasks, especially for modern applications. `wait`-ing on elements and organizing page objects, selectors, etc
   * Con: flaky, especially with modern, async frontend applications. very inflexible runtime which is difficult to run in ci
* [Cypress](https://www.cypress.io/) is another browser-automation tool that seeks to be simpler for developers and address gaps in the capabilities of older tools to test more modern, asynchronous application arhitectures.
   * Pro: growing community adoption, support for major frameworks and most architectures.
   * Pro: substantial runtime improvement on Selenium with native support for async frontends, works very well locally and in CI, Cypress dashboard provides test replay analysis
   * Con: Cypress doesn't support testing more than one "superdomain", which means redirects to Login.gov to authenticate are not supported. Authentication workarounds are generally required.

Pro: Both tools would allow us to use [Cucumber/Gherkin](https://cucumber.io/docs/gherkin/) to write frontend test scenarios in plain-language steps, which document the system behavior in business-language (useful for Q2 tests).



## Decision


### Which type of test?

The team has expressed interest in expanding the integration testing suite. We have a well-rounded unit test suite that addresses most of our quadrant-1 needs, but we're lacking q2 "business scenario" tests that can be run against `develop` or another deployed environment to test our system end-to-end. These types of tests would provide continuous regression testing and improve our release confidence.

We recommend creating a new "end-to-end" integration test suite, which mocks the least amount of the system possible. These tests will perform actions by launching a browser and going through the actual steps a user would use to perform a task in the system.

### Which tool?

Cypress improves the end-to-end testing game a lot by providing a simple interface that requires minimal configuration. Selenium suites require a lot of command-line configuration that Cypress simply removes, allowing us to focus on writing quality tests. We still need to understand some of the basics of testing with a browser automation tool in order to make the most of it, but overall Cypress lowers the barrier to entry for automated testing, makes tests easier to write and debug, and provides a well-documented and well-supported environment requiring minimal configuration. For those reasons, we recommend Cypress.

### When will tests be run?

Tests should be run locally as much as possible during development to ensure changes don't unexpectedly break something else in the system. Tests should at least be run before and during the PR process, so we should add a CircleCI task to run Cypress tests along with the unit tests.

We should also regularly run tests in a deployed environment. In order to best simulate a production deployment, we should automatically deploy to a specific environment after merges to `develop`, after which the end-to-end tests should automaticfally be run. This would require a few more changes to our CircleCI configuration and processes.

### How will failures be responded to?

Failures during development should be addressed by the developer that broke the tests. Tests should be passing in the PR pipeline before a PR is merged, so if a PR fails after a merge, the developer of the PR should look into the failure. With Cypress, failures due to test flakiness should be minimized, but are still possible. Depending on risk and priority, tests can be rerun or work prioritized to fix/rearchitect the test or feature to improve reliability.

### How will we plan tests into the scope of upcoming work?

Tests for new work should be planned into the scope of that work before it is assigned, so may impact any existing estimates.

Tests for existing features require new work items to be prioritized among the backlog.

## Consequences

The benefits and any known/potential risks of the decision should be described herein. See Michael Nygard's article, linked above, for more details.

benefits
- more consistent deployments, testing more often in deployed environments
- opens the door to more continuous delivery

risks
- make changes to the ci/deployment workflow, cannot enable in prod
- authentication workaround, potential security risk
- additional tooling; learning curve and additional support
- impacts scope of future work and requires new work be prioriized

## Notes

