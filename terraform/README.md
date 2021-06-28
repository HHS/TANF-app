# Terraform

These docs are verbose because this is technology with which developers will rarely interact. I suggest you read them entirely before attempting to run any listed commands.

## Prior Art

### Persistent vs Ephemeral Infrastructure
Adapted from: <https://github.com/HHS/Head-Start-TTADP#persistent-vs-ephemeral-infrastructure>

**The infrastructure used to run this application can be categorized into two distinct types: _ephemeral_ and _persistent_**

* **Ephemeral infrastructure** is all the infrastructure that is recreated each time the application deploys. Ephemeral infrastructure includes the "application(s)" (as defined in Cloud.gov), the EC2 instances the application runs on, and the routes that application utilizes. Our CircleCI configuration describes this infrastructure and deploys it to Cloud.gov.
* **Persistent infrastructure** is all the infrastructure that remains constant and unchanged despite application deployments. Persistent infrastructure includes the database used in each development environment. Our Terraform configuration files describe this infrastructure and instantiates it on Cloud.gov.

> This concept is often referred to as _mutable_ vs _immutable_ infrastructure.

### Infrastructure as Code

A high-level configuration syntax, called [Terraform language][language], describes our infrastructure. This allows a blueprint of our system to be versioned and treated as we do any other code. This configuration can be acted on locally by a developer if deployments need to be created manually, but it is mostly and ideally executed by CircleCI.

###  Terraform workflow

Terraform integrates into our CircleCI pipeline via the [Terraform orb][orb], and is formally described in our `deploy-infrastructure` CircleCI job. Upon validating its configuration, Terraform reads the current state of any already-existing remote objects to make sure that the Terraform state is up-to-date, and compares the current configuration to the prior state, noting all differences. Terraform creates a "plan" and proposes a set of change actions that should, if applied, make the remote objects match the configuration – this is the essence of _infrastructure as code_.

### Terraform state

We use an S3 bucket created by Cloud Foundry in Cloud.gov as our remote backend for Terraform. This backend maintains the "state" of Terraform and makes it possible for us to make automated deployments based on changes to the Terraform configuration files. **This is the only part of our infrastructure that must be manually configured.**

Note that a single S3 bucket maintains the Terraform State for both the development and staging environments, and this instance is deployed in the development space.

|   | development  | staging  | production | 
|---|---|---|---|
| S3 Key | `terraform.tfstate.dev`   | `terraform.tfstate.staging`  | `terraform.tfstate.prod`  |
| Service Space | `tanf-dev`  | `tanf-dev`  | `tanf-prod`  |


## Local Set Up For Manual Deployments

Sometimes a developer will need to run Terraform locally to perform manual operations. Perhaps a new TF State S3 bucket needs to be created in another environment, or there are new services or other major configuration changes that need to be tested first.

1. **Install terraform**

    - On macOS: `brew install terraform`
    - On other platforms: [Download and install terraform][tf]

1. **Install Cloud Foundry CLI tool**

    - On macOS: `brew install cloudfoundry/tap/cf-cli`
    - On other platforms: [Download and install cf][cf-install]

1. **Login to Cloud Foundry**
    ```bash
       # login
       cf login -a api.fr.cloud.gov --sso
       # Follow temporary authorization code prompt.
       
       # Select the target org (probably `hhs-acf-prototyping`), 
       # and the space within which you want to provision infrastructure.
       
       # Spaces:
       # dev = tanf-dev
       # staging = tanf-staging
       # prod = tanf-prod
   ```

1. **Set up Terraform environment variables**

   In the `/terraform` directory, you can run the `create_tf_vars.sh` script which can be modified with details of your current environment, and will yield a `variables.tfvars` file which must be later passed in to Terraform. For more on this, check out [terraform variable definitions][tf-vars].

   ```bash
   ./create_tf_vars.sh
   
   # Should generate a file `variables.tfvars` in the current directory.
   # Your file should look something like this:
   #
   # cf_user = "some-dev-user"
   # cf_password = "some-dev-password"
   # cf_space_name = "tanf-dev"
   ```
   
## Test Deployment in Development

1. Follow the instructions above and ensure the `variables.tfvars` file has been generated with proper values.
1. `cd` into `/terraform/dev`

1. Prepare terraform backend:
   
   **Remote vs. Local Backend:**
   
   If you merely wish to test some new changes without regards to the currently deployed remote state stored in the, you may want to use a "local" backend with Terraform.
   ```terraform
   terraform {
    backend "local" {}
   }
   ```
   
   With this change, you should be able to run `terraform init` successfully.

   **Get Remote S3 Credentials:**
   
   In the `/terraform` directory, you can run the `create_backend_vars.sh` script which can be modified with details of your current environment, and will yield a `backend_config.tfvars` file which must be later passed in to Terraform. For more on this, check out [terraform variable definitions][tf-vars].

   ```bash
   ./create_backend_vars.sh
   
   # Should generate a file `backend_config.tfvars` in the current directory.
   # Your file should look something like this:
   #
   # access_key = "some-access-key"
   # secret_key = "some-secret-key"
   # region = "us-gov-west-1"
   ```
   
   You can now run `terraform init -backend-config backend_config.tfvars` and load the remote state stored in S3 into your local Terraform config.

1. Run `terraform init` if using a local backend, or `terraform init -backend-config backend_config.tfvars` with the remote backend.
1. Run `terraform destroy -var-file variables.tfvars` to clear the current deployment (if there is one).
   - If the current deployment isn't destroyed, `terraform apply` will fail later because the unique service instance names are already taken.
   - Be cautious and weary of your target environment when destroying infrastructure.
1. Run `terraform plan -out tfapply -var-file variables.tfvars` to create a new execution plan.
1. Run `terraform apply "tfapply"` to create the new infrastructure.

A similar test deployment can also be executed from the `/scripts/deploy-infrastructure-dev.sh` script, albeit without the `destroy` step.

### Terraform State S3 Bucket

These instructions describe the creation of a new S3 bucket to hold Terraform's state. _This need only be done once per environment_ (note that currently development and staging environments share a single S3 bucket that exists in the development space). This is the only true manual steps that needs to be taken upon the initial application deployment in new environments. This should only need to be done at the beginning of a deployed app's lifetime. 

1. **Create S3 Bucket for Terraform State**

   ```bash
    cf create-service s3 basic-sandbox tdp-tf-states
   ```

1. **Create service key**
   
   Now we need a new service key with which to authenticate to our Cloud.gov S3 bucket from CircleCI.

   ```bash
   cf create-service-key tdp-tf-states tdp-tf-key
   ```
   The service key details provide you with the credentials that are used with common file transfer programs by humans or configured in external systems. Typically, you would create a unique service key for each external client of the bucket to make it easy to rotate credentials in case they are leaked.

   > To later revoke access (e.g. when no longer required, or when compromised), you can run `cf delete-service-key tdp-tf-states tdp-tf-key`.

1. **Get the credentials from the service key**
   ```bash
   cf service-key tdp-tf-states tdp-tf-key
   ```
   
#### Security
   
   The Terraform State S3 instance is set to be encrypted (see `main.tf#backend`). Amazon S3 [protects data at rest][s3] using 256-bit Advanced Encryption Standard. 

   > **Rotating credentials:**
   > 
   > The S3 service creates unique IAM credentials for each application binding or service key. To rotate credentials associated with an application binding, unbind and rebind the service instance to the application. To rotate credentials associated with a service key, delete and recreate the service key.
   

<!-- Links -->

[cloudgov-service-keys]: https://cloud.gov/docs/services/s3/#interacting-with-your-s3-bucket-from-outside-cloudgov
[cf-install]: https://docs.cloudfoundry.org/cf-cli/install-go-cli.html
[tf]: https://www.terraform.io/downloads.html
[tf-vars]: https://www.terraform.io/docs/configuration/variables.html#variable-definitions-tfvars-files
[orb]: https://circleci.com/developer/orbs/orb/circleci/terraform
[language]: https://www.terraform.io/docs/language/index.html
[s3]: https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingServerSideEncryption.html
