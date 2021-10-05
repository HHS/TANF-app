"""Unit tests for OWASP ZAP scan operations."""
from django.contrib.admin.models import LogEntry
import pytest

from tdpservice.security.models import OwaspZapScan
from tdpservice.users.models import User


@pytest.mark.django_db
@pytest.mark.parametrize(
    'owasp_zap_scan__fail_count, '
    'owasp_zap_scan__pass_count, '
    'owasp_zap_scan__warn_count, '
    'expected_result',
    [
        (5, 95, 0, 'Failed'),
        (0, 95, 5, 'Warning'),
        (0, 100, 0, 'Passed'),
        (0, 0, 0, 'Error')
    ]
)
def test_owasp_zap_scan_result(owasp_zap_scan, expected_result):
    """Test that the result is appropriately returned for given metrics."""
    assert owasp_zap_scan.result == expected_result
    assert str(owasp_zap_scan) == (
        f'{owasp_zap_scan.get_app_target_display()}: '
        f'{owasp_zap_scan.scanned_at.date()} ({expected_result})'
    )


@pytest.mark.django_db
def test_owasp_zap_scan_manager_record_scan(owasp_zap_scan):
    """Test model manager functionality to record new scans."""
    assert not User.objects.filter(username='system').exists()

    # Record a new scan, using auto generated values from the factoryboy
    # fixture for simplicity.
    zap_scan = OwaspZapScan.objects.record_scan(
        owasp_zap_scan.app_target,
        owasp_zap_scan.html_report,
        owasp_zap_scan.fail_count,
        owasp_zap_scan.pass_count,
        owasp_zap_scan.warn_count
    )
    assert isinstance(zap_scan, OwaspZapScan)

    # Assert that the system user was created, if it didn't already exist.
    assert User.objects.filter(username='system').exists()

    # Assert that the relevant LogEntry was created alongside the OwaspZapScan.
    assert LogEntry.objects.filter(
        content_type__model='owaspzapscan',
        object_id=zap_scan.pk
    ).exists()
