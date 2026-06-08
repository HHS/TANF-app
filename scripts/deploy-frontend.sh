#!/bin/sh

# source deploy-util.sh

# The deployment strategy you wish to employ ( rolling update or setting up a new environment)
DEPLOY_STRATEGY=${1}

#The application name  defined via the manifest yml for the frontend
CGHOSTNAME_FRONTEND=${2}
CGAPPNAME_FRONTEND="tdp-frontend-${CGHOSTNAME_FRONTEND}"
CGHOSTNAME_BACKEND=${3}
CF_SPACE=${4}
ENVIRONMENT=${5}

env=${CF_SPACE#"tanf-"}

update_frontend()
{
    echo DEPLOY_STRATEGY: "$DEPLOY_STRATEGY"
    echo FRONTEND_HOST: "$CGHOSTNAME_FRONTEND"
    echo BACKEND_HOST: "$CGHOSTNAME_BACKEND"
    cd tdrs-frontend || exit

    if [ "$CF_SPACE" = "tanf-prod" ]; then
        echo "REACT_APP_BACKEND_URL=https://tanfdata.acf.hhs.gov/v1" >> .env.production
        echo "REACT_APP_AUTH_URL=https://tanfdata.acf.hhs.gov" >> .env.production
        echo "REACT_APP_FRONTEND_URL=https://tanfdata.acf.hhs.gov" >> .env.production
        echo "REACT_APP_BACKEND_HOST=https://tanfdata.acf.hhs.gov" >> .env.production
        echo "REACT_APP_LOGIN_GOV_URL=https://secure.login.gov/" >> .env.production
        echo "REACT_APP_CF_SPACE=$CF_SPACE" >> .env.production
        # RUM config
        echo "REACT_APP_ENABLE_RUM=true" >> .env.production
        echo "REACT_APP_FARO_ENDPOINT=https://tanfdata.acf.hhs.gov/collect" >> .env.production
        echo "REACT_APP_VERSION=v3.8.4" >> .env.production
        #Nginx
        echo "BACK_END=" >> .env.production
    elif [ "$CF_SPACE" = "tanf-staging" ]; then
        echo "REACT_APP_BACKEND_URL=https://$CGHOSTNAME_FRONTEND.tanfdata.acf.hhs.gov/v1" >> .env.development
        echo "REACT_APP_AUTH_URL=https://$CGHOSTNAME_FRONTEND.tanfdata.acf.hhs.gov" >> .env.development
        echo "REACT_APP_FRONTEND_URL=https://$CGHOSTNAME_FRONTEND.tanfdata.acf.hhs.gov" >> .env.development
        echo "REACT_APP_BACKEND_HOST=https://$CGHOSTNAME_FRONTEND.tanfdata.acf.hhs.gov" >> .env.development
        echo "REACT_APP_CF_SPACE=$CF_SPACE" >> .env.development

        cf set-env "$CGAPPNAME_FRONTEND" ALLOWED_ORIGIN "https://$CGHOSTNAME_FRONTEND.tanfdata.acf.hhs.gov"
        cf set-env "$CGAPPNAME_FRONTEND" CONNECT_SRC '*.tanfdata.acf.hhs.gov'
    else
        echo "REACT_APP_BACKEND_URL=https://$CGHOSTNAME_FRONTEND.tanfdata.acf.hhs.gov/v1" >> .env.development
        echo "REACT_APP_AUTH_URL=https://$CGHOSTNAME_FRONTEND.tanfdata.acf.hhs.gov" >> .env.development
        echo "REACT_APP_FRONTEND_URL=https://$CGHOSTNAME_FRONTEND.tanfdata.acf.hhs.gov" >> .env.development
        echo "REACT_APP_BACKEND_HOST=https://$CGHOSTNAME_FRONTEND.tanfdata.acf.hhs.gov" >> .env.development
        echo "REACT_APP_CF_SPACE=$CF_SPACE" >> .env.development

        cf set-env "$CGAPPNAME_FRONTEND" ALLOWED_ORIGIN "https://$CGHOSTNAME_FRONTEND.tanfdata.acf.hhs.gov"
        cf set-env "$CGAPPNAME_FRONTEND" CONNECT_SRC '*.tanfdata.acf.hhs.gov'
    fi

    cf set-env "$CGAPPNAME_FRONTEND" BACKEND_HOST "$CGHOSTNAME_BACKEND"

    yarn build:$ENVIRONMENT
    unlink .env.production
    mkdir deployment


    cp -r build deployment/public
    cp nginx/cloud.gov/buildpack.nginx.conf deployment/nginx.conf
    cp nginx/cloud.gov/locations.conf deployment/locations.conf
    cp nginx/cloud.gov/ip_whitelist_ipv4.conf deployment/ip_whitelist_ipv4.conf
    cp nginx/cloud.gov/ip_whitelist_ipv6.conf deployment/ip_whitelist_ipv6.conf
    if [ "$CGHOSTNAME_FRONTEND" = "develop" ]; then
        cp nginx/cloud.gov/ip_whitelist_develop.conf deployment/ip_whitelist.conf
        bash ../scripts/generate-circleci-ip-ranges.sh
    else
        cp nginx/cloud.gov/ip_whitelist.conf deployment/ip_whitelist.conf
    fi
    cp nginx/mime.types deployment/mime.types
    cp nginx/src/503.html deployment/public/503_.html
    cp -r nginx/src/static/ deployment/public/

    cp manifest.buildpack.yml deployment/manifest.buildpack.yml
    cd deployment || exit

    if [ "$1" = "rolling" ] ; then
        # Do a zero downtime deploy.  This requires enough memory for
        # two apps to exist in the org/space at one time.
        cf push "$CGAPPNAME_FRONTEND" --no-route -f manifest.buildpack.yml --strategy rolling || exit 1
    else
        cf push "$CGAPPNAME_FRONTEND" --no-route -f manifest.buildpack.yml
    fi

    if [ "$CF_SPACE" = "tanf-prod" ]; then
        cf map-route "$CGAPPNAME_FRONTEND" tanfdata.acf.hhs.gov
    elif [ "$CF_SPACE" = "tanf-staging" ]; then
        cf map-route "$CGAPPNAME_FRONTEND" "$CGHOSTNAME_FRONTEND".tanfdata.acf.hhs.gov
    else
        cf map-route "$CGAPPNAME_FRONTEND" tanfdata.acf.hhs.gov --hostname "${CGHOSTNAME_FRONTEND}"
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
