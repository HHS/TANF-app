#!/bin/sh
#
# This is what sets up and actually runs the test
#
# You can run it like ./test.sh nodelete to leave the test env running
#

if command -v sha256sum >/dev/null ; then
	SHASUM=sha256sum
elif command -v shasum >/dev/null ; then
	SHASUM=shasum
fi

# Set some secrets up
export MINIO_SECRET_KEY=$(date +%s | $SHASUM | base64 | head -c 40)
sleep 1
export MINIO_ACCESS_KEY=$(date +%s | $SHASUM | base64 | head -c 20)

docker-compose down
docker-compose up -d --build
docker-compose run tanf ./wait-for postgres:5432 -- python3 manage.py migrate
docker-compose run tanf python3 manage.py createsuperuser --email timothy.spencer@gsa.gov --noinput

echo "====================================== Python tests"
docker-compose exec tanf python3 manage.py test
PYTESTEXIT=$?


# XXX This takes too long to run.  :-(
if [ "$1" = 'zapscan' ] ; then
	# do an OWASP ZAP scan
	docker exec "$CONTAINER" ./manage.py migrate
	export ZAP_CONFIG=" \
	  -config globalexcludeurl.url_list.url\(0\).regex='.*/robots\.txt.*' \
	  -config globalexcludeurl.url_list.url\(0\).description='Exclude robots.txt' \
	  -config globalexcludeurl.url_list.url\(0\).enabled=true \
	  -config spider.postform=true"

	CONTAINER=$(docker-compose images | awk '/zaproxy/ {print $1}')
	echo "====================================== OWASP ZAP tests"
	docker exec "$CONTAINER" zap-full-scan.py -t http://tanf:8000/about/ -m 5 -z "${ZAP_CONFIG}" | tee /tmp/zap.out 
	if grep 'FAIL-NEW: 0' /tmp/zap.out >/dev/null ; then
		ZAPEXIT=0
	else
		ZAPEXIT=1
	fi
fi


# clean up (if desired)
if [ "$1" != "nodelete" ] ; then
	docker-compose down
fi

echo "====================================== Overall test failures: "
EXIT=0
if [ "$ZAPEXIT" = 1 ] ; then
	echo "OWASP ZAP scan failed"
	EXIT=1
fi

if [ "$PYTESTEXIT" != 0 ] ; then
	echo "Python tests failed"
	EXIT=1
fi

exit $EXIT
