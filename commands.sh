#!/usr/bin/sh
# You will need to set this variable to match your local directory structure
# TDRS_HOME="$HOME/Where/Ever/You/Want/TANF-app"

TDRS_HOME="$HOME/devel/goraft.tech/tdrs/instances/TANF-app"

# navigate terminal to tdrs home if $TDRS_HOME is set
alias cd-tdrs='cd "$TDRS_HOME"'

# navigate terminal to tdrs frontend if $TDRS_HOME is set
alias cd-tdrs-frontend='cd "$TDRS_HOME/tdrs-frontend"'

# navigate terminal to tdrs backend if $TDRS_HOME is set
alias cd-tdrs-backend='cd "$TDRS_HOME/tdrs-backend"'

# shortcut for applying all relavent compose files for local development
alias tdrs-compose-local='docker-compose -f docker-compose.yml -f docker-compose.local.yml'

# Stop tdrs backend entirely, then start it up again
alias tdrs-backend-hard-restart='tdrs-backend-down && tdrs-backend-up'

# run flake8 in backend container
alias tdrs-backend-lint='tdrs-backend-compose run --rm web bash -c "flake8 ."'

# shortcut for running bash commands in backend container
alias tdrs-backend-exec='tdrs-backend-compose exec web /bin/bash'

# Open shell_plus for django backend inside of container
alias tdrs-shell='tdrs-backend-compose run --rm web bash -c "python manage.py shell_plus"'

# TDRS Frontend aliases

# start both the frontend and backend
alias start-tdrs='tdrs-start-frontend && tdrs-start-backend'

# Stop both the frontend and the backend
alias stop-tdrs='tdrs-stop-frontend && tdrs-stop-backend'

# Restart frontend and backend
alias restart-tdrs='tdrs-restart-frontend && tdrs-restart-backend'

# start all backend containers
tdrs-start-backend() {
    cd-tdrs
    cd tdrs-backend && tdrs-compose-local up -d
    cd ..
}

# run npm install updating all dependencies and start the dev server
tdrs-start-frontend() {
    cd-tdrs
    cd tdrs-frontend && tdrs-compose-local up -d
    cd ..
}

# Stop all containers for the backend
tdrs-stop-backend() {
    cd-tdrs
    cd tdrs-backend && tdrs-compose-local down
    cd ..
}
# stop the frontend development server
tdrs-stop-frontend() {
    cd-tdrs
    cd tdrs-frontend && tdrs-compose-local down
    cd ..
}

# restart the frontends, mainly to rebuild dependencies
tdrs-restart-frontend() {
    cd-tdrs
    cd tdrs-frontend && tdrs-compose-local restart
    cd ..
}

# restart all containers for the backend
tdrs-restart-backend() {
    cd-tdrs
    cd tdrs-backend && tdrs-compose-local restart
    cd ..
}

# Stop the backend if its running and rebuild the docker container for django
tdrs-rebuild-backend() {
    cd-tdrs
    tdrs-stop-backend
    cd tdrs-backend && tdrs-compose-local up --build -d web
    cd ..
}

# to restart just django, keeping the other containers intact.
restart-django() {
    cd-tdrs
    cd tdrs-backend && docker-compose restart web
    cd ..
}

# run flake8 against backend source from inside of web container
tdrs-lint-backend() {
    cd-tdrs
    cd tdrs-backend/ && tdrs-compose-local run --rm web bash -c 'flake8 .'
    cd ..
}
# Run eslint against frontend source from frontend container
tdrs-lint-frontend() {
    cd-tdrs
    cd tdrs-frontend/ && tdrs-compose-local run --rm tdp-frontend bash -c 'yarn lint'
    cd ..
}

# Fix all automaticly fixable linting errors for the frontend
tdrs-fix-lint-frontend() {
    cd-tdrs
    cd tdrs-frontend/ && tdrs-compose-local run --rm tdp-frontend bash -c 'eslint --fix ./src'
    cd ..
}
# tdrs-run-jest() {}
# tdrs-run-pa11y() {}
# tdrs-run-pytest() {}
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
}

prune-docker-data() {
    docker system prune -a
    docker system prune --volumes
}

function pytest-tdrs () {
    if [ "$#" -lt 1 ]; then
        quoted_args=""
    else
        quoted_args="$(printf " %q" "${@}")"
    fi
    tdrs-backend-compose run --rm web bash -c "./wait_for_services.sh && pytest ${quoted_args}"
}
