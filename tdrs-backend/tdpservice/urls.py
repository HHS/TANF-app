"""Define Django routing."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path, reverse_lazy
from django.views.generic.base import RedirectView
from drf_yasg2 import openapi
from drf_yasg2.views import get_schema_view
from rest_framework.permissions import AllowAny

from .users.api.authorization_check import AuthorizationCheck
from .users.api.login import TokenAuthorizationOIDC
from .users.api.login_redirect_oidc import LoginRedirectOIDC
from .users.api.logout import LogoutUser
from .users.api.logout_redirect_oidc import LogoutRedirectOIDC

urlpatterns = [
    path("login", TokenAuthorizationOIDC.as_view(), name="login"),
    path("login/oidc", LoginRedirectOIDC.as_view(), name="oidc-auth"),
    path("logout", LogoutUser.as_view(), name="logout"),
    path("logout/oidc", LogoutRedirectOIDC.as_view(), name="oidc-logout"),
    path("auth_check", AuthorizationCheck.as_view(), name="authorization-check"),
    path("", include("tdpservice.users.urls")),
    path("stts/", include("tdpservice.stts.urls")),
    # the 'test_api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(
        r"^$", RedirectView.as_view(url=reverse_lazy("test_api-root"), permanent=False)
    ),
]

# Add 'prefix' to all urlpatterns to make it easier to version/group endpoints
urlpatterns = [
    path("v1/", include(urlpatterns)),
    path("admin/", admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


schema_view = get_schema_view(
    openapi.Info(
        title="TDP API",
        default_version='v1',
        description="TANF Data Portal API documentation",
        terms_of_service="TODO",
        contact=openapi.Contact(email="TODO"),
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
