"""Generate test data for users."""

import factory


class UserFactory(factory.django.DjangoModelFactory):
    """Generate test data for users."""

    class Meta:
        """Hardcoded metata data for users."""

        model = "users.User"
        django_get_or_create = ("username",)

    id = factory.Faker("uuid4")
    username = factory.Sequence(lambda n: f"testuser{n}")
    password = "test_password"  # Static password so we can login.
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    is_staff = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)
