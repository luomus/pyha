from django.test import TestCase, Client
from django.conf import settings
import unittest

class NotLoggedInTests(unittest.TestCase):
	def setUp(self):
		self.client = Client() 

	def test_not_logged_in_gets_redirected(self):
		response = self.client.get('/index/')
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, settings.LAJIAUTH_URL+'login?target='+settings.TARGET+'&next')

class LoggedInTests(unittest.TestCase):
	def setUp(self):
		self.client = Client() 
		session = self.client.session
		session['user_name'] = 'paisti'
		session['user_id'] = 10
		session['user_email'] = 'ex.apmle@example.com'
		session['token'] = 'asd213'
		session.save()

	def test_user_sees_the_index_page(self):
		response = self.client.get('/index/')
		self.assertEqual(response.status_code, 200)

	def test_logging_out_clears_session_information(self):
		self.client.post('/logout/')
		response = self.client.get('/index/')
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, settings.LAJIAUTH_URL+'login?target='+settings.TARGET+'&next')
