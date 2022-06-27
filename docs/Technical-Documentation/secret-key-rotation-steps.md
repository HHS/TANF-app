# Rotating Secret Keys

## Context

To maintain good security, we will periodically rotate the following secret keys, which are used to control authentication and authorization to our application:
- JWT keys (_external user auth_)
- ACF AMS keys (_internal user auth_)
- Django secret keys ([_cryptographic signing_](https://docs.djangoproject.com/en/4.0/topics/signing/#module-django.core.signing))

This document outlines the process for doing this for each set of keys. 

**Recommendation:** Create a new issue to track key rotation for team awareness.

**Warning(s):** 
- Production sites will need to be taken down for maintenance when rotating keys, as the rotation will automatically invalidate all current sessions.
- As of June 2022, CircleCI supplies environment variable key-value pairs to multiple environments (e.g. Raft's CircleCI deploys applications to dev and staging environments). The values from CircleCI are expected to be unique per environment, so until [#1826](https://github.com/raft-tech/TANF-app/issues/1826) is researched and addressed, these values will need to be manually corrected in cloud.gov immediately following the execution of the [`<env>-deployment` CircleCI workflow](../../.circleci/config.yml). This workaround applies to backend applications in the TDP staging environment. 

## Rotation procedures
**<details><summary>JWT Keys</summary>**

#### The following steps are applicable for **lower environments (dev and staging) _only_**. See [here](#Production-Environment) for prod environment procedure. 
    
### 1. Generate New Keys

In your Mac terminal (or bash terminal in Windows), enter the following command:
```bash=
yes 'XX' | openssl req -nodes -x509 -days 100 -newkey rsa:4096 -keyout jwtRS256prv.pem -out jwtRS256pub.crt
```

You can now check the contents of your keys with these commands
```bash=
cat jwtRS256prv.pem
# returns private key
cat jwtRS256pub.crt
# returns public key
```

### 2. Base64 Encode Private Key

We use Base64 Encoded Private Keys to make it easier to save to cloud environments and local `.env` files.

```bash
openssl enc -base64 -in jwtRS256prv.pem -out jwtRS256prv.pem.base64

cat jwtRS256prv.pem.base64
```

NOTE: Linux users must disable line wrapping by adding the argument `-w 0` to get a properly formatted one-line value.
```bash
cat jwtRS256prv.pem | base64 -w 0 > jwtRS256prv.pem.base64
cat jwtRS256prv.pem.base64
```

### 3. Copy Keys

#### Dev Environments
1. Distribute the private key to development staff securely to copy to `.env` files as the value for key `JWT_KEY`
2. Update the environment variables `JWT_KEY` with the base64-encoded private key and `JWT_CERT`  in cloud.gov backend development and staging environments
```
cf set-env $cgbackendappname JWT_KEY $JWT_KEY_VALUE
cf set-env $cgbackendappname JWT_CERT "$JWT_CERT_VALUE\
> _IS_TYPICALLY_\
>MULTILINE"
```
3. Login to the [Login.gov Sandbox](https://dashboard.int.identitysandbox.gov/) and verify the values are updated across all environments (4 dev + 2 staging)

**Note:** Login.gov requires the key to be uploaded in PEM format, which is the format we produced in the `jwtRS256pub.crt` file.

![pem_upload](https://user-images.githubusercontent.com/1181427/114887693-ae6eef00-9dd6-11eb-98cc-2de3f061337a.png)

#### Staging Environments
**Note** _Please generate a separate set of keys for the staging environments._
The steps here will be the same as development but you will need to generate a separate key-value pair and upload them to the separate app listing in Login.gov's dashboard as linked above.

#### CI/CD Environment
1. Distribute the private key to development staff securely to copy to `.env` 
2. Update the variables `JWT_KEY` and `JWT_CERT_TEST` in CircleCI with the new keypair.

### Production Environment
**Note:** Please generate a separate set of keys for the Production environment.The steps here will be the same as development but you will need to generate a separate key-value pair and upload them to the separate app listing in Login.gov's dashboard as linked above.

Production environment key generation, change requests, and distribution will be handled by Government-authorized personnel with Government computers and PIV access (e.g. TDP sys admins)
1. Copy the private key to cloud.gov backend environment variable `JWT_KEY`
2. Copy the public key to the login.gov production environment
3. _In order for the key change to take effect, a change request must be submitted to the [login.gov support portal](https://logingov.zendesk.com/). These requests can take approx. 2 weeks to be completed._

**References** 
- More information on `openssl` can be found at [openssl.org](https://www.openssl.org/docs/manmaster/man1/openssl.html)
</details>

**<details><summary>ACF AMS Keys</summary>**
The ACF AMS Ops team manages these credentials for all environments (dev, staging, and prod), so we will need to submit a service request ticket whenever we need keys rotated. 

Service requests tickets must be submitted by Government-authorized personnel with Government computers and PIV access (e.g. Raft tech lead for lower environments and TDP sys admins for production environment). Please follow the procedures below:

1. Submit request tickets from government-issued email address and use the email template located on **page 2** of [this document.](https://hhsgov.sharepoint.com/:w:/r/sites/TANFDataPortalOFA/Shared%20Documents/compliance/Authentication%20%26%20Authorization/ACF%20AMS%20docs/OCIO%20OPERATIONS%20REQUEST%20TEMPLATES.docx?d=w5332585c1ecf49a4aeda17674f687154&csf=1&web=1&e=aQyIPz) cc OFA tech lead on lower environment requests. 
2. Update environment variables in CircleCI and relevant cloud.gov backend applications after ticket completed by OCIO. [Restage applications](https://cloud.gov/docs/deployment/app-maintenance/#restaging-your-app).
</details>

**<details><summary>Django secret keys</summary>**

`DJANGO_SECRET_KEY` is dynamically generated since [Issue 967: Dynamically generate DJANGO_SECRET_KEY for initial deployments]([#1151](https://github.com/raft-tech/TANF-app/pull/1151)), so all that needs to be done to rotate this key in any environment is to re-run the relevant environment's deployment workflow in CircleCI. These are as follows:
- dev environment workflow (`dev-deployment`) is run from CircleCI for _raft-tech/TANF-app_. 
- staging environment workflow (`staging-deployment`) is run from CircleCI for _raft-tech/TANF-app_  via `deploy-develop`.
- staging environment workflow  (`staging-deployment`) is run from CircleCI for _HHS/TANF-app_ via `deploy-staging`.
- prod environment workflow (`production-deployment`) is run from CircleCI for _HHS/TANF-app_.     
</details>