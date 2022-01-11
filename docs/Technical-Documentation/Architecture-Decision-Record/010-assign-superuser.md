# 10. Assigning the Superuser
Date: 2021-02-15 (_Updated 2021-12-28_)

## Status

Accepted

## Context

Usually in Django we would assign the first superuser through the CLI, but because this will not
be available in production, we will need another method.

## Decision

The Django Admin provides the easiest way to assign superuser status, so for most users that will
be the method employed. However, we still need a method for creating the first superuser, so that
user will be able to assign others as needed. We will assign this with a data migration using a 
username defined in environment variables.

## Consequences
Provides a simple way to create superusers, while maintaining proper security by hiding
the username of the first superuser.

## Notes