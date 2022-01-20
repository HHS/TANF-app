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
alias tdrs-compose-local='docker-compose -f docker-compose.yml -f docker-compose.local.yml'

# Stop tdrs backend entirely, then start it up again
alias tdrs-backend-hard-restart='tdrs-start-backend && tdrs-start-backend'

# shortcut for running bash commands in backend container
alias tdrs-backend-exec='tdrs-backend-compose exec web /bin/bash'

# Open shell_plus for django backend inside of container
alias tdrs-django-shell='tdrs-backend-compose run --rm web bash -c "python manage.py shell_plus"'

# TDRS Frontend aliases

# start both the frontend and backend
alias tdrs-start='tdrs-start-frontend && tdrs-start-backend'

# Stop both the frontend and the backend
alias tdrs-stop='tdrs-stop-frontend && tdrs-stop-backend'

# Restart frontend and backend
alias tdrs-restart='tdrs-restart-frontend && tdrs-restart-backend'

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
alias restart-django='tdrs-compose-django restart web'

# run flake8 against backend source from inside of web container
alias tdrs-lint-backend='tdrs-compose-backend run --rm web bash -c "flake8 ."'

# short cut for running compose sub commands on backend
tdrs-compose-backend() {
    cd-tdrs
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

# Run eslint against frontend source from frontend container
tdrs-lint-frontend() {
    cd-tdrs
    yarn lint
    cd ..
}

# Fix all automaticly fixable linting errors for the frontend
tdrs-fix-lint-frontend() {
    cd-tdrs
    eslint --fix ./src
    cd ..
}

tdrs-npm-run() {
    cd-tdrs
    cd tdrs-frontend/ && npm run $1
    cd ..
}

tdrs-run-jest() {
    tdrs-yarn test
}


tdrs-run-jest-cov() {
    tdrs-yarn test:cov
}

tdrs-run-pa11y() {
    cd tdrs-frontend; mkdir pa11y-screenshots/; yarn test:accessibility
}

# tdrs-run-owasp() {}

tdrs-run-migrations() {
    cd-tdrs
    cd tdrs-backend/
    docker-compose run web sh -c 'python manage.py migrate'
    cd ..
}

tdrs-merge-migrations() {
    cd-tdrs
    cd tdrs-backend/
    docker-compose run web sh -c 'python manage.py makemigrations --merge'
    cd ..
}

tdrs-prune-all-docker-data() {
    docker system prune -a
    docker system prune --volumes
}

tdrs-run-pytest () {

    cd-tdrs
    cd tdrs-backend/

    if [ "$#" -lt 1 ]; then
        quoted_args=""
    else
        quoted_args="$(printf " %q" "${@}")"
    fi
    tdrs-compose-local run --rm web bash -c "./wait_for_services.sh && pytest ${quoted_args}"
    cd ..
}
tdrs-run-backend-owasp() {
    cd-tdrs
    ./scripts/zap-scanner.sh backend circle
}

tdrs-run-frontend-owasp() {
    cd-tdrs
    ./scripts/zap-scanner.sh frontend circle
}
