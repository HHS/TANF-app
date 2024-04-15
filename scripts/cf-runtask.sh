#!/bin/bash

# pipefail is needed to correctly carry over the exit code from zap-full-scan.py
set -uo pipefail

PROJECT_SLUG=$1
TARGET=$2
BUILD_NO=$3
ZAP_BACKEND_PASS_COUNT=$4
ZAP_BACKEND_WARN_COUNT=$5
ZAP_BACKEND_FAIL_COUNT=$6
ZAP_FRONTEND_PASS_COUNT=$7
ZAP_FRONTEND_WARN_COUNT=$8
ZAP_FRONTEND_FAIL_COUNT=$9

CMD="python manage.py process_owasp_scan $CIRCLE_BUILD_NUM --backend-pass-count ${ZAP_BACKEND_PASS_COUNT:-0} --backend-warn-count ${ZAP_BACKEND_WARN_COUNT:-0} --backend-fail-count ${ZAP_BACKEND_FAIL_COUNT:-0} --frontend-pass-count ${ZAP_FRONTEND_PASS_COUNT:-0} --frontend-warn-count ${ZAP_FRONTEND_WARN_COUNT:-0} --frontend-fail-count ${ZAP_FRONTEND_FAIL_COUNT:-0} --project-slug $PROJECT_SLUG"
echo .
sleep 120
echo .
echo START!
APP=tdp-backend-$TARGET
cf run-task "$APP" --wait --command "python -V" --name "nightly-owasp-scan"
echo DONE!
