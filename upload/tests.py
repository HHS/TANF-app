from django.test import TestCase
from django.test import Client
from django.contrib.auth import get_user_model

# Create your tests here.


class CheckUI(TestCase):
    anonymousclient = Client()

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(email='tanfuser@gsa.gov')
        cls.superuser = User.objects.create_superuser(email='tanfsuperuser@gsa.gov')
        cls.staffuser = User.objects.create_user(email='tanfstaff@gsa.gov', is_staff=True)

    def test_about(self):
        """about page has proper data"""
        response = self.anonymousclient.get("/about/")
        self.assertIn(b'Welcome to the TANF Data Reporting system', response.content)

    def test_authentication(self):
        """We cannot get into pages if we are not authenticated"""
        pages = {
            '/': b'Current user',
            '/status/': b'Current user',
            '/viewquarter/': b'Current user',
        }
        for k, v in pages.items():
            response = self.anonymousclient.get(k)
            self.assertNotEqual(response.status_code, 200)
            self.assertNotIn(v, response.content, msg='anonymous ' + k)

            self.client.force_login(self.user)
            response = self.client.get(k)
            self.assertEqual(response.status_code, 200)
            self.assertIn(v, response.content, msg='user ' + k)

            self.client.force_login(self.staffuser)
            response = self.client.get(k)
            self.assertEqual(response.status_code, 200)
            self.assertIn(v, response.content, msg='user ' + k)

            self.client.force_login(self.superuser)
            response = self.client.get(k)
            self.assertEqual(response.status_code, 200)
            self.assertIn(v, response.content, msg='superuser ' + k)

    def test_staffuser_authentication(self):
        """We cannot get into admin pages if we are not staff or superuser authenticated"""
        self.assertTrue(self.staffuser.is_staff)

        page = '/useradmin'
        response = self.anonymousclient.get(page)
        self.assertRedirects(response, '/admin/login/?next=/useradmin', status_code=302, target_status_code=200)

        self.client.force_login(self.user)
        response = self.client.get(page)
        self.assertRedirects(response, '/admin/login/?next=/useradmin', status_code=302, target_status_code=200)

        self.client.force_login(self.superuser)
        response = self.client.get(page)
        self.assertRedirects(response, '/admin/users/tanfuser/', status_code=302, target_status_code=200)

        self.client.force_login(self.staffuser)
        response = self.client.get(page)
        self.assertRedirects(response, '/admin/users/tanfuser/', status_code=302, target_status_code=200)

    def test_upload_exists(self):
        """upload page has proper data"""
        self.client.force_login(self.user)
        response = self.client.get("/")
        self.assertIn(b'Upload to the TANF Data Reporting system', response.content)

    def test_upload_data(self):
        """upload page accepts data, sends us to the Status page, and status page has a file"""
        self.client.force_login(self.user)
        with open('upload/fixtures/testdata.txt') as f:
            response = self.client.post("/", {'name': 'myfile', 'myfile': f}, follow=True)
            self.assertIn(b'<th>Status</th>', response.content)
            self.assertIn(b'tanfuser@gsa.gov_', response.content)
            self.assertIn(b'_testdata.txt', response.content)
