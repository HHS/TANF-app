# 1. Record architecture decisions

Date: 2021-09-09 (yyyy-mm-dd)

## Status

Accepted

## Context

To satisfy ATO compliance we have sought to used OWASP's ZAP security scanner tool which displayed that we had not set a Content Security Policy (CSP). Upon implementing CSP headers to resolve this, we needed to take a compromise for style-src and utilize "unsafe inline" to allow use of the fedramped library 'uswds' as detailed in [the original ticket](https://github.com/raft-tech/TANF-app/issues/907) and [spike follow-up](https://github.com/raft-tech/TANF-app/issues/1208). 

## Decision

When investigating, we sought out information on what other agencies utilizing uswds had done in this situation. Another team had simply waived the requirement with the following justification: 

> Weakness Description: Style-src unsafe-inline;: TTAHUB utilize javascript libraries to provide "typeahead search" functionality to filter select box options for end users. These libraries require setting the 'style' attribute on the HTML elements in a way that is incompatible with not including 'style-src: unsafe-inline' in our Content-Security-Policy (CSP) header.
> Remediation Plan: This potential vulnerability is mitigated by utilizing React and JSX for generating HTML. JSX automatically escapes all user-supplied input)[sic] and thus is a compensating control for the CSP header.
> TTAHUB will continue to evaluate options in implementing the typeahead search ro see if one is developed that does not require the use of style attributes.

While we also investigated and developed technical solutions utilizing either React-app-rewired or Next.js, we felt that the departure from our existing stack was not a worthwhile investment and could lead to other complications down the road.

## Consequences
Unsafe-inline will continue to be used in our 'react-scripts' frontend framework but we will waive this ZAP alert for both frontend and backend as it is an already mitigated vulnerability within our current stack and the attack vector is small. For verbosity, the attack vector is for vetted, approved users potentially targetting other system users for account credentials or privilege escalation using XSS against inline style sheets.
