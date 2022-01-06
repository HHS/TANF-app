# You will need to set this variable to match your local directory structure
# TDRS_HOME="$HOME/Where/Ever/You/Want/TANF-app"

export TDRS_HOME="$HOME/devel/goraft.tech/tdrs/instances/TANF-app"

alias cd-tdrs='cd "$TDRS_HOME"'
alias cd-tdrs-frontend='cd "$TDRS_HOME/tdrs-frontend"'
alias cd-tdrs-backend='cd "$TDRS_HOME/tdrs-backend"'
alias tdrs-compose-local='docker-compose -f docker-compose.yml -f docker-compose.local.yml'

alias tdrs-backend-hard-restart='tdrs-backend-down && tdrs-backend-up'
alias tdrs-backend-rebuild='tdrs-backend-down && tdrs-backend-compose up --build -d web'
alias tdrs-backend-lint='tdrs-backend-compose run --rm web bash -c "flake8 ."'
alias tdrs-backend-exec='tdrs-backend-compose exec web /bin/bash'
alias tdrs-shell='tdrs-backend-compose run --rm web bash -c "python manage.py shell_plus"'

# TDRS Frontend aliases
# alias cd-tdrs-frontend='cd "$TDRS_HOME/tdrs-frontend"'
alias tdrs-frontend-compose='docker-compose -f docker-compose.yml -f docker-compose.local.yml'
alias tdrs-frontend-down='tdrs-frontend-compose down'
alias tdrs-frontend-up='tdrs-frontend-compose up -d tdp-frontend'
alias tdrs-frontend-restart='tdrs-frontend-compose restart tdp-frontend'
alias tdrs-frontend-hard-restart='tdrs-frontend-down && tdrs-frontend-up'
alias tdrs-frontend-rebuild='tdrs-frontend-compose down && tdrs-frontend-compose up --build -d tdp-frontend'

alias start-tdrs="tdrs-start-frontend && tdrs-start-backend"
alias stop-tdrs="tdrs-stop-frontend && tdrs-stop-backend"
alias restart-tdrs="tdrs-restart-frontend && tdrs-restart-backend"

tdrs-start-backend() {
    cd-tdrs
    cd tdrs-backend && tdrs-compose-local up
    cd ..
}
tdrs-start-frontend() {
    cd-tdrs
    cd tdrs-frontend && tdrs-compose-local up
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

# to restart just django, keeping the other containers intact.
restart-django() {
    cd-tdrs
    cd tdrs-backend && docker-compose restart web
    cd ..
}


stop-tdrs() {
    tdrs-stop-frontend && tdrs-stop-backend
}
