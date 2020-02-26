from django.test import TestCase
from django.contrib.auth import get_user_model

# Create your tests here.


class UsersManagersTests(TestCase):

    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(email='tanfnormal@user.com')
        self.assertEqual(user.email, 'tanfnormal@user.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(user.username)
        except AttributeError:
            pass
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(ValueError):
            User.objects.create_user(email='')

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(email='tanfsuper@user.com')
        self.assertEqual(admin_user.email, 'tanfsuper@user.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(admin_user.username)
        except AttributeError:
            pass
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='tanfsuper2@user.com', is_superuser=False)

    def test_create_staffuser(self):
        User = get_user_model()
        staff_user = User.objects.create_user(email='tanfstaff@user.com', is_staff=True)
        self.assertEqual(staff_user.email, 'tanfstaff@user.com')
        self.assertTrue(staff_user.is_active)
        self.assertTrue(staff_user.is_staff)
        self.assertFalse(staff_user.is_superuser)
        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(staff_user.username)
        except AttributeError:
            pass
