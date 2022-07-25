"""Generic middleware for use across the TDP platform."""
from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils.cache import add_never_cache_headers


class NoCacheMiddleware(object):
    """Disable client caching with a Cache-Control header."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Add appropriate headers to the response before sending it out."""
        response = self.get_response(request)
        add_never_cache_headers(response)
        return response


class SessionMiddleware(SessionMiddleware):
    def process_response(self, request, response):
        response = super(SessionMiddleware, self).process_response(request, response)

        # if settings.SESSION_COOKIE_NAME in response.cookies:
        #     response.cookies[settings.SESSION_COOKIE_NAME]['samesite'] = 'None'
        if settings.CSRF_COOKIE_NAME in response.cookies:
            response.cookies[settings.CSRF_COOKIE_NAME]['samesite'] = 'None'
            response.cookies[settings.CSRF_COOKIE_NAME]['Secure'] = True
        return response
