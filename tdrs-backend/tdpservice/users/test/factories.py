"""Generate test data for users."""

import factory

from tdpservice.stts.test.factories import STTFactory


class UserFactory(factory.django.DjangoModelFactory):
    """Generate test data for users."""

    class Meta:
        """Hardcoded metata data for users."""

        model = "users.User"
        django_get_or_create = ("username",)

    id = factory.Faker("uuid4")
    username = factory.Sequence(lambda n: "testuser%d" % n)
    password = "test_password"  # Static password so we can login.
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    is_staff = False
    is_superuser = False
    stt = factory.SubFactory(STTFactory)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)


class AdminUserFactory(UserFactory):
    """Generate Admin User."""

    is_staff = True
    is_superuser = True


class StaffUserFactory(UserFactory):
    """Generate Staff User."""

    is_staff = True
