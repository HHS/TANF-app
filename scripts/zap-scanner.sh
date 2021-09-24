#!/bin/sh


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

    # docker-compose down
    # docker-compose up -d --build

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

if [ -z ${CONFIG_FILE+x} ]; then
    echo "No config file"
    docker-compose run zaproxy zap-full-scan.py \
                   -t $APP_URL \
                   -m 5 \
                   -z "${ZAP_CONFIG}" \
                   -r "$REPORT_NAME" | tee /dev/tty | grep -q "FAIL-NEW: 0"
else
    echo "Config file $ENVIRONMENT"
    docker-compose run zaproxy zap-full-scan.py \
                   -t $APP_URL \
                   -m 5 \
                   -z "${ZAP_CONFIG}" \
                   -c "$CONFIG_FILE" \
                   -r "$REPORT_NAME"  | tee /dev/tty | grep -q "FAIL-NEW: 0"
fi


# The `grep -q` piped to the end of the previous command will return a
# 0 exit code if the term is found and 1 otherwise.
ZAPEXIT=$?

if [ "$TARGET" = "frontend" ]; then
    docker-compose down --remove-orphan
fi

EXIT=0

if [ "$ZAPEXIT" = 1 ] ; then
	echo "OWASP ZAP scan failed"
	EXIT=1
fi

exit $EXIT
cd ..
