#!/bin/bash

# pipefail is needed to correctly carry over the exit code from zap-full-scan.py
set -o pipefail

TARGET=$1
ENVIRONMENT=$2

TARGET_DIR="$(pwd)/tdrs-$TARGET"
REPORT_NAME=owasp_report.html

if [ "$ENVIRONMENT" = "nightly" ]; then
    APP_URL="https://tdp-$TARGET-staging.app.cloud.gov/"
    CONFIG_FILE="zap.conf"
elif [ "$ENVIRONMENT" = "circle" ]; then
    CONFIG_FILE="zap.conf"
    if [ "$TARGET" = "frontend" ]; then
        APP_URL="http://tdp-frontend/"
    elif [ "$TARGET" = "backend" ]; then
        APP_URL="http://web:8080/"
    else
        echo "Invalid target $TARGET"
        exit 1
    fi
elif [ "$ENVIRONMENT" = "local" ]; then
    if [ "$TARGET" = "frontend" ]; then
        APP_URL="http://tdp-frontend/"
    elif [ "$TARGET" = "backend" ]; then
        APP_URL="http://web:8080/"
    else
        echo "Invalid target $TARGET"
        exit 1
    fi
else
    echo "Invalid environment $ENVIRONMENT"
    exit 1
fi

cd "$TARGET_DIR" || exit 2

# Ensure the APP_URL is reachable from the zaproxy container
if ! docker-compose run --rm zaproxy curl -Is "$APP_URL" > /dev/null 2>&1; then
  echo "Target application at $APP_URL is unreachable by ZAP scanner"
  exit 3
fi

echo "================== OWASP ZAP tests =================="

# Ensure the reports directory can be written to
chmod 777 "$(pwd)"/reports

# Command line options to the ZAP application
ZAP_CLI_OPTIONS="\
  -config globalexcludeurl.url_list.url\(0\).regex='.*/robots\.txt.*' \
  -config globalexcludeurl.url_list.url\(0\).description='Exclude robots.txt' \
  -config globalexcludeurl.url_list.url\(0\).enabled=true \
  -config spider.postform=true"

# How long ZAP will crawl the app with the spider process
ZAP_SPIDER_MINS=5

ZAP_ARGS=(-t "$APP_URL" -m "$ZAP_SPIDER_MINS" -r "$REPORT_NAME" -z "$ZAP_CLI_OPTIONS")
if [ -z ${CONFIG_FILE+x} ]; then
    echo "No config file, defaulting all alerts to WARN"
else
    echo "Config file found"
    ZAP_ARGS+=(-c "$CONFIG_FILE")
fi

# TODO: Remove this after all open alerts are categorized in the config files
# Don't trigger a failure on WARNING level alerts, until we have a complete config file this will cause us to never
# fail this step. However, if we do fail on warnings with the current configuration state every build will fail.
# This is because ZAP defaults all alerts to WARN level, and any warnings found will trigger a failing exit code
# from the zap-full-scan.py script.
ZAP_ARGS+=(-I)

# Run the ZAP full scan and store output for further processing if needed.
ZAP_OUTPUT=$(docker-compose run --rm zaproxy zap-full-scan.py "${ZAP_ARGS[@]}" | tee /dev/tty)
ZAP_EXIT=$?

if [ "$ZAP_EXIT" -eq 0 ]; then
  echo "OWASP ZAP scan successful"
else
  echo "OWASP ZAP scan failed"
fi

# Nightly scans in Circle CI need to persist some values across multiple steps.
if [ "$ENVIRONMENT" = "nightly" ]; then
  ZAP_SUMMARY=$(echo "$ZAP_OUTPUT" | tail -1 | xargs)

  function get_summary_value () {
    echo "$ZAP_SUMMARY" | grep -o "$1: [^ ]*" | cut -d':' -f2 | xargs
  }

  ZAP_PASS_COUNT=$(get_summary_value PASS)
  ZAP_WARN_COUNT=$(get_summary_value WARN-NEW)
  ZAP_FAIL_COUNT=$(get_summary_value FAIL-NEW)

  TARGET=$(echo "$TARGET" | awk '{print toupper($0)}')
  {
    echo "export ZAP_${TARGET}_PASS_COUNT=$ZAP_PASS_COUNT"
    echo "export ZAP_${TARGET}_WARN_COUNT=$ZAP_WARN_COUNT"
    echo "export ZAP_${TARGET}_FAIL_COUNT=$ZAP_FAIL_COUNT"
  } >> "$BASH_ENV"
fi

exit $ZAP_EXIT
