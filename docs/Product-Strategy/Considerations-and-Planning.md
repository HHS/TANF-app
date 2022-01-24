# Product Considerations
Like most projects in government, our team is trying to weigh and balance three primary considerations and make sure what we build is...
* what users need
* advances the mission
* feasible to implement

We will use a variety of tools and methods to weigh these considerations. Some of these help us understand one specific consideration, while others help us understand two or even all three considerations. Here are some of these tools and question we have or might use:

![three product considerations](https://i.imgur.com/0Zf24DK.png)

From here, we use our understanding of the considerations to develop a plan for building a solution. The plan has different levels of detail. At the highest level, the plan is very conceptual, and there are a lot of possible ways to achieve those conceptual goals. Then the plan narrows to increasing specificity.

![considerations to the plan](https://i.imgur.com/jLVwsJn.png)

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

* For us, the highest level of the plan is the TANF program goals--what the TANF program is ultimately trying to achieve. We developed the [TANF Program Theory of Change](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/docs/Product-Strategy/Vision-and-Stakeholders.md#tanf-program-theory-of-change) at this level of the plan to help us understand how the new TDRS fits into the program's larger goals.
* The next level down is our [Product Vision](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/docs/Product-Strategy/Vision-and-Stakeholders.md#product-vision). This level is slightly more defined and narrowly focused. The vision about what we're trying to achieve within the scope of this specific project. It answers: What’s the problem? Who’s affected? How are we helping? What’s the outcome?
* Below that is our [Product Roadmap](https://app.mural.co/invitation/mural/raft2792/1629476801275?sender=laurenfrohlich3146&key=5328c2c6-a097-4b3d-bcf7-f2e551a01a72) which represents our latest thinking about the order in which we’ll tackle the various pieces of the overarching problem. The roadmap is not a promise--it is just a plan to bridge the strategic vision and to the tackle tasks.
* And finally, at the bottom and on the ground is the [Product Backlog](https://github.com/raft-tech/TANF-app/issues). That’s the most defined and tangible part of our plan--an ever-evolving list of bite-sized pieces of work that deliver value to our users.

![TDRS product plan at four levels](https://i.imgur.com/IUV7euD.png)

Because we will be working in an agile way, the backlog is going to change frequently as we build and learn. The roadmap will also be adjusted as we progress. The product vision and TANF Theory of Change are unlikely to change.

---

### Prodtastic Resources
Prod-tastic was a **_workshop series_** created to familiarize the OFA product owner and other stakeholders with Product Thinking and Human Centered Design concepts and to collaborate on building alignment artifacts for the new TDP project. We developed the TANF Theory of Change, product vision statement, a first draft of Design Principles, product roadmap, and product backlog in these conversations.


**<details><summary> Workshops</summary>**
    
[Gross Anatomy of an App](https://app.mural.co/t/gsa6/m/gsa6/1593633056023/5da6f5bf19d208f2961eb73df4634cbffc4bd411)
* Service-oriented architecture
* Frontend, Backend, Database, User Authorization
* Hosting
* 3rd Party Connections + APIs

[How We Make Software](https://app.mural.co/t/gsa6/m/gsa6/1593633082612/085d533c32c78e5cd3d8ae21b0d039b622655eb8)
* Agile
* User-Centered Design
* Defining the Work
* Writing Code

[Product Strategy](https://teams.microsoft.com/l/file/0631A2BC-3CB6-46A3-9D5B-C9B757198300?tenantId=d58addea-5053-4a80-8499-ba4d944910df&fileType=pptx&objectUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA%2FShared%20Documents%2FGeneral%2FTeam%20Meetings%20%2B%20Presentations%2F2020%20June%20Prod-tastic%2FSharable%2C%201st%20Block_%20TDRS%20Prod-tastic%202.0%20Series_%20Product%20Vision%20_%20Roadmap.pptx&baseUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA&serviceName=teams&threadId=19:f769bbcb029f4f02b55ae7fad90e310d@thread.skype&groupId=41f194a6-c1d3-4680-933e-c8ee7d17e287)
* A Product Thinking Framework
* Program Goals
* Product Vision
* Roadmap

[User Types + Personas](https://teams.microsoft.com/l/file/29692124-55FD-4150-B386-0F6DDEBE0CB5?tenantId=d58addea-5053-4a80-8499-ba4d944910df&fileType=pptx&objectUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA%2FShared%20Documents%2FGeneral%2FTeam%20Meetings%20%2B%20Presentations%2F2020%20June%20Prod-tastic%2FSharable%2C%202nd%20Block_%20TDRS%20Prod-tastic%202.0%20Series_%20Design%20Principles%20_%20Personas.pptx&baseUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA&serviceName=teams&threadId=19:f769bbcb029f4f02b55ae7fad90e310d@thread.skype&groupId=41f194a6-c1d3-4680-933e-c8ee7d17e287)
* Design Principles
* What are user types
* Refine our user types

[User Stories + Backlog Prioritization](https://teams.microsoft.com/l/file/8E0D04C5-542D-4337-B01B-B0F6782E03D8?tenantId=d58addea-5053-4a80-8499-ba4d944910df&fileType=pptx&objectUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA%2FShared%20Documents%2FGeneral%2FTeam%20Meetings%20%2B%20Presentations%2F2020%20June%20Prod-tastic%2FSharable%2C%203rd%20Block_%20TDRS%20Prod-tastic%202.0%20Series_%20User%20Stories%20_%20priorization.pptx&baseUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA&serviceName=teams&threadId=19:f769bbcb029f4f02b55ae7fad90e310d@thread.skype&groupId=41f194a6-c1d3-4680-933e-c8ee7d17e287)
* What’s a user story?
* How are user stories developed?
* What makes a good user story?
* How do we estimate effort?
* How do we prioritize them?

[DevOps](https://app.mural.co/t/gsa6/m/gsa6/1593461317883/8e4862ab79e1c566d1a105acef96d1ce6e783885)
* How does a user story become an app in production?
</details>