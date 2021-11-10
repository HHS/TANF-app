"""Define Django routing."""

import os
from django.conf import settings

from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path, reverse_lazy
from django.views.generic.base import RedirectView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

from .users.api.authorization_check import AuthorizationCheck
from .users.api.login import TokenAuthorizationOIDC
from .users.api.login_redirect_oidc import LoginRedirectAMS, LoginRedirectLoginDotGov
from .users.api.logout import LogoutUser
from .users.api.logout_redirect_oidc import LogoutRedirectOIDC
from django.contrib.auth.decorators import login_required
from .core.views import write_logs, IndexView

admin.autodiscover()
admin.site.login = login_required(admin.site.login)
admin.site.site_header = "Django administration"

urlpatterns = [
    path("login", TokenAuthorizationOIDC.as_view(), name="login"),
    path("login/dotgov", LoginRedirectLoginDotGov.as_view(), name="oidc-auth"),
    path("login/ams", LoginRedirectAMS.as_view(), name="oidc-auth"),
    path("logout", LogoutUser.as_view(), name="logout"),
    path("logout/oidc", LogoutRedirectOIDC.as_view(), name="oidc-logout"),
    path("auth_check", AuthorizationCheck.as_view(), name="authorization-check"),
    path("", include("tdpservice.users.urls")),
    path("stts/", include("tdpservice.stts.urls")),
    path("data_files/", include("tdpservice.data_files.urls")),
    path("logs/", write_logs),
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(
        r"^$", RedirectView.as_view(url=reverse_lazy("test_api-root"), permanent=False)
    ),
]

# Add 'prefix' to all urlpatterns to make it easier to version/group endpoints
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
urlpatterns = [
    path("v1/", include(urlpatterns)),
    path("admin/", admin.site.urls, name="admin"),
    path("", IndexView.as_view(), name="index"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# TODO: Supply `terms_of_service` argument in OpenAPI Info once implemented
schema_view = get_schema_view(
    openapi.Info(
        title="TDP API",
        default_version='v1',
        description="TANF Data Portal API documentation",
        contact=openapi.Contact(email="tanfdata@acf.hhs.gov"),
    ),
    public=True,
    permission_classes=(AllowAny,),
)

doc_patterns = [
    re_path(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    path('redocs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns.extend(doc_patterns)
