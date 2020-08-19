"""Define Django routing."""

from django.conf import settings
from django.urls import path, re_path, include, reverse_lazy
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from .users.views import UserViewSet, UserCreateViewSet
from .users.api.login import TokenAuthorizationOIDC
from .users.api.logout import LogoutUser
from .users.api.login_redirect_oidc import LoginRedirectOIDC
from .users.api.logout_redirect_oidc import LogoutRedirectOIDC


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'users', UserCreateViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls), name="api"),
    path('login', TokenAuthorizationOIDC.as_view(), name="login"),
    path('login/oidc', LoginRedirectOIDC.as_view(), name='oidc-auth'),
    path('logout', LogoutUser.as_view(), name="logout"),
    path('logout/oidc', LogoutRedirectOIDC.as_view(), name='oidc-logout'),


    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r'^$', RedirectView.as_view(
        url=reverse_lazy('api-root'), permanent=False)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
