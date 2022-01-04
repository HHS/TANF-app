# Temporary Assistance for Needy Families (TANF) Data Portal - TDP

Welcome to the project for the New TANF Data Portal, which will replace the legacy TANF Data Reporting System!

Our vision is to build a new, secure, web-based data reporting system to improve the federal reporting experience for TANF grantees and federal staff. The new system will allow grantees to easily submit accurate data and be confident that they have fulfilled their reporting requirements. This will reduce the burden on all users, improve data quality, lead to better policy and program decision-making, and ultimately help low-income families.

## Current Build

|| Raft-Tech(raft-tdp-main) |  HHS(main) |
|---|---|---|
|**Build**| [![CircleCI-Dev](https://circleci.com/gh/raft-tech/TANF-app/tree/raft-tdp-main.svg?style=shield)](https://circleci.com/gh/raft-tech/TANF-app/tree/raft-tdp-main) | [![CircleCI-HHS](https://circleci.com/gh/HHS/TANF-app/tree/main.svg?style=shield)](https://circleci.com/gh/HHS/TANF-app/tree/main)|
|**Security**| [Dependabot-Dev](https://github.com/raft-tech/TANF-app/security/dependabot) | [Advisories-HHS](https://github.com/HHS/TANF-app/security/advisories) |
|**Frontend Coverage**| [![Codecov-Frontend-Dev](https://codecov.io/gh/raft-tech/TANF-app/branch/raft-tdp-main/graph/badge.svg?flag=dev-frontend)](https://codecov.io/gh/raft-tech/TANF-app?flag=dev-frontend) | [![Codeco-Frontend-HHS](https://codecov.io/gh/HHS/TANF-app/branch/main/graph/badge.svg?flag=main-frontend)](https://codecov.io/gh/HHS/TANF-app?flag=main-frontend)   |
|**Backend Coverage**|  [![Codecov-Backend-Dev](https://codecov.io/gh/raft-tech/TANF-app/branch/raft-tdp-main/graph/badge.svg?flag=dev-backend)](https://codecov.io/gh/raft-tech/TANF-app/branch/raft-tdp-main?flag=dev-backend)|   [![Codecov-Backend-HHS]( https://codecov.io/gh/HHS/TANF-app/branch/main/graph/badge.svg?flag=main-backend)](https://codecov.io/gh/HHS/TANF-app/branch/main?flag=main-backend) |

*Due to limitations imposed by Github and occasional slow server response times, some badges may require a page refresh to load.*

# Table of Contents

+ **[Background](./docs/Background)**: Project, agency, legacy system, TDP prototype, acquisition, and program background
+ **[Product-Strategy](./Product-Strategy)**: Product Vision, roadmap, and planning
+ **[How-We-Work](./docs/How-We-Work)**: Team composition, sprint schedule, regular meetings, and workflows
+ **[Security-Compliance](./Security-Compliance)**: Supplementary information in support of the ATO process
+ **[Sprint-Review](./docs/Sprint-Review)**: Summaries of delivered stories per sprint
+ **[Technical-Documentation](./docs/Technical-Documentation)**: Architectural Decision Records, System documentation; technical workflows
+ **[User-Experience](./docs/User-Experience)**: Research-related project background, strategy and planning documents, and research syntheses
+ **[Frontend](./tdrs-frontend)**: Frontend ReactJS codebase
+ **[Backend](./tdrs-backend)**: Django codebase for backend
+ Web-based tools
    + **[Figma]():** Design
    + **[MURAL](https://app.mural.co/t/raft2792):** User research and product planning collabortation
    + **[HHS Teams]()**: File storage, historic chats
    + **[Zenhub]()**: Tracking issues

## Infrastructure

TDP Uses Infrastructure as Code (IaC) and DevSecOps automation

### Authentication

TDP application requires strong multi-factor authentication (MFA) for all users, and Personal Identity Verification (PIV) authentication must be used as the 2nd factor for all internal ACF staff. 
[ACF AMS]() authentication service is being used for ACF users, and [NextGen XMS]() authentication service is being used for external users. 

See [Architecture Decision Record 005 - Application Authentication](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/docs/Technical-Documentation/Architecture-Decision-Record/005-application-authentication.md) - for more details.

### Cloud Environment

[Cloud.gov](https://cloud.gov/) is being used as the cloud environment. This platform-as-a-service (PaaS) removes almost all of the infrastructure monitoring and maintenance from the system, is already procured for OFA, and has a FedRAMP Joint Authorization Board Provisional Authority to Operate (JAB P-ATO) on file. 

See [Architecture Decision Record 003 - Application Hosting](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/docs/Technical-Documentation/Architecture-Decision-Record/003-Application-hosting) - for more details.
### CI/CD Pipelines with CircleCI

#### Continuous Integration (CI)

On each git push and merge, a comprehensive list of automated checks are run: Unit tests ([Jest](https://jestjs.io/), Linting tests ([ESLint](https://eslint.org/), Accessibility tests ([Pa11y](https://pa11y.org/)), and Security Scanning ([OWASP ZAP](https://owasp.org/www-project-zap/)). The configurations for CI are kept in [`.circleci/config.yml`](https://github.com/HHS/TANF-app/blob/main/.circleci/config.yml). 

See [Architecture Decision Record 006 - Continuous integration](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/docs/Technical-Documentation/Architecture-Decision-Record/006-continuous-integration.md) and [TDP's CircleCi Workflows, Environment Variables, and Builds](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/docs/Technical-Documentation/circle-ci.md)- for more details.

#### Continuous Deployment

The application is continuously deployed to the dev, staging, or prod environments based on the git branch the code is merged in. The configuration for different branches is maintained in [`.circleci/config.yml`](https://github.com/HHS/TANF-app/blob/main/.circleci/config.yml#L107).

See [Architecture Decision Record 008 - Deployment Flow](docs/Technical-Documentation/Architecture-Decision-Record/008-deployment-flow.md) - for more details.

## Points of Contact
| Position |Name | GitHub Username | E-mail |
|--|--|--|--|
| Product Owner |Lauren Frohlich |@lfrohlich |Lauren.Frohlich@acf.hhs.gov|
| Government Technical Monitor |Alex Pennington |@adpennington |Alexandra.Pennington@acf.hhs.gov|
| Vendor Project Manager |Valerie Collignon |@valcollignon |vcollignon@goraft.tech |