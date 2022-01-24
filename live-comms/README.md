# Design Environment for web hosted live comms

The live comms website is for communicating

## How is this hosted?

It is a static website using the static file buildpack provided by cloud foundry on cloud.gov

## Deployment process

### Automated

When ever any PR is approved and merged into raft-tdp-main, any changes that were made to this static site will be deployed
to https://tdp-live-comms.app.cloud.gov/

## Review process

Government tech lead and product owner do content review
Government A11y review, currently done by Thomas Tran
Design review as per [Our workflow](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/docs/How-We-Work/our-workflow.md)



