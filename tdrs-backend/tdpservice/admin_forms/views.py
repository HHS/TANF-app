"""Generic React admin form endpoints."""

from django import forms
from django.core.exceptions import ValidationError

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from tdpservice.admin_forms.errors import normalize_form_errors
from tdpservice.admin_forms.metadata import build_admin_form_metadata
from tdpservice.admin_forms.permissions import IsAdminConsoleFormUser
from tdpservice.admin_forms.registry import get_admin_form_workflow


def _validation_error_response(form: forms.Form) -> Response:
    """Return the normalized validation failure response for an admin form."""
    return Response(
        {
            "ok": False,
            "errors": normalize_form_errors(form.errors),
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


class AdminFormMetadataView(APIView):
    """Return Django-derived metadata for an allowlisted admin form workflow."""

    permission_classes = [IsAdminConsoleFormUser]

    def get(self, request, workflow, object_id):
        """Return metadata for the requested workflow object."""
        admin_workflow = get_admin_form_workflow(workflow)
        instance = admin_workflow.get_object(object_id)
        form = admin_workflow.get_form(instance=instance)
        return Response(build_admin_form_metadata(form, admin_workflow, instance))


class AdminFormView(APIView):
    """Validate and save an allowlisted admin form through Django."""

    permission_classes = [IsAdminConsoleFormUser]

    def patch(self, request, workflow, object_id):
        """Validate and save the requested workflow object."""
        admin_workflow = get_admin_form_workflow(workflow)
        instance = admin_workflow.get_object(object_id)
        form = admin_workflow.get_form(data=request.data, instance=instance)

        if not form.is_valid():
            return _validation_error_response(form)

        try:
            saved_instance = admin_workflow.save(form) or instance
        except ValidationError as exc:
            form.add_error(None, exc)
            return _validation_error_response(form)

        refreshed_instance = admin_workflow.get_object(str(saved_instance.pk))
        refreshed_form = admin_workflow.get_form(instance=refreshed_instance)
        return Response(
            {
                "ok": True,
                "object": admin_workflow.serialize_response_object(
                    refreshed_instance, request
                ),
                "metadata": build_admin_form_metadata(
                    refreshed_form, admin_workflow, refreshed_instance
                ),
            }
        )
