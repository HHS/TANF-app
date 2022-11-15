# 5. Application Authentication

Date: 2020-08-04 (_Updated 2022-09-01_)

## Status

Accepted. 

## Context

TDP application requires strong multi-factor authentication (MFA) for all users, and Personal Identity Verification (PIV) authentication must be used as the 2nd factor for all internal ACF staff. To date, TDP has been leveraging Login.gov authentication for all users because (1) it requires MFA for all user accounts by default and accepts PIV for authentication, (2) it has a FedRAMP ATO on file, and (3) HHS already has an IAA for this service. 

Since then, ACF OCIO (TDP's Authorizing Official) has recommended use of HHS-vetted authentication services for both internal ACF and external (i.e.non-ACF) users.

We initiated the integratation with NextGen XMS for external users in Spring 2022 because of the estimated cost savings, and because the refactoring was expected to be minimal (since NextGen leverages login.gov as one of its credential service providers). However, the time/effort to integrate with this newer service led to significant roadmap delays.  

## Decision

We will use [ACF AMS](https://hhsgov.sharepoint.com/:w:/s/TANFDataPortalOFA/EYsh4YvAE0hLrr_rVhYKsGABgeA_yuHzt-v7TGbxaBF2jA?e=zriBjY) authentication service for ACF users and [Login.gov](login.gov) authentication service for all non-ACF users.

## Consequences

**Benefits** 
- ACF users will not need to sign up for additional user account credentials, since their default ACF (PIV) credentials will be accepted by ACF AMS for authentication. 
- Over the longer term, the costs for leveraging these authentication services may be shared with other ACF program offices who leverage these services. 

**Risks**
- The NextGen integration attempt uncovered questions about the extent to which our codebase can be easily adapted if ever it becomes necessary to consider alternative CSPs (e.g. ID.me). 

## Notes
