# 1. Application Architecture
Date: 2021-08-04

## Status

Accepted

## Context

The backend and frontend are two separate apps, the backend is a Django Rest Framework (DRF) app and the frontend is ReactJS. Two apps allow for greater separation between the two components. 

## Decision

The backend and frontend will be two separate apps, the backend a DRF app and the frontend ReactJS.

## Consequences

Two apps allow for greater separation between the two components. This will allow the backend endpoints to exist before the frontend starts work and won't slow the frontend. There will be a main README that will point to two separate backend and frontend READMEs.
