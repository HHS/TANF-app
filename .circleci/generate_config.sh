#!/usr/bin/sh

cat base_config.yml > generated_config.yml
cat commands.yml >> generated_config.yml
cat jobs.yml >> generated_config.yml
cat workflows.yml >> generated_config.yml

cat generated_config.yml
