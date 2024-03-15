#!/bin/bash

sshcfg=~/.ssh/config
echo "" > $sshcfg

for host in a11y raft qasp; do
	guid=$(cf curl /v3/apps/$(cf app "tdp-backend-$host" --guid)/processes | jq --raw-output '.resources | .[] | select(.type == "web").guid')
	echo "Host $host
	  HostName ssh.fr.cloud.gov
	  Port 2222
	  User cf:$guid/0
	  
	  " >> $sshcfg
done
cat $sshcfg
