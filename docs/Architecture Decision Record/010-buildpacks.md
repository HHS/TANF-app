# 1. Record architecture decisions

Date: 2021-02-26

## Status

Pending

## Context

We need to know how much effort would be involved in switching to Cloud.gov build packs from Docker.
We need to determine impact on local development if we were to choose to switch to build packs.
We need to have an idea of the steps required to implement build packs.

We run a pretty common python/django/postgres stack, the build packs are optimized for it. 
We would have to do all optimizations our selves if we went with docker. 
Build packs are pre ramped, they are preapproved for use in a gov tech stack.

## Decision

We have decided we should use build packs, they would be relatively low efforts. 
Minor changes to manifest and a new, similar script to the ones we already have.

We want to make it explicit in the mainifest file that we want a build pack

https://docs.cloudfoundry.org/devguide/deploy-apps/manifest-attributes.html#buildpack

https://direnv.net/
https://github.com/cloudfoundry/python-buildpack
https://www.pivotaltracker.com/n/projects/1042066
https://docs.cloudfoundry.org/buildpacks/python/index.html

## Instructions for build pack
To build this buildpack, run the following commands from the buildpack's directory:

    Source the .envrc file in the buildpack directory.

    source .envrc

    To simplify the process in the future, install direnv which will automatically source .envrc when you change directories.

    Install buildpack-packager

    go install github.com/cloudfoundry/libbuildpack/packager/buildpack-packager

    Build the buildpack

    buildpack-packager build [ --cached=(true|false) ]

    Use in Cloud Foundry

    Upload the buildpack to your Cloud Foundry and optionally specify it by name

    cf create-buildpack [BUILDPACK_NAME] [BUILDPACK_ZIP_FILE_PATH] 1
    cf push my_app [-b BUILDPACK_NAME]



## Consequences

Build packs depreciate an assumption we'd previously been making which is a garentee brought by docker, 
  that if it is running in docker, 
  it will work in all our environments.

While having a docker file and using it to deploy has several development advantages, 
  we have decided that the advantages given to us by builld packs to be worth changing over to. 

We would still plan to use docker for all local development.

The cloud deployment will no longer exactly match our development environment via docker.

Much of the hardening we'd have to do our selves to a docker image will already be done.

We will not have to keep updated a docker image, all we need is the code. No need for dockerhub.

There will need to be minor changes and testing in order to move over.
There will need to be more emphasis on testing on platform to be sure our code works with in the build pack.

