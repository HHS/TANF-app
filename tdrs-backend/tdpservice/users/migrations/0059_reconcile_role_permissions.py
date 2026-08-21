"""Reconcile role permissions after late-created app permissions exist."""

from django.contrib.auth.management import create_permissions
from django.db import migrations


DEFAULT_ACTIONS = ("add", "change", "view")
ADD_VIEW_ACTIONS = ("add", "view")
VIEW_ACTIONS = ("view",)


DIGIT_SEARCH_INDEX_MODELS = tuple(
    model_prefix + str(index)
    for model_prefix in ("tanf_t", "tribal_tanf_t", "ssp_m")
    for index in range(1, 8)
)


OFA_SYSTEM_ADMIN_SEARCH_INDEX_MODELS = (
    "programaudit_t1",
    "programaudit_t2",
    "programaudit_t3",
    "reparsemeta",
    "ssp_m1",
    "ssp_m2",
    "ssp_m3",
    "ssp_m4",
    "ssp_m5",
    "ssp_m6",
    "ssp_m7",
    "tanf_exiter1",
    "tanf_t1",
    "tanf_t2",
    "tanf_t3",
    "tanf_t4",
    "tanf_t5",
    "tanf_t6",
    "tanf_t7",
    "tribal_tanf_t1",
    "tribal_tanf_t2",
    "tribal_tanf_t3",
    "tribal_tanf_t4",
    "tribal_tanf_t5",
    "tribal_tanf_t6",
    "tribal_tanf_t7",
)


SHADOW_SEARCH_INDEX_MODELS = (
    "shadowprogramaudit_t1",
    "shadowprogramaudit_t2",
    "shadowprogramaudit_t3",
    "shadowssp_m1",
    "shadowssp_m2",
    "shadowssp_m3",
    "shadowssp_m4",
    "shadowssp_m5",
    "shadowssp_m6",
    "shadowssp_m7",
    "shadowtanf_exiter1",
    "shadowtanf_t1",
    "shadowtanf_t2",
    "shadowtanf_t3",
    "shadowtanf_t4",
    "shadowtanf_t5",
    "shadowtanf_t6",
    "shadowtanf_t7",
    "shadowtribal_tanf_t1",
    "shadowtribal_tanf_t2",
    "shadowtribal_tanf_t3",
    "shadowtribal_tanf_t4",
    "shadowtribal_tanf_t5",
    "shadowtribal_tanf_t6",
    "shadowtribal_tanf_t7",
)


ETL_MODELS = (
    "etlartifact",
    "etlnoderun",
    "etlpipelinerun",
    "etlqaresult",
    "statisticalweight",
    "statisticalweightscasecount",
)


def create_current_permissions(apps, schema_editor):
    """Create auth permissions before assigning them inside this migration."""
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None


def permission_ids(apps, app_label, model_name, actions):
    """Return permission ids for exact action/model codename pairs."""
    permission_model = apps.get_model("auth", "Permission")
    codenames = [f"{action}_{model_name}" for action in actions]
    return list(
        permission_model.objects.filter(
            content_type__app_label=app_label,
            content_type__model=model_name,
            codename__in=codenames,
        ).values_list("id", flat=True)
    )


def permission_ids_for_models(apps, app_label, model_names, actions):
    ids = []
    for model_name in model_names:
        ids.extend(permission_ids(apps, app_label, model_name, actions))
    return ids


def add_permissions(apps, group_name, permission_ids_to_add):
    group = apps.get_model("auth", "Group").objects.get(name=group_name)
    group.permissions.add(*permission_ids_to_add)


def remove_permissions(apps, group_name, permission_ids_to_remove):
    group = apps.get_model("auth", "Group").objects.get(name=group_name)
    group.permissions.remove(*permission_ids_to_remove)


def fra_access_permission_id(apps):
    permission_model = apps.get_model("auth", "Permission")
    content_type_model = apps.get_model("contenttypes", "ContentType")
    user_content_type = content_type_model.objects.get(app_label="users", model="user")
    permission, _ = permission_model.objects.get_or_create(
        codename="has_fra_access",
        name="Can access FRA Data Files",
        content_type=user_content_type,
    )
    return permission.id


def report_permission_ids(apps, actions):
    return permission_ids_for_models(
        apps,
        "reports",
        ("reportfile", "reportsource"),
        actions,
    )


def reconcile_role_permissions(apps, schema_editor):
    """Make role permissions match the policy expected by API permissions."""
    add_permissions(
        apps,
        "OFA Admin",
        permission_ids_for_models(
            apps,
            "security",
            ("clamavfilescan", "owaspzapscan"),
            VIEW_ACTIONS,
        )
        + [fra_access_permission_id(apps)],
    )
    remove_permissions(apps, "OFA Admin", report_permission_ids(apps, DEFAULT_ACTIONS))

    add_permissions(
        apps,
        "OFA System Admin",
        report_permission_ids(apps, DEFAULT_ACTIONS)
        + permission_ids_for_models(
            apps,
            "security",
            ("clamavfilescan", "owaspzapscan", "securityeventtoken"),
            VIEW_ACTIONS,
        )
        + permission_ids(apps, "security", "securityeventtoken", ("add", "change"))
        + permission_ids_for_models(
            apps,
            "data_files",
            ("datafile", "legacyfiletransfer", "reparsefilemeta", "shadowdatafile"),
            DEFAULT_ACTIONS,
        )
        + permission_ids_for_models(
            apps,
            "parsers",
            ("datafilesummary", "parsererror"),
            DEFAULT_ACTIONS,
        )
        + permission_ids_for_models(
            apps,
            "search_indexes",
            OFA_SYSTEM_ADMIN_SEARCH_INDEX_MODELS,
            DEFAULT_ACTIONS,
        )
        + permission_ids_for_models(
            apps,
            "parsers",
            ("shadowdatafilesummary", "shadowparsererror"),
            DEFAULT_ACTIONS,
        )
        + permission_ids_for_models(
            apps,
            "search_indexes",
            SHADOW_SEARCH_INDEX_MODELS,
            DEFAULT_ACTIONS,
        )
        + permission_ids(apps, "sessions", "session", DEFAULT_ACTIONS)
        + permission_ids_for_models(apps, "etl", ETL_MODELS, DEFAULT_ACTIONS)
        + [fra_access_permission_id(apps)],
    )

    add_permissions(
        apps,
        "Data Analyst",
        permission_ids(apps, "reports", "reportfile", VIEW_ACTIONS),
    )

    add_permissions(
        apps,
        "DIGIT Team",
        permission_ids_for_models(
            apps,
            "data_files",
            ("datafile",),
            ADD_VIEW_ACTIONS,
        )
        + permission_ids_for_models(
            apps,
            "parsers",
            ("datafilesummary", "parsererror"),
            VIEW_ACTIONS,
        )
        + permission_ids(apps, "stts", "stt", VIEW_ACTIONS)
        + permission_ids_for_models(
            apps,
            "search_indexes",
            DIGIT_SEARCH_INDEX_MODELS,
            VIEW_ACTIONS,
        )
        + report_permission_ids(apps, ADD_VIEW_ACTIONS)
        + permission_ids_for_models(apps, "etl", ETL_MODELS, VIEW_ACTIONS),
    )

    add_permissions(
        apps,
        "OFA Regional Staff",
        permission_ids(apps, "reports", "reportfile", VIEW_ACTIONS),
    )


class Migration(migrations.Migration):
    # Several older users migrations grant group permissions for models owned by
    # later apps, such as reports, security, parsers, search_indexes, and etl.
    # Those migrations lack dependencies on the app migrations that create the
    # target content types and auth permissions, so a fresh database can apply a
    # grant migration, query an empty permission set, and still mark the
    # migration successful.
    #
    # This became visible after adding the ETL app because etl.0001 depends on
    # users.0058. That dependency changed the fresh-DB migration topology enough
    # that the full users chain now runs before reports/security/parsers/etc.
    # create some of the permissions the users migrations attempted to grant.
    # Making etl.0001 depend on reports would not repair this by itself: the
    # report permission grants are in users.0052/0054/0055/0056, and those
    # migrations would still be free to run before reports unless they also
    # gained the needed dependencies. This migration intentionally runs after the
    # affected app migrations and idempotently reconciles the role matrix for
    # both fresh CI databases and already-upgraded environments.
    dependencies = [
        ("auth", "__latest__"),
        ("sessions", "0001_initial"),
        ("users", "0058_merge_20260318_2105"),
        ("security", "0004_security_event_token"),
        ("data_files", "0028_alter_datafile_state_alter_shadowdatafile_state"),
        ("parsers", "0017_shadowdatafilesummary_shadowparsererror"),
        ("search_indexes", "0037_shadowprogramaudit_t1_shadowprogramaudit_t2_and_more"),
        ("reports", "0005_alter_reportfile_report_type_and_more"),
        ("etl", "0002_etl_model_verbose_names"),
    ]

    operations = [
        migrations.RunPython(
            create_current_permissions,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunPython(
            reconcile_role_permissions,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
