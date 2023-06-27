# CICD Walkthrough

This app mainly uses CircleCi for cicd. GitHub actions is used to trigger some CircleCi pipelines, such as deploying on label and qasp scans.

## Dynamic Configuration

To make the config yaml easier to read we are using CircleCi's [Dynamic Configuration](https://circleci.com/docs/dynamic-config/) feature.

### Continuation orb
CicleCi has an orb that allows for another config file to be specified. Using a script this new config is generated based on the info passed via the pipeline parameters. This can later be used in conjuction with the path filtering orb to make our build time shorter. It could also be used to build different configuration files for different pipelines.
#### generate_config.sh
This script will generate a complete config for building, testing, and deploying.

### Directory structure

#### build-and-test
Contains workflows, jobs, and commands for building and testing the application. For all development side builds, these are now triggered by GitHub Actions that serve as a filter so only the code that's changed is tested. See [build-all](../.github/workflows/build-all.yml), [build-backend](../.github/workflows/build-backend.yml), and [build-frontend](../.github/workflows/build-frontend.yml)

#### infrastructure
Contains workflows, jobs, and commands for setting up the infrastructure on Cloud gov. For all development side builds, this is now triggered by GitHub Actions that serve as a filter so only runs when infrastructure code is changed. See [deploy-infrastructure](../.github/workflows/deploy-infrastructure.yml)

#### deployment
Contains workflows, jobs, and commands for deploying the application on Cloud gov. Note: merges to develop now automatically trigger a develop deploy using [deploy-develop-on-merge](../.github/workflows/deploy-develop-on-merge.yml) and deploys to dev environments happen when a label is created on the PR using [deploy-on-label](../.github/workflows/deploy-on-label.yml)

#### owasp
Contains workflows, jobs, and commands for running OWASP scans on the application in during the pipeline against Cloud.gov environments.

#### util
Contains utility workflows like `cf-check` that are reused in different versions of the generated_config.yml as to have access to these common functions. It also has one-offs like `erd`.

### Navigation examples
What if you want to look at the jobs that we used to build and test the application?

This is easy. We first go to the `build-and-test` directory then open the jobs.yml

`build-and-test/ -> jobs.yml`

<hr />

What if you want to know how Terraform is used by our pipeline?

Terraform is used to set up infrastruture so we would start in the `infrastructure` directory. To see how terraform is actualy used you would look in commands since that is generally where Circle Ci actually runs things. Within the `deploy-infrastructure` command in the commands.yml you can see that a terraform orb is beign used to run terraform commands.

`infrastructure/ -> commands.yml -> deploy-infrastructure`

<hr />

What if you want to know how the deployments are triggered?

We know we want the `deployments` directory. To see how a pipeline is started we look at workflow.yml. Then we find the desired workflow.

`deployment/ -> workflows.yml -> desired workflow`

## Setting up scheduled pipeline for nightly OWASP scans
We want a scheduled pipeline that runs once a day with the pipeline parameter `run_nightly_owasp_scan` set to `true`. You can use [these instructions](https://circleci.com/docs/scheduled-pipelines/#project-settings) from the docs or follow the instructions below.

In Circle Ci go to `Project Settings -> Triggers -> Add Triggers`

You want the Trigger Source to be scheduled.

You want Repeats to be weekly.

You want to select all for days and months.

You want the start time to be at 0:00 UTC.

You want to repeat once per hour.

You want to set the branch to be the branch you want this scan to be run on.

You want to add a Pipeline Parameter with `run_nightly_owasp_scan`to be a boolean and set to `true`.

You want Attribution set to Scheduled Actor (Scheduling System)

## Updating Cloud Foundry App OS
Cloud Foundry (CF) occasionally releases OS updates. In doing so they deprecate the previous OS and after a short time
do not allow any apps to run/deploy on anything but the latest OS. The steps below describe how the main TDP apps are
updated along with the secondary apps running in CF.

### Frontend/Backend
 - Before updating, make sure the current buildpacks that these apps use are supported by the latest OS. If they aren't you can update the manifest to point them to the correct buildpacks.
 - To update the apps you can either deploy each of the environments (sandbox, raft, qasp, etc) from CircleCi or you can use the `tdrs-deploy <ENVIRONMENT>` command from `commands.sh`. Assuming the buildpacks are up to date, that is all you need to do.

### Secondary apps
 - Before you can make the update, you need to ensure you have the CF plugin that allows you to do so. Download the binary for your respective OS [HERE](https://github.com/cloudfoundry/stack-auditor/releases) and follow the installation instructions [HERE](https://docs.cloudfoundry.org/adminguide/stack-auditor.html#install).
  - Verify the installation succeeded by running `cf audit-stack`. Note you need to be logged in and have targeted a space via `cf target -o hhs-acf-ofa -s <SPACE>`
 - To update the remaining apps you need to run `cf change-stack <APP_NAME> <OS_NAME>` against every app that is not a frontend/backend app.
