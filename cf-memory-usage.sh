#!/usr/bin/env bash
# Show memory allocation per app in the current CF space vs the space's quota.

set -euo pipefail

if ! command -v cf &>/dev/null; then
  echo "Error: cf CLI not found. Install it first."
  exit 1
fi

if ! cf target &>/dev/null; then
  echo "Error: Not logged in to Cloud Foundry. Run 'cf login' first."
  exit 1
fi

target_info=$(cf target)
org=$(echo "$target_info" | awk '/^org:/{print $2}')
space=$(echo "$target_info" | awk '/^space:/{print $2}')

echo "Org:   $org"
echo "Space: $space"
echo ""

# Get app names from cf apps (skip header lines)
app_names=$(cf apps | awk 'NR>4 && NF>0 {print $1}')

if [ -z "$app_names" ]; then
  echo "No apps found in this space."
  exit 0
fi

printf "%-40s %8s %12s %15s %15s\n" "APP" "STATE" "INSTANCES" "ALLOCATED" "USED"
printf "%-40s %8s %12s %15s %15s\n" "---" "-----" "---------" "---------" "----"

total_allocated_mb=0

for app_name in $app_names; do
  app_info=$(cf app "$app_name" 2>/dev/null || true)

  state=$(echo "$app_info" | awk '/^requested state:/{print $3}')
  instances=$(echo "$app_info" | awk '/^instances:/{print $2}')
  mem_alloc=$(echo "$app_info" | awk '/^memory usage:/{print $3}')

  # Parse instance memory usage from the instance line (e.g. "809M of 1G")
  mem_used=$(echo "$app_info" | awk '/^#[0-9]/{print $4}' | head -1)
  [ -z "$mem_used" ] && mem_used="N/A"

  # Parse allocated memory into MB
  alloc_val=$(echo "$mem_alloc" | sed 's/[^0-9.]//g')
  alloc_unit=$(echo "$mem_alloc" | sed 's/[0-9.]//g')
  case "$alloc_unit" in
    G) alloc_mb=$(echo "$alloc_val * 1024" | bc) ;;
    M) alloc_mb="$alloc_val" ;;
    *) alloc_mb=0 ;;
  esac

  # Multiply by total instances
  total_inst=$(echo "$instances" | cut -d'/' -f2)
  [ -z "$total_inst" ] && total_inst=1
  app_total_mb=$(echo "$alloc_mb * $total_inst" | bc)

  total_allocated_mb=$(echo "$total_allocated_mb + $app_total_mb" | bc)

  printf "%-40s %8s %12s %13sMB %15s\n" "$app_name" "$state" "$instances" "$app_total_mb" "$mem_used"
done

echo ""
echo "--- Summary ---"
echo "Total memory allocated across all apps: ${total_allocated_mb}MB"


echo ""
echo ""
echo ""
echo "--- Space Quota Available ---"

# Derive env from space name (expects space like "tanf-dev", "tanf-staging", "tanf-prod")
env=$(echo "$space" | awk -F'-' '{print $NF}')
quota_name="${env}_quota"

echo "Using space quota: $quota_name"
cf space-quota "$quota_name" 2>/dev/null || echo "Could not find space quota '$quota_name'."
