#!/usr/bin/env bash

set -euo pipefail

read_credential() {
  local service_label=$1
  local credential_name=$2

  jq -er \
    --arg service_label "$service_label" \
    --arg credential_name "$credential_name" \
    '.[$service_label][0].credentials[$credential_name] | select(. != null and . != "") | tostring' \
    <<<"$VCAP_SERVICES"
}

url_encode() {
  jq -nr --arg value "$1" '$value | @uri'
}

environment_name=${CGAPPNAME_BACKEND#tdp-backend-}
if [[ -z "$environment_name" || "$environment_name" == "$CGAPPNAME_BACKEND" ]]; then
  echo "CGAPPNAME_BACKEND must use the tdp-backend-<environment> naming convention" >&2
  exit 1
fi

space_name=$(jq -er '.space_name | select(. != null and . != "")' <<<"$VCAP_APPLICATION")
database_name="tdp_db_${environment_name}"
if [[ "$environment_name" == "raft" ]]; then
  database_name=tdp_db_test
elif [[ "$space_name" == "tanf-prod" ]]; then
  database_name=$(read_credential aws-rds db_name)
fi

case "$environment_name" in
  test|raft|develop|prod)
    redis_database=0
    ;;
  qasp|staging)
    redis_database=3
    ;;
  a11y)
    redis_database=6
    ;;
  *)
    echo "No Celery Redis database is configured for ${environment_name}" >&2
    exit 1
    ;;
esac

database_host=$(read_credential aws-rds host)
database_port=$(read_credential aws-rds port)
database_username=$(read_credential aws-rds username)
database_password=$(read_credential aws-rds password)
redis_host=$(read_credential aws-elasticache-redis host)
redis_port=$(read_credential aws-elasticache-redis port)
redis_password=$(read_credential aws-elasticache-redis password)

database_url="postgres://$(url_encode "$database_username"):$(url_encode "$database_password")@${database_host}:${database_port}/$(url_encode "$database_name")"
redis_url="rediss://:$(url_encode "$redis_password")@${redis_host}:${redis_port}/${redis_database}"
aws_access_key_id=$(read_credential s3 access_key_id)
aws_default_region=$(read_credential s3 region)
aws_secret_access_key=$(read_credential s3 secret_access_key)
s3_bucket=$(read_credential s3 bucket)

export DATABASE_URL="$database_url"
export REDIS_URL="$redis_url"
export AWS_ACCESS_KEY_ID="$aws_access_key_id"
export AWS_DEFAULT_REGION="$aws_default_region"
export AWS_SECRET_ACCESS_KEY="$aws_secret_access_key"
export S3_BUCKET="$s3_bucket"
export S3_KEY_PREFIX="$CGAPPNAME_BACKEND"
export GO_PARSER_POST_PARSE_QUEUE="${GO_PARSER_POST_PARSE_QUEUE:-$environment_name}"

exec "${PARSER_BINARY:-./build/go-parser}" "$@"
