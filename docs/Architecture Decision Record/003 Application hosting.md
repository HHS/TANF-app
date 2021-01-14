# 3. Application Hosting
Date: 2020-08-04

## Status

Accepted

## Context
Cloud.gov is a GovCloud-based platform-as-a-service that removes almost all of the infrastructure monitoring and maintenance from the system, is already procured for OFA, and has a FedRAMP Joint Authorization Board Provisional Authority to Operate (JAB P-ATO) on file. FedRAMP is a standardized federal security assessment for cloud services, and the FedRAMP ATO helps agencies by providing confidence in the security of cloud solutions and security assessments. Cloud.gov supports Django rest framework (DRF) and ReactJS.

## Decision

We will use Cloud.gov to host the new TDRS app. 

## Consequences

Inheriting security controls from Cloud.gov will make the ATO process simpler. 
