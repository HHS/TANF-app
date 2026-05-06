"""Test appropriate permissions are assigned to each Group."""

import pytest

DEFAULT_NON_DELETE_ACTIONS = ["add", "change", "view"]


def permissions_for_models(model_permissions):
    """Build permission strings from app/model/action mappings."""
    return {
        f"{app_label}.{action}_{model_name}"
        for app_label, model_actions in model_permissions.items()
        for action, model_names in model_actions.items()
        for model_name in model_names
    }


def default_permissions_for_models(app_models):
    """Build add/change/view permission strings from app/model mappings."""
    return permissions_for_models(
        {
            app_label: {action: model_names for action in DEFAULT_NON_DELETE_ACTIONS}
            for app_label, model_names in app_models.items()
        }
    )


OFA_SYSTEM_ADMIN_TABLE_PERMISSIONS = (
    default_permissions_for_models(
        {
            "admin": ["logentry"],
            "admin_interface": ["theme"],
            "auth": ["group", "permission"],
            "authtoken": ["token", "tokenproxy"],
            "contenttypes": ["contenttype"],
            "core": [
                "featureflag",
                "globalpermission",
                "historicalfeatureflag",
                "historicalgroup",
                "historicalgroup_permissions",
            ],
            "data_files": ["datafile", "legacyfiletransfer", "reparsefilemeta"],
            "django_celery_beat": [
                "clockedschedule",
                "crontabschedule",
                "intervalschedule",
                "periodictask",
                "periodictasks",
                "solarschedule",
            ],
            "parsers": ["datafilesummary", "parsererror"],
            "reports": ["reportfile", "reportsource"],
            "search_indexes": [
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
            ],
            "sessions": ["session"],
            "stts": ["region", "stt"],
        }
    )
    | permissions_for_models(
        {
            "security": {
                "add": ["securityeventtoken"],
                "change": ["securityeventtoken"],
                "view": ["clamavfilescan", "owaspzapscan", "securityeventtoken"],
            },
            "users": {
                "change": ["user"],
                "view": ["user"],
            },
        }
    )
    | {
        "users.has_fra_access",
    }
)


SHADOW_TABLE_PERMISSIONS = default_permissions_for_models(
    {
        "data_files": [
            "shadowdatafile",
        ],
        "parsers": [
            "shadowdatafilesummary",
            "shadowparsererror",
        ],
        "search_indexes": [
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
        ],
    }
)


@pytest.mark.django_db
def test_ofa_admin_permissions(ofa_admin):
    """Test that an OFA Admin user inherits the correct permissions."""
    expected_permissions = {
        "admin.view_logentry",
        "auth.view_group",
        "data_files.add_datafile",
        "data_files.view_datafile",
        "security.view_clamavfilescan",
        "security.view_owaspzapscan",
        "stts.view_region",
        "stts.view_stt",
        "users.add_user",
        "users.change_user",
        "users.view_user",
        "users.has_fra_access",
        # Note: OFA Admin does NOT have reports permissions (removed in migration 0054)
    }
    group_permissions = ofa_admin.get_group_permissions()
    assert group_permissions == expected_permissions


@pytest.mark.django_db
def test_ofa_system_admin_permissions(ofa_system_admin):
    """Test that an OFA System Admin user inherits the correct permissions."""
    expected_permissions = OFA_SYSTEM_ADMIN_TABLE_PERMISSIONS | SHADOW_TABLE_PERMISSIONS
    group_permissions = ofa_system_admin.get_group_permissions()
    assert group_permissions == expected_permissions


@pytest.mark.django_db
def test_data_analyst_permissions(data_analyst):
    """Test that a Data Analyst user inherits the correct permissions."""
    expected_permissions = {
        "data_files.add_datafile",
        "data_files.view_datafile",
        "reports.view_reportfile",
    }
    group_permissions = data_analyst.get_group_permissions()
    assert group_permissions == expected_permissions


@pytest.mark.django_db
def test_digit_team_permissions(digit_team):
    """Test that a DIGIT Team user inherits the correct permissions."""
    expected_permissions = {
        "parsers.view_parsererror",
        "parsers.view_datafilesummary",
        "data_files.view_datafile",
        "data_files.add_datafile",
        "stts.view_stt",
        "search_indexes.view_ssp_m3",
        "search_indexes.view_tribal_tanf_t5",
        "search_indexes.view_tribal_tanf_t3",
        "search_indexes.view_ssp_m4",
        "search_indexes.view_tanf_t5",
        "search_indexes.view_tanf_t3",
        "search_indexes.view_tanf_t1",
        "search_indexes.view_tribal_tanf_t7",
        "search_indexes.view_tribal_tanf_t6",
        "search_indexes.view_ssp_m7",
        "search_indexes.view_tanf_t7",
        "search_indexes.view_ssp_m2",
        "search_indexes.view_tribal_tanf_t1",
        "search_indexes.view_tribal_tanf_t4",
        "search_indexes.view_ssp_m1",
        "search_indexes.view_ssp_m5",
        "search_indexes.view_tanf_t2",
        "search_indexes.view_tanf_t4",
        "search_indexes.view_ssp_m6",
        "search_indexes.view_tribal_tanf_t2",
        "search_indexes.view_tanf_t6",
        # Reports permissions added in migration 0054
        "reports.add_reportfile",
        "reports.add_reportsource",
        "reports.view_reportfile",
        "reports.view_reportsource",
    }
    group_permissions = digit_team.get_group_permissions()
    assert group_permissions == expected_permissions
