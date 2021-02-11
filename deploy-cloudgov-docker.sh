#!/bin/sh
#

# WHAT THIS DOES

# This script creates and launches the Cloud.gov services required to run the TDP app.

# DEPENDENCIES

# This script assumes that the user is logged in to Cloud.gov via the Cloud Foundry CLI,
# and has permissions to provision services in the relevant Cloud.gov spaces and orgs.
# For more, see: https://cloud.gov/docs/getting-started/setup/.

# ARGUMENTS

# The deployment strategy you wish to employ.
# One of "rolling" (rolling update; deploy) or "setup" (setting up a new environment).
DEPLOY_STRATEGY=${1}

# The environment in which you want to execute these commands.
# If set to "prod", provisions medium-psql-redundant in Cloud.gov instead of shared-psql.
# For more, see: https://cloud.gov/docs/services/relational-database/.
# (TODO: Consider renaming this argument to better reflect what it does.)
DEPLOY_ENV=${2}

# The application name supplied to the manifest yml for the backend.
CGHOSTNAME_BACKEND=${3}

# The application name supplied to the manifest yml for the frontend.
CGHOSTNAME_FRONTEND=${4}

# The docker image referenced for the backend deployment.
# Please ensure this is published in a public docker repo.
DOCKER_IMAGE_BACKEND=${5}

# The docker image referenced for the backend deployment.
# Please ensure this is published in a public docker repo.
DOCKER_IMAGE_FRONTEND=${6}

echo DEPLOY_STRATEGY: $DEPLOY_STRATEGY
echo DEPLOY_ENV=$DEPLOY_ENV
echo BACKEND_HOST: $CGHOSTNAME_BACKEND
echo FRONTEND_HOST: $CGHOSTNAME_FRONTEND
echo DOCKER_BACKEND_IMAGE: $DOCKER_IMAGE_BACKEND
echo DOCKER_FRONTEND_IMAGE: $DOCKER_IMAGE_FRONTEND

# EXAMPLES

# For an example rolling deploy:
# See .circleci/config.yml, which calls this script as part of the deploy process.

# Example vendor staging deploy:
# ./deploy-cloudgov-docker.sh setup test tdp-backend-vendor-staging tdp-frontend-vendor-staging lfrohlich/tdp-backend:raft-tdp-main lfrohlich/tdp-frontend:raft-tdp-main

# Remember, the script assumes that the user is logged in to Cloud.gov via the Cloud Foundry CLI.

# SCRIPT HELPERS AND TASKS

# Helper function to check if a service exists.
service_exists()
{
	cf service "$1" >/dev/null 2>&1
}

# Performs a normal deployment unless rolling is specified:
update_frontend()
{
	if [ "$1" = "rolling" ] ; then
		# Do a zero downtime deploy.
		# This requires enough memory for two apps to exist in the org/space at one time.
		# The `--var` parameter ingests a value into the ((docker-backend)) environment variable in the manifest.yml.
		cf push $CGHOSTNAME_FRONTEND --no-route -f tdrs-frontend/manifest.yml --var docker-frontend=$DOCKER_IMAGE_FRONTEND --strategy rolling || exit 1
	else
		cf push $CGHOSTNAME_FRONTEND --no-route -f tdrs-frontend/manifest.yml --var docker-frontend=$DOCKER_IMAGE_FRONTEND
		echo "Set REACT_APP_BACKEND_URL ENV variable for the frontend if not already set."
	fi
	cf map-route $CGHOSTNAME_FRONTEND app.cloud.gov --hostname "${CGHOSTNAME_FRONTEND}"
}

# Performs a normal deployment unless rolling is specified:
update_backend()
{
	if [ "$1" = "rolling" ] ; then
		# Do a zero downtime deploy.
		# This requires enough memory for two apps to exist in the org/space at one time.
		# The `--var` parameter ingests a value into the ((docker-backend)) environment variable in the manifest.yml.
		cf push $CGHOSTNAME_BACKEND --no-route -f tdrs-backend/manifest.yml --var docker-backend=$DOCKER_IMAGE_BACKEND --strategy rolling || exit 1

	else
		cf push $CGHOSTNAME_BACKEND --no-route -f tdrs-backend/manifest.yml --var docker-backend=$DOCKER_IMAGE_BACKEND
		# Set up JWT key if needed:
		if cf e $CGHOSTNAME_BACKEND | grep -q JWT_KEY ; then
			echo "jwt cert already created."
		else
			echo "jwt cert needs to be created and set: see generate_jwt_cert.sh in the /scripts folder."
		fi
	fi
	cf map-route $CGHOSTNAME_BACKEND app.cloud.gov --hostname "$CGHOSTNAME_BACKEND"
}

# Perform a rolling update for the backend and frontend deployments if specifed,
# otherwise perform a normal deployment, e.g. for setting up a new app.
if [ $DEPLOY_STRATEGY = "rolling" ] ; then
	update_backend 'rolling'
	update_frontend 'rolling'
else
	update_backend
	update_frontend
fi

# 1. Create a new deployment environment.
# 2. Setup needed services.
# 3. Deploy the backend.
# 4. Bind the backend to needed services.
# 5. Deploy the frontend.
if [ "$1" = "setup" ] ; then echo
	# Create services (if needed):
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
			cf bind-service $CGHOSTNAME_BACKEND tdp-db
			cf restage $CGHOSTNAME_BACKEND

			echo sleeping until db is awake
			for i in 1 2 3 ; do
				sleep 60
				echo $i minutes...
			done
		else
			cf create-service aws-rds shared-psql tdp-db
			cf bind-service $CGHOSTNAME_BACKEND tdp-db
			cf restage $CGHOSTNAME_BACKEND

			sleep 2
		fi
	fi
fi

# Tell people where to go:
echo
echo
echo "to log into the site, you will want to go to https://${CGHOSTNAME_FRONTEND}.app.cloud.gov/"
echo 'Have fun!'