#coding=utf-8
from django.test import TestCase, Client
from django.conf import settings
from pyha.models import Collection, Request
from pyha.warehouse import store 
from pyha.database import update_request_status, testing 
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
		store(JSON_MOCK)

	def test_requests(self):
		req = store(JSON_MOCK6)
		req.status = 1
		req.sensstatus = 1
		req.save()
		for c in Collection.objects.filter(request=req.id):
			c.status = 2
			c.save()
		requestCollections = Collection.objects.filter(request=req.id)
		print(requestCollections[0].status)
		update_request_status(req, "fi")
		print(Request.requests.get(id=req.id).status)
		print(testing())
		settings.TESTING = True
		print(testing())
		self.assertTrue(True)


		

#Haluttiin että poistaa collectionin
	'''def test_removing_sens_secure_reasons_doesnt_remove_collection(self):
		req = warehouse.store(JSON_MOCK7)
		response = self.client.get('/pyha/request/2')
		self.assertContains(response, 'Talvilintulaskenta')
		col = Collection.objects.all().get(address="HR.39", request=2)
		self.client.post('/pyha/removeSens', {'collectionId': col.id, 'requestid':req.id })
		response = self.client.get('/request/2')
		
		self.assertContains(response, 'Talvilintulaskenta')'''


#Nyt pyynnön sivulla näkyy lähtökohtaisesti pelkästään yleisesti salattu data
'''	def test_requests_collections_are_shown_in_its_page(self):
		warehouse.store(JSON_MOCK6)
		response = self.client.get('/request/2')
		self.assertContains(response, "Pyyntöösi sisältyvät havainnot:")
		self.assertContains(response, "Talvilintulaskenta")
		self.assertContains(response, "Hatikka.fi")
		self.assertContains(response, "Lintujen ja nisäkkäiden ruokintapaikkaseuranta")'''
