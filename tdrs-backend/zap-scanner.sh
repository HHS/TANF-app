#!/bin/sh

if command -v sha256sum >/dev/null ; then
	SHASUM=sha256sum
elif command -v shasum >/dev/null ; then
	SHASUM=shasum
fi


docker-compose down
docker-compose up -d --build
	# do an OWASP ZAP scan
	CONTAINER=$(docker-compose images | awk '/zaproxy/ {print $1}')
 	export ZAP_CONFIG=" \
	  -config globalexcludeurl.url_list.url\(0\).regex='.*/robots\.txt.*' \
	  -config globalexcludeurl.url_list.url\(0\).description='Exclude robots.txt' \
	  -config globalexcludeurl.url_list.url\(0\).enabled=true \
	  -config spider.postform=true"

	echo "================== OWASP ZAP tests =================="
	docker exec "$CONTAINER" zap-full-scan.py -t http://web:8080/ -m 5 -z "${ZAP_CONFIG}" | tee /tmp/zap.out 
	if grep 'FAIL-NEW: 0' /tmp/zap.out >/dev/null ; then
		ZAPEXIT=0
	else
		ZAPEXIT=1
	fi

EXIT=0

if [ "$ZAPEXIT" = 1 ] ; then
	echo "OWASP ZAP scan failed"
	EXIT=1
fi

 docker-compose down --remove-orphan

exit $EXIT
