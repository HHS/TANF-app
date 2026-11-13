# Design environment for web hosted project updates

The project updates website was created for use as a tool to communicate project updates and research findings to the broader OFA team and to grantees. It is also aimed at improving the accessibility of these updates from that of the prior PDF format. The structure of the site is aimed at being simple to extend and maintain via simple HTML/CSS skills so as to allow the current design team or other non-developer team members to easily update it without requiring additional development time to be spent on non-feature work.

## How is this hosted?

It is a static website using the static file buildpack provided by cloud foundry on cloud.gov

## Deployment process

### Automated

Whenever a PR is approved and merged into `develop`, changes to this
static site are deployed to its Cloud Foundry application. The public, canonical
URL is [https://tanfdata.acf.hhs.gov/help/](https://tanfdata.acf.hhs.gov/help/).
The frontend nginx proxy reaches the separate application through the private
`tdp-project-updates.apps.internal` route. A cross-space network policy limits
access to the frontend applications on port 8080.

### Legacy URL handoff

`https://tdp-project-updates.app.cloud.gov` is a legacy public URL. Before the
first production deployment of the `/help` proxy, verify that every frontend
environment can load `/help/` through the internal route. Then transfer the
legacy route to the production frontend app. Target the space that owns the
legacy route, unmap it from the static application, and delete the now-unmapped
route:

```bash
cf unmap-route <legacy-app-name> app.cloud.gov --hostname tdp-project-updates
cf delete-route app.cloud.gov --hostname tdp-project-updates -f
```

The production deployment then maps that hostname to `tdp-frontend-prod`.
Frontend nginx redirects requests to `https://tanfdata.acf.hhs.gov/help` while
preserving the original path and query string. Do not map the legacy route to
both applications; Cloud Foundry would load balance requests instead of
consistently redirecting them. Future static-site deployments map only the
internal route, so they do not reclaim the legacy public hostname.

Lower environments use an environment-specific legacy-style route so the
redirect can be tested without taking ownership of the production hostname:

```text
https://tdp-project-updates-develop.app.cloud.gov
https://tdp-project-updates-staging.app.cloud.gov
https://tdp-project-updates-<dev-name>.app.cloud.gov
```

The existing application-networking deployment step maps the appropriate route
to each frontend. Nginx uses that frontend's `FRONTEND_ROUTE` environment
variable to redirect the original path and query string to `/help` on the same
environment.

## Review process

While the project updates site is stored in the TANF-app repo, it is not a part of the TDP application. Given that and the nature of updates involving simple HTML modifications/additions, the review process for updates to live comms should be made via the [review process](https://github.com/HHS/TANF-app/blob/main/docs/How-We-Work/our-workflow.md) for design tickets rather than dev tickets involving:

- Content review by the government product owner and tech lead
- Accessibility review by the government accessibility reviewer
