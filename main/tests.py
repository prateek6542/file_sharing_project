from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import User, FileUpload

class UserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.ops_user_data = {
            "username": "opsuser",
            "password": "password123",
            "is_ops": True
        }
        self.client_user_data = {
            "username": "clientuser",
            "password": "password123"
        }
        self.ops_user = User.objects.create_user(**self.ops_user_data)
        self.client_user = User.objects.create_user(**self.client_user_data)

    def test_signup(self):
        response = self.client.post(reverse('signup'), {
            "username": "newclient",
            "password": "newpassword123"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login(self):
        response = self.client.post(reverse('login'), {
            "username": self.ops_user_data['username'],
            "password": self.ops_user_data['password']
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_upload_file(self):
        self.client.force_authenticate(user=self.ops_user)
        with open('testfile.docx', 'rb') as file:
            response = self.client.post(reverse('upload-file'), {'file': file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_files(self):
        self.client.force_authenticate(user=self.client_user)
        response = self.client.get(reverse('list-files'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_download_file(self):
        self.client.force_authenticate(user=self.client_user)
        file = FileUpload.objects.create(file='testfile.docx', uploaded_by=self.ops_user)
        response = self.client.get(reverse('download-file', args=[file.id]), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('download-link', response.data)
