# Generates and sets JWT cert and keys for new environment.
# Called as part of new environment setup.

echo "regenerating JWT cert/key"
yes 'XX' | openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -sha256
cf set-env $CGHOSTNAME_BACKEND JWT_CERT "$(cat cert.pem)"
cf set-env $CGHOSTNAME_BACKEND JWT_KEY "$(cat key.pem)"

# Let user of this script know that they will need fto set an OIDC_RP_CLIENT_ID.
if cf e $CGHOSTNAME_BACKEND | grep -q OIDC_RP_CLIENT_ID ; then
  echo OIDC_RP_CLIENT_ID already set up
else
  echo "once you have gotten your client ID set up with login.gov, you will need to set the OIDC_RP_CLIENT_ID to the proper value"
  echo "you can do this by running: cf set-env tdp-backend OIDC_RP_CLIENT_ID 'your_client_id'"
  echo "login.gov will need this cert when you are creating the app:"
  cat cert.pem
  cf set-env $CGHOSTNAME_BACKEND OIDC_RP_CLIENT_ID "XXX"
fi
