# Rotating Secret Keys

## Context

To maintain good security, we will periodically rotate the following secret keys, which are used to control authentication and authorization to our application:
- JWT keys 

This document outlines the process of how to do this.

**Warning** Production sites will need to be taken down for maintenance when rotating keys, as the rotation will automatically invalidate all current sessions.

## Rotation procedure
**<summary>JWT Keys</summary>**
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

Note: Login.gov requires the key to be uploaded in PEM format, which is the format we produced in the `jwtRS256pub.crt` file.

![pem_upload](https://user-images.githubusercontent.com/1181427/114887693-ae6eef00-9dd6-11eb-98cc-2de3f061337a.png)

#### Staging Environments
**Note** _Please generate a separate set of keys for the Staging environments_
The steps here will be the same as development but you will need to generate a separate keypair and upload them to the separate app listing in Login.gov's dashboard as linked above.

#### CI/CD Environment
1. Distribute the private key to development staff securely to copy to `.env` 
2. Update the variables `JWT_KEY` and `JWT_CERT_TEST` in CircleCI with the new keypair.

#### Production Environment
**Note** _Please generate a separate set of keys for the Production environment_

Production environment key distribution will be handled by Government authorized personnel with Government computers and PIV access.
1. Copy the private key to cloud.gov backend environment variable `JWT_KEY`
2. Copy the public key to the login.gov production environment

**Note** 
- More information on `openssl` can be found at [openssl.org](https://www.openssl.org/docs/manmaster/man1/openssl.html)
