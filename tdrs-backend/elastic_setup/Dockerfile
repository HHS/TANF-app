ARG ELASTIC_VERSION

FROM docker.elastic.co/elasticsearch/elasticsearch:${ELASTIC_VERSION}

COPY . /

RUN ["chmod", "+x", "/entrypoint.sh"]
RUN ["chmod", "+x", "/util.sh"]

ENTRYPOINT ["/entrypoint.sh"]
