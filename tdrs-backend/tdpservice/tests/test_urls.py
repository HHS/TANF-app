from django.urls import reverse

def test_create(self):
    response = self.client.get(reverse('login'))
    self.assertEqual(response.status_code, 200)
