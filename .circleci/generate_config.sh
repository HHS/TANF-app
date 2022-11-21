#!/usr/bin/sh

cat base_config.yml > generated_config.yml

# Commands
echo 'commands:' >> generated_config.yml
cat build-and-test/commands.yml >> generated_config.yml
cat infrastructure/commands.yml >> generated_config.yml
cat deployment/commands.yml >> generated_config.yml
cat owasp/commands.yml >> generated_config.yml
cat util/commands.yml >> generated_config.yml

# Jobs
echo 'jobs:' >> generated_config.yml
cat build-and-test/jobs.yml >> generated_config.yml
cat infrastructure/jobs.yml >> generated_config.yml
cat deployment/jobs.yml >> generated_config.yml
cat owasp/jobs.yml >> generated_config.yml
cat util/jobs.yml >> generated_config.yml

# Workflows
echo 'workflows:' >> generated_config.yml
cat build-and-test/workflows.yml >> generated_config.yml
cat deployment/workflows.yml >> generated_config.yml
cat owasp/workflows.yml >> generated_config.yml
cat util/workflows.yml >> generated_config.yml

cat generated_config.yml