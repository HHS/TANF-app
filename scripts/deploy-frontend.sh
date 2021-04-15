#!/bin/sh

# source deploy-util.sh

# The deployment strategy you wish to employ ( rolling update or setting up a new environment)
DEPLOY_STRATEGY=${1}

# The environment in which you want to execute these commands
DEPLOY_ENV=${2}

#The application name  defined via the manifest yml for the frontend
CGHOSTNAME_FRONTEND=${3}
CGHOSTNAME_BACKEND=${4}


update_frontend()
{


    echo DEPLOY_STRATEGY: $DEPLOY_STRATEGY
    echo DEPLOY_ENV: $DEPLOY_ENV
    echo FRONTEND_HOST: $CGHOSTNAME_FRONTEND
    echo BACKEND_HOST: $CGHOSTNAME_BACKEND
    cd tdrs-frontend

    echo "REACT_APP_BACKEND_URL=https://$CGHOSTNAME_BACKEND.app.cloud.gov/v1" >> .env.production
    echo "REACT_APP_BACKEND_HOST=https://$CGHOSTNAME_BACKEND.app.cloud.gov" >> .env.production
    npm run build
    unlink .env.production
    mkdir deployment

    cp -r build deployment/public
    cp  nginx/buildpack.nginx.conf deployment/nginx.conf
    cp  nginx/mime.types deployment/mime.types

    cp manifest.buildpack.yml deployment/manifest.buildpack.yml

    cd deployment
	  if [ "$1" = "rolling" ] ; then
		    # Do a zero downtime deploy.  This requires enough memory for
		    # two apps to exist in the org/space at one time.
		    cf push $CGHOSTNAME_FRONTEND --no-route -f manifest.buildpack.yml --strategy rolling || exit 1
	  else
		    cf push $CGHOSTNAME_FRONTEND --no-route -f manifest.buildpack.yml
	  fi
	  cf map-route $CGHOSTNAME_FRONTEND app.cloud.gov --hostname "${CGHOSTNAME_FRONTEND}"
    cd ../..
    rm -r tdrs-frontend/deployment
}


# perform a rolling update for the backend and frontend deployments if specifed,
# otherwise perform a normal deployment 
if [ $DEPLOY_STRATEGY = "rolling" ] ; then

	  update_frontend 'rolling'
else
	  update_frontend
fi
