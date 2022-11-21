# Temporary Assistance for Needy Families (TANF) Data Portal - TDP

Welcome to the project for the New TANF Data Portal, which will replace the legacy TANF Data Reporting System!

Our vision is to build a new, secure, web-based data reporting system to improve the federal reporting experience for TANF grantees and federal staff. The new system will allow grantees to easily submit accurate data and be confident that they have fulfilled their reporting requirements. This will reduce the burden on all users, improve data quality, lead to better policy and program decision-making, and ultimately help low-income families.

---

## Current Build

|| Raft-Tech(develop) |  HHS(main) | HHS(master)
|---|---|---|---|
|**Build**| [![CircleCI-Dev](https://circleci.com/gh/raft-tech/TANF-app/tree/develop.svg?style=shield)](https://circleci.com/gh/raft-tech/TANF-app/tree/develop) | [![CircleCI-HHS](https://circleci.com/gh/HHS/TANF-app/tree/main.svg?style=shield)](https://circleci.com/gh/HHS/TANF-app/tree/main)|[![CircleCI-HHS](https://circleci.com/gh/HHS/TANF-app/tree/master.svg?style=shield)](https://circleci.com/gh/HHS/TANF-app/tree/master)
|**Security**| [Dependabot-Dev](https://github.com/raft-tech/TANF-app/security/dependabot) | [Advisories-HHS](https://github.com/HHS/TANF-app/security/advisories) | [Advisories-HHS](https://github.com/HHS/TANF-app/security/advisories)
|**Frontend Coverage**| [![Codecov-Frontend-Dev](https://codecov.io/gh/raft-tech/TANF-app/branch/develop/graph/badge.svg?flag=dev-frontend)](https://codecov.io/gh/raft-tech/TANF-app?flag=dev-frontend) | [![Codeco-Frontend-HHS](https://codecov.io/gh/HHS/TANF-app/branch/main/graph/badge.svg?flag=main-frontend)](https://codecov.io/gh/HHS/TANF-app?flag=main-frontend)   | [![Codeco-Frontend-HHS](https://codecov.io/gh/HHS/TANF-app/branch/master/graph/badge.svg?flag=master-frontend)](https://codecov.io/gh/HHS/TANF-app?flag=master-frontend) 
|**Backend Coverage**|  [![Codecov-Backend-Dev](https://codecov.io/gh/raft-tech/TANF-app/branch/develop/graph/badge.svg?flag=dev-backend)](https://codecov.io/gh/raft-tech/TANF-app/branch/develop?flag=dev-backend)|   [![Codecov-Backend-HHS]( https://codecov.io/gh/HHS/TANF-app/branch/main/graph/badge.svg?flag=main-backend)](https://codecov.io/gh/HHS/TANF-app/branch/main?flag=main-backend) |  [![Codecov-Backend-HHS]( https://codecov.io/gh/HHS/TANF-app/branch/master/graph/badge.svg?flag=master-backend)](https://codecov.io/gh/HHS/TANF-app/branch/master?flag=master-backend)

*Due to limitations imposed by Github and occasional slow server response times, some badges may require a page refresh to load.*

*TDP is subject to the **[ACF Privacy Policy](https://www.acf.hhs.gov/privacy-policy)** and **[HHS Vulnerability Disclosure Policy](https://www.hhs.gov/vulnerability-disclosure-policy/index.html)***.

---
## Table of Contents

+ **[Background](./docs/Background)**: Project, agency, legacy system, TDP prototype, acquisition, and program background
+ **[Product-Strategy](./docs/Product-Strategy)**: Product Vision, roadmap, and planning
+ **[How-We-Work](./docs/How-We-Work)**: Team composition, sprint schedule, regular meetings, and workflows
+ **[Security-Compliance](./docs/Security-Compliance)**: Supplementary information in support of the ATO process
+ **[Sprint-Review](./docs/Sprint-Review)**: Summaries of delivered stories per sprint
+ **[Technical-Documentation](./docs/Technical-Documentation)**: Architectural Decision Records, System documentation; technical workflows
+ **[User-Experience](./docs/User-Experience)**: Research-related project background, strategy and planning documents, and research syntheses
+ Codebase
  + **[Frontend](./tdrs-frontend)**: Frontend ReactJS codebase
  + **[Backend](./tdrs-backend)**: Backend Django codebase
  + **[Terraform](./terraform)**: Documentation and syntax on CI process for automated provisioning of Cloud.gov brokered services
+ Web-based tools
    + **[Figma](https://www.figma.com/file/irgQPLTrajxCXNiYBTEnMV/TDP-Mockups-For-Feedback):** Design
    + **[MURAL](https://app.mural.co/t/raft2792):** User research and product planning collaboration
    + **[ACF's TDP Sharepoint Site](https://hhsgov.sharepoint.com/sites/TANFDataPortalOFA/Shared%20Documents/Forms/AllItems.aspx)**: File storage, historic chats
    + **[Zenhub](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/board?repos=281707402)**: Tracking issues
    + **[Product Updates](./product-updates)**: communication on project updates and research findings to the broader TDP stakeholders and target users

## Infrastructure

TDP Uses Infrastructure as Code (IaC) and DevSecOps automation

### **Authentication**

TDP application requires strong multi-factor authentication (MFA) for all users, and Personal Identity Verification (PIV) authentication must be used as the 2nd factor for all internal ACF staff. 
**ACF AMS** authentication service is being used for ACF users, and **Login.gov** authentication service is being used for external users. 

See [Architecture Decision Record 005 - Application Authentication](./docs/Technical-Documentation/Architecture-Decision-Record/005-application-authentication.md) - for more details.

### **Cloud Environment**

[Cloud.gov](https://cloud.gov/) is being used as the cloud environment. This platform-as-a-service (PaaS) removes almost all of the infrastructure monitoring and maintenance from the system, is already procured for OFA, and has a FedRAMP Joint Authorization Board Provisional Authority to Operate (JAB P-ATO) on file. 

See [Architecture Decision Record 003 - Application Hosting](./docs/Technical-Documentation/Architecture-Decision-Record/003-Application-hosting.md) - for more details.

### **CI/CD Pipelines with CircleCI**

#### Continuous Integration (CI)

On each git push and merge, a comprehensive list of automated checks are run: Unit tests ([Jest](https://jestjs.io/), Linting tests ([ESLint](https://eslint.org/), Accessibility tests ([Pa11y](https://pa11y.org/)), and Security Scanning ([OWASP ZAP](https://owasp.org/www-project-zap/)). The configurations for CI are generated by [`.circleci/config.yml`](https://github.com/HHS/TANF-app/blob/master/.circleci/config.yml). Circle Ci workflows, jobs, and commands are separated into respective yaml files.

See [Architecture Decision Record 006 - Continuous integration](./docs/Technical-Documentation/Architecture-Decision-Record/006-continuous-integration.md) and [TDP's CircleCi Workflows, Environment Variables, and Builds](./docs/Technical-Documentation/circle-ci.md)- for more details.

#### Continuous Deployment

The application is continuously deployed to the dev, staging, or prod environments based on the git branch the code is merged in. The configuration for different branches is maintained in [`.circleci/config.yml`](./.circleci/config.yml#L107).

See [Architecture Decision Record 008 - Deployment Flow](docs/Technical-Documentation/Architecture-Decision-Record/008-deployment-flow.md) - for more details.

## Points of Contact
| Position |Name | GitHub Username | E-mail |
|--|--|--|--|
| Product Owner |Lauren Frohlich |@lfrohlich |Lauren.Frohlich@acf.hhs.gov|
| Government Technical Monitor |Alex Pennington |@adpennington |Alexandra.Pennington@acf.hhs.gov|
| Vendor Product Manager |Steve Nino |@stevenino |snino@goraft.tech |
