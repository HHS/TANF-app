#!/bin/bash
APP_NAME=$1
bash ./scripts/update-ssh-config.sh
sshpass -p $(cf ssh-code) rsync -r ./tdrs-backend/tdpservice/ $APP_NAME:/app/tdpservice
