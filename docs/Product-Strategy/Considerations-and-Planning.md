# Product considerations
Like most projects in government, our team is trying to weigh and balance three primary considerations and make sure what we build is...
* what users need
* advances the mission
* feasible to implement

We will use a variety of tools and methods to weigh these considerations. Some of these help us understand one specific consideration, while others help us understand two or even all three considerations. Here are some of these tools and question we have or might use:

![three overlapping circles what users need advance mission feasible to implement](https://github.com/HHS/TANF-app/blob/master/design-assets/research-artifacts/three%20product%20considerations.png?raw=true)

From here, we use our understanding of the considerations to develop a plan for building a solution. The plan has different levels of detail. At the highest level, the plan is very conceptual, and there are a lot of possible ways to achieve those conceptual goals. Then the plan narrows to increasing specificity.

![three considerations lead to the plan](https://github.com/HHS/TANF-app/blob/master/design-assets/research-artifacts/considerations%20to%20the%20plan.png?raw=true)

## Considerations on feasibility to implement
### Engineering practice considerations
* **Reusability** Is there a compliant existing tool or library that can be used to meet this business need?

* **Complexity** How challenging will it be to implement this?

* **Length** How long will it take to implement this?

* **Maintainability** Will the technology used to implement this be easy to maintain (especially if new engineers were to join the team)?

### Privacy
* **Minimal collection** The best way to protect information is to not collect it at all as it can increase risk and reduce privacy for the public. For all information, especially personally identifiable information, determine if the information can be inferred without the use of or increased collection of PII.

* **Anonymization** Ensure all PII is encrypted or fully anonymized.

* **Notice** Individuals are given transparent notice about what information is collected about them and how it is used.

* **Consent and control** Individuals are given meaningful consent about their data being collected, can access what data is collected about them and if need be can request deletion and/or revoke their consent.


### Security
* **Least privilege and minimize access** In order to expose the least amount of data, make sure that users only have access to what they need and not much more.

* **Auditable** Ensure that all actions are logged so that actions can be reviewed to triage issues or security concerns.

* **Continuous** Security is ongoing and new concerns could always arise, so treat security as an ongoing consideration, not a one time event.


# Levels of planning

"Strategy without tactics is just a pipe dream. Tactics without strategy is a nightmare."

* For us, the highest level of the plan is the TANF program goals--what the TANF program is ultimately trying to achieve. We developed the [TANF Program Theory of Change](https://github.com/HHS/TANF-app/wiki/Vision-and-Stakeholders#tanf-program-theory-of-change) at this level of the plan to help us understand how the new TDRS fits into the program's larger goals.
* The next level down is our [Product Vision](https://github.com/HHS/TANF-app/wiki/Vision-and-Stakeholders#product-vision). This level is slightly more defined and narrowly focused. The vision about what we're trying to achieve within the scope of this specific project. It answers: What’s the problem? Who’s affected? How are we helping? What’s the outcome?
* Below that is our [Product Roadmap](https://github.com/HHS/TANF-app/wiki/Roadmap-and-backlog#product-roadmap) which represents our latest thinking about the order in which we’ll tackle the various pieces of the overarching problem. The roadmap is not a promise--it is just a plan to bridge the strategic vision and to the tackle tasks.
* And finally, at the bottom and on the ground is the [Product Backlog](https://github.com/HHS/TANF-app/wiki/Roadmap-and-backlog#backlog). That’s the most defined and tangible part of our plan--an ever-evolving list of bite-sized pieces of work that deliver value to our users.

![TDRS product four levels of plan](https://github.com/HHS/TANF-app/blob/master/design-assets/research-artifacts/TDRS%20product%20plan%20at%20four%20levels.png?raw=true)

Because we will be working in an agile way, the backlog is going to change frequently as we build and learn. The roadmap will also be adjusted as we progress. The product vision and TANF Theory of Change are unlikely to change.