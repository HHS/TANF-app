# Security Policy

The TANF Data Portal (TDP) is subject to the
[ACF Privacy Policy](https://www.acf.hhs.gov/privacy-policy) and the
[HHS Vulnerability Disclosure Policy](https://www.hhs.gov/vulnerability-disclosure-policy/index.html).

## Reporting a Vulnerability

Active development takes place in [raft-tech/TANF-app](https://github.com/raft-tech/TANF-app).
The private reporting process below applies to vulnerabilities found in either
`HHS/TANF-app` or `raft-tech/TANF-app` and related TDP systems.

Do not report security vulnerabilities through GitHub Issues, pull requests,
discussions, or public comments.

Submit vulnerability reports through the HHS responsible disclosure portal:

[https://hhs.responsibledisclosure.com](https://hhs.responsibledisclosure.com)

Reports submitted to the portal must mention **ACF TANF Data Portal (TDP)**
so they can be routed to the appropriate team. After submitting through the
portal, send a copy of the submission by email to both
[tanfdata@acf.hhs.gov](mailto:tanfdata@acf.hhs.gov) and
[tdp-devs@teamraft.com](mailto:tdp-devs@teamraft.com). Include both addresses
whenever contacting the repository owners about a security vulnerability.
The email copy does not replace the required portal submission.

Reports may be submitted anonymously. The HHS Vulnerability Disclosure Policy
describes eligible systems, authorized research, reporting requirements,
disclosure timelines, and researcher expectations.

If you believe you have found a vulnerability involving live TDP environments,
production data, credentials, tokens, personally identifiable information, or
other sensitive information, stop testing and report it through the HHS
responsible disclosure portal as soon as possible.

## Scope

Security reports for this repository and related TDP systems are governed by the
HHS Vulnerability Disclosure Policy. Review that policy before testing to confirm
which systems and research activities are authorized.

This repository also contains project security and compliance documentation in
[docs/Security-Compliance](./docs/Security-Compliance).

## Supported Branches

Security fixes are applied to branches and deployed environments that are
actively maintained by the TDP team. Historical, archived, or otherwise
unmaintained branches may not receive security updates.

## Contributor Guidance

Do not commit secrets, credentials, private keys, access tokens, production data,
or personally identifiable information to this repository.

If sensitive information is accidentally exposed, report it through the HHS
responsible disclosure portal and follow the project's incident response
documentation, including
[Secret Key Management](./docs/Security-Compliance/Incidence-Response/Secret-Key-Mgmt.md)
where applicable.

TDP uses automated checks, dependency monitoring, and security scanning as part
of the development workflow. See the project
[README](./README.md), [CONTRIBUTING](./CONTRIBUTING.md), and
[Security & Compliance Documentation](./docs/Security-Compliance) for additional
context.
