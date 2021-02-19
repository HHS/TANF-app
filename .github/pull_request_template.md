### Deliverable 1: Accepted Features

> *Performance Standard(s): At the beginning of each sprint, the Product Owner and development team will collaborate to define a set of user stories to be completed during the sprint. Acceptance criteria for each story will also be defined. The development team will deliver code and functionality to satisfy these user stories.*

> *Acceptable Quality Level: Delivered code meets the acceptance criteria for each user story. Incomplete stories will be assessed and considered for inclusion in the next sprint.*

+ [ ] Look up the acceptance criteria in the related issue; paste ACs below in checklist format.
+ [ ] Check against the criteria:

As Product Owner, @lfrohlich will decide if ACs are met.

### Deliverable 2: Tested Code

> *Performance Standard(s): Code delivered under the order must have substantial test code coverage. Version-controlled HHS GitHub repository of code that comprises products that will remain in the government domain.*

> *Acceptable Quality Level: Minimum of 90% test coverage of all code. All areas of code are meaningfully tested.*

+ Are all areas of code introduced in this PR meaningfully tested?
  + [ ] If this PR introduces backend code changes, are they meaningfully tested?
  + [ ] If this PR introduces frontend code changes, are they meaningfully tested?
+ Are code coverage minimums met?
  + [ ] Frontend coverage: ___ (see https://github.com/raft-tech/TANF-app README coverage dashboard)
  + [ ] Backend coverage: ___ (see https://github.com/raft-tech/TANF-app README coverage dashboard)

### Deliverable 3: Properly Styled Code

> *Performance Standard(s): GSA 18F Front- End Guide*

> *Acceptable Quality Level: 0 linting errors and 0 warnings*

+ [ ] Are backend code style checks passing on CircleCI?
+ [ ] Are frontend code style checks passing on CircleCI?
+ [ ] Does this PR change any linting or CI settings?

### Deliverable 4: Accessible

> *Performance Standard(s): Web Content Accessibility Guidelines 2.1 AA standards*

> *Acceptable Quality Level: 0 errors reported using an automated scanner and 0 errors reported in manual testing*

+ [ ] Did automated and manual testing with @iamjolly and @ttran-hub using Accessibility Insights reveal any errors introduced in this PR?
    + [See the full Accessibility Assessment plan here.](https://github.com/HHS/TANF-app/blob/main/docs/a11y/how-18f-will-test-a11y.md)

### Deliverable 5: Deployed

> *Performance Standard(s): Code must successfully build and deploy into the staging environment.*

> *Acceptable Quality Level: Successful build with a single command*

+ [ ] Was the code successfully deployed via automated CircleCI process to development on Cloud.gov?

### Deliverable 6: Documented

> *Performance Standard(s): Summary of user stories completed every two weeks. All dependencies are listed and the licenses are documented. Major functionality in the software/source code is documented, including system diagram. Individual methods are documented inline in a format that permits the use of tools such as JSDoc. All non-inherited 800-53 system security controls are documented in the Open Control or OSCAL format and HHS Section 508 Product Assessment Template (PAT) are updated as appropriate.*

> *Acceptable Quality Level: Combination of manual review and automated testing, if available*

+ [ ] If this PR introduces backend code, is that code documented both inline and overall?
+ [ ] If this PR introduces frontend code, is that code documented both inline and overall?
+ [ ] If this PR introduces dependencies, are their licenses documented?

### Deliverable 7: Secure

> *Performance Standard(s): Open Web Application Security Project (OWASP) Application Security Verification Standard 3.0*

> *Acceptable Quality Level: Code submitted must be free of medium- and high-level static and dynamic security vulnerabilities*

+ [ ] Does the OWASP Scan pass on CircleCI?
+ [ ] Do manual code review and manual testing detect any security issues?
