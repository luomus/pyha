#coding=utf-8
from django.test import TestCase, Client
from django.conf import settings
from pyha.models import Collection, Request, RequestLogEntry
from pyha import warehouse
from django.core import mail
from django.urls import reverse
from pyha.roles import *
from pyha import login
from pyha.test.mocks import *
import unittest
import mock

def fake_is_allowed_to_view(request, requestId):
	return True

def fake_is_download_handler_in_collection(userId, collectionId):
	return True

class RequestTesting(TestCase):
			
	def setUp(self):
		self.client = Client() 
		session = self.client.session
		session['user_name'] = 'paisti'
		session['user_id'] = 'MA.309'
		session['user_email'] = 'ex.apmle@example.com'
		session["current_user_role"] = USER
		session['token'] = 'asd213'
		session.save()
		warehouse.store(JSON_MOCK)
		warehouse.update_collections()

	def test_request_has_its_own_page(self):
		response = self.client.get('/request/1')
		self.assertEqual(len(Request.objects.all()), 1)
		self.assertEqual(response.status_code, 200)

	def test_user_can_only_see_their_own_requests(self):
		warehouse.store(JSON_MOCK2)
		response = self.client.get(reverse('pyha:root'))
		self.assertEqual(len(Request.objects.all()), 2)
		self.assertContains(response, "1 742")

	def test_request_with_missing_attributes_is_not_saved(self):
		warehouse.store(JSON_MOCK3)
		response = self.client.get(reverse('pyha:root'))
		self.assertEqual(len(Request.objects.all()), 1)
		self.assertNotContains(response, "http://tun.fi/HBF.C60AB314-43E9-41F8-BB7D-0775773B15555")
		
	def test_requests_filters_labels_and_values_comes_from_apitest(self):
		warehouse.store(JSON_MOCK7)
		response = self.client.get('/request/2')
		self.assertContains(response, "Vain salatut")
		self.assertContains(response, "true")
		self.assertContains(response, "Lajin hallinnollinen rajaus")
		self.assertContains(response, "Uhanalaiset lajit")
		self.assertContains(response, "Lajiryhmä")
		self.assertContains(response, "Käet")
		self.assertContains(response, "Jyrsijät")
		self.assertContains(response, "Aika")
		self.assertContains(response, "2000/")

	def test_RequestLogEntry_view_own_request(self):
		self.client.get('/request/1')
		self.assertEqual(len(RequestLogEntry.requestLog.all()), 0)

	
	@mock.patch("pyha.views.requestview.is_allowed_to_view", fake_is_allowed_to_view)
	@mock.patch("pyha.views.requestview.is_download_handler_in_collection", fake_is_download_handler_in_collection)
	def test_RequestLogEntry_view_someone_elses_request(self):
		warehouse.store(JSON_MOCK6)
		wanted = Request.objects.get(id=2)
		wanted.status = 1
		wanted.changedBy = "test"
		wanted.save()
		session = self.client.session
		session['user_id'] = 'MA.313'
		session["user_roles"] = CAT_HANDLER_BOTH in session["current_user_role"] = HANDLER_ANY
		session.save()
	
		response = self.client.get('/request/2')
		logEntry = RequestLogEntry.requestLog.get(request = wanted)	
		self.assertEqual(logEntry.user, "MA.313")
		self.assertEqual(logEntry.role, CAT_HANDLER_BOTH)	
		self.assertEqual(logEntry.collection, None)
		self.assertEqual(logEntry.action, "VIEW")
		self.assertEqual(len(RequestLogEntry.requestLog.all()), 1) 

	def test_RequestLogEntry_accept(self):
		warehouse.store(JSON_MOCK6)
		self.client.post(reverse('pyha:approve'), {'requestid': 2, 'checkb': ['sens','colcustomsec1'] })
		logEntry = RequestLogEntry.requestLog.get(request = Request.objects.get(id=2), collection = None )
		self.assertEqual(logEntry.user, "MA.309")
		self.assertEqual(logEntry.role, USER)
		self.assertEqual(logEntry.action, "ACC")
		self.assertEqual(len(RequestLogEntry.requestLog.all()), 1)

	def test_RequestLogEntry_answer_sens_positive(self):
		request1 = Request.objects.get(id=1)
		request1.status = 1
		request1.changedBy = "test"
		request1.save()
		session = self.client.session
		session['user_id'] = 'MA.313'
		session["user_roles"] = CAT_HANDLER_BOTH in session["current_user_role"] = HANDLER_ANY
		session.save()

		self.client.post(reverse('pyha:answer'), {'requestid': 1,'answer' : 1, 'collectionid':'sens'})
		logEntry = RequestLogEntry.requestLog.get(request = request1)
		self.assertEqual(logEntry.user, "MA.313")
		self.assertEqual(logEntry.role, CAT_HANDLER_SENS)		
		self.assertEqual(logEntry.action, 'POS')
		self.assertEqual(len(RequestLogEntry.requestLog.all()), 1)

	def test_RequestLogEntry_answer_sens_negative(self):
		warehouse.store(JSON_MOCK6)
		request2 = Request.objects.get(id=2)
		request2.status = 1
		request2.changedBy = "test"
		request2.save()
		session = self.client.session
		session['user_id'] = 'MA.313'
		session["user_roles"] = CAT_HANDLER_BOTH	
		session["current_user_role"] = HANDLER_ANY
		session.save()

		self.client.post(reverse('pyha:answer'), {'requestid': 2,'answer' : 0,'collectionid': 'sens', 'reason': 'ei sovi' })
		logEntry = RequestLogEntry.requestLog.get(request = request2)
		self.assertEqual(logEntry.user, "MA.313")
		self.assertEqual(logEntry.role, CAT_HANDLER_SENS)
		self.assertEqual(logEntry.action, 'NEG')
		self.assertEqual(len(RequestLogEntry.requestLog.all()), 1)

	@mock.patch("pyha.views.requestview.is_allowed_to_view", fake_is_allowed_to_view)
	@mock.patch("pyha.views.requestview.is_download_handler_in_collection", fake_is_download_handler_in_collection)
	def test_RequestLogEntry_answer_coll_positive(self):
		request1 = Request.objects.get(id=1)
		request1.status = 1
		request1.changedBy = "test"
		request1.save()
		col = Collection.objects.all().get(address="HR.39", request=1)
		col.downloadRequestHandler = ['MA.313']
		col.changedBy = "test"
		col.save()
		session = self.client.session
		session['user_id'] = 'MA.313'
		session["user_roles"] = CAT_HANDLER_COLL	
		session["current_user_role"] = HANDLER_ANY
		session.save()

		self.client.post(reverse('pyha:answer'), {'requestid': 1,'answer' : 1, 'collectionid':"HR.39"})
		logEntry = RequestLogEntry.requestLog.get(request = request1, collection = col)
		self.assertEqual(logEntry.user, "MA.313")
		self.assertEqual(logEntry.role, CAT_HANDLER_COLL)
		self.assertEqual(logEntry.action, 'POS')
		self.assertEqual(len(RequestLogEntry.requestLog.all()), 1)

	@mock.patch("pyha.views.requestview.is_allowed_to_view", fake_is_allowed_to_view)
	@mock.patch("pyha.views.requestview.is_download_handler_in_collection", fake_is_download_handler_in_collection)
	def test_RequestLogEntry_answer_coll_negative(self):
		warehouse.store(JSON_MOCK6)
		request2 = Request.objects.get(id=2)
		request2.status = 1
		request2.changedBy = "test"
		request2.save()
		col = Collection.objects.all().get(address="colcustomsec1", request=2)
		col.downloadRequestHandler = ['MA.313']
		col.changedBy = "test"
		col.save()
		session = self.client.session
		session['user_id'] = 'MA.313'
		session["user_roles"] = CAT_HANDLER_BOTH	
		session["current_user_role"] = HANDLER_ANY
		session.save()

		self.client.post(reverse('pyha:answer'), {'requestid': 2,'answer' : 0,'collectionid': 'colcustomsec1', 'reason': 'ei sovi' })
		logEntry = RequestLogEntry.requestLog.get(request = request2, collection = col )
		self.assertEqual(logEntry.user, "MA.313")
		self.assertEqual(logEntry.role, CAT_HANDLER_COLL)	
		self.assertEqual(logEntry.action, 'NEG')
		self.assertEqual(len(RequestLogEntry.requestLog.all()), 1)

'''	def test_removing_both_secure_reasons_removes_collection(self):
		warehouse.store(JSON_MOCK7)
		response = self.client.get('/pyha/request/2')
		self.assertContains(response, 'Talvilintulaskenta')
		col = Collection.objects.all().get(address="HR.39", request=2)
		response = self.client.post('/pyha/removeCustom', {'collectionId': col.id})
		self.client.post('/pyha/removeSens', {'collectionId': col.id})
		col = Collection.objects.all().get(address="HR.39", request=2)
		
		
		self.assertNotContains(response, 'Talvilintulaskenta')'''
