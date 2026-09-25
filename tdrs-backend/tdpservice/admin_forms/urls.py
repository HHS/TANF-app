"""Routing for generic React admin forms."""

from django.urls import path

from tdpservice.admin_forms.views import AdminFormMetadataView, AdminFormView

urlpatterns = [
    path(
        "<str:workflow>/<str:object_id>/metadata/",
        AdminFormMetadataView.as_view(),
        name="admin-form-metadata",
    ),
    path(
        "<str:workflow>/<str:object_id>/",
        AdminFormView.as_view(),
        name="admin-form",
    ),
]
