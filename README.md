# Temporary Assistance for Needy Families (TANF) Data Portal - TDP

|| Raft-Tech(raft-tdp-main) |  HHS(main) |
|---|---|---|
|**Build**| [![CircleCI-Dev](https://circleci.com/gh/raft-tech/TANF-app/tree/raft-tdp-main.svg?style=shield)](https://circleci.com/gh/raft-tech/TANF-app/tree/raft-tdp-main) | [![CircleCI-HHS](https://circleci.com/gh/HHS/TANF-app/tree/main.svg?style=shield)](https://circleci.com/gh/HHS/TANF-app/tree/main)|
|**Security Frontend**| [![Security-Frontend-Dev](https://snyk.io/test/github/raft-tech/TANF-app/badge.svg)](https://snyk.io/test/github/raft-tech/TANF-app)  | [![Security-Frontend-HHS](https://snyk.io/test/github/HHS/TANF-app/badge.svg)](https://snyk.io/test/github/HHS/TANF-app)|
|**Security Backend**| [![Security-Backend-Dev](https://snyk.io/test/github/raft-tech/TANF-app/badge.svg?targetFile=tdrs-backend/requirements.txt)](https://snyk.io/test/github/raft-tech/TANF-app) | [![Security-Backend-HHS](https://snyk.io/test/github/HHS/TANF-app/badge.svg?targetFile=tdrs-backend/requirements.txt)](https://snyk.io/test/github/HHS/TANF-app)
|**Frontend Coverage**| [![Codecov-Frontend-Dev](https://codecov.io/gh/raft-tech/TANF-app/branch/raft-tdp-main/graph/badge.svg?flag=dev-frontend)](https://codecov.io/gh/raft-tech/TANF-app?flag=dev-frontend) | [![Codeco-Frontend-HHS](https://codecov.io/gh/HHS/TANF-app/branch/main/graph/badge.svg?flag=main-frontend)](https://codecov.io/gh/HHS/TANF-app?flag=main-frontend)   |
|**Backend Coverage**|  [![Codecov-Backend-Dev](https://codecov.io/gh/raft-tech/TANF-app/branch/raft-tdp-main/graph/badge.svg?flag=dev-backend)](https://codecov.io/gh/raft-tech/TANF-app/branch/raft-tdp-main?flag=dev-backend)|   [![Codecov-Backend-HHS]( https://codecov.io/gh/HHS/TANF-app/branch/main/graph/badge.svg?flag=main-backend)](https://codecov.io/gh/HHS/TANF-app/branch/main?flag=main-backend) |

**Due to limitations imposed by Github and occasional slow server response times, some badges may require a page refresh to load.**

## Office of Family Assistance (OFA) & Temporary Assistance for Needy Families (TANF) Data Portal.

Welcome to the home of the TANF Data Portal (TDP), a new software development project from the Office of Family Assistance (OFA), an office within the Administration for Children Families (ACF).

## What We're Building and Why

- [Product planning page]( https://github.com/HHS/TANF-app/blob/main/docs/README.md) includes latest information on our product mission, goals, roadmap, and backlog. 

## Getting Started

### Running the Application locally

Both the frontend (`http://localhost:3000`) and the backend (`http://localhost:8080`) applications run within Docker.  Instructions for running these containers are below:

```
$ cd tdrs-frontend && docker-compose up -d
$ cd tdrs-backend && docker-compose -f docker-compose.yml -f docker-compose.local.yml up -d 
```

After the above commands there will be a total of 5 running containers

```
CONTAINER ID        IMAGE                        COMMAND                  CREATED             STATUS                            PORTS                    NAMES
c803336c1f61        tdp                          "bash -c 'python wai…"   3 seconds ago       Up 3 seconds                      0.0.0.0:8080->8080/tcp   tdrs-backend_web_1
20912a347e00        postgres:11.6                "docker-entrypoint.s…"   4 seconds ago       Up 3 seconds                      5432/tcp                 tdrs-backend_postgres_1
9c3e6c2a88b0        owasp/zap2docker-weekly      "sleep 3600"             4 seconds ago       Up 3 seconds (health: starting)                            tdrs-backend_zaproxy_1
7fa018dc68d1        owasp/zap2docker-stable      "sleep 3600"             41 seconds ago      Up 40 seconds (unhealthy)         0.0.0.0:8090->8090/tcp   zap-scan
63f6da197629        tdrs-frontend_tdp-frontend   "/docker-entrypoint.…"   41 seconds ago      Up 40 seconds                     0.0.0.0:3000->80/tcp     tdp-ui
```

Below is a GIF of both the frontend and backend running locally

![GIF of frontend and backend running locally](https://user-images.githubusercontent.com/44377678/104548466-e1022380-55fe-11eb-9a7b-eea7cda395d4.gif)

Detailed instructions for running unit and end-to-end integration testing on frontend and backend are available below

- [Frontend](https://github.com/HHS/TANF-app/tree/main/tdrs-frontend)
- [Backend](https://github.com/HHS/TANF-app/tree/main/tdrs-backend)


## Infrastructure

TDP Uses Infrastructure as Code (IaC) and DevSecOps automation

### Authentication

[Login.gov](https://login.gov/) TDP requires strong multi-factor authentication for the states, tribes, and territories and Personal Identity Verification (PIV) authentication for OFA staff. Login.gov is being used to meet both of these requirements. 

### Cloud Environment

[Cloud.gov](https://cloud.gov/) is being used as the cloud environment. This platform-as-a-service (PaaS) removes almost all of the infrastructure monitoring and maintenance from the system, is already procured for OFA, and has a FedRAMP Joint Authorization Board Provisional Authority to Operate (JAB P-ATO) on file. 

## CI/CD Pipelines with CircleCI

### Continuous Integration (CI)

On each git push and merge, a comprehensive list of automated checks are run: Unit tests ([Jest](https://jestjs.io/), [Cypress](https://www.cypress.io/)), Integration tests (Cypress), Linting tests ([ESLint](https://eslint.org/) and [Black](https://black.readthedocs.io/en/stable/)), Accessibility tests ([Pa11y](https://pa11y.org/)), and Security Scanning ([OWASP ZAP](https://owasp.org/www-project-zap/)). The configurations for CI are kept in [`.circleci/config.yml`](https://github.com/HHS/TANF-app/blob/main/.circleci/config.yml). 

### Continuous Deployment

The application is continuously deployed to the dev, staging, or prod environments based on the git branch the code is merged in. The configuration for different branches is maintained in [`.circleci/config.yml`](https://github.com/HHS/TANF-app/blob/main/.circleci/config.yml#L107). The application is deployed to the following environments:

Environment | URL | Git Branch
------------|----|-------------
Development | https://tdp-frontend.app.cloud.gov/ | [`raft-tdp-main`](https://github.com/raft-tech/TANF-app) in Raft fork
Staging | TBD | [`main`](https://github.com/HHS/TANF-app) in HHS
Production | TBD | `production` in HHS





