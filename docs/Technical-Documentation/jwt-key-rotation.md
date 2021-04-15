# Rotating JWT Keys

## Context

To maintain good security, we will periodically rotate our JWT keys. This document outlines the process of how to do this.

**Warning** Production sites will need to be taken down for maintenance when rotating keys, as the rotation will automatically invalidate all current sessions.

### 1. Generate New Keys

In your Mac terminal (or bash terminal in Windows), enter the following command:
```bash=
ssh-keygen -t rsa -b 4096 -m PEM -f jwtRS256.key
```
You will receive the following response. Do not add a passphrase when prompted.
```
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in jwtRS256.key
Your public key has been saved in jwtRS256.key.pub
The key fingerprint is:
# returns key fingerprint
The key's randmart image is:
# returns key's randmart image
```
Then enter
```bash=
openssl rsa -in jwtRS256.key -pubout -outform PEM -out jwtRS256.key.pub
```

You can now check the contents of your keys with these commands
```bash=
cat jwtRS256.key
# returns private key
cat jwtRS256.key.pub
# returns public key
```

### 2. Base64 Encode Private Key

We use Base64 Encoded Private Keys to make it easier to save to cloud environments and local `.env` files.

```bash=
openssl enc -base64 -w 0 -in jwtRS256.key -out jwtRS256.key.base64
cat jwtRS256.key.base64
```

### 3. Copy Keys

#### Dev/Staging Environments
1. Distribute the private key to development staff securely to copy to `.env` files as the value for key `JWT_KEY`
2. Update the environment variable `JWT_KEY` with the private key in cloud.gov backend development and staging environments
3. Login to the [Login.gov Sandbox](https://dashboard.int.identitysandbox.gov/) and update the public key there

Note: Login.gov requires the key to be uploaded in PEM format, which is the format we produced in the `jwtRS256.key.pub` file.

![pem_upload](https://user-images.githubusercontent.com/1181427/114887693-ae6eef00-9dd6-11eb-98cc-2de3f061337a.png)

#### CI/CD Environment
**Note** _Please generate a separate set of keys for the CI/CD environment_
1. Distribute the private key to development staff securely to copy to `.env` files as the value for key `JWT_CERT_TEST`
2. Update the variable `JWT_KEY_TEST` in CircleCI with the new public key.

#### Production Environment
**Note** _Please generate a separate set of keys for the Production environment_

Production environment key distribution will be handled by Government authorized personnel with Government computers and PIV access.
1. Copy the private key to cloud.gov backend environment variable `JWT_KEY`
2. Copy the public key to the login.gov production environment

**Note** 
- We will need to update this document with the link to login to the login.gov production environment setup when we have access to it.
- More information on `ssh-keygen` can be found at [ssh.com](https://www.ssh.com/academy/ssh/keygen)
- More information on `openssl` can be found at [openssl.org](https://www.openssl.org/docs/manmaster/man1/openssl.html)
