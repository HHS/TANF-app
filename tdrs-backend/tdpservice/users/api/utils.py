"""Define utility methods for users api."""

import logging
import time


LOGGER = logging.getLogger(__name__)


def add_state_and_nonce_to_session(request, state, nonce):
    """Add state and nonce to session."""
    if 'openid_authenticity_tracker' not in request.session or \
            not isinstance(request.session['openid_authenticity_tracker'], dict):
        request.session['openid_authenticity_tracker'] = {}

    limit = 1
    if len(request.session['openid_authenticity_tracker']) >= limit:
        LOGGER.info(
            'User has more than {} "openid_authenticity_tracker" in his session, '
            'deleting the oldest one!'.format(limit)
        )
        oldest_state = None
        oldest_added_on = time.time()
        for item_state, item in request.session['openid_authenticity_tracker'].items():
            if item['added_on'] < oldest_added_on:
                oldest_state = item_state
                oldest_added_on = item['added_on']
        if oldest_state:
            del request.session['openid_authenticity_tracker'][oldest_state]

    request.session['openid_authenticity_tracker'][state] = {
        'nonce': nonce,
        'added_on': time.time(),
    }
    # Tell the session object explicitly that it has been modified by setting
    # the modified attribute on the session object:
    request.session.modified = True
