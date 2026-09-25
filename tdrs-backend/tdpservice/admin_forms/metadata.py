"""Build generic React admin form metadata from Django forms."""

from typing import Any

from django import forms
from django.db.models import QuerySet
from django.forms.models import ModelChoiceIteratorValue


def _field_type(field: forms.Field) -> str:
    """Return a frontend-friendly field type for a Django form field."""
    if isinstance(field, (forms.ModelMultipleChoiceField, forms.MultipleChoiceField)):
        return "multiselect"
    if isinstance(field, (forms.ModelChoiceField, forms.ChoiceField)):
        return "select"
    if isinstance(field, forms.BooleanField):
        return "checkbox"
    if isinstance(field, forms.EmailField):
        return "email"
    if isinstance(field, forms.IntegerField):
        return "number"
    if isinstance(field.widget, forms.Textarea):
        return "textarea"
    return "text"


def _choice_value(value: Any) -> str:
    """Serialize a Django choice value for browser form controls."""
    if isinstance(value, ModelChoiceIteratorValue):
        value = value.value
    if value is None:
        return ""
    return str(value)


def _field_choices(field: forms.Field) -> list[dict[str, str]]:
    """Serialize Django field choices."""
    choices = getattr(field, "choices", None)
    if choices is None:
        return []

    serialized_choices = []
    for value, label in choices:
        if isinstance(label, (list, tuple)):
            for nested_value, nested_label in label:
                serialized_choices.append(
                    {"value": _choice_value(nested_value), "label": str(nested_label)}
                )
            continue

        serialized_choices.append({"value": _choice_value(value), "label": str(label)})

    return serialized_choices


def _serialize_initial_value(field: forms.Field, value: Any) -> Any:
    """Serialize a Django initial value for JSON metadata."""
    if isinstance(field, (forms.ModelMultipleChoiceField, forms.MultipleChoiceField)):
        if value in (None, ""):
            return []
        if isinstance(value, QuerySet):
            value = list(value)
        if not isinstance(value, (list, tuple, set)):
            value = [value]
        return [_choice_value(getattr(item, "pk", item)) for item in value]

    if isinstance(field, forms.ModelChoiceField):
        if value in (None, ""):
            return None
        return _choice_value(getattr(value, "pk", value))

    if hasattr(value, "isoformat"):
        return value.isoformat()

    return value


def _field_constraints(field: forms.Field) -> dict[str, Any]:
    """Return generic constraints supported by the React admin form."""
    constraints = {}
    for attr_name in ["max_length", "min_length", "max_value", "min_value"]:
        value = getattr(field, attr_name, None)
        if value is not None:
            constraints[attr_name] = value

    pattern = field.widget.attrs.get("pattern")
    if pattern:
        constraints["pattern"] = pattern

    return constraints


def build_admin_form_fields(form: forms.Form) -> list[dict[str, Any]]:
    """Build generic field metadata from a Django form."""
    fields = []
    for field_name, field in form.fields.items():
        fields.append(
            {
                "name": field_name,
                "label": str(field.label or field_name.replace("_", " ").title()),
                "type": _field_type(field),
                "required": field.required,
                "help_text": str(field.help_text or ""),
                "initial": _serialize_initial_value(field, form[field_name].value()),
                "choices": _field_choices(field),
                "constraints": _field_constraints(field),
            }
        )

    return fields


def build_admin_form_metadata(
    form: forms.Form, workflow: Any, instance: Any
) -> dict[str, Any]:
    """Build React admin metadata from a registered Django admin form workflow."""
    return {
        "workflow": workflow.key,
        "title": workflow.title,
        "object": workflow.serialize_metadata_object(instance),
        "submit_url": workflow.submit_url(instance),
        "fields": build_admin_form_fields(form),
    }
