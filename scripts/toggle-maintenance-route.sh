#!/bin/sh

set -eu

usage() {
  cat <<'EOF'
Usage:
  # Single-app in-place toggle (no restart)
  scripts/toggle-maintenance-route.sh <enable|disable> <app>

Examples:
  # Production/custom-domain style: single-app in-place toggle
  scripts/toggle-maintenance-route.sh enable tdp-frontend
  scripts/toggle-maintenance-route.sh disable tdp-frontend

  # app.cloud.gov style: single-app in-place toggle
  scripts/toggle-maintenance-route.sh enable tdp-frontend-a11y
  scripts/toggle-maintenance-route.sh disable tdp-frontend-a11y

Notes:
  - You must already be authenticated with Cloud Foundry CLI and target the correct org/space.
  - This changes live containers via cf ssh (no restart), but changes are ephemeral
    and are lost on restart/restage/redeploy.
EOF
}

if [ "$#" -ne 2 ]; then
  usage
  exit 1
fi

ACTION="$1"
APP_NAME="$2"

if [ "$ACTION" != "enable" ] && [ "$ACTION" != "disable" ]; then
  echo "Error: action must be 'enable' or 'disable'."
  usage
  exit 1
fi

run_single_app_toggle() {
  APP_NAME="$1"

  echo "Verifying app exists..."
  cf app "$APP_NAME" >/dev/null

  INSTANCES_LINE="$(cf app "$APP_NAME" | awk '/^instances:/{print $2}')"
  RUNNING_INSTANCES="${INSTANCES_LINE%%/*}"

  case "$RUNNING_INSTANCES" in
    ''|*[!0-9]*)
      echo "Error: could not determine running instance count for $APP_NAME."
      echo "Make sure the app is started and try again."
      exit 1
      ;;
  esac

  if [ "$RUNNING_INSTANCES" -eq 0 ]; then
    echo "Error: app has 0 running instances. Start the app first."
    exit 1
  fi

  echo "Applying '$ACTION' across $RUNNING_INSTANCES running instance(s) for $APP_NAME..."
  i=0
  while [ "$i" -lt "$RUNNING_INSTANCES" ]; do
    if [ "$ACTION" = "enable" ]; then
      echo "  - Instance $i: enabling maintenance page"
      cf ssh "$APP_NAME" -i "$i" -c '
set -eu

# Target path for cloud.gov nginx buildpack (root public; rewrite checks $document_root/503.html).
TARGET="/home/vcap/app/public/503.html"

# Try known source locations first.
if [ -f /home/vcap/app/public/503_.html ]; then
  cp /home/vcap/app/public/503_.html "$TARGET"
elif [ -f /home/vcap/app/nginx/src/503.html ]; then
  cp /home/vcap/app/nginx/src/503.html "$TARGET"
elif [ -f /usr/share/nginx/html/503_.html ]; then
  cp /usr/share/nginx/html/503_.html "$TARGET"
elif [ -f /usr/share/nginx/html/503.html ]; then
  cp /usr/share/nginx/html/503.html "$TARGET"
else
  # Last resort: write a minimal maintenance page so toggle still works.
  cat > "$TARGET" <<"HTML"
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Site Under Maintenance</title>
  <style>
    body { font-family: sans-serif; margin: 2rem; line-height: 1.5; }
    h1 { margin-bottom: 0.5rem; }
  </style>
</head>
<body>
  <h1>Site Under Maintenance</h1>
  <p>We are currently performing maintenance. Please check back shortly.</p>
</body>
</html>
HTML
fi
'
    else
      echo "  - Instance $i: disabling maintenance page"
      cf ssh "$APP_NAME" -i "$i" -c 'rm -f /home/vcap/app/public/503.html /usr/share/nginx/html/503.html'
    fi
    i=$((i + 1))
  done

  if [ "$ACTION" = "enable" ]; then
    echo "Maintenance mode enabled in-place for $APP_NAME."
  else
    echo "Maintenance mode disabled in-place for $APP_NAME."
  fi
}

run_single_app_toggle "$APP_NAME"
