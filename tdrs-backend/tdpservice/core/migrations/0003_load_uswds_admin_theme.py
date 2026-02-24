"""Load the U.S. Web Design Standards theme for django-admin-interface."""

from django.core.management import call_command
from django.db import migrations


def load_uswds_theme(apps, schema_editor):
    """Load the USWDS theme fixture and set it as the active theme."""
    Theme = apps.get_model("admin_interface", "Theme")

    # Deactivate any existing themes
    Theme.objects.all().update(active=False)

    # Load the USWDS theme fixture shipped with django-admin-interface
    call_command("loaddata", "admin_interface_theme_uswds.json", verbosity=0)

    # Ensure the USWDS theme is the active one
    Theme.objects.filter(name="U.S. Web Design Standards").update(active=True)


def revert_to_default(apps, schema_editor):
    """Revert to the default Django theme."""
    Theme = apps.get_model("admin_interface", "Theme")
    Theme.objects.filter(name="U.S. Web Design Standards").update(active=False)
    # Re-activate the default Django theme if it exists
    default = Theme.objects.filter(name="Django").first()
    if default:
        default.active = True
        default.save()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_auto_20201013_0630"),
        ("admin_interface", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_uswds_theme, revert_to_default),
    ]
