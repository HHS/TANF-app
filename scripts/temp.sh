#!/bin/bash
# Construct the project slug from the current branch name and user
PROJECT_SLUG=$CIRCLE_PROJECT_USERNAME/$CIRCLE_PROJECT_REPONAME

# These environment variables are exported to Circle CI's BASH_ENV
# by the zap-scanner.sh script for each respective app target.
# Evaluate the full command before passing it in so it doesn't
# get improperly interpolated by Cloud.gov.
CMD="python manage.py process_owasp_scan $CIRCLE_BUILD_NUM --backend-pass-count ${ZAP_BACKEND_PASS_COUNT:-0} --backend-warn-count ${ZAP_BACKEND_WARN_COUNT:-0} --backend-fail-count ${ZAP_BACKEND_FAIL_COUNT:-0} --frontend-pass-count ${ZAP_FRONTEND_PASS_COUNT:-0} --frontend-warn-count ${ZAP_FRONTEND_WARN_COUNT:-0} --frontend-fail-count ${ZAP_FRONTEND_FAIL_COUNT:-0} --project-slug $PROJECT_SLUG"
echo "$CMD"

# Submit a CF Task for execution that will run the necessary command
cf run-task tdp-backend-staging --wait --command "$CMD" --name nightly-owasp-scan
