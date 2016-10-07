from django.test import TestCase, Client
from django.conf import settings
from pyha.models import Collection, Request
from pyha import warehouse
import unittest


class NotLoggedInTests(TestCase):
	def setUp(self):
		self.client = Client() 

	def test_not_logged_in_gets_redirected(self):
		response = self.client.get('/index/')
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, settings.LAJIAUTH_URL+'login?target='+settings.TARGET+'&next=')

class LoggedInTests(TestCase):
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
		self.assertEqual(response.url, settings.LAJIAUTH_URL+'login?target='+settings.TARGET+'&next=')
		
class RequestTesting(TestCase):
	def setUp(self):
		self.client = Client() 
		session = self.client.session
		session['user_name'] = 'paisti'
		session['user_id'] = 10
		session['user_email'] = 'ex.apmle@example.com'
		session['token'] = 'asd213'
		session.save()
		warehouse.store(JSON_MOCK)
		

	def test_request_has_its_own_page(self):
		response = self.client.get('/pyha/request/1')
		self.assertEqual(len(Request.requests.all()), 1)
		self.assertEqual(response.status_code, 200)

	def test_user_can_only_see_their_own_requests(self):
		warehouse.store(JSON_MOCK2)
		response = self.client.get('/pyha/')
		self.assertEqual(len(Request.requests.all()), 2)
		self.assertContains(response, "Osumia:1742")
		self.assertNotContains(response, "Osumia:1741")

	def test_request_with_missing_attributes_is_not_saved(self):
		warehouse.store(JSON_MOCK3)
		response = self.client.get('/pyha/')
		self.assertEqual(len(Request.requests.all()), 1)
		self.assertNotContains(response, "http://tun.fi/HBF.C60AB314-43E9-41F8-BB7D-0775773B15555")

JSON_MOCK = '''
{
	"id": "http://tun.fi/HBF.C60AB314-43E9-41F8-BB7D-0775773B16BD",
	"source": "KE.398",
	"email": "ex.apmle@example.com",
	"approximateMatches": 1742,
	"downloadFormat": "CSV_FLAT",
	"downloadIncludes": [
	  "DOCUMENT_FACTS",
	  "GATHERING_FACTS",
	  "UNIT_FACTS"
	],
	"filters": [
		{
			"target": [
				"linnut",
				"nisaat"
			]
		},
		{
			"time": [
				"2000/"
			]
		}
	],
	"collections": [
		{
			"id": "http://tun.fi/HR.39",
			"count": 1031
		},
		{
			"id": "http://tun.fi/HR.447",
			"count": 904
		},
		{
			"id": "http://tun.fi/HR.60",
			"count": 14
		}
	]
}'''

JSON_MOCK2 = '''
{
	"id": "http://tun.fi/HBF.C60AB314-43E9-41F8-BB7D-0775773B16BE",
	"source": "KE.398",
	"email": "ex@example.com",
	"approximateMatches": 1742,
	"downloadFormat": "CSV_FLAT",
	"downloadIncludes": [
	  "DOCUMENT_FACTS",
	  "GATHERING_FACTS",
	  "UNIT_FACTS"
	],
	"filters": [
		{
			"target": [
				"linnut",
				"salaporsaat"
			]
		},
		{
			"time": [
				"2000/"
			]
		}
	],
	"collections": [
		{
			"id": "http://tun.fi/HR.39",
			"count": 1031
		},
		{
			"id": "http://tun.fi/HR.447",
			"count": 904
		},
		{
			"id": "http://tun.fi/HR.60",
			"count": 14
		}
	]
}'''

JSON_MOCK3 = '''
{
	"id": "http://tun.fi/HBF.C60AB314-43E9-41F8-BB7D-0775773B15555",
	"source": "KE.398",
	"email": "filters@example.com",
	"approximateMatches": 1742,
	"downloadFormat": "CSV_FLAT",
	"downloadIncludes": [
	  "DOCUMENT_FACTS",
	  "GATHERING_FACTS",
	  "UNIT_FACTS"
	],
	"collections": [
		{
			"id": "http://tun.fi/HR.39",
			"count": 1031
		},
		{
			"id": "http://tun.fi/HR.447",
			"count": 904
		},
		{
			"id": "http://tun.fi/HR.60",
			"count": 14
		}
	]
}'''

