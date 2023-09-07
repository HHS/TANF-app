# 21. Backend email relay - SendGrid

Date: 2023-08-22

## Status

Accepted

## Context

HHS ITIO has moved to deprecate connections to their SMTP server via IronPort and has required all services to switch to a different email provider as described in this message, received 06/28/2023

> In quick summary we will need you to:
> 1. Establish a relationship with a third-party email service provider
> 2. Generate a DKIM + SPF record from the email service provider for you verified domain identity: @acf.hhs.gov
> 3. Submit DKIM + SPF record to DNS team
> 4. Point your application to the email service provider’s SMTP server(s)
> 5. Test sending email from your @acf.hhs.gov mail from address(es)

* https://github.com/raft-tech/TANF-app/issues/1784#issuecomment-1613321602

Options
* Host an SMTP server
    * Pro: theoretically, we would have more control over our system and security by deploying our own services
    * Con: this comes with a potentially high maintenance cost
    * Con: no cloud.gov provided SMTP infrastructure available
    * Con: SMTP in general is somewhat flaky with low visibility into failures, may be increased effort to debug or add necessary features
* Utilize a third-party SMTP email service
    * Pro: a managed service means less maintenance for our team
    * Con: possibly less secure, as it would be managed by another company on another network
    * Con: same as self-hosted SMTP - flaky, low visibility
* Utilize a third-party, non-SMTP email service
    * Pro: http requests to email provider then email provider handles signing, SMTP relay, retry, analytics, etc; more reliable, more features and visibility compared to SMTP on its own
    * Pro: less maintenance than either SMTP option
    * Con: less system control, dependency on a third party (possible outages, breaking changes)

Any chosen solution must support the signing of emails with DKIM as a method of sender authentication.

## Decision

We will utilize a third-party, non-SMTP email service - [SendGrid](https://sendgrid.com/). SendGrid provides a python library, [`sendgrid-python`](https://github.com/sendgrid/sendgrid-python) that we will implement in a Django `EmailBackend`, allowing a drop-in replacement to the existing `SMTPEmailBackend`. SendGrid also provides more features than similar Email as a Service solutions, such as Amazon Simple Email Service (SES), including deliverability insights and analytics. This allows us to more easily verify and debug issues with email deliverability in production settings.

## Consequences

### Benefits

* Reliable managed email service, less flaky than SMTP
* Increased visibility vs. SMTP - deliverability insights allow us to view whether or not an email was delivered and reason it bounced back, as well as if it has been opened.
* Large feature set - retry, analytics, automation, templates; saves us debugging/implementation time by utilizing a well-used, well-documented service.
* ACF Tech security team assessed SendGrid along the following dimensions and approved its use for TDP:
  - _compliance:_ SendGrid earned the SOC 2 Type II certification, based on rigorous controls to safeguard customer data
  - _data security:_ access to SendGrid system and data is restricted only to to those who need access in order to provide support. All customer data is encrypted in transit via TLS. 
  - _business continuity/disaster recovery:_ SendGrid has separate data centers to support consistent service delivery for customers in the event of an outage 
  - _privacy:_ SendGrid takes appropriate technical and organizational measures to protect the security of users/ PII both online and offline. For reference, SendGrid only accesses TDP user emails. 

### Risks
* Api/library versioning - any breaking changes to the api or python library will have to be prioritized and fixed quickly or risk breaking email notifications for the application.
* Relying on a third party service - outages, service shutoffs, etc. would affect the deliverability of notification emails and security vulnerabilities could affect user privacy.

## Notes

* [link to boundary diagram]()
* [link to technical diagram]()
* [Pro/Con List for SendGrid and Amazon SES](https://hackmd.io/25liUecySPSXOtyiF6YugA)
* [[SPIKE] Backend Email Relay](https://github.com/raft-tech/TANF-app/issues/1784)
