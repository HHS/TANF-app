"""Model instance factories related to Security models to be used in tests."""
from faker import Factory as FakerFactory
import factory

from tdpservice.security.models import OwaspZapScan

faker = FakerFactory.create()


class OwaspZapScanFactory(factory.django.DjangoModelFactory):
    """Factory for OwaspZapScan instances."""

    class Meta:
        """Meta options tying the factory to the model."""

        model = OwaspZapScan

    app_target = factory.Iterator(OwaspZapScan.AppTarget.choices)
    html_report = factory.django.FileField(filename='owasp_report.html')
    scanned_at = factory.LazyAttribute(lambda x: faker.date_time())

    fail_count = factory.LazyAttribute(
        lambda x: faker.random_int(min=0, max=256)
    )
    pass_count = factory.LazyAttribute(
        lambda x: faker.random_int(min=0, max=256)
    )
    warn_count = factory.LazyAttribute(
        lambda x: faker.random_int(min=0, max=256)
    )
