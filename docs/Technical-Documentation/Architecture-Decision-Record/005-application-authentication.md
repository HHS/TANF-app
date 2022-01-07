# 5. Application Authentication

Date: 2020-08-04 (_Updated 2021-12-27_)

## Status

Accepted. 

## Context

TDP application requires strong multi-factor authentication (MFA) for all users, and Personal Identity Verification (PIV) authentication must be used as the 2nd factor for all internal ACF staff. To date, TDP has been leveraging Login.gov authentication for all users because (1) it requires MFA for all user accounts by default and accepts PIV for authentication, (2) it has a FedRAMP ATO on file, and (3) HHS already has an IAA for this service. 

Since then, ACF OCIO (TDP's Authorizing Official) has recommended use of HHS-vetted authentication services for both internal ACF and external (i.e.non-ACF) users.

## Decision

We will use [ACF AMS](https://hhsgov.sharepoint.com/:w:/s/TANFDataPortalOFA/EYsh4YvAE0hLrr_rVhYKsGABgeA_yuHzt-v7TGbxaBF2jA?e=zriBjY) authentication service for ACF users and [NextGen XMS](https://hhsgov.sharepoint.com/:f:/s/TANFDataPortalOFA/EpDotsWsib1DgLradoN-m0oB8jWPsNswjLZJqeOc3gU_ZQ?e=16f4mF) authentication service for all non-ACF users.

## Consequences

**Benefits** 
- NextGen XMS leverages Login.gov for authentication, so refactoring should be minimal. Additionally, we expect maintain the inherited security controls from Login.gov.
- ACF users will not need to sign up for additional user account credentials, since their default ACF (PIV) credentials will be accepted by ACF AMS for authentication. 
- Over the longer term, the costs for leveraging these authentication services may be shared with other ACF program offices who leverage these services. 

**Risks**
- TDP will be one of the first ACF-authorized systems to use both _relatively new_ authentication services, and documentation provided to-date is minimal. So it is likely to take time to develop/refine a support structure to help us to identify and resolve root causes of issues if the need arises. This will also likely impact (at least temporarily) the product timeline and implementation of other TDP features. 

## Notes
