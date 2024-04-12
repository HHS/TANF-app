#!/bin/bash

# pipefail is needed to correctly carry over the exit code from zap-full-scan.py
set -uxo pipefail

PROJECT_SLUG=$1
CMD_ARGS=$2
TARGET=$3
BUILD_NO=$4
ZAP_BACKEND_PASS_COUNT=$5
ZAP_BACKEND_WARN_COUNT=$6
ZAP_BACKEND_FAIL_COUNT=$7
ZAP_FRONTEND_PASS_COUNT=$8
ZAP_FRONTEND_WARN_COUNT=$9
ZAP_FRONTEND_FAIL_COUNT=$10

CMD="python manage.py process_owasp_scan $CIRCLE_BUILD_NUM --backend-pass-count ${ZAP_BACKEND_PASS_COUNT:-0} --backend-warn-count ${ZAP_BACKEND_WARN_COUNT:-0} --backend-fail-count ${ZAP_BACKEND_FAIL_COUNT:-0} --frontend-pass-count ${ZAP_FRONTEND_PASS_COUNT:-0} --frontend-warn-count ${ZAP_FRONTEND_WARN_COUNT:-0} --frontend-fail-count ${ZAP_FRONTEND_FAIL_COUNT:-0} --project-slug $PROJECT_SLUG"
echo $CMD
echo START!
cf run-task tdp-backend-$TARGET --wait --command "$CMD" --name nightly-owasp-scan
echo DONE!