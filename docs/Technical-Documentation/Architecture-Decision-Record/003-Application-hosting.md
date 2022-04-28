# 3. Application Hosting
Date: 2020-08-04 (_updated 2021-12-20_)

## Status

Accepted

## Context
OFA has two options for application hosting for TDP: ACF AWS and Cloud.gov. ACF AWS offers infrastructure-as-a-service (IaaS) and is to being managed by ACF OCIO, with direct operational support via AWS. As of Summer 2020, ACF AWS is not yet in a mature state. Cloud.gov is a GovCloud-based platform-as-a-service (PaaS) that removes almost all of the infrastructure monitoring and maintenance from the system, is already procured for OFA, and has a FedRAMP Joint Authorization Board Provisional Authority to Operate (JAB P-ATO) on file. FedRAMP is a standardized federal security assessment for cloud services, and the FedRAMP ATO helps agencies by providing confidence in the security of cloud solutions and security assessments. Cloud.gov supports Django rest framework (DRF) and ReactJS, which make up TDP's backend and frontend application architecture, respectively.

## Decision

We will use Cloud.gov to host the new TDP app. 

## Consequences

### Benefits 
 - Inheriting security controls from Cloud.gov will make the ATO process simpler. 
 - Less infrastructure for OFA and its vendor to maintain (time/cost savings)
 - Instant provisioning of services (e.g. S3, ElasticSearch, RDS, load balancers, URL routers), environments, and easy deployment. 


### Risks
 - Maintaining compliance with any new security standards (e.g. [White House Cybersecurity Executive Order 14208](https://github.com/raft-tech/TANF-app/blob/develop/docs/Security-Compliance/WH_CybersecurityEO.md#white-house-cybersecurity-executive-order-14208) enforced by ACF OCIO may take time and coordination with cloud.gov. 
 

## Notes
- May consider revisiting this decision once ACF AWS is in a more mature state with a wider user base. 