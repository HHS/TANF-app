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
  docker-compose run zaproxy zap-full-scan.py \
    -t http://tdp-frontend \
    -m 5 \
    -z "${ZAP_CONFIG}" \
    -r owasp_report.html | tee /dev/tty | grep -q "FAIL-NEW: 0"
  ZAPEXIT=$?

 docker-compose down --remove-orphan


EXIT=0

if [ "$ZAPEXIT" = 1 ] ; then
	echo "OWASP ZAP scan failed"
	EXIT=1
fi

exit $EXIT
