#!/bin/sh

if command -v sha256sum >/dev/null ; then
	SHASUM=sha256sum
elif command -v shasum >/dev/null ; then
	SHASUM=shasum
fi

docker-compose down
docker-compose up -d --build
    # do an OWASP ZAP scan
     export ZAP_CONFIG=" \
      -config globalexcludeurl.url_list.url\(0\).regex='.*/robots\.txt.*' \
      -config globalexcludeurl.url_list.url\(0\).description='Exclude robots.txt' \
      -config globalexcludeurl.url_list.url\(0\).enabled=true \
      -config spider.postform=true"

    echo "================== OWASP ZAP tests =================="
    chmod 777 $(pwd)/reports
    # check if running in circle CI
    if [ -z "${CIRCLE_BRANCH+x}"]; then
        docker-compose run zaproxy zap-full-scan.py \
                       -t http://web:8080/ \
                       -m 5 \
                       -z "${ZAP_CONFIG}" \
                       -c "zap.conf" \
                       -r owasp_report.html | tee /dev/tty | grep -q "FAIL-NEW: 0"
    else
        docker-compose run zaproxy zap-full-scan.py \
                       -t http://web:8080/ \
                       -m 5 \
                       -z "${ZAP_CONFIG}" \
                       -c "zap.conf" \
                       -r owasp_report.html | tee /dev/tty | grep -q "FAIL-NEW: 0"
    fi

    ZAPEXIT=$?

EXIT=0

if [ "$ZAPEXIT" = 1 ] ; then
    echo "OWASP ZAP scan failed"
    EXIT=1
fi

docker-compose down --remove-orphan

exit $EXIT
