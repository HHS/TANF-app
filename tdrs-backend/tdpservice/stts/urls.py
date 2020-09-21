from django.urls import path
from . import views

urlpatterns = [path("", views.RegionAPIView.as_view(), name="stts-all")]
