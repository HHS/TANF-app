# Security Policy

The TANF Data Portal (TDP) is subject to the
[ACF Privacy Policy](https://www.acf.hhs.gov/privacy-policy) and the
[HHS Vulnerability Disclosure Policy](https://www.hhs.gov/vulnerability-disclosure-policy/index.html).

## Reporting a Vulnerability

Do not report security vulnerabilities through GitHub Issues, pull requests,
discussions, public comments, or unsecured email.

Submit vulnerability reports through the HHS responsible disclosure portal:

[https://hhs.responsibledisclosure.com](https://hhs.responsibledisclosure.com)

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
