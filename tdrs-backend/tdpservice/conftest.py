"""Globally available pytest fixtures."""
import pytest
from django.contrib.admin.models import LogEntry
from django.contrib.admin.sites import AdminSite
from io import StringIO
import uuid

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import Group
from factory.faker import faker
from rest_framework.test import APIClient

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import datetime

from tdpservice.stts.test.factories import STTFactory, RegionFactory
from tdpservice.core.admin import LogEntryAdmin
from tdpservice.reports.test.factories import ReportFileFactory
from tdpservice.users.test.factories import (
    UserFactory,
    AdminUserFactory,
    StaffUserFactory,
    STTUserFactory,
    InactiveUserFactory,
    AdminSTTUserFactory,
    DeactivatedUserFactory,
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
def stt_user():
    """Return a user without an STT for STT tests."""
    return STTUserFactory.create()

@pytest.fixture
def ofa_admin_stt_user():
    """Return an admin user without an STT for Data Report tests."""
    return AdminSTTUserFactory.create(groups=(Group.objects.get(name="OFA Admin"),))


@pytest.fixture
def ofa_admin():
    """Return an ofa admin user."""
    return UserFactory.create(groups=(Group.objects.get(name="OFA Admin"),))


@pytest.fixture
def data_analyst():
    """Return a data analyst user."""
    return UserFactory.create(groups=(Group.objects.get(name="Data Analyst"),))


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
def stt():
    """Return an STT."""
    return STTFactory.create()


@pytest.fixture
def other_stt():
    """Return a secondary STT."""
    return STTFactory.create()


@pytest.fixture
def region():
    """Return a region."""
    return RegionFactory.create()


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
def base_report_data(fake_file_name, user):
    """Return report creation data without a file."""
    return {
        "original_filename": fake_file_name,
        "slug": str(uuid.uuid4()),
        "extension": "txt",
        "section": "Active Case Data",
        "user": str(user.id),
        "quarter": "Q1",
        "year": 2020,
        "stt": int(user.stt.id)
    }


@pytest.fixture
def report_data(base_report_data, data_file):
    """Return report creation data."""
    return {
        "file": data_file,
        **base_report_data
    }


@pytest.fixture
def other_report_data(base_report_data, other_data_file):
    """Return report creation data."""
    return {
        "file": other_data_file,
        **base_report_data
    }


@pytest.fixture
def infected_report_data(base_report_data, infected_data_file):
    """Return report creation data."""
    return {
        "file": infected_data_file,
        **base_report_data
    }


@pytest.fixture
def report():
    """Return a report file."""
    return ReportFileFactory.create()


@pytest.fixture
def admin():
    """Return a custom LogEntryAdmin."""
    return LogEntryAdmin(LogEntry, AdminSite())


def generate_test_jwt():
    """Dynamically create randomized JWT keys for each run of tests"""
    # deploy-backend.sh:
    #   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -sha256
    # jwt-key-rotation.md:
    #   openssl enc -base64 -w 0 -in jwtRS256prv.pem -out jwtRS256prv.pem.base64
    #   update JWT_KEY with this value
    

    KEY_FILE = "key.pem"
    CERT_FILE = "cert.pem"

    #   openssl req -x509 -newkey rsa:4096
    # Generate our key
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )

    # -keyout key.pem
    # Write our key to disk for safe keeping
    with open(KEY_FILE, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(b"passphrase"), # -nodes 
        ))
    
    # Various details about who we are. For a self-signed certificate the
    # subject and issuer are always the same.
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Distrint of Columbia"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Washington D.C."),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"OCIO OFA"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"tdp-frontend.app.cloud.gov"),
    ])

     
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        # Our certificate will be valid for 10 days
        datetime.datetime.utcnow() + datetime.timedelta(days=365) # -days 365 
    ).add_extension(
        x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
        critical=False,
    # Sign our certificate with our private key
    ).sign(key, hashes.SHA256()) # -sha256
    # Write our certificate out to disk.
    #-out cert.pem
    with open(CERT_FILE, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    return key

def get_private_key(private_key):
    #private_key = generate_test_jwt()

    private_key_der = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()) #\
        #.decode("utf-8")
        
    """
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption())
    """
    # strip off header
    #private_key_der_encoded = ''.join(private_key_der.split('\n')[1:-2])
    return private_key_der

def get_public_key(private_key):
    #private_key = generate_test_jwt()
    public_key_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo) \
        .decode("utf-8")
    # strip off header
    #public_key_der_encoded = ''.join(public_key_pem.split('\n')[1:-2])

    return public_key_der
