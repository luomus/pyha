# coding=utf-8
from django.conf import settings
from pyha.test.base_test import BaseTestCase


class NotLoggedInTests(BaseTestCase):
    def test_not_logged_in_gets_redirected(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, settings.LAJIAUTH_URL+'login?target='+settings.TARGET+'&next=')
