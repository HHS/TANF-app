import os
import requests
import jwt
import secrets
import time
from jwcrypto import jwk
from urllib.parse import urlencode, quote_plus
from django.views.generic.base import RedirectView 
from django.http import HttpResponseRedirect, JsonResponse

from .utils import add_state_and_nonce_to_session

class LogoutRedirectOIDC(RedirectView): 
    permanent = False
    query_string = True
    pattern_name = 'oidc-logout'
    
    def get(self, request, *args, **kwargs):

        #generate a random secured hex string for the state parameter
        state = secrets.token_hex(32)   

        token_hint= request.session.get('token',"None")
        logout_params = {
            'id_token_hint': token_hint,
            'post_logout_redirect_uri': 'http://localhost:8000/logout',
            "state": state
        }
        #escape params dict into a url encoded query string
        encoded_params = urlencode(logout_params, quote_via=quote_plus)

        #build out full API GET call to authorize endpoint
        logout_endpoint  = os.environ['OIDC_OP_LOGOUT_ENDPOINT'] + '?' + encoded_params
        return HttpResponseRedirect(logout_endpoint)