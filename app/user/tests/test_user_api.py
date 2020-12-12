from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    """
    Helper function to create a new user
    """
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """
    Test the user API (public).
    """
    def setUp(self):
        """
        Creating one client for our test suit that
        can be reused for all of the tests.
        """
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """
        Test creating user with valid payload is successful.
        """
        payload = {
            'email': 'test@gmail.com',
            'password': 'testpass',
            'name': 'Name',
        }

        request = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**request.data)

        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', request.data)

    def test_user_exists(self):
        """
        Test creating a user that already exist fails.
        """
        payload = {
            'email': 'test@gmail.com',
            'password': 'testpass',
            'name': 'Test',
        }

        create_user(**payload)

        request = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """
        Test that tha password must be more than 5 characters
        """
        payload = {
            'email': 'test@gmail.com',
            'password': 'pw',
            'name': 'Test',
        }

        request = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """
        Test that a token is created for the user
        """
        payload = {
            'email': 'test@gmail.com',
            'password': 'pw',
        }

        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)

        # check to see there is a key called 'token' in the response data
        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """
        Test that token is not created if invalid credentials are given
        """
        create_user(email='test@gmail.com', password='pass')

        payload = {
            'email': 'test@gmail.com',
            'password': 'wrong',
        }

        response = self.client.post(TOKEN_URL, payload)

        # check to see there is NO key called 'token' in the response data
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """
        Test that token is not created if user doesn't exist
        """
        payload = {
            'email': 'test@gmail.com',
            'password': 'pass',
        }

        response = self.client.post(TOKEN_URL, payload)

        # check to see there is NO key called 'token' in the response data
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """
        Test that email and password are required
        """
        response = self.client.post(TOKEN_URL, {'email': 'test@gmail.com',
                                                'password': ''})

        # check to see there is NO key called 'token' in the response data
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
