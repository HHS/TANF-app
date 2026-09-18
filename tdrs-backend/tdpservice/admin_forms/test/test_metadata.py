"""Tests for generic admin form metadata."""

from django import forms

from tdpservice.admin_forms.metadata import build_admin_form_fields


class ExampleAdminForm(forms.Form):
    """Example plain form used to verify generic field metadata."""

    email = forms.EmailField(max_length=50, initial="admin@example.gov")
    notes = forms.CharField(required=False, widget=forms.Textarea)
    enabled = forms.BooleanField(required=False, initial=True)
    count = forms.IntegerField(min_value=1, max_value=10, initial=3)
    status = forms.ChoiceField(
        choices=[
            ("draft", "Draft"),
            ("published", "Published"),
        ],
        initial="draft",
    )


def test_build_admin_form_fields_supports_plain_django_forms():
    """Build generic metadata for supported Django Form field types."""
    fields = {
        field["name"]: field for field in build_admin_form_fields(ExampleAdminForm())
    }

    assert fields["email"]["type"] == "email"
    assert fields["email"]["constraints"]["max_length"] == 50
    assert fields["notes"]["type"] == "textarea"
    assert fields["enabled"]["type"] == "checkbox"
    assert fields["enabled"]["initial"] is True
    assert fields["count"]["type"] == "number"
    assert fields["count"]["constraints"] == {"max_value": 10, "min_value": 1}
    assert fields["status"]["type"] == "select"
    assert fields["status"]["choices"] == [
        {"value": "draft", "label": "Draft"},
        {"value": "published", "label": "Published"},
    ]
