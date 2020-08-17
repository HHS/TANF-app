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

class LoginRedirectOIDC(RedirectView): 
    permanent = False
    query_string = True
    pattern_name = 'oidc-auth'
    
    def get(self, request, *args, **kwargs):
        state = secrets.token_hex(32)
        nonce = secrets.token_hex(32)
        auth_params = {
            'acr_values': os.environ['ACR_VALUES'],
            'client_id': os.environ['CLIENT_ID'],
            'nonce': nonce,
            "prompt": 'select_account',
            'redirect_uri': os.environ['BASE_URL']+'/login',
            'response_type': 'code',
            'state': state
        }
        #login.gov expects unescaped '+' value for scope parameter
        auth_scope='&scope=openid+email'

        #escape params dict into a url encoded query string
        encoded_params = urlencode(auth_params, quote_via=quote_plus)

        #build out full API GET call to authorize endpoint
        auth_endpoint  = os.environ['OIDC_OP_AUTHORIZATION_ENDPOINT'] + '?' + encoded_params
        auth_endpoint_scope = auth_endpoint + '&' + auth_scope
        
        #update the user session so OIDC logout URL has token_hint
        request.session['state_nonce_tracker']= {
        'nonce': nonce,
        'state': state,
        'added_on': time.time(),
        }

        return HttpResponseRedirect(auth_endpoint_scope)