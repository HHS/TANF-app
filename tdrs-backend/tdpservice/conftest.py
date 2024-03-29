"""Globally available pytest fixtures."""
import uuid
from io import StringIO

from django.contrib.admin.models import LogEntry
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from factory.faker import faker
from pytest_factoryboy import register
from rest_framework.test import APIClient

from tdpservice.core.admin import LogEntryAdmin
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.security.test.factories import OwaspZapScanFactory
from tdpservice.stts.models import STT, Region
from tdpservice.users.models import AccountApprovalStatusChoices
from tdpservice.users.test.factories import (
    AdminSTTUserFactory,
    AdminUserFactory,
    DeactivatedUserFactory,
    InactiveUserFactory,
    StaffUserFactory,
    STTUserFactory,
    UserFactory,
)

_faker = faker.Faker()


@pytest.fixture(scope="function")
def api_client():
    """Return an API client for testing."""
    return APIClient()


@pytest.fixture
def user():
    """Return a basic, non-admin user."""
    return UserFactory.create()


@pytest.fixture
def stt_data_analyst():
    """Return a basic, approved, data analyst stt user."""
    user = UserFactory.create(groups=(Group.objects.get(name="Data Analyst"),),)
    user.account_approval_status = AccountApprovalStatusChoices.APPROVED
    user.save()
    return user

@pytest.fixture
def stt_data_analyst_initial():
    """Return a basic, data analyst stt user."""
    return UserFactory.create(groups=(Group.objects.get(name="Data Analyst"),),)

@pytest.fixture
def regional_user(region, stt):
    """Return a regional staff user."""
    user = STTUserFactory.create(
        groups=(Group.objects.get(name="OFA Regional Staff"),),
    )
    user.region = region
    user.account_approval_status = AccountApprovalStatusChoices.APPROVED
    user.save()
    return user


# Might be made redundent by changes in 1587
@pytest.fixture
def user_in_region(stt, region):
    """Return a user in the same region as a regional staff user."""
    user = STTUserFactory.create(
        groups=(Group.objects.get(name="Data Analyst"),),
    )
    user.stt = stt
    user.account_approval_status = AccountApprovalStatusChoices.APPROVED
    user.save()
    return user


@pytest.fixture
def user_in_other_region(other_stt, other_region):
    """Return a user that is not in the same region as the tested regional staff."""
    user = STTUserFactory.create(
        groups=(Group.objects.get(name="Data Analyst"),),
    )
    user.stt = other_stt
    user.account_approval_status = AccountApprovalStatusChoices.APPROVED
    user.save()
    return user


@pytest.fixture
def stt_user():
    """Return a user without an STT for STT tests."""
    return STTUserFactory.create()


@pytest.fixture
def stt_user_with_group():
    """Return a user without an STT but with a group for STT tests."""
    return STTUserFactory.create(groups=(Group.objects.get(name="Data Analyst"),))


@pytest.fixture
def ofa_admin_stt_user():
    """Return an admin user without an STT for Data File tests."""
    ofa_admin = AdminSTTUserFactory.create(groups=(Group.objects.get(name="OFA Admin"),))
    ofa_admin.account_approval_status = AccountApprovalStatusChoices.APPROVED
    ofa_admin.save()
    return ofa_admin


@pytest.fixture
def ofa_admin():
    """Return an ofa admin user."""
    ofa_admin = UserFactory.create(groups=(Group.objects.get(name="OFA Admin"),))
    ofa_admin.account_approval_status = AccountApprovalStatusChoices.APPROVED
    ofa_admin.save()
    return ofa_admin


@pytest.fixture
def ofa_system_admin():
    """Return on OFA System Admin user."""
    ofa_sys_adming = UserFactory.create(groups=(Group.objects.get(name='OFA System Admin'),))
    ofa_sys_adming.account_approval_status = AccountApprovalStatusChoices.APPROVED
    ofa_sys_adming.save()
    return ofa_sys_adming


@pytest.fixture
def data_analyst(stt):
    """Return a data analyst user."""
    user = UserFactory.create(groups=(Group.objects.get(name="Data Analyst"),),)
    user.stt = stt
    user.account_approval_status = AccountApprovalStatusChoices.APPROVED
    user.save()
    return user


@pytest.fixture
def admin_user():
    """Return an admin user."""
    return AdminUserFactory.create()


@pytest.fixture
def staff_user():
    """Return a staff user."""
    return StaffUserFactory.create()


@pytest.fixture
def inactive_user():
    """Return an inactive user."""
    return InactiveUserFactory.create()


@pytest.fixture
def deactivated_user():
    """Return a user with an deactivated account."""
    return DeactivatedUserFactory.create()


@pytest.fixture
def stt(region):
    """Return an STT."""
    stt, _ = STT.objects.get_or_create(name="Wisconsin", region=region, stt_code="55")
    return stt


@pytest.fixture
def region():
    """Return a region."""
    region, _ = Region.objects.get_or_create(id=5)
    return region


@pytest.fixture
def fake_file_name():
    """Generate a random, but valid file name ending in .txt."""
    return _faker.file_name(extension='txt')


@pytest.fixture
def fake_file():
    """Generate an in-memory file-like object with random contents."""
    return StringIO(_faker.sentence())


@pytest.fixture
def infected_file():
    """Generate an EICAR test file that will be treated as an infected file.

    https://en.wikipedia.org/wiki/EICAR_test_file
    """
    return StringIO(
        r'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
    )


def create_temporary_file(file, file_name) -> SimpleUploadedFile:
    """Create a temporary file with an explicit name from a given string."""
    file.seek(0)
    file_contents = file.read().encode()
    return SimpleUploadedFile(file_name, file_contents)


@pytest.fixture
def data_file(fake_file, fake_file_name):
    """Temporary file for testing file uploads."""
    return create_temporary_file(fake_file, fake_file_name)


@pytest.fixture
def other_data_file(fake_file, fake_file_name):
    """Additional temporary file for testing file uploads.

    Since temporary files are destroyed as soon as they are closed and fixtures
    are only run once per function by default we need to have a second file
    available for tests that perform multiple uploads.
    """
    return create_temporary_file(fake_file, fake_file_name)


@pytest.fixture
def infected_data_file(infected_file, fake_file_name):
    """Temporary file intended to be marked as infected by ClamAV-REST."""
    return create_temporary_file(infected_file, fake_file_name)


@pytest.fixture
def base_data_file_data(fake_file_name, data_analyst):
    """Return data file creation data without a file."""
    return {
        "original_filename": fake_file_name,
        "slug": str(uuid.uuid4()),
        "extension": "txt",
        "section": "Active Case Data",
        "user": str(data_analyst.id),
        "quarter": "Q1",
        "year": 2020,
        "stt": int(data_analyst.stt.id),
        "ssp": False,
    }


@pytest.fixture
def base_regional_data_file_data(fake_file_name, regional_user):
    """Return data file creation data without a file."""
    return {
        "original_filename": fake_file_name,
        "slug": str(uuid.uuid4()),
        "extension": "txt",
        "section": "Active Case Data",
        "user": str(regional_user.id),
        "region": regional_user.region.id,
        "quarter": "Q1",
        "year": 2020,
        "stt": int(regional_user.region.stts.first().id)
    }


@pytest.fixture
def other_region():
    """Return a region that is not associated with the tested regional staff user."""
    region, _ = Region.objects.get_or_create(id=2)
    return region


@pytest.fixture
def other_stt(other_region):
    """Return an stt not in the region of a regional staff."""
    stt, _ = STT.objects.get_or_create(name="second", region=other_region)
    return stt


@pytest.fixture
def other_base_regional_data_file_data(
        fake_file_name, regional_user, other_stt):
    """Return data file creation data without a file."""
    return {
        "original_filename": fake_file_name,
        "slug": str(uuid.uuid4()),
        "extension": "txt",
        "section": "Active Case Data",
        "user": str(regional_user.id),
        "region": other_stt.region.id,
        "quarter": "Q1",
        "year": 2020,
        "stt": int(other_stt.id)
    }


@pytest.fixture
def data_file_data(base_data_file_data, data_file):
    """Return data file creation data."""
    return {
        "file": data_file,
        **base_data_file_data
    }


@pytest.fixture
def regional_data_file_data(base_regional_data_file_data, data_file):
    """Return data file creation data for a reigon."""
    return {
        "file": data_file,
        **base_regional_data_file_data
    }


@pytest.fixture
def other_regional_data_file_data(
        other_base_regional_data_file_data,
        data_file):
    """Return data file creation data for the other reigon."""
    return {
        "file": data_file,
        **other_base_regional_data_file_data
    }


@pytest.fixture
def other_data_file_data(base_data_file_data, other_data_file):
    """Return data file creation data."""
    return {
        "file": other_data_file,
        **base_data_file_data
    }


@pytest.fixture
def infected_data_file_data(base_data_file_data, infected_data_file):
    """Return data file creation data."""
    return {
        "file": infected_data_file,
        **base_data_file_data
    }


@pytest.fixture
def data_file_instance(stt):
    """Return a data file."""
    return DataFileFactory.create(stt=stt)


@pytest.fixture
def admin():
    """Return a custom LogEntryAdmin."""
    return LogEntryAdmin(LogEntry, AdminSite())


def get_private_key(private_key):
    """Getter function for transforming RSA key object to bytes for private key."""
    private_key_der = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption())
    return private_key_der


def get_public_key(private_key):
    """Getter function for transforming RSA key object to bytes for public key."""
    public_key_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo)
    return public_key_pem


@pytest.fixture()
def test_private_key():
    """Dynamically create randomized JWT keys for each run of tests."""
    # Generate our key
    # Equivalent to ~ openssl req -x509 -newkey rsa:4096
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )
    yield get_private_key(key)


# Register factories with pytest-factoryboy for automatic dependency injection
# of model-related fixtures into tests.
register(OwaspZapScanFactory)


@pytest.fixture(autouse=True)
def change_test_dir(monkeypatch, tmp_path):
    """Change the working directory to a temporary directory for all tests."""
    monkeypatch.chdir(tmp_path)
