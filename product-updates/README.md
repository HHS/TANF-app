# Design environment for web hosted project updates

The project updates website was created for use as a tool to communicate project updates and research findings to the broader OFA team and to grantees. It is also aimed at improving the accessibility of these updates from that of the prior PDF format. The structure of the site is aimed at being simple to extend and maintain via simple HTML/CSS skills so as to allow the current design team or other non-developer team members to easily update it without requiring additional development time to be spent on non-feature work. 

## How is this hosted?

It is a static website using the static file buildpack provided by cloud foundry on cloud.gov

## Deployment process

### Automated

When ever any PR is approved and merged into raft-tdp-main, any changes that were made to this static site will be deployed
to [https://tdp-project-updates.app.cloud.gov/](https://tdp-project-updates.app.cloud.gov/)

## Review process

While the project updates site is stored in the TANF-app repo, it is not a part of the TDP application. Given that and the nature of updates involving simple HTML modifications/additions, the review process for updates to live comms should be made via the [review process](https://github.com/HHS/TANF-app/blob/main/docs/How-We-Work/our-workflow.md) for design tickets rather than dev tickets involving:

- Content review by the government product owner and tech lead
- Accessibility review by the government accessibility reviewer

