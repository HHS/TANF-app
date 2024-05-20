# 16. Using OWASP Zap Scanner for Application Security Monitoring

Date: 2021-09-09 (_Updated 2021-12-29_)

## Status

Accepted

## Context

To satisfy ATO compliance, we have sought to use OWASP's ZAP security scanner tool to test TDP application security. The tool is free, open-source, and updated and released weekly. Our CI pipeline is configured to run the [ZAP API scan](https://github.com/raft-tech/TANF-app/issues/1367) automatically each time code is committed via GitHub. The pipeline jobs will fail when the scanner finds vulnerabilities marked as FAIL in the ZAP configuration file. This pipeline failure prevents vulnerable code from being deployed.

Recently, the scan results found that we had not set a Content Security Policy (CSP). Upon implementing CSP headers to resolve this, we needed to take a compromise for style-src and utilize "unsafe inline" to allow use of the fedramped library 'uswds' as detailed in [the original ticket](https://github.com/raft-tech/TANF-app/issues/907) and [spike follow-up](https://github.com/raft-tech/TANF-app/issues/1208). 

## Decision

When investigating, we sought out information on what other, modern ACF systems utilizing uswds had done in this situation. [Another team](https://github.com/HHS/Head-Start-TTADP) had simply waived the requirement with the following justification: 

> Weakness Description: Style-src unsafe-inline;: TTAHUB utilize javascript libraries to provide "typeahead search" functionality to filter select box options for end users. These libraries require setting the 'style' attribute on the HTML elements in a way that is incompatible with not including 'style-src: unsafe-inline' in our Content-Security-Policy (CSP) header.
> Remediation Plan: This potential vulnerability is mitigated by utilizing React and JSX for generating HTML. JSX automatically escapes all user-supplied input)[sic] and thus is a compensating control for the CSP header.
> TTAHUB will continue to evaluate options in implementing the typeahead search ro see if one is developed that does not require the use of style attributes.

While we also investigated and developed technical solutions utilizing either React-app-rewired or Next.js, we decided that the departure from our existing stack was not a worthwhile investment and could lead to other complications down the road.

### 2024 Update

Another instance of this alert appeared in the Webinspect scans for January/February 2024, after the introduction of Kibana to our stack

`HTML5: Misconfigured Content Security Policy` - `Recommendation: Remove the unsafe-eval and unsafe-inline values from the CSP directive values.`

Referring to the following directives in our nginx config
```
set $CSP "${CSP}script-src 'self' 'unsafe-eval' 'unsafe-inline' http://{{env "KIBANA_BASE_URL"}}:5601;";
set $CSP "${CSP}script-src-elem 'self' 'unsafe-inline' http://{{env "KIBANA_BASE_URL"}}:5601;";
set $CSP "${CSP}script-src-attr 'self' 'unsafe-inline' http://{{env "KIBANA_BASE_URL"}}:5601;";
```

Kibana performs ajax requests from its frontend to scripts hosted on the server in order to provide styling and javascript functionality - in order to serve Kibana from behind a proxy, which is a requirement with cloud.gov, these `unsafe-inline` and `unsafe-eval` directives are required.
We currently use Kibana version 7.4 [released October, 2019](https://www.elastic.co/blog/kibana-7-4-0-released). This requirement is present in our current version as mentioned by the Elastic team in
* [elastic/kibana #27047](https://github.com/elastic/kibana/issues/27047#issuecomment-799680263) in March 2021
* an [elastic discussion post](https://discuss.elastic.co/t/does-kibana-need-the-autorisation-of-unsafe-inline-or-unsafe-eval-to-work-properly/234390/2) in May 2020

The CSP exceptions are fairly low risk as they are limited to artifacts within the Kibana domain.

## Consequences

Unsafe-inline will continue to be used in our 'react-scripts' frontend framework but we will waive this ZAP alert for both frontend and backend as it is an already mitigated vulnerability within our current stack and the attack vector is small. For verbosity, the attack vector is for vetted, approved users potentially targetting other system users for account credentials or privilege escalation using XSS against inline style sheets.

## Notes
