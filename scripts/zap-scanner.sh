#!/bin/bash

set -o pipefail

TARGET=$1
ENVIRONMENT=$2

TARGET_DIR="$(pwd)/tdrs-$TARGET"
REPORT_NAME=owasp_report.html
REPORTS_DIR="$TARGET_DIR/reports"

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


# do an OWASP ZAP scan
export ZAP_CONFIG=" \
  -config globalexcludeurl.url_list.url\(0\).regex='.*/robots\.txt.*' \
  -config globalexcludeurl.url_list.url\(0\).description='Exclude robots.txt' \
  -config globalexcludeurl.url_list.url\(0\).enabled=true \
  -config spider.postform=true"

echo "================== OWASP ZAP tests =================="
cd $TARGET_DIR

if [ "$TARGET" = "frontend" ]; then
    docker-compose down
    docker-compose up -d --build
fi

# Ensure the reports directory can be written to
chmod 777 $(pwd)/reports

ZAP_ARGS=(-t "$APP_URL" -m 5 -r "$REPORT_NAME" -z "$ZAP_CONFIG")
if [ -z ${CONFIG_FILE+x} ]; then
    echo "No config file, defaulting all alerts to WARN"
else
    echo "Config file found"
    ZAP_ARGS+=(-c "$CONFIG_FILE")
fi

ZAP_OUTPUT=$(docker-compose run --rm zaproxy zap-full-scan.py "${ZAP_ARGS[@]}" | tee /dev/tty)
ZAP_EXIT=$?

if [ "$ZAP_EXIT" -ne 0 ] ; then
	echo "OWASP ZAP scan failed"
fi

exit $ZAP_EXIT
