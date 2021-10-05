# 3. Application Hosting
Date: 2020-08-04 (Updated 2021-10-05)

## Status

Accepted

## Context
Cloud.gov is a GovCloud-based platform-as-a-service that removes almost all of the infrastructure monitoring and maintenance from the system, is already procured for OFA, and has a FedRAMP Joint Authorization Board Provisional Authority to Operate (JAB P-ATO) on file. FedRAMP is a standardized federal security assessment for cloud services, and the FedRAMP ATO helps agencies by providing confidence in the security of cloud solutions and security assessments. Cloud.gov supports Django rest framework (DRF) and ReactJS.

## Decision

We will use Cloud.gov to host the new TDRS app. 

## Consequences

Inheriting security controls from Cloud.gov will make the ATO process simpler. 

## Addendum

We will be using the tool [Terraform as outlined in ADR 17](./017-terraform-service-provisioning.md) to manage users and roles within Cloud.gov permission schema. This will centralize management and facilitate [rotating django secret key with user offoboarding](https://www.github.com/raft-tech/TANF-app/issues/1362). Two consequences of managing users this way is that 1) the service account will be the primary vehicle for administration and 2) that control of cloud.gov will live in our repo and not in the administration pages of Cloud.gov itself.
