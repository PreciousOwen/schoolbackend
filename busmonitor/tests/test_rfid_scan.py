from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

class RFIDScanViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('rfid_scan')
        # Create a test user and log in if the view requires authentication
        self.user = get_user_model().objects.create_user(
            username='testuser', password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_rfid_scan_post(self):
        data = {
            'rfid': 'TEST_RFID_123',
            'bus_id': 1
        }
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertIn(response.status_code, [200, 201, 400])  # Acceptable codes depending on logic
        # Optionally, check response content or database changes
