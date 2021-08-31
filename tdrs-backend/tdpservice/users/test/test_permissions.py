"""Test appropriate permissions are assigned to each Group."""
import pytest


@pytest.mark.django_db
def test_ofa_admin_permissions(ofa_admin):
    """Test that an OFA Admin user inherits the correct permissions."""
    expected_permissions = {
        'admin.view_logentry',
        'auth.view_group',
        'data_files.add_datafile',
        'data_files.view_datafile',
        'stts.view_region',
        'stts.view_stt',
        'users.add_user',
        'users.change_user',
        'users.view_user',
    }
    group_permissions = ofa_admin.get_group_permissions()
    assert group_permissions == expected_permissions


@pytest.mark.django_db
def test_ofa_system_admin_permissions(ofa_system_admin):
    """Test that an OFA System Admin user inherits the correct permissions."""
    expected_permissions = {
        'admin.add_logentry',
        'admin.change_logentry',
        'admin.view_logentry',
        'admin_interface.add_theme',
        'admin_interface.change_theme',
        'admin_interface.view_theme',
        'auth.add_group',
        'auth.add_permission',
        'auth.change_group',
        'auth.change_permission',
        'auth.view_group',
        'auth.view_permission',
        'authtoken.add_token',
        'authtoken.add_tokenproxy',
        'authtoken.change_token',
        'authtoken.change_tokenproxy',
        'authtoken.view_token',
        'authtoken.view_tokenproxy',
        'contenttypes.add_contenttype',
        'contenttypes.change_contenttype',
        'contenttypes.view_contenttype',
        'core.add_globalpermission',
        'core.change_globalpermission',
        'core.view_globalpermission',
        'data_files.add_datafile',
        'data_files.change_datafile',
        'data_files.view_datafile',
        'sessions.add_session',
        'sessions.change_session',
        'sessions.view_session',
        'stts.add_region',
        'stts.add_stt',
        'stts.change_region',
        'stts.change_stt',
        'stts.view_region',
        'stts.view_stt',
        'users.add_user',
        'users.change_user',
        'users.view_user',
    }
    group_permissions = ofa_system_admin.get_group_permissions()
    assert group_permissions == expected_permissions


@pytest.mark.django_db
def test_data_analyst_permissions(data_analyst):
    """Test that a Data Analyst user inherits the correct permissions."""
    expected_permissions = {
        'data_files.add_datafile',
        'data_files.view_datafile',
    }
    group_permissions = data_analyst.get_group_permissions()
    assert group_permissions == expected_permissions
