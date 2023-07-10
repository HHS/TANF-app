"""Generate test data for stts."""

import factory
from ..models import STT, Region


class RegionFactory(factory.django.DjangoModelFactory):
    """Generate test data for regions."""

    class Meta:
        """Metadata for regions."""

        model = "stts.Region"

    id = factory.Sequence(int)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return Region.objects.create(*args, **kwargs)


class STTFactory(factory.django.DjangoModelFactory):
    """Generate test data for stts."""

    class Meta:
        """Hardcoded metadata for stts."""

        model = "stts.STT"

    id = factory.Sequence(int)
    name = factory.Sequence(lambda n: "teststt%d" % n)
    postal_code = "TT"
    type = "STATE"
    filenames = "{'Active Case Data': 'ADS.E2J.FTP1.TS72', 'Closed Case Data': 'ADS.E2J.FTP2.TS72', " \
                "'Aggregate Data': 'ADS.E2J.FTP3.TS72', 'Stratum Data': 'ADS.E2J.FTP4.TS72'}"
    stt_code = '42'
    region = factory.SubFactory(RegionFactory)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return STT.objects.create(*args, **kwargs)
