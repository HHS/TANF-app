#!/bin/bash

# pipefail is needed to correctly carry over the exit code from zap-full-scan.py
set -uxo pipefail

PROJECT_SLUG=$1
CMD_ARGS=$2
TARGET=$3

CMD="python manage.py process_owasp_scan ${CMD_ARGS[*]}"
echo $CMD
echo START!
cf run-task tdp-backend-$TARGET --wait --command "$CMD" --name nightly-owasp-scan
echo DONE!