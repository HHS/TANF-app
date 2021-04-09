#!/bin/sh
#
# This script will attempt to create the services required
# and then launch everything.
#

# The deployment strategy you wish to employ ( rolling update or setting up a new environment)
DEPLOY_STRATEGY=${1}

# The environment in which you want to execute these commands
DEPLOY_ENV=${2}

#The application name  defined via the manifest yml for the backend
CGHOSTNAME_BACKEND=${3}

#The application name  defined via the manifest yml for the frontend
CGHOSTNAME_FRONTEND=${4}

#The docker image to beferenced for the backend deployment ( please ensure this
#is pushed to a public docker repo)
DOCKER_IMAGE_BACKEND=${5}

#The docker image to beferenced for the frontend deployment 
#(please ensure this is pushed to a public docker repo)
DOCKER_IMAGE_FRONTEND=${6}

#The Github Branch triggered to execure this script if triggered in circleci
CIRCLE_BRANCH=${7}

echo DEPLOY_STRATEGY: $DEPLOY_STRATEGY
echo DEPLOY_ENV=$DEPLOY_ENV
echo BACKEND_HOST: $CGHOSTNAME_BACKEND
echo FRONTEND_HOST: $CGHOSTNAME_FRONTEND
echo DOCKER_BACKEND_IMAGE: $DOCKER_IMAGE_BACKEND
echo DOCKER_FRONTEND_IMAGE: $DOCKER_IMAGE_FRONTEND
echo CIRCLE_BRANCH=$CIRCLE_BRANCH


# function to check if a service exists
service_exists()
{
  cf service "$1" >/dev/null 2>&1
}


# Performs a normal deployment unless rolling is specified in the fucntion call
update_frontend()
{
	if [ "$1" = "rolling" ] ; then
		# Do a zero downtime deploy.  This requires enough memory for
		# two apps to exist in the org/space at one time.
		#The `--var` parameter ingest a value into the ((docker-frontend)) environment variable in the manifest.yml**
		cf push $CGHOSTNAME_FRONTEND --no-route -f tdrs-frontend/manifest.yml --var docker-frontend=$DOCKER_IMAGE_FRONTEND --strategy rolling || exit 1
	else
		cf push $CGHOSTNAME_FRONTEND --no-route -f tdrs-frontend/manifest.yml --var docker-frontend=$DOCKER_IMAGE_FRONTEND
	fi
	cf map-route $CGHOSTNAME_FRONTEND app.cloud.gov --hostname "${CGHOSTNAME_FRONTEND}"
}

# Performs a normal deployment unless rolling is specified in the fucntion call
update_backend()
{
	if [ "$1" = "rolling" ] ; then
		# Do a zero downtime deploy.  This requires enough memory for
		# two apps to exist in the org/space at one time.
		#The `--var` parameter ingest a value into the ((docker-backend)) environment variable in the manifest.yml**
		cf push $CGHOSTNAME_BACKEND --no-route -f tdrs-backend/manifest.yml --var docker-backend=$DOCKER_IMAGE_BACKEND --strategy rolling || exit 1

	else
		cf push $CGHOSTNAME_BACKEND --no-route -f tdrs-backend/manifest.yml --var docker-backend=$DOCKER_IMAGE_BACKEND
		# set up JWT key if needed
		if cf e $CGHOSTNAME_BACKEND | grep -q JWT_KEY ; then
		   echo jwt cert already created
		else
		   generate_jwt_cert
	   fi
	fi
	cf map-route $CGHOSTNAME_BACKEND app.cloud.gov --hostname "$CGHOSTNAME_BACKEND"

	# Deploy the latest ClamAV REST server alongside the backend
	echo "Deploying clamav..."
	cf push clamav-rest --strategy rolling -f tdrs-backend/manifest.yml
}

# perform a rolling update for the backend and frontend deployments if specifed,
# otherwise perform a normal deployment 
if [ $DEPLOY_STRATEGY = "rolling" ] ; then

	update_backend 'rolling'
	update_frontend 'rolling'
else 
    update_backend 
	update_frontend 
fi

# create a new deployment environment 
# Setup needed services
# Deploy the backend
# Bind the backend to needed services
# Deploy the frontend
if [ "$1" = "setup" ] ; then  echo
	# create services (if needed)
	if service_exists "tdp-app-deployer" ; then
	  echo tdp-app-deployer already created
	else
	  cf create-service cloud-gov-service-account space-deployer tdp-app-keys
	  cf create-service-key tdp-app-keys deployer
	  echo "to get the CF_USERNAME and CF_PASSWORD, execute 'cf service-key tdp-app-keys deployer'"
	fi

	if service_exists "tdp-db" ; then
	  echo tdp-db already created
	else
	  if [ $DEPLOY_ENV = "prod" ] ; then
	    cf create-service aws-rds medium-psql-redundant tdp-db
		  echo sleeping until db is awake
		  for i in 1 2 3 ; do
		  	sleep 60
		  	echo $i minutes...
		  done
	  else
	    cf create-service aws-rds shared-psql tdp-db
	    sleep 2
	  fi
	fi

	# set up backend
	if cf app $CGHOSTNAME_BACKEND >/dev/null 2>&1 ; then
		echo $CGHOSTNAME_BACKEND app already set up
	else
	    update_backend
		cf bind-service $CGHOSTNAME_BACKEND tdp-db
		cf restage $CGHOSTNAME_BACKEND
	fi

	# set up frontend
	if cf app $CGHOSTNAME_FRONTEND >/dev/null 2>&1 ; then
		echo $CGHOSTNAME_FRONTEND app already set up
	else
	    update_frontend
	fi
fi

#Helper method to generate JWT cert and keys for new environment
generate_jwt_cert() 
{
	echo "regenerating JWT cert/key"
	yes 'XX' | openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -sha256
	cf set-env $CGHOSTNAME_BACKEND JWT_CERT "$(cat cert.pem)"
	cf set-env $CGHOSTNAME_BACKEND JWT_KEY "$(cat key.pem)"

	# make sure that we have something set that you can later override with the
	# proper value so that the app can start up
	if cf e $CGHOSTNAME_BACKEND | grep -q OIDC_RP_CLIENT_ID ; then
		echo OIDC_RP_CLIENT_ID already set up
	else
		echo "once you have gotten your client ID set up with login.gov, you will need to set the OIDC_RP_CLIENT_ID to the proper value"
		echo "you can do this by running: cf set-env tdp-backend OIDC_RP_CLIENT_ID 'your_client_id'"
		echo "login.gov will need this cert when you are creating the app:"
		cat cert.pem
		cf set-env $CGHOSTNAME_BACKEND OIDC_RP_CLIENT_ID "XXX"
	fi
}

# Tell people where to go
echo
echo
echo "to log into the site, you will want to go to https://${CGHOSTNAME_FRONTEND}.app.cloud.gov/"
echo 'Have fun!'