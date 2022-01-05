# You will need to set this variable to match your local directory structure
# TDRS_HOME="$HOME/Where/Ever/You/Want/TANF-app"

TDRS_HOME="$HOME/devel/goraft.tech/tdrs/instances/TANF-app"

alias cd-tdrs=cd "$TDRS_HOME/tdrs-frontend"
alias cd-tdrs-frontend='cd "$TDRS_HOME/tdrs-frontend"'
alias cd-tdrs-backend='cd "$TDRS_HOME/tdrs-backend"'

alias tdrs-backend-compose='cd-tdrs-backend && docker-compose -f docker-compose.yml -f docker-compose.local.yml'

alias tdrs-backend-down='tdrs-backend-compose down'
alias tdrs-backend-up='tdrs-backend-compose up -d web'


alias tdrs-backend-restart='tdrs-backend-compose restart web'

tdrs-start-backend() {
    cd-tdrs
    tdrs-backend up
    cd ..
}
tdrs-start-frontend() {
    cd-tdrs
    cd tdrs-frontend && docker-compose -f docker-compose.yml -f docker-compose.local.yml up -d
    cd ..
}
tdrs-stop-backend() {
    cd-tdrs
    cd tdrs-backend && docker-compose down
    cd ..
}
tdrs-stop-frontend() {
    cd-tdrs
    cd tdrs-frontend && docker-compose down
    cd ..
}
tdrs-restart-frontend() {
    cd-tdrs
}
