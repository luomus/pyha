#coding=utf-8
from django.test import TestCase, Client
from django.conf import settings
from pyha.models import Collection, Request
from pyha import warehouse
from django.core import mail
from pyha.test.mocks import *
from pyha.email import *
from pyha.database import update
import unittest
import mock

#mock method
def fake_fetch_email_address(personId):
	return 'test123@321.asdfgh'

class EmailTesting (TestCase):

	def setUp(self):
		self.client = Client() 
	
	def test_send_mail_after_receiving_request(self):
		req = warehouse.store(JSON_MOCK4)
		req.description = "Testausta"
		req.save()
		send_mail_after_receiving_request(req.id, "fi")
		self.assertEqual(len(mail.outbox), 1)
		msg = mail.outbox[0]
		self.assertEqual(msg.subject, 'Aineistopyyntö: Testausta')
		
	
	
	def test_mail_send_for_approval(self):
		req = warehouse.store(JSON_MOCK4)
		req.save()
		collections = Collection.objects.filter(request = req.id)
		for c in collections:
			send_mail_for_approval(req.id, c, "fi")
		self.assertEqual(len(mail.outbox), 1)
		msg = mail.outbox[0]
		self.assertEqual(msg.subject, 'Aineistopyyntö Lajitietokeskuksesta odottaa hyväksymispäätöstänne')
		self.assertTrue( "testaajapyha@gmail.com" in mail.outbox[0].to )
		self.assertTrue( "pyharengastusdata@gmail.com" in mail.outbox[0].to )
		
	
	def test_send_mail_after_request_status_change_to_requester(self):
		req = warehouse.store(JSON_MOCK4)
		req.save()
		send_mail_after_request_status_change_to_requester(req.id, "fi")
		self.assertEqual(len(mail.outbox), 1)
		msg = mail.outbox[0]
		self.assertEqual(msg.subject, 'Aineistopyyntösi tila Lajitietokeskuksessa on muuttunut')
		
	
	#does not test fetch_email_address
	@mock.patch("pyha.email.fetch_email_address", fake_fetch_email_address)
	def test_mail_is_actually_sent_when_request_is_recieved(self):
		json_str= JSON_MOCK4
		self.client.post('/api/request/', data= json_str, content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(len(mail.outbox), 1)
		msg = mail.outbox[0]
		self.assertEqual(msg.to, ['test123@321.asdfgh'])
	
	
		
	#does not test fetch_email_address
	@mock.patch("pyha.email.fetch_email_address", fake_fetch_email_address)
	def test_mail_is_actually_sent_when_request_status_is_changed(self):
		req = warehouse.store(JSON_MOCK6)
		req.save()
		wantedRequest = Request.requests.get(id=req.id)
		requestCollections = Collection.objects.filter(request=req.id)
		requestCollections[0].status = 4
		wantedRequest.sensstatus = 2
		wantedRequest.save()
		update(req, "fi")
		self.assertEqual(len(mail.outbox), 1)
		msg = mail.outbox[0]
		self.assertEqual(msg.subject, 'Aineistopyyntösi tila Lajitietokeskuksessa on muuttunut')
		self.assertEqual(msg.to, ['test123@321.asdfgh'])
	
	#does not test fetch_email_address
	@mock.patch("pyha.email.fetch_email_address", fake_fetch_email_address)
	def test_correct_mail_is_sent_when_request_is_handled(self):
		req = warehouse.store(JSON_MOCK6)
		req.save()
		wantedRequest = Request.requests.get(id=req.id)
		wantedRequest.sensstatus = 4
		wantedRequest.save()
		
		requestCollections = Collection.objects.filter(request=req.id)
		for i in requestCollections:
			i.status=4
			i.save()
		
		update(req, "fi")
		self.assertEqual(len(mail.outbox), 1)
		msg = mail.outbox[0]
		self.assertEqual(msg.subject, 'Pyyntösi käsittely on valmistunut')
		self.assertEqual(msg.to, ['test123@321.asdfgh'])
	
	#does not test fetch_email_address
	@mock.patch("pyha.email.fetch_email_address", fake_fetch_email_address)
	def test_correct_mail_is_sent_when_request_is_handled_perms(self):
		req = warehouse.store(JSON_MOCK6)
		req.save()
		mailsTotal = 1
		
		for j in range(0,2):
			wantedRequest = Request.requests.get(id=req.id)
			if j == 0:
				wantedRequest.sensstatus = 0
			elif j == 1:
				wantedRequest.sensstatus = 3
			elif j == 2:
				wantedRequest.sensstatus = 4
			wantedRequest.save()
			for k in range(-1,4):
				if k != 1:
					requestCollections = Collection.objects.filter(request=req.id)
					for i in requestCollections:
						i.status=k
						i.save()
					
					update(req, "fi")
					self.assertEqual(len(mail.outbox), mailsTotal)
					mailsTotal+=1
					msg = mail.outbox[0]
					self.assertEqual(msg.subject, 'Pyyntösi käsittely on valmistunut')
					self.assertEqual(msg.to, ['test123@321.asdfgh'])













