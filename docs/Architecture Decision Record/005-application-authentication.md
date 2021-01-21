# 5. Application Authentication
Date: 2020-08-04

## Status

Accepted. 

Note: We are evaluating NextGen XMS for user authentication. New ADR will be added when decision is made to replace login.gov with NextGen XMS.  

## Context

TDP application requires strong multi-factor authentication for the states, tribes, and territories and Personal Identity Verification (PIV) authentication for OFA staff. Login.gov can meet both of these requirements and HHS already has an IAA for this service. Login.gov has a FedRAMP ATO on file.

## Decision

We will use login.gov for authentication.

## Consequences
Inheriting security controls from Login.gov will make the ATO process simpler.
