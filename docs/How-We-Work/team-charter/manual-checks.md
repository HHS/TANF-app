# Raft's manual checks to meet QASP

This document describes the manual practices that the Raft team will follow to manually check deliverables against the QASP in addition to the automated testing checks.

## Deliverable 1: Features

Prior to product owner and government review, Raft design team reviews during Raft review to confirm the features meet the acceptance criteria stated in the issue.

## Deliverable 2: Tested Code

Review to ensure code coverage isn’t manually skipped (using “pragma: no cover” or other similar techniques). If code coverage is skipped on certain sections of the code, provide in-line code comments as to why the coverage is being skipped. Review to make sure components of the system are tested and how they are tested.

## Deliverable 3: Properly Styled Code

Review Circle CI to ensure [flake8](https://pypi.org/project/flake8/) and [AirBnb’s react style guides](https://github.com/airbnb/javascript/tree/master/react) are being used. Also, review to ensure methods, variables, etc. are appropriately named. For methods that are more than 75 lines, consider refactoring into multiple shorter methods or by extracting functionality by following Don’t Repeat Yourself (DRY) principles.

## Deliverable 4: Accessibility

Review to ensure each frontend screen with the following the guidelines below to meet the accessibility WCAG2.1 AA performance standard as stated in the QASP.

- Use [DHS Trusted Tester v5 Conformance Test](https://section508coordinators.github.io/TrustedTester/), [Tota11y](https://github.com/Khan/tota11y), and [WAVE](https://wave.webaim.org/)
- Run the Accessibility Insight for [Web “Fast Pass” tool](https://accessibilityinsights.io/docs/en/web/getstarted/fastpass)
- Run the Accessibility Insight for Web "Manual test for tab stops"
- Test using screen reader VoiceOver for Mac and keyboard (Tab) only
- Review design accessibility using [Stark](https://www.figma.com/community/plugin/732603254453395948) (Figma contrast ratio plugin).
- Also, review [Raft’s Do’s and Don’ts](https://github.com/HHS/TANF-app/blob/SelenaJV-patch-1/docs/team-charter/rafts-accessibility-dos-and-donts.md)

## Deliverable 5: Deployed

Review CircleCI output to ensure there are no issues with the code being deployed deployment to Cloud.gov* Dev Instance. If manual code deployment is needed, the single command to deploy should be documented in README.md. As applicable, review to make sure environment variables have passed.

## Deliverable 6: Code documentation

### README files

- Must be complete and clear enough for a new team member or an outside contributor to gain context and start contributing quickly and with minimal assistance
- Should include relevant architectural decisions using Architectural Decision Log (this should live in wiki but for now we have added the template to Teams)
- Should include the single command to deploy if manual code deployment is needed

### Comments

- Should be precise and relevant
- Should describe what the code does and how the code does it
- Inline code comments should describe the code in context by using Docstrings for Django and JSDoc for React
- Should be included with a PR to call out other potential approaches that have already been considered and rejected

### Other items to document

- Non-inherited 800-53 system security controls in Open Control, OSCAL, and HHS Section 508 Product Assessment Template
- For any security vulnerabilities that are being ignored or have false positives found via Snyk or Zap, review to ensure granular details to describe Snyk vulnerabilities, what we did to investigate, and what is the mitigation plan.

## Deliverable 7: Secure

Review to ensure any false positives are documented and granular details on describe the Snyk vulnerabilities, what we did to investigate, and what is the mitigation plan. These details will be documented in the readme.

## Deliverable 8: User Research

Prior to product owner review, Raft reviews against the acceptance criteria stated in the issue and updates the issue description to include links to relevant artifacts.
