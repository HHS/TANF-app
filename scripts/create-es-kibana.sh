#!/bin/bash

##############################
# Global Variable Decls 
##############################

# The deployment strategy you wish to employ ( rolling update or setting up a new environment)
DEPLOY_STRATEGY=${1}
CF_SPACE=${2}             # dev, staging, prod


#The application name  defined via the manifest yml for the frontend
CGAPPNAME_KIBANA="tdp-kibana"
CGAPPNAME_PROXY="tdp-elastic-proxy"


strip() {
    # Usage: strip "string" "pattern"
    printf '%s\n' "${1##$2}"
}
# The cloud.gov space defined via environment variable (e.g., "tanf-dev", "tanf-staging")
env=$(strip $CF_SPACE "tanf-")

# Update the Kibana and Elastic proxy names to include the environment
CGAPPNAME_KIBANA="${CGAPPNAME_KIBANA}-${env}" # tdp-kibana-staging, tdp-kibana-prod, tdp-kibana-dev
CGAPPNAME_PROXY="${CGAPPNAME_PROXY}-${env}"   # tdp-elastic-proxy-staging, tdp-elastic-proxy-prod, tdp-elastic-proxy-dev

echo DEPLOY_STRATEGY: "$DEPLOY_STRATEGY"
echo KIBANA_HOST: "$CGAPPNAME_KIBANA"
echo ELASTIC_PROXY_HOST: "$CGAPPNAME_PROXY"
echo CF_SPACE: "$CF_SPACE"
echo env: "$env"


update_kibana()
{
  cd ../tdrs-backend || exit

  # Run template evaluation on manifest
  # 2814: need to update this and set it to env instaead of app name
  yq eval -i ".applications[0].services[0] = \"es-${env}\""  manifest.proxy.yml
  yq eval -i ".applications[0].env.CGAPPNAME_PROXY = \"${CGAPPNAME_PROXY}\""  manifest.kibana.yml

  if [ "$1" = "rolling" ] ; then
      # Do a zero downtime deploy.  This requires enough memory for
      # two apps to exist in the org/space at one time.
      cf push "$CGAPPNAME_PROXY" --no-route -f manifest.proxy.yml -t 180 --strategy rolling || exit 1
      cf push "$CGAPPNAME_KIBANA" --no-route -f manifest.kibana.yml -t 180 --strategy rolling || exit 1
  else
      cf push "$CGAPPNAME_PROXY" --no-route -f manifest.proxy.yml -t 180
      cf push "$CGAPPNAME_KIBANA" --no-route -f manifest.kibana.yml -t 180
  fi
  
  cf map-route "$CGAPPNAME_PROXY" apps.internal --hostname "$CGAPPNAME_PROXY"
  cf map-route "$CGAPPNAME_KIBANA" apps.internal --hostname "$CGAPPNAME_KIBANA"

  # Add network policy allowing Kibana to talk to the proxy and to allow the backend to talk to Kibana
  cf add-network-policy "$CGAPPNAME_KIBANA" "$CGAPPNAME_PROXY" --protocol tcp --port 8080
  cd ..
}

##############################
# Main script body
##############################

echo "Deploying Kibana and Elastic Proxy to $CF_SPACE"
echo "Deploy strategy: $DEPLOY_STRATEGY"

if [ "$DEPLOY_STRATEGY" = "rolling" ] ; then
    # Perform a rolling update for the backend and frontend deployments if
    # specified, otherwise perform a normal deployment
    update_kibana 'rolling'
elif [ "$DEPLOY_STRATEGY" = "bind" ] ; then
    # Bind the services the application depends on and restage the app.
    echo "Deploying Kibana and Elastic Proxy to $CF_SPACE"
elif [ "$DEPLOY_STRATEGY" = "initial" ]; then
    # There is no app with this name, and the services need to be bound to it
    # for it to work. the app will fail to start once, have the services bind,
    # and then get restaged.
    update_kibana
elif [ "$DEPLOY_STRATEGY" = "rebuild" ]; then
    # You want to redeploy the instance under the same name
    # Delete the existing app (with out deleting the services)
    # and perform the initial deployment strategy.
    cf delete "$CGAPPNAME_KIBANA" -r -f
    cf delete "$CGAPPNAME_PROXY" -r -f
    update_kibana
else
    # No changes to deployment config, just deploy the changes and restart
    update_kibana
fi
