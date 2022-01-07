# 15. Adding Terraform to CI Pipeline for Automated Service Provisioning

Date: 2021-06-30 (_Updated 2021-12-29_)  
  
## Status  
  
Accepted
  
## Context

In [this issue](https://github.com/raft-tech/TANF-app/issues/609) we propose tasks to automate the provisioning of Cloud.gov-brokered services via our CI pipeline.

This project plans to use Cloud.gov-brokered S3 buckets for TANF data file storage (sensitive PII data) and for Django Admin static assets (public), and a Cloud.gov-brokered RDS PostgreSQL service. Currently, there are no scripts to provision and secure these S3 buckets and RDS instance, and no dev documentation on how to deploy them, secure them, and verify that they are configured correctly. Additionally, this same initial provisioning must be done again for all additional target environments.
  
## Proposed Decision  

[Terraform](https://www.terraform.io/) is a tool for building, changing, and versioning infrastructure safely and efficiently, and was proposed as a solution for managing our persistent Cloud.gov-brokered infrastructure. We can closely model what is done in [another HHS project](https://github.com/HHS/Head-Start-TTADP) and create per-environment infrastructure configurations which are leveraged by Terraform in CircleCI, with environment-specific settings read directly from Cloud.gov during our CI process. Note that this workflow was a [recommendation from Cloud.gov](https://www.youtube.com/watch?v=86wfgNK_0o4), and they themselves use Terraform to provision their own infrastructure.

## Consequences  
  
- Need to maintain Terraform config (`main.tf`) and variable declarations (`variables.tf`) per-environment.
- Need to install Terraform in our CI pipeline and configure it for every target environment.
  
**Benefits**
- Versioning of configuration changes for infrastructure
- Codifies our application infrastructure, reducing human error by provisioning infrastructure as code.
- Automates the provisioning of reproducible infrastructure across environments.
- Capability provisioning infrastructure locally via scripts that closely resemble what is done in CI.
  
**Risks** 
- (Minor) There is an initial need to set up the Terraform State S3 bucket, making this the one piece of persistent infrastructure whose provisioning cannot be automated. 

## Notes
