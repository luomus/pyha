#coding=utf-8
from django.test import TestCase, Client
from django.conf import settings
from pyha.models import Collection, Request
from pyha import warehouse
from django.core import mail
from pyha.roles import USER
from pyha.test.mocks import *
import unittest

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

	def test_request_has_its_own_page(self):
		response = self.client.get('/pyha/request/1')
		self.assertEqual(len(Request.requests.all()), 1)
		self.assertEqual(response.status_code, 200)

	def test_user_can_only_see_their_own_requests(self):
		warehouse.store(JSON_MOCK2)
		response = self.client.get('/pyha/')
		self.assertEqual(len(Request.requests.all()), 2)
		self.assertContains(response, "1 742")

	def test_request_with_missing_attributes_is_not_saved(self):
		warehouse.store(JSON_MOCK3)
		response = self.client.get('/pyha/')
		self.assertEqual(len(Request.requests.all()), 1)
		self.assertNotContains(response, "http://tun.fi/HBF.C60AB314-43E9-41F8-BB7D-0775773B15555")
		
	def test_requests_filters_labels_and_values_comes_from_apitest(self):
		warehouse.store(JSON_MOCK7)
		response = self.client.get('/pyha/request/2')
		self.assertContains(response, "Pyyntösi rajaukset:")
		self.assertContains(response, "Vain salatut")
		self.assertContains(response, "true")
		self.assertContains(response, "Lajin hallinnollinen rajaus")
		self.assertContains(response, "Uhanalaiset lajit (Luonnonsuojeluasetus 14.2.1997/160, liite 4)")
		self.assertContains(response, "Lajiryhmä")
		self.assertContains(response, "Käet")
		self.assertContains(response, "Jyrsijät")
		self.assertContains(response, "Aika")
		self.assertContains(response, "2000/")



'''	def test_removing_both_secure_reasons_removes_collection(self):
		warehouse.store(JSON_MOCK7)
		response = self.client.get('/pyha/request/2')
		self.assertContains(response, 'Talvilintulaskenta')
		col = Collection.objects.all().get(address="HR.39", request=2)
		response = self.client.post('/pyha/removeCustom', {'collectionId': col.id})
		self.client.post('/pyha/removeSens', {'collectionId': col.id})
		col = Collection.objects.all().get(address="HR.39", request=2)
		
		
		self.assertNotContains(response, 'Talvilintulaskenta')'''
