# 2. Application Architecture
Date: 2020-08-04 (Updated 2021-12-20)

## Status

Accepted

## Context
When designing the solution, we needed to establish our technology stack best suited for the solution.

## Decision

For TANF Data Portal, the team decided that the backend shall be  Django Rest Framework (DRF) app and the frontend is ReactJS. 

## Consequences

Two apps allow for greater separation between the two components. This will allow the backend endpoints to exist before the frontend starts work and won't slow the frontend. There will be a main README that will point to two separate backend and frontend READMEs.

## Notes
