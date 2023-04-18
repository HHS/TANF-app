#!/bin/sh

# source deploy-util.sh

# The deployment strategy you wish to employ ( rolling update or setting up a new environment)
DEPLOY_STRATEGY=${1}

#The application name  defined via the manifest yml for the frontend
CGHOSTNAME_FRONTEND=${2}
CGHOSTNAME_BACKEND=${3}
CF_SPACE=${4}
ENVIRONMENT=${5}

update_frontend()
{
    echo DEPLOY_STRATEGY: "$DEPLOY_STRATEGY"
    echo FRONTEND_HOST: "$CGHOSTNAME_FRONTEND"
    echo BACKEND_HOST: "$CGHOSTNAME_BACKEND"
    cd tdrs-frontend || exit

    if [ "$CF_SPACE" = "tanf-prod" ]; then
        echo "REACT_APP_BACKEND_URL=https://tanfdata.acf.hhs.gov/v1" >> .env.production
        echo "REACT_APP_FRONTEND_URL=https://tanfdata.acf.hhs.gov" >> .env.production
        echo "REACT_APP_BACKEND_HOST=https://tanfdata.acf.hhs.gov" >> .env.production
        echo "REACT_APP_LOGIN_GOV_URL=https://secure.login.gov/" >> .env.production
        echo "REACT_APP_CF_SPACE=$CF_SPACE" >> .env.production
        echo "BACK_END=" >> .env.production
    elif [ "$CF_SPACE" = "tanf-staging" ]; then
        echo "REACT_APP_BACKEND_URL=https://$CGHOSTNAME_FRONTEND.acf.hhs.gov/v1" >> .env.development
        echo "REACT_APP_FRONTEND_URL=https://$CGHOSTNAME_FRONTEND.acf.hhs.gov" >> .env.development
        echo "REACT_APP_BACKEND_HOST=https://$CGHOSTNAME_FRONTEND.acf.hhs.gov" >> .env.development
        echo "REACT_APP_CF_SPACE=$CF_SPACE" >> .env.development

        cf set-env "$CGHOSTNAME_FRONTEND" ALLOWED_ORIGIN "https://$CGHOSTNAME_FRONTEND.acf.hhs.gov"
        cf set-env "$CGHOSTNAME_FRONTEND" CONNECT_SRC '*.acf.hhs.gov'
    else
        echo "REACT_APP_BACKEND_URL=https://$CGHOSTNAME_FRONTEND.app.cloud.gov/v1" >> .env.development
        echo "REACT_APP_FRONTEND_URL=https://$CGHOSTNAME_FRONTEND.app.cloud.gov" >> .env.development
        echo "REACT_APP_BACKEND_HOST=https://$CGHOSTNAME_FRONTEND.app.cloud.gov" >> .env.development
        echo "REACT_APP_CF_SPACE=$CF_SPACE" >> .env.development

        cf set-env "$CGHOSTNAME_FRONTEND" ALLOWED_ORIGIN "https://$CGHOSTNAME_FRONTEND.app.cloud.gov"
        cf set-env "$CGHOSTNAME_FRONTEND" CONNECT_SRC '*.app.cloud.gov'
    fi

    cf set-env "$CGHOSTNAME_FRONTEND" BACKEND_HOST "$CGHOSTNAME_BACKEND"
    
    npm run build:$ENVIRONMENT
    unlink .env.production
    mkdir deployment

    cp -r build deployment/public
    cp nginx/cloud.gov/buildpack.nginx.conf deployment/nginx.conf
    cp nginx/cloud.gov/locations.conf deployment/locations.conf
    cp nginx/cloud.gov/ip_whitelist.conf deployment/ip_whitelist.conf
    cp nginx/mime.types deployment/mime.types

    cp manifest.buildpack.yml deployment/manifest.buildpack.yml
    cd deployment || exit

    if [ "$1" = "rolling" ] ; then
        # Do a zero downtime deploy.  This requires enough memory for
        # two apps to exist in the org/space at one time.
        cf push "$CGHOSTNAME_FRONTEND" --no-route -f manifest.buildpack.yml --strategy rolling || exit 1
    else
        cf push "$CGHOSTNAME_FRONTEND" --no-route -f manifest.buildpack.yml
    fi

    if [ "$CF_SPACE" = "tanf-prod" ]; then
        cf map-route "$CGHOSTNAME_FRONTEND" tanfdata.acf.hhs.gov
    elif [ "$CF_SPACE" = "tanf-staging" ]; then
        cf map-route "$CGHOSTNAME_FRONTEND" "$CGHOSTNAME_FRONTEND".acf.hhs.gov
    else
        cf map-route "$CGHOSTNAME_FRONTEND" app.cloud.gov --hostname "${CGHOSTNAME_FRONTEND}"
    fi
    
    cd ../..
    rm -r tdrs-frontend/deployment
}

# perform a rolling update for the backend and frontend deployments if
# specified, otherwise perform a normal deployment
if [ "$DEPLOY_STRATEGY" = "rolling" ] ; then
    update_frontend 'rolling'
else
    update_frontend
fi
