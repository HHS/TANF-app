#!/bin/sh
# Downloads AWS and GCP IP ranges for CircleCI runner regions
# and generates nginx allow directives.
#
# Usage: ./scripts/generate-circleci-ip-ranges.sh
# Output: tdrs-frontend/nginx/cloud.gov/ip_circleci_runners.conf
#
# Requires: curl, jq

set -e

OUTPUT_FILE="tdrs-frontend/nginx/cloud.gov/ip_circleci_runners.conf"

{
    echo "# CircleCI runner IP ranges"
    echo "# AWS EC2: us-east-1, us-east-2"
    echo "# GCP: us-east1, us-central1"
    echo "# Generated: $(date -u +%Y-%m-%d)"
    echo ""
    echo "# AWS EC2 us-east-1 and us-east-2"
    curl -s https://ip-ranges.amazonaws.com/ip-ranges.json | \
        jq -r '.prefixes[] | select(.service=="EC2" and (.region=="us-east-1" or .region=="us-east-2")) | "allow \(.ip_prefix);"'
    echo ""
    echo "# GCP us-east1 and us-central1 (IPv4)"
    curl -s https://www.gstatic.com/ipranges/cloud.json | \
        jq -r '.prefixes[] | select(.scope=="us-east1" or .scope=="us-central1") | .ipv4Prefix // empty | "allow \(.);"'
    echo ""
    echo "# GCP us-east1 and us-central1 (IPv6)"
    curl -s https://www.gstatic.com/ipranges/cloud.json | \
        jq -r '.prefixes[] | select(.scope=="us-east1" or .scope=="us-central1") | .ipv6Prefix // empty | "allow \(.);"'
} > "$OUTPUT_FILE"

echo "Generated $OUTPUT_FILE with $(grep -c '^allow' "$OUTPUT_FILE") entries"
