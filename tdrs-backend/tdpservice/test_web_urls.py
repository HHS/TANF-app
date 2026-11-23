"""Tests for public frontend URL helpers."""

from tdpservice.web_urls import help_url


def test_help_url_uses_frontend_base_url(settings):
    """Help URLs should follow the configured frontend environment."""
    settings.FRONTEND_BASE_URL = "https://portal.example.gov/"

    assert help_url() == "https://portal.example.gov/help/"
    assert help_url("/knowledge-center/faq.html") == (
        "https://portal.example.gov/help/knowledge-center/faq.html"
    )
