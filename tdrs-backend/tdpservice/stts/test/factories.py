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
        """Hardcoded metata data for stts."""

        model = "stts.STT"

    id = factory.Sequence(int)
    name = factory.Sequence(lambda n: "teststt%d" % n)
    code = "TT"
    type = "STATE"
    region = factory.SubFactory(RegionFactory)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return STT.objects.create(*args, **kwargs)
