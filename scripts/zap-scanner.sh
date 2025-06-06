#!/bin/bash

# pipefail is needed to correctly carry over the exit code from zap-full-scan.py
set -uxo pipefail

TARGET=$1
ENVIRONMENT=$2
TARGET_ENV=$3
REGISTRY_OWNER=$4

TARGET_DIR="$(pwd)/tdrs-$TARGET"
CONFIG_FILE="zap.conf"
REPORT_NAME=owasp_report.html


if [ "$ENVIRONMENT" = "nightly" ]; then
    APP_URL="https://tdp-frontend-$TARGET_ENV.acf.hhs.gov/"
    if [ "$TARGET_ENV" = "prod" ]; then
        APP_URL="https://tanfdata.acf.hhs.gov/"
    fi
elif [ "$ENVIRONMENT" = "circle" ] || [ "$ENVIRONMENT" = "local" ]; then
    if [ "$TARGET" = "frontend" ]; then
        APP_URL="http://tdp-frontend/"
    elif [ "$TARGET" = "backend" ]; then
        APP_URL="http://tdp-frontend/"
    else
        echo "Invalid target $TARGET"
        exit 1
    fi
else
    echo "Invalid environment $ENVIRONMENT"
    exit 1
fi

# The backend also needs to include the path of the OpenAPI specification
if [ "$TARGET" = "backend" ]; then
  APP_URL+="swagger.json"
fi

cd "$TARGET_DIR" || exit 2


if [[ $(docker network inspect external-net 2>&1 | grep -c Scope) == 0 ]]; then
  docker network create external-net
fi

# Ensure the APP_URL is reachable from the zaproxy container
if ! REGISTRY_OWNER="$REGISTRY_OWNER" docker-compose run --rm zaproxy curl -Is "$APP_URL" > /dev/null 2>&1; then
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

  -config globalexcludeurl.url_list.url\(1\).regex='^https?://.*\.cdn\.mozilla\.(?:com|org|net)/.*$' \
  -config globalexcludeurl.url_list.url\(1\).description='Site - Mozilla CDN (requests such as getpocket)' \
  -config globalexcludeurl.url_list.url\(1\).enabled=true \

  -config globalexcludeurl.url_list.url\(2\).regex='^https?://.*\.amazonaws\.(?:com|org|net)/.*$' \
  -config globalexcludeurl.url_list.url\(2\).description='TDP S3 buckets' \
  -config globalexcludeurl.url_list.url\(2\).enabled=true \

  -config globalexcludeurl.url_list.url\(4\).regex='^https:\/\/.*\.google.com\/.*$' \
  -config globalexcludeurl.url_list.url\(4\).description='Site - Google.com' \
  -config globalexcludeurl.url_list.url\(4\).enabled=true \

  -config globalexcludeurl.url_list.url\(5\).regex='^https:\/\/.*\.youtube.com\/.*$' \
  -config globalexcludeurl.url_list.url\(5\).description='Site - youtube.com' \
  -config globalexcludeurl.url_list.url\(5\).enabled=true \

  -config globalexcludeurl.url_list.url\(6\).regex='^https:\/\/.*\.monsido.com\/.*$' \
  -config globalexcludeurl.url_list.url\(6\).description='Site - monsido.com' \
  -config globalexcludeurl.url_list.url\(6\).enabled=true \

  -config globalexcludeurl.url_list.url\(7\).regex='^https:\/\/.*\.crazyegg.com\/.*$' \
  -config globalexcludeurl.url_list.url\(7\).description='Site - crazyegg.com' \
  -config globalexcludeurl.url_list.url\(7\).enabled=true \

  -config globalexcludeurl.url_list.url\(8\).regex='^https:\/\/.*\.gstatic.com\/.*$' \
  -config globalexcludeurl.url_list.url\(8\).description='Site - gstatic.com' \
  -config globalexcludeurl.url_list.url\(8\).enabled=true \

  -config globalexcludeurl.url_list.url\(9\).regex='^https:\/\/.*\.googleapis.com\/.*$' \
  -config globalexcludeurl.url_list.url\(9\).description='Site - GoogleAPIs.com' \
  -config globalexcludeurl.url_list.url\(9\).enabled=true \

  -config globalexcludeurl.url_list.url\(10\).regex='^https:\/\/.*\.crazyegg.com\/.*$' \
  -config globalexcludeurl.url_list.url\(10\).description='Site - CrazyEgg.com' \
  -config globalexcludeurl.url_list.url\(10\).enabled=true \

  -config globalexcludeurl.url_list.url\(11\).regex='^https:\/\/.*\.doubleclick.net\/.*$' \
  -config globalexcludeurl.url_list.url\(11\).description='Site - DoubleClick.net' \
  -config globalexcludeurl.url_list.url\(11\).enabled=true \

  -config globalexcludeurl.url_list.url\(12\).regex='^https:\/\/.*unpkg.com\/.*$' \
  -config globalexcludeurl.url_list.url\(12\).description='Site - Unpkg.com' \
  -config globalexcludeurl.url_list.url\(12\).enabled=true \

  -config globalexcludeurl.url_list.url\(13\).regex='^https:\/\/.*\.readspeaker.com\/.*$' \
  -config globalexcludeurl.url_list.url\(13\).description='Site - ReadSpeaker.com' \
  -config globalexcludeurl.url_list.url\(13\).enabled=true \

  -config globalexcludeurl.url_list.url\(14\).regex='^https:\/\/.*\.fontawesome.com\/.*$' \
  -config globalexcludeurl.url_list.url\(14\).description='Site - FontAwesome.com' \
  -config globalexcludeurl.url_list.url\(14\).enabled=true \

  -config globalexcludeurl.url_list.url\(16\).regex='^https:\/\/.*\.googletagmanager.com\/.*$' \
  -config globalexcludeurl.url_list.url\(16\).description='Site - googletagmanager.com' \
  -config globalexcludeurl.url_list.url\(16\).enabled=true \

  -config globalexcludeurl.url_list.url\(17\).regex='^https:\/\/.*\.cloudflare.com\/.*$' \
  -config globalexcludeurl.url_list.url\(17\).description='Site - CloudFlare.com' \
  -config globalexcludeurl.url_list.url\(17\).enabled=true \

  -config globalexcludeurl.url_list.url\(18\).regex='^https:\/\/.*\.google-analytics.com\/.*$' \
  -config globalexcludeurl.url_list.url\(18\).description='Site - Google-Analytics.com' \
  -config globalexcludeurl.url_list.url\(18\).enabled=true \

  -config globalexcludeurl.url_list.url\(19\).regex='^https:\/\/.*\.googletagmanager.com\/.*$' \
  -config globalexcludeurl.url_list.url\(19\).description='Site - googletagmanager.com' \
  -config globalexcludeurl.url_list.url\(19\).enabled=true \

  -config globalexcludeurl.url_list.url\(20\).regex='^https:\/\/.*\.digitalgov.gov\/.*$' \
  -config globalexcludeurl.url_list.url\(20\).description='Site - DigitalGov.gov' \
  -config globalexcludeurl.url_list.url\(20\).enabled=true \

  -config globalexcludeurl.url_list.url\(21\).regex='^https:\/\/.*\.identitysandbox.gov\/.*$' \
  -config globalexcludeurl.url_list.url\(21\).description='Site - IdentitySandbox.gov' \
  -config globalexcludeurl.url_list.url\(21\).enabled=true \
  -config spider.postform=true"
# How long ZAP will crawl the app with the spider process
ZAP_SPIDER_MINS=10

ZAP_ARGS=(-t "$APP_URL" -m "$ZAP_SPIDER_MINS" -r "$REPORT_NAME" -z "$ZAP_CLI_OPTIONS")
if [ -z ${CONFIG_FILE+x} ]; then
    echo "No config file, defaulting all alerts to WARN"
else
    echo "Config file found"
    ZAP_ARGS+=(-c "$CONFIG_FILE")
fi

# Prevent failures for alerts triggered at WARN level.
# At this time rules at this level are known issues to correct, but if ZAP
# adds new rules we don't have categorized they will default to WARN.
ZAP_ARGS+=(-I)

# Use custom hook to disable passive scan rules - these don't get disabled by
# setting them to IGNORE in the config file, unlike active rules.
ZAP_ARGS+=(--hook=/zap/scripts/zap-hook.py)

# Alter the script used and options passed to it based on target
if [ "$TARGET" = "backend" ]; then
  # Use the API scan for the backend, in order to allow crawling the API based
  # on the Swagger/OpenAPI spec provided by drf-yasg2.
  ZAP_SCRIPT="zap-api-scan.py"
  # The API scan needs to know the format of the API specification provided.
  ZAP_ARGS+=(-f openapi)
else
  # Otherwise, use the full scan as we have been.
  ZAP_SCRIPT="zap-full-scan.py"
  # Allow use of the optional AJAX spider to effectively crawl the React webapp.
  ZAP_ARGS+=(-j)
fi

# Run the ZAP full scan and store output for further processing if needed.
ZAP_OUTPUT=$(docker-compose run --rm zaproxy "$ZAP_SCRIPT" "${ZAP_ARGS[@]}" | tee /dev/tty)
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
    echo "$ZAP_SUMMARY" | grep -o "$1: [^ ]*" | cut -d':' -f2 | sed 's/[^0-9]*//g'
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
