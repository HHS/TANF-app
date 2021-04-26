"""Generate test data for users."""

import factory

from tdpservice.stts.test.factories import STTFactory


class BaseUserFactory(factory.django.DjangoModelFactory):
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

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        """Add groups to user instance."""
        if not create:
            return

        if extracted:
            for group in extracted:
                self.groups.add(group)


class UserFactory(BaseUserFactory):
    """General purpose user factory used through out most tests."""

    stt = factory.SubFactory(STTFactory)


class STTUserFactory(BaseUserFactory):
    """User factory for use in STT tests."""

    # To prevent an error that happens when calling the `populate_stt` command.
    # The stt factory and the command were competing over the right to set the stt.
    # Our solution was to not set the STT specifically for the STT tests that
    # were calling the `populate_stt` command.
    stt = None


class AdminUserFactory(UserFactory):
    """Generate Admin User."""

    is_staff = True
    is_superuser = True


class StaffUserFactory(UserFactory):
    """Generate Staff User."""

    is_staff = True


class InactiveUserFactory(UserFactory):
    """Generate inactive user."""

    is_active = False
