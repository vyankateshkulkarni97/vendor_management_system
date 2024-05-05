from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Vendor

class VendorAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.vendor = Vendor.objects.create(name='Test Vendor', contact_details='test@example.com', address='123 Test St', vendor_code='TEST001')

    def test_get_vendor_details(self):
        response = self.client.get(reverse('vendor-detail', args=[self.vendor.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Vendor')

    def test_create_vendor(self):
        data = {'name': 'New Vendor', 'contact_details': 'new@example.com', 'address': '456 New St', 'vendor_code': 'NEW001'}
        response = self.client.post(reverse('vendor-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vendor.objects.count(), 2)  
