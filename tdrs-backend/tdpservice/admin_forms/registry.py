"""Allowlisted React admin form workflows."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.db import models, transaction
from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404

from tdpservice.users.forms import UserAdminWorkflowForm
from tdpservice.users.models import User
from tdpservice.users.serializers import UserSerializer


QuerysetFactory = Callable[[], QuerySet]
ObjectLabel = Callable[[Any], str]
SaveCallback = Callable[[forms.Form], Any]
ModelFormFields = Sequence[str] | str


@dataclass(frozen=True)
class AdminFormWorkflow:
    """Registered admin form workflow backed by a Django Form or ModelForm."""

    key: str
    title: str
    form_class: type[forms.Form] | None = None
    queryset: QuerySet | QuerysetFactory | None = None
    model: type[models.Model] | None = None
    fields: ModelFormFields | None = None
    object_serializer_class: type | None = None
    object_label: ObjectLabel = str
    save_callback: SaveCallback | None = None

    def _get_model(self) -> type[models.Model] | None:
        """Return the workflow model when it can be inferred."""
        if self.model is not None:
            return self.model

        form_class = self.form_class
        if form_class is None or not issubclass(form_class, forms.ModelForm):
            return None

        return form_class._meta.model

    def get_form_class(self) -> type[forms.Form]:
        """Return the explicit or generated workflow form class."""
        if self.fields is None:
            if self.form_class is None:
                raise ImproperlyConfigured(
                    f"{self.key} must define form_class or model and fields."
                )
            return self.form_class

        model = self._get_model()
        if model is None:
            raise ImproperlyConfigured(
                f"{self.key} must define model when fields are configured."
            )

        form_class = self.form_class or forms.ModelForm
        if not issubclass(form_class, forms.ModelForm):
            raise ImproperlyConfigured(
                f"{self.key} form_class must inherit ModelForm when fields are "
                "configured."
            )

        return forms.modelform_factory(model, form=form_class, fields=self.fields)

    def get_queryset(self) -> QuerySet:
        """Return the workflow queryset."""
        if self.queryset is not None:
            queryset = self.queryset() if callable(self.queryset) else self.queryset
        else:
            model = self._get_model()
            if model is None:
                raise ImproperlyConfigured(
                    f"{self.key} must define queryset or model."
                )
            queryset = model._default_manager

        return queryset.all()

    def get_object(self, object_id: str) -> Any:
        """Return the workflow object for the submitted object id."""
        return get_object_or_404(self.get_queryset(), pk=object_id)

    def get_form(self, *, instance: Any, data: Any | None = None) -> forms.Form:
        """Build the workflow form for metadata or validation."""
        kwargs = {}
        if data is not None:
            kwargs["data"] = data
        form_class = self.get_form_class()
        if issubclass(form_class, forms.ModelForm):
            kwargs["instance"] = instance
        return form_class(**kwargs)

    def save(self, form: forms.Form) -> Any:
        """Persist a valid workflow form and return the saved object."""
        if self.save_callback:
            return self.save_callback(form)

        if not isinstance(form, forms.ModelForm):
            raise ImproperlyConfigured(
                f"{self.key} must define save_callback for non-ModelForm saves."
            )

        with transaction.atomic():
            instance = form.save(commit=False)
            instance.save()
            form.save_m2m()
        return instance

    def serialize_metadata_object(self, instance: Any) -> dict[str, str]:
        """Return the compact object metadata included with form metadata."""
        return {"id": str(instance.pk), "label": self.object_label(instance)}

    def serialize_response_object(self, instance: Any, request: Any) -> Any:
        """Return the saved object representation for mutation responses."""
        if self.object_serializer_class is None:
            return self.serialize_metadata_object(instance)

        serializer = self.object_serializer_class(
            instance, context={"request": request}
        )
        return serializer.data

    def submit_url(self, instance: Any) -> str:
        """Return the generic admin form mutation path for the object."""
        workflow_key = quote(self.key, safe="")
        object_id = quote(str(instance.pk), safe="")
        return f"/admin-forms/{workflow_key}/{object_id}/"


def _user_admin_queryset() -> QuerySet:
    """Return the queryset for the user admin workflow."""
    return User.objects.select_related("stt").prefetch_related(
        "groups__permissions",
        "regions",
    )


ADMIN_FORM_WORKFLOWS = {
    "users.user.change": AdminFormWorkflow(
        key="users.user.change",
        title="Edit user",
        form_class=UserAdminWorkflowForm,
        queryset=_user_admin_queryset,
        object_serializer_class=UserSerializer,
    ),
}


def get_admin_form_workflow(workflow_key: str) -> AdminFormWorkflow:
    """Return an allowlisted admin form workflow by key."""
    workflow = ADMIN_FORM_WORKFLOWS.get(workflow_key)
    if workflow is None:
        raise Http404("Admin form workflow is not available.")
    return workflow
