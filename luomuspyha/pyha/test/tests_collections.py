#coding=utf-8
from django.test import TestCase, Client
from django.conf import settings
from pyha.models import Collection, Request
from pyha import warehouse
from django.core import mail
from pyha.roles import USER
from pyha.test.mocks import *
import unittest

class CollectionTesting(TestCase):
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

	def test_requests_collections_secure_reason_amounts_are_saved(self):
		warehouse.store(JSON_MOCK6)
		col1 = Collection.objects.get(address="colcustomsec1")
		col2 = Collection.objects.get(address="colsecured")
		self.assertEqual(col1.customSecured, 1)
		self.assertEqual(col2.customSecured, 2)
		self.assertEqual(col2.taxonSecured, 3)

	def test_collection_has_correct_secure_reason_amounts(self):
		warehouse.store(JSON_MOCK6)
		col = Collection.objects.all().get(address="colcustomsec1")
		self.assertEqual(col.customSecured, 1)
		self.assertEqual(col.taxonSecured, 0)
		
	def test_collection_has_correct_secure_reason_amounts2(self):
		warehouse.store(JSON_MOCK6)
		col = Collection.objects.all().get(address="colsecured")
		self.assertEqual(col.customSecured, 2)
		self.assertEqual(col.taxonSecured, 3)
		
	def test_collections_sensitive_secure_reasons_can_be_deleted(self):
		warehouse.store(JSON_MOCK6)
		col = Collection.objects.all().get(address="colsecured")
		self.assertEqual(col.customSecured, 2)

		response = self.client.post('/pyha/removeCustom', {'collectionId': col.id})
		col = Collection.objects.all().get(address="colsecured")

		self.assertEqual(col.customSecured, 0)
		
	def test_collections_sensitive_secure_reasons_can_be_deleted(self):
		req = warehouse.store(JSON_MOCK6)
		col = Collection.objects.all().get(address="colsecured")
		self.assertEqual(col.taxonSecured, 3)

		response = self.client.post('/pyha/removeSens', {'collectionId': col.id, 'requestid':req.id })
		col = Collection.objects.all().get(address="colsecured")

		self.assertEqual(col.taxonSecured, 0)

#Haluttiin että poistaa collectionin
	'''def test_removing_sens_secure_reasons_doesnt_remove_collection(self):
		req = warehouse.store(JSON_MOCK7)
		response = self.client.get('/pyha/request/2')
		self.assertContains(response, 'Talvilintulaskenta')
		col = Collection.objects.all().get(address="HR.39", request=2)
		self.client.post('/pyha/removeSens', {'collectionId': col.id, 'requestid':req.id })
		response = self.client.get('/pyha/request/2')
		
		self.assertContains(response, 'Talvilintulaskenta')'''


#Nyt pyynnön sivulla näkyy lähtökohtaisesti pelkästään yleisesti salattu data
'''	def test_requests_collections_are_shown_in_its_page(self):
		warehouse.store(JSON_MOCK6)
		response = self.client.get('/pyha/request/2')
		self.assertContains(response, "Pyyntöösi sisältyvät havainnot:")
		self.assertContains(response, "Talvilintulaskenta")
		self.assertContains(response, "Hatikka.fi")
		self.assertContains(response, "Lintujen ja nisäkkäiden ruokintapaikkaseuranta")'''
