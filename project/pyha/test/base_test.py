from django.test import TestCase, Client
from mock import patch
from argparse import Namespace


def dummy_post(*args, **kwargs):
    return Namespace(ok=True)


class BaseTestCase(TestCase):
    def setUp(self):
        self.patcher = patch('pyha.warehouse.requests.post', dummy_post)
        self.mock_send_download_request = self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.client = Client()
