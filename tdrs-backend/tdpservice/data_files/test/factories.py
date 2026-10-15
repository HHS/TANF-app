"""Generate test data for Data files."""

import factory

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import Program, Section
from tdpservice.stts.test.factories import STTFactory
from tdpservice.users.test.factories import UserFactory


def canonical_section_for(program_code, section_name):
    """Create canonical program/section rows if a transactional test flushed them."""
    program, _ = Program.objects.get_or_create(
        code=program_code,
        defaults={
            "slug": program_code.lower(),
            "name": program_code,
        },
    )
    section, _ = Section.objects.get_or_create(
        program=program,
        name=section_name,
    )
    return section


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
    state = SubmissionState.UPLOADED
    user = factory.SubFactory(UserFactory)
    stt = factory.SubFactory(STTFactory)
    file = factory.django.FileField(data=b"test", filename="my_data_file.txt")
    s3_versioning_id = 0

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        """Resolve scalar inputs to unsaved relation objects for build()."""
        program_code = kwargs.pop("program_type", "TAN")
        section = kwargs.get("section")
        if not isinstance(section, Section):
            program = Program(
                code=program_code,
                slug=program_code.lower(),
                name=program_code,
            )
            kwargs["section"] = Section(program=program, name=section)
        return super()._build(model_class, *args, **kwargs)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Populate canonical section rows only for database-backed instances."""
        program_code = kwargs.pop("program_type", "TAN")
        section = kwargs.get("section")
        if not isinstance(section, Section):
            kwargs["section"] = canonical_section_for(program_code, section)
        return super()._create(model_class, *args, **kwargs)
