"""Allow CORS connections."""


class CorsMiddleware(object):
    """Add CORS Middleware."""

    def process_response(self, req, resp):
        """Process the response."""
        response["Access-Control-Allow-Origin"] = "*"
        return response
