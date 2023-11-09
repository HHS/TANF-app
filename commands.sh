#!/usr/bin/sh
# You will need to set this variable to match your local directory structure
# TDRS_HOME="$HOME/Where/Ever/You/Want/TANF-app"

# navigate terminal to tdrs home if $TDRS_HOME is set
alias cd-tdrs='cd "$TDRS_HOME"'

# navigate terminal to tdrs frontend if $TDRS_HOME is set
alias cd-tdrs-frontend='cd "$TDRS_HOME/tdrs-frontend"'

# navigate terminal to tdrs backend if $TDRS_HOME is set
alias cd-tdrs-backend='cd "$TDRS_HOME/tdrs-backend"'

# shortcut for applying all relavent compose files for local development
# I.E. `cd-tdrs-frontend && tdrs-compose-local up`
alias tdrs-compose-local='docker-compose -f docker-compose.local.yml'

# Stop tdrs backend entirely, then start it up again
alias tdrs-backend-hard-restart='tdrs-stop-backend && tdrs-start-backend'

# shortcut for running bash commands in backend container
alias tdrs-backend-exec='tdrs-compose-backend exec web /bin/bash'

# Open shell_plus for django backend inside of container
alias tdrs-django-shell='tdrs-compose-backend run --rm web bash -c "python manage.py shell_plus"'

# start both the frontend and backend
alias tdrs-start='tdrs-start-backend && tdrs-start-frontend'

# Stop both the frontend and the backend
alias tdrs-stop='tdrs-stop-frontend && tdrs-stop-backend'

# Restart frontend and backend
alias tdrs-restart='tdrs-restart-backend && tdrs-restart-frontend' 

# start all backend containers
alias tdrs-start-backend='tdrs-compose-backend up -d'

# run npm install updating all dependencies and start the dev server
alias tdrs-start-frontend='tdrs-compose-frontend up -d'

# Stop all containers for the backend
alias tdrs-stop-backend='tdrs-compose-backend down'

# stop the frontend development server
alias tdrs-stop-frontend='tdrs-compose-frontend down'

# restart the frontends, mainly to rebuild dependencies
alias tdrs-restart-frontend='tdrs-compose-frontend restart'

# restart all containers for the backend
alias tdrs-restart-backend='tdrs-compose-backend restart'

# to restart just django, keeping the other containers intact.
alias tdrs-restart-django='tdrs-compose-backend restart web'

# starts containers with the optional clamav image
alias tdrs-start-av='tdrs-start-frontend --remove-orphans && cd-tdrs-backend && tdrs-compose-local up -d --remove-orphans && docker-compose up -d clamav-rest && cd ..'

# Run frontend unit tests through jest
alias tdrs-run-jest='tdrs-npm-run test'

# Run frontend unit tests through jest with coverage report
alias tdrs-run-jest-cov='tdrs-npm-run test:cov'

# run any new migrations for django backend
alias tdrs-run-migrations='tdrs-compose-backend run web python manage.py migrate'

# Generate new migrations from changes to models for django backend
alias tdrs-make-migrations='tdrs-compose-backend run --rm web python manage.py makemigrations'

# Nuke all non running docker data
alias tdrs-prune-all-docker-data='docker system prune -a && docker system prune --volumes'

# Run eslint against frontend source from frontend container
alias tdrs-lint-frontend='tdrs-npm-run lint'

# Opens up logs for backend
alias tdrs-logs-backend='docker logs tdrs-backend-web-1 -f'

# Update backend lockfile
alias tdrs-piplock="tdrs-compose-backend run --rm web pipenv lock"

# I had to deal with the following issue:
# https://stackoverflow.com/questions/27093746/django-stops-working-with-runtimeerror-populate-isnt-reentrant
# So let's create an alias to ssh into container and sed the file
alias tdrs-fix-django-populate='tdrs-backend-exec && sed -i "s/raise Runtime..populate.. isn.t reentrant../self.app_configs = {}/g" /usr/local/lib/python3.10/site-packages/django/apps/registry.py'

# A recurring pattern I was doing to get a fresh setup
alias tdrs-fresh-start='tdrs-stop && docker system prune --volumes && tdrs-start'

# Deploy current branch to the given environment
# See comments in main function for to set up Circle CI token
alias tdrs-deploy='tdrs-run-deploy'

# run flake8 against backend source from inside of web container
tdrs-lint-backend() {
    tdrs-compose-backend run --rm web bash -c "flake8 . && if [ $? -eq 0 ]; then echo 'Flake8 linter found no issues'; fi"
}

# create docker network for tdrs if it doesn't exist
 tdrs-docker-net() {
     docker network inspect external-net >/dev/null 2>&1 \
     || docker network create external-net
 }

# short cut for running compose sub commands on backend
tdrs-compose-backend() {
    cd-tdrs
    tdrs-docker-net
    cd tdrs-backend && tdrs-compose-local $@
    cd ..
}

# short cut for running compose sub commands on backend
tdrs-compose-frontend() {
    cd-tdrs
    cd tdrs-frontend && tdrs-compose-local $@
    cd ..
}

# Stop the backend if its running and rebuild the docker container for django
tdrs-rebuild-backend() {
    cd-tdrs
    tdrs-stop-backend
    cd tdrs-backend && tdrs-compose-local up --build -d web
    cd ..
}

# Fix all automatically fixable linting errors for the frontend
tdrs-fix-lint-frontend() {
    cd-tdrs-frontend
    eslint --fix ./src
    cd ..
}

# Shortcut for running npm scripts for the frontend
tdrs-npm-run() {
    cd-tdrs
    cd tdrs-frontend/ && npm run $@
    cd ..
}

# Run pa11y tests on frontend
tdrs-run-pa11y() {
    cd tdrs-frontend; mkdir pa11y-screenshots/; npm run test:accessibility
    cd ..
}


# Spin up backend services and run pytest in docker
tdrs-run-pytest () {

    cd-tdrs
    tdrs-start-av
    cd tdrs-backend/

    # to escape quoted arguements that would be passed to docker inside of a quote
    if [ "$#" -lt 1 ]; then
        quoted_args=""
    else
        quoted_args="$(printf " %q" "${@}")"
    fi
    tdrs-compose-local run --rm web bash -c "./wait_for_services.sh && pytest ${quoted_args}"
    cd ..
}


# Run owasp scan for backend assuming circle ci environment
tdrs-run-backend-owasp() {
    if [[ $(docker network inspect external-net 2>&1 | grep -c Scope) == 0 ]]; then 
        docker network create external-net
    fi
    cd-tdrs-backend

    # We don't need to use the local compose file
    # because we are trying to simulate a production environment

    docker-compose up -d --build
    docker-compose run --rm zaproxy bash -c \
                   "PATH=$PATH:/home/zap/.local/bin &&
               pip install wait-for-it &&
               wait-for-it --service http://web:8080 \
                           --timeout 60 \
                           -- echo \"Django is ready\""
    cd ..
    cd-tdrs-frontend
    docker-compose up -d --build
    cd ..
    ./scripts/zap-scanner.sh backend circle
}

# Run owasp scan for frontend assuming circle ci environment
tdrs-run-frontend-owasp() {
    if [[ $(docker network inspect external-net 2>&1 | grep -c Scope) == 0 ]]; then 
        docker network create external-net
    fi
    cd-tdrs-backend

    # We don't need to use the local compose file
    # because we are trying to simulate a production environment

    docker-compose up -d --build
    docker-compose run --rm zaproxy bash -c \
                   "PATH=$PATH:/home/zap/.local/bin &&
               pip install wait-for-it &&
               wait-for-it --service http://web:8080 \
                           --timeout 60 \
                           -- echo \"Django is ready\""
    cd ..
    cd-tdrs-frontend
    docker-compose up -d --build
    cd ..
    ./scripts/zap-scanner.sh frontend circle
}

tdrs-run-deploy() {
    # Circle CI token can be generated here: https://app.circleci.com/settings/user/tokens
    # Once generated add it to your shell profile as CIRCLE_CI_TOKEN
    # Use like: tdrs-deploy sandbox
    TARGET_ENV=$1
    BRANCH=$(git rev-parse --abbrev-ref HEAD)

    echo "Deploying branch $BRANCH to $TARGET_ENV"

    curl --request POST \
    --url https://circleci.com/api/v2/project/github/raft-tech/TANF-app/pipeline \
    --header 'Circle-Token: '$CIRCLE_CI_TOKEN \
    --header 'content-type: application/json' \
    --data '{"parameters":{"run_dev_deployment": true, "target_env":"'$TARGET_ENV'"}, "branch":"'$BRANCH'"}'
}

# List all aliases and functions associated with tdrs
alias tdrs-functions='declare -F|grep tdrs && alias|grep tdrs|cut -d" " -f1 --complement'

# Get logs on backend
alias tdrs-backend-log="docker logs $(docker ps|grep web|awk '{print $1}')"
