# How We Use GitHub Actions
For now, the only use case we have for GitHub Actions is to help up trigger CircleCI builds the way we want to. This is actually the preferred method CircleCI advises for branch, path, pull-request, and labelled filtering and job triggering. See this [blog](https://circleci.com/blog/trigger-circleci-pipeline-github-action/) for details, though we use [promiseofcake/circleci-trigger-action@v](https://github.com/promiseofcake/circleci-trigger-action) plugin vs circleci/trigger_circleci_pipeline@v1.0

## Path Filtering
We use Actions to filter which workflows are getting run by CircleCI by sending different flags to CircleCI through the promiseofcake CircleCI API trigger. See the individual files in [.github](../../.github/) for detailed instructions for how to use each.
