#!/bin/sh

ENVIRONMENT=$1

# do an OWASP ZAP scan
export ZAP_CONFIG=" \
  -config globalexcludeurl.url_list.url\(0\).regex='.*/robots\.txt.*' \
  -config globalexcludeurl.url_list.url\(0\).description='Exclude robots.txt' \
  -config globalexcludeurl.url_list.url\(0\).enabled=true \
  -config spider.postform=true"

echo "================== OWASP ZAP tests =================="
chmod 777 $(pwd)/reports

# check if running in circle CI
if [ "$ENVIRONMENT" = "circle" ]; then
    echo "Using config file"
    docker-compose run zaproxy zap-full-scan.py \
                    -t http://web:8080/ \
                    -m 5 \
                    -z "${ZAP_CONFIG}" \
                    -c "zap.conf" \
                    -r owasp_report.html | tee /dev/tty | grep -q "FAIL-NEW: 0"
else
    echo "No config file"
    docker-compose run zaproxy zap-full-scan.py \
                    -t http://web/ \
                    -m 5 \
                    -z "${ZAP_CONFIG}" \
                    -r owasp_report.html | tee /dev/tty | grep -q "FAIL-NEW: 0"
fi

ZAPEXIT=$?

EXIT=0

if [ "$ZAPEXIT" = 1 ] ; then
    echo "OWASP ZAP scan failed"
    EXIT=1
fi

exit $EXIT
