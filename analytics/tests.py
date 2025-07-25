from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from rest_framework.test import APITestCase
from rest_framework import status

from .models import AnalyticsEvent, DailySummary, CustomerAnalytics
from .services import AnalyticsService
from orders.models import Order
from menu.models import MenuItem, Category


class AnalyticsServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_track_event(self):
        """Test event tracking"""
        event = AnalyticsService.track_event(
            event_type=AnalyticsEvent.USER_LOGIN,
            user=self.user,
            properties={'test': 'data'}
        )
        
        self.assertIsNotNone(event)
        self.assertEqual(event.event_type, AnalyticsEvent.USER_LOGIN)
        self.assertEqual(event.user, self.user)
        
    def test_generate_daily_summary(self):
        """Test daily summary generation"""
        target_date = date.today()
        summary = AnalyticsService.generate_daily_summary(target_date)
        
        self.assertIsNotNone(summary)
        self.assertEqual(summary.date, target_date)


class AnalyticsAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_overview_endpoint(self):
        """Test analytics overview endpoint"""
        url = reverse('analytics-overview')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('kpis', response.data['data'])
        
    def test_revenue_endpoint(self):
        """Test revenue analytics endpoint"""
        url = reverse('analytics-revenue')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
