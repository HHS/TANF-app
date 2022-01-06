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

# rebuild backend docker containers
alias tdrs-backend-rebuild='tdrs-backend-down && tdrs-backend-compose up --build -d web'

# run flake8 in backend container
alias tdrs-backend-lint='tdrs-backend-compose run --rm web bash -c "flake8 ."'

# shortcut for running bash commands in backend container
alias tdrs-backend-exec='tdrs-backend-compose exec web /bin/bash'

# Open shell_plus for django backend inside of container
alias tdrs-shell='tdrs-backend-compose run --rm web bash -c "python manage.py shell_plus"'

# TDRS Frontend aliases

alias tdrs-frontend-down='tdrs-frontend-compose down'
alias tdrs-frontend-up='tdrs-frontend-compose up -d tdp-frontend'

alias tdrs-frontend-restart='tdrs-frontend-compose restart tdp-frontend'
alias tdrs-frontend-hard-restart='tdrs-frontend-down && tdrs-frontend-up'
alias tdrs-frontend-rebuild='tdrs-frontend-compose down && tdrs-frontend-compose up --build -d tdp-frontend'

alias start-tdrs='tdrs-start-frontend && tdrs-start-backend'
alias stop-tdrs='tdrs-stop-frontend && tdrs-stop-backend'
alias restart-tdrs='tdrs-restart-frontend && tdrs-restart-backend'

tdrs-start-backend() {
    cd-tdrs
    cd tdrs-backend && tdrs-compose-local up
    cd ..
}

tdrs-start-frontend() {
    cd-tdrs
    cd tdrs-frontend && tdrs-compose-local up -d
    cd ..
}
tdrs-stop-backend() {
    cd-tdrs
    cd tdrs-backend && tdrs-compose-local down
    cd ..
}
tdrs-stop-frontend() {
    cd-tdrs
    cd tdrs-frontend && tdrs-compose-local down
    cd ..
}
tdrs-restart-frontend() {
    cd-tdrs
    cd tdrs-frontend && tdrs-compose-local restart
    cd ..
}

tdrs-restart-backend() {
    cd-tdrs
    cd tdrs-backend && tdrs-compose-local restart
    cd ..
}

tdrs-rebuild-backend() {
    cd-tdrs
    cd tdrs-backend && tdrs-backend-rebuild
    cd ..
}

# to restart just django, keeping the other containers intact.
restart-django() {
    cd-tdrs
    cd tdrs-backend && docker-compose restart web
    cd ..
}
