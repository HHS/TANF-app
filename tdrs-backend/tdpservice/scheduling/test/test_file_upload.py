"""Test class for the upload configurations."""

from datetime import datetime

import pytest
from paramiko import Transport
from paramiko.sftp_client import SFTPClient
from tdpservice.scheduling.tasks import upload
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.stts.models import STT


@pytest.fixture
def stt_instance(region):
    """Return an STT."""
    stt, _ = STT.objects.get_or_create(
        name="first",
        region=region,
        code="AR",
        stt_codee=1234,
    )
    return stt

@pytest.fixture
def data_file_instance():
    """Data file fixture instance for testing datafile."""
    return DataFileFactory.create(
        created_at=datetime.now(),
    )


@pytest.fixture
def sftp_connection_values(sftpserver):
    """SFTP connection values for local sftp server."""
    server_address = sftpserver.host
    local_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEpQIBAAKCAQEAsf16LYNvP6vAcxZhSueDCxIpgUbOr4Hj6f37B/nAU+EIbU+3
i54NXTMmtDjG+xzRNOH110h3o7P3A5B7cFu+IlG0AHzlsBbfO/JAGzcLbtKnxDwn
/C5gFpUNKWqvj9kgqRmrmqPLl7UjfYxZVUSRD8Gh/zIONvTl3C0/EsPn/77e0YH/
wC7QDyg4rikK9Cksekp9PiskgkeqCIJTk0ETiGGhOODUBOWrhHCZBXAvbbhBe/EV
diU0IUKU869Ci0dKKP3h6YjeDhNwrkNa7jZnXPYPRHdsmWi+RK70dsoZe/MkK2GE
yucjsh8gCHWvltlJ7NQJ0fkrcrEdTp5K9ddVAQIDAQABAoIBAHMMDYIHt8vm/1Ek
gSTCeiCYz70hAI3PHntr0Gv6UgelqCXH5jLXqXm5i2XoYS2FFfDhsV9DFxn4REzI
ghFBK6fROdEq6eglEIwV7Lvqm3g5r3kXDR1i+HcARu6jZ/FJ/mNvFU2yW/Gmgtcu
9bs4w670kPp751Y8e6sSj/dYK8hRCoQlN7B5Ald8bZpVcZA/aVmJLfGvzNBY0D+x
wsTRvZn5Q7XG/BJL0+ZWJoSEi4SPrkENUdlHueRHpwPlzBuiGmksrpYvlnnqwvZD
ld90hxkGgnDCmReTzBRKqSPh3wab+OKzePVrLGDFzhd4V5rSsOJl01uOHac/8QLZ
vHCQEDECgYEA2VHvIkmwu+BpDLXAmD8aiKfzcrEGT32SDVZaNdRcrADXKbtVmSKN
I/UCmtfwNVHZk/FMPqarnfWtqv0B62eovI8qaYNCzNUFCKW3aUcACnnMc9HKlYsf
25jJF2X3JzMv319xYnniy77fr6RsxFw2l/7J3dg0tNeFUvPVMPt8trUCgYEA0at/
eqzMowG/8dwFubY3t/hlwPT4HuvD1A+/yC5jThU280l7lCwRjk9Eh9024Ihy0XuP
+m6af1IMzhg5fYqrF7sU7Tqxx2m+47J5iQZ+m2n6jSLDslqTcAYKj9XOHMJ3/ANe
+eZKpXxpTstfX7A5Yug9a58PjleMjdm1VpDzKJ0CgYEAhOem58FJZJ0JocxFzNZK
0+hi6nF4+oRBHgcBhIorYsXg0JTQ9KY8yxC8VxZYwUMdXWzkxCwKKMBnRXsWAXGT
sD2eIok0ATEFsxQl5yyUydNTRkG3M12yTgpScQza6g5T6LfmD+Oa4CALjM9x9WSv
vqUDr7jaAv8Len/EkgA7dUECgYEAx5X5/pvZHF5BCgkIhjTXq09QBTLrsft56Tao
t/S4YQ6+xS4w7eZZO99m+/HvGCOrMI/viVOZzBMdz12t9Dx5C1jx3bTeoFWf+X3e
RTqicGycrZbnNLMV4DBQA4Vh82yG7KWE1luKuSbJ09CyVBMbPXSXawf5teTPDgSs
ot/OJ90CgYEAvWYQHspz7irepznaDSwnUqbfDPNQr16IN6s3KnR/MGKl6q54uQ80
2U/k4d3KxHMAFEUVBXSBOwFswoz0ZgR9bzMUDsoSwtnfXoyFvG1GiW20diNpjPIg
toSg3kO4adt6TdPPc1hRlbKah+Ft20qVhvaPAmQDJD3Ow8we7UAZIas=
-----END RSA PRIVATE KEY-----"""
    username = "user"
    port = sftpserver.port

    return {
        'server_address': server_address,
        'username': username,
        'local_key': local_key,
        'port': port
    }

@pytest.fixture(scope="session")
def sftpclient(sftpserver):
    """SFTP client fixture for testing sftp."""
    transport = Transport((sftpserver.host, sftpserver.port))
    transport.connect(username="a", password="b")
    sftpclient = SFTPClient.from_transport(transport)
    yield sftpclient
    sftpclient.close()
    transport.close()

@pytest.mark.django_db
def test_new_data_file(sftpserver, data_file_instance, sftp_connection_values, sftpclient):
    """Datafile object for testing the file."""
    data_file_instance.save()
    with sftpserver.serve_content({'a_dir': {'somefile.txt': "File content"}}):
        upload(data_file_instance.pk,
               server_address=sftp_connection_values['server_address'],
               local_key=sftp_connection_values['local_key'],
               username=sftp_connection_values['username'],
               port=sftp_connection_values['port'])
        today_date = datetime.today()
        upper_directory_name = today_date.strftime('%Y%m%d')
        lower_directory_name = today_date.strftime(str(data_file_instance.year) +
                                                   '-' +
                                                   str(data_file_instance.quarter))
        assert sftpclient.listdir(upper_directory_name+'/'+lower_directory_name)[0] == \
               data_file_instance.create_filename()
