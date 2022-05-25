
APP_NAME="tdp-backend-sandbox"
APP_GUID=$(cf curl /v3/apps/$(cf app $APP_NAME --guid)/processes | jq --raw-output '.resources | .[] | select(.type == "web").guid')

echo "APP NAME:$APP_NAME"
echo "APP GUID:$APP_GUID"

cat <<EOF > ~/.ssh/config
Host $APP_NAME
    HostName ssh.fr.cloud.gov
    User cf:$APP_GUID/0
    Port 2222
EOF

cat ~/.ssh/config

sshpass -p $(cf ssh-code) rsync -r ./tdrs-backend/tdpservice/ $APP_NAME:/app/tdpservice
