from django.test import TestCase, Client
import unittest

class SimpleTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_not_logged_in_gets_redirected(self):
    	response = self.client.get('/login/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'https://fmnh-ws-test.it.helsinki.fi/laji-auth/login?target=KE.541&next')