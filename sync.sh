
APP_NAME="tdp-backend-sandbox"
APP_GUID=$(cf curl /v3/apps/$(cf app $APP_NAME --guid)/processes | jq --raw-output '.resources | .[] | select(.type == "web").guid')

echo "APP NAME:$APP_NAME"
echo "APP GUID:$APP_GUID"

echo "Your ssh config file is currently, but don't worry, we're gonna fix that."
cat <<EOF > ~/.ssh/config
Host $APP_NAME
    HostName ssh.fr.cloud.gov
    User cf:$APP_GUID/0
    Port 2222
EOF

echo "Your ssh config file is now different, your welcome:"
cat ~/.ssh/config

# echo "TRYIN TO HACK THE SYSTEM"
# sudo pacman -S sshpass

sshpass -p $(cf ssh-code) rsync -r ./tdrs-backend/tdpservice/ $APP_NAME:/app/tdpservice
echo "I'm in."
