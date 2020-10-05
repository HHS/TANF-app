"""Generate test data for stts."""

import factory


class RegionFactory(factory.django.DjangoModelFactory):
    """Generate test data for regions."""

    class Meta:
        """Metadata for regions."""

        model = "stts.Region"

    id = factory.Sequence(int)


class STTFactory(factory.django.DjangoModelFactory):
    """Generate test data for stts."""

    class Meta:
        """Hardcoded metata data for stts."""

        model = "stts.STT"

    name = factory.Sequence(lambda n: "teststt%d" % n)
    code = "TT"
    type = "STATE"
    region = factory.SubFactory(RegionFactory)
