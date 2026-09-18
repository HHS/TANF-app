"""Tests for admin form workflow registry behavior."""

from django import forms
from django.contrib.auth.models import Group

import pytest

from tdpservice.admin_forms.registry import AdminFormWorkflow


class FailingSaveM2MGroupForm(forms.ModelForm):
    """ModelForm that fails after the instance save step."""

    class Meta:
        """Expose a simple mutable model field."""

        model = Group
        fields = ["name"]

    def _save_m2m(self):
        """Simulate an error while saving many-to-many relations."""
        raise RuntimeError("save_m2m failed")


@pytest.mark.django_db
def test_workflow_builds_model_form_from_model_and_fields():
    """Generate and save a generic ModelForm from registry model metadata."""
    group = Group.objects.create(name="Original")
    workflow = AdminFormWorkflow(
        key="auth.group.change",
        title="Edit group",
        model=Group,
        fields=["name"],
    )

    form = workflow.get_form(instance=group)
    assert isinstance(form, forms.ModelForm)
    assert list(form.fields) == ["name"]

    bound_form = workflow.get_form(instance=group, data={"name": "Updated"})
    assert bound_form.is_valid(), bound_form.errors

    saved_group = workflow.save(bound_form)

    group.refresh_from_db()
    assert saved_group.pk == group.pk
    assert group.name == "Updated"
    assert workflow.get_object(str(group.pk)) == group


@pytest.mark.django_db
def test_workflow_generic_save_rolls_back_when_save_m2m_fails():
    """Keep the instance unchanged when the generic m2m save fails."""
    group = Group.objects.create(name="Original")
    workflow = AdminFormWorkflow(
        key="auth.group.change",
        title="Edit group",
        form_class=FailingSaveM2MGroupForm,
        queryset=Group.objects.all(),
    )
    form = workflow.get_form(instance=group, data={"name": "Updated"})
    assert form.is_valid(), form.errors

    with pytest.raises(RuntimeError, match="save_m2m failed"):
        workflow.save(form)

    group.refresh_from_db()
    assert group.name == "Original"
