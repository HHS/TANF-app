# Our Priorities, Values, and Quality Expectations

An overview of how our team works together to deliver a quality TDP product is included herein. 

- **[Our priorities for developing a quality TDP product](#Our-Priorities)**
- **[Our values for working together on TDP development](#Our-values)**
- **[How quality will be assessed](#Our-Quality-Expectations)** 
- **[Additional resources](#Additional-resources)**

## Our Priorities

The [TDP product team](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/docs/How-We-Work/Team-Composition.md#primary-product-team) is committed to the following:

1. **Prioritizing quality over time and scope.**  Issues should be written and completed in a way that delivers quality insights, design, and/or features and should not come at the cost of time and scope. Issue scope should be refined to ensure progress toward the product vision is timely and demonstrable. 
2. **Accessibility needs are considered early in the [our workflow](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/docs/How-We-Work/team-charter/our-workflow.md).** Issues must be refined before the work to address it starts, and refinement includes consideration for how users will interact with TDP features ([ref](https://www.deque.com/shift-left/)). 
3. **Issues move to `QASP review` pipeline on a rolling basis and must first pass through the `Raft review` pipeline.** Raft is responsible for ensuring acceptance criteria are met before submitting the issue for government review. For each sprint, at least one issue passes `raft review` and is submitted for `QASP review`.

## Our Values 

- **We work together and ask for help.** We don’t fall into a pit of silence trying to solve or finish something alone. Pairing is the norm. We are a team and should feel comfortable asking for help when it is needed.  
- **We invite feedback and give it graciously.** We ask for feedback early and often. We trust our teammates to tell us when we can do better. We share with the team  our preferences about giving and receiving feedback.
- **We reflect on our own process and behaviors.** We acknowledge our mistakes and learn from them. It’s only “failure” if you fail to learn from it. We constantly look to refine and improve how we work together. 
- **We assume best intent.** We separate intention from impact. Use specific examples, and avoid generalizations. Forgive. 
- **We default to openness and transparency.** We ask questions and discuss issues in open channels (i.e. Mattermost and Github) whenever possible. Don’t be afraid to surface problems that you may become aware of, “ping” a teammate on a stale ticket, or provide feedback. Acknowledge and discuss things that aren’t working well (without blame or judgement) with an eye towards improvements. Have a real chat about resolving something rather than perpetuating misunderstandings.  
- **We state our goals explicitly and follow up on our commitments.** Whether it is a team meeting, sprint goal, project milestone, retrospective, or one-on-one sync, we state our goals at the beginning and follow-up continuously. We adjust our goals, as necessary, by providing each other with honest feedback along the way.  

## Our Quality Expectations

The government uses the **Quality Assurance Surveillance Plan (QASP)** to monitor the quality of the team's deliverables and performance. This helps ensure that TDP is a quality product built using agile practices. [Our workflow for developing TDP](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/docs/How-We-Work/team-charter/our-workflow.md) is designed with the QASP in mind. 

Research, design, and feature work must pass both [`raft review`](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/docs/How-We-Work/team-charter/our-workflow.md#the-issue-is-ready-for-raft-review) and the [`QASP review`](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/docs/How-We-Work/team-charter/our-workflow.md#the-issue-is-ready-for-qasp-review) and will involve an assessment of 8 **[deliverables](#Deliverables)**. 

Below is a description of each deliverable and the manual practices that the team will follow to check deliverables against the QASP in addition to the automated testing checks.

### Deliverables

#### Deliverable 1: Accepted Features

<details>

##### Performance standard(s): The development team will deliver code and functionality to satisfy pre-defined acceptance criteria (AC).

##### Acceptable quality level: Features developed meet AC stated in the issue

Prior to submitting issues for `qasp review`, the `raft review` should include checking the ACs to confirm the features meet the acceptance criteria stated in the issue. This review should also include documenting the steps to manually test that the features developed meet the ACs. 
</details>

#### Deliverable 2: Tested Code

<details>

##### Performance Standard(s): Version-controlled HHS GitHub repository of code that has substantial test code coverage that will remain in the government domain. 
##### Acceptable Quality level: Minimum of 90% test coverage of all code. All areas of code are meaningfully tested.

Review to ensure code coverage isn’t manually skipped (using “pragma: no cover” or other similar techniques). If code coverage is skipped on certain sections of the code, provide in-line code comments as to why the coverage is being skipped. Review to make sure components of the system are tested and how they are tested.
</details>

#### Deliverable 3: Properly Styled Code

<details>

##### Performance Standard(s): [GSA 18F Frontend Style Guide - JS](https://engineering.18f.gov/javascript/#style), [GSA 18F Backend Style Guide](https://engineering.18f.gov/python/#style)
##### Acceptable Quality level: 0 linting errors and 0 warnings

Review Circle CI to ensure: [flake8](https://pypi.org/project/flake8/) and [AirBnb’s react style guides](https://github.com/airbnb/javascript/tree/master/react) are being used. 

Also, review to ensure methods, variables, etc. are appropriately named. For methods that are more than 75 lines, consider refactoring into multiple shorter methods or by extracting functionality by following Don’t Repeat Yourself (DRY) principles. See [guidelines government uses to assess code maintainability](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/docs/How-We-Work/Heuristics.md#code-maintainability).
</details>

#### Deliverable 4: Accessibility

<details>

##### Performance Standard(s): Web Content Accessibility Guidelines 2.1 AA standards
##### Acceptable Quality level: 0 errors reported using an automated scanner and 0 errors reported in manual testing

Review to ensure each screen follows the guidelines below to meet the accessibility WCAG2.1 AA performance standard (**_see dropdown below for more details on how gov will test a11y_**). Aditionally, `raft review` should include documenting evidence that the guidelines below were followed. 

- Follow [Raft’s Accessibility Do’s and Don’ts](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/docs/Technical-Documentation/rafts-accessibility-dos-and-donts.md#raftsaccessibility-dos-and-donts) guidelines
- Use [DHS Trusted Tester v5 Conformance Test](https://section508coordinators.github.io/TrustedTester/), [Tota11y](https://github.com/Khan/tota11y), and [WAVE](https://wave.webaim.org/)
- Run the Accessibility Insight for [Web “Fast Pass” tool](https://accessibilityinsights.io/docs/en/web/getstarted/fastpass)
- Run the Accessibility Insight for Web "Manual test for tab stops"
- Test using screen reader VoiceOver for Mac and keyboard (Tab) only

**<details><summary>How government will test a11y</summary>**
   
#### How government plans to carry out the Method of Assessment

Our web testing tool will be [Accessibility Insights](https://accessibilityinsights.io/).

Accessibility Insights includes both a [Fast Pass](https://accessibilityinsights.io/docs/en/web/getstarted/fastpass/) tool and a comprehensive [Assessment](https://accessibilityinsights.io/docs/en/web/getstarted/assessment/) tool.

We will conduct accessibility review at the epic-level (i.e., when the last  or only feature associated with the epic has been submitted for QASP review). We will check new pages, features, and interactions added during the course of each sprint using:

- Accessibility Insights Fast Pass tool
- Accessibility Insights Assessment tool
- Manual screen reader testing using one or more of the following combinations:
  - JAWS on Windows
  - VoiceOver on Safari, Mac OS
  - VoiceOver on iOS

We will consider all documentation from Raft's a11y reviews included in each PR associated with the epic. We won't re-test pages or elements that have previously been tested and haven't changed since, such as header or footer elements.

We will invite in ACF's 508 Coordinator to review the accessibility of the site at strategic points in the process.

The ultimate goal of this evaluation plan is to ensure that the site is accessible to its users, meets WCAG 2.1 AA standards as per contract, and meets Section 508 legal requirements.

If we find that this evaluation plan isn't helping us meet those goals, we may adjust the plan after consulting with subject matter experts and the development team. 
  </details>
    
</details>

#### Deliverable 5: Deployed

<details> 
    
##### Performance Standard(s): Code must successfully build and deploy into the staging environment.
##### Acceptable Quality level: Successful build with a single command

Review CircleCI output to ensure there are no issues with the code being deployed to Cloud.gov* Dev Instance. If manual code deployment is needed, the single command to deploy should be documented. As applicable, review to make sure environment variables have passed.
</details>

#### Deliverable 6: Code documentation

<details>

##### Performance Standard(s): All dependencies are listed and the licenses are documented. Major functionality in the software/source code is documented, including system diagram. Individual methods are documented inline in a format that permits the use of tools such as JSDoc. All non-inherited 800-53 system security controls are documented in the Open Control or OSCAL format and HHS Section 508 Product Assessment Template (PAT) are updated as appropriate.
    
##### Acceptable Quality level: Code must be understandable and contextualized for the reviewers possess the knowledge and background necessary for analysis and constructive criticism to take place.
    
    
**README files**

- Must be complete and clear enough for a new team member or an outside contributor to gain context and start contributing quickly and with minimal assistance
- Should include relevant architectural decisions using Architectural Decision Log (this should live in wiki but for now we have added the template to Teams)
- Should include the single command to deploy if manual code deployment is needed

**Comments**

- Should be easy to understand, precise, and relevant
- Should describe what the code does and how the code does it
- Inline code comments should describe the code in context by using Docstrings for Django and JSDoc for React
- Should be included with a PR to call out other potential approaches that have already been considered and rejected

**Other items to document**

- Non-inherited 800-53 system security controls in Open Control, OSCAL, and HHS Section 508 Product Assessment Template
- For any security vulnerabilities that are being ignored or have false positives found via Dependabot or Zap, review to ensure granular details to describe Dependabot/Zap vulnerabilities, what we did to investigate, and what is the mitigation plan.
- 
</details>

#### Deliverable 7: Secure

<details>
    
##### Performance Standard(s): Open Web Application Security Project (OWASP) Application Security Verification Standard 3.0
##### Acceptable Quality level: Code submitted must be free of medium- and high-level static and dynamic security vulnerabilities
Review to ensure any false positives are documented and granular details on describe the Dependabot vulnerabilities, what we did to investigate, and what is the mitigation plan. These details will be documented in the readme.
</details>

#### Deliverable 8: User Research
<details>

##### Performance Standard(s): Usability testing and other user research methods must be conducted at regular intervals throughout the development process (not just at the beginning or end). 
    
##### Acceptable Quality level: Research plans and artifacts from usability testing and/or other research methods with end users are available at the end of every applicable sprint, in accordance with the contractor’s research plan.


Prior to government review, Raft reviews the artifacts based on a research plan
    
See [guidelines](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/docs/How-We-Work/Heuristics.md#design) government uses to assess user research and design work.
    
    
</details>


## Additional resources

- [Final TDRS/TDP RFQ](https://github.com/18F/tdrs-app-rfq/blob/main/Final-RFQ/FINAL-TDRS-software-development-RFQ.md) 
- [Government Heuristics ](https://github.com/raft-tech/TANF-app/tree/raft-tdp-main/docs/How-We-Work/Heuristics.md)
- [PR template](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/.github/pull_request_template.md)







