from django.urls import path, include
from django.conf import settings

from . import views

urlpatterns = [
    path('about/', views.about, name='about'),
    path('useradmin', views.useradmin, name='useradmin'),
    path('status/', views.status, name='status'),
    path('fileinfo/<file>/', views.fileinfo, name='fileinfo'),
    path('deletesuccessful/', views.deletesuccessful, name='deletesuccessful'),
    path('delete/<file>/', views.delete, name='delete'),
    path('delete/<file>/<confirmed>', views.delete, name='delete'),
    path('viewtables/', views.viewTables, name='viewtables'),
    path('viewquarter/', views.viewquarter, name='viewquarter'),
    path('download/<file>', views.download, name='download'),
    path('download/<file>/<json>/', views.download, name='download'),
]

if settings.NOLOGINGOV:
    urlpatterns.append(path('accounts/', include('django.contrib.auth.urls')))
else:
    urlpatterns.append(path('openid/', include('djangooidc.urls')))

urlpatterns.append(path('', views.upload, name='upload'))
