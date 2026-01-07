"""Generate test data for Data files."""

import factory

from tdpservice.stts.test.factories import STTFactory
from tdpservice.users.test.factories import UserFactory


class DataFileFactory(factory.django.DjangoModelFactory):
    """Generate test data for data files."""

    class Meta:
        """Hardcoded meta data for data files."""

        model = "data_files.DataFile"

    original_filename = "data_file.txt"
    slug = "data_file-txt-slug"
    extension = "txt"
    section = "Active Case Data"
    program_type = "TAN"
    quarter = "Q1"
    year = 2020
    version = 1
    user = factory.SubFactory(UserFactory)
    stt = factory.SubFactory(STTFactory)
    file = factory.django.FileField(data=b"test", filename="my_data_file.txt")
    s3_versioning_id = 0
