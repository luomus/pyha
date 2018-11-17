#coding=utf-8
from django.test import TestCase, Client
from django.conf import settings
from pyha.models import Collection, Request, Sens_StatusEnum
from pyha.warehouse import store
from django.core import mail
from django.core.cache import cache
from pyha.test.mocks import JSON_MOCK4, JSON_MOCK6
from pyha.email import send_mail_after_receiving_request, send_mail_for_approval, send_mail_after_request_status_change_to_requester
from pyha.database import update_request_status
import mock
import base64

class EmailTesting (TestCase):

	def setUp(self):
		self.client = Client() 
		cache.set('emailMA.309','test123@321.asdfgh')
	
	def test_send_mail_after_receiving_request(self):
		req = store(JSON_MOCK4)
		req.description = "Testausta"
		req.changedBy = "test"
		req.save()
		send_mail_after_receiving_request(req.id, "fi")
		self.assertEqual(len(mail.outbox), 1)
		msg = mail.outbox[0]
		self.assertEqual(msg.subject, 'Aineistopyyntö: Testausta')
		
	
	
	def test_mail_send_for_approval(self):
		req = store(JSON_MOCK4)
		req.changedBy = "test"
		req.save()
		collections = Collection.objects.filter(request = req.id)
		for c in collections:
			send_mail_for_approval(req.id, c, "fi")
		self.assertGreater(len(mail.outbox), 0)
		msg = mail.outbox[0]
		self.assertEqual(msg.subject, 'Aineistopyyntö Lajitietokeskuksesta odottaa hyväksymispäätöstänne')
		self.assertTrue( "testaajapyha@gmail.com" in mail.outbox[0].to )
		self.assertTrue( "pyharengastusdata@gmail.com" in mail.outbox[0].to )
		
	
	def test_send_mail_after_request_status_change_to_requester(self):
		req = store(JSON_MOCK4)
		req.changedBy = "test"
		req.save()
		send_mail_after_request_status_change_to_requester(req.id, "fi")
		self.assertEqual(len(mail.outbox), 1)
		msg = mail.outbox[0]
		self.assertEqual(msg.subject, 'Aineistopyyntösi tila Lajitietokeskuksessa on muuttunut')
		

	def test_mail_is_actually_sent_when_request_is_received(self):
		json_str= JSON_MOCK4
		self.client.post('/api/request', data= json_str, content_type='application/json', HTTP_AUTHORIZATION='Basic ' + base64.b64encode((settings.SECRET_HTTPS_USER+':'+settings.SECRET_HTTPS_PW).encode()).decode())
		self.assertEqual(len(mail.outbox), 1)
		msg = mail.outbox[0]
		self.assertEqual(msg.to, ['test123@321.asdfgh'])
	
	
	def test_mail_is_actually_sent_when_request_status_is_changed(self):
		req = store(JSON_MOCK6)
		req.changedBy = "test"
		req.save()
		wantedRequest = Request.objects.get(id=req.id)
		requestCollections = Collection.objects.filter(request=req.id)
		requestCollections[0].status = 4
		wantedRequest.sensStatus = Sens_StatusEnum.REJECTED
		wantedRequest.changedBy = "test"
		wantedRequest.save()
		update_request_status(req, "fi")
		self.assertEqual(len(mail.outbox), 1)
		msg = mail.outbox[0]
		self.assertEqual(msg.subject, 'Aineistopyyntösi tila Lajitietokeskuksessa on muuttunut')
		self.assertEqual(msg.to, ['test123@321.asdfgh'])
	

	#DEPRECATED
	#SKIP STRAIGHT TO DOWNLOAD
	#def test_correct_mail_is_sent_when_request_is_handled(self):
	#	req = store(JSON_MOCK6)
	#	req.save()
	#	wantedRequest = Request.objects.get(id=req.id)
	#	wantedRequest.sensStatus = 4
	#	wantedRequest.save()
	#	
	#	requestCollections = Collection.objects.filter(request=req.id)
	#	for i in requestCollections:
	#		i.status=4
	#		i.save()
	#	
	#	update(req, "fi")
	#	self.assertEqual(len(mail.outbox), 1)
	#	msg = mail.outbox[0]
	#	self.assertEqual(msg.subject, 'Pyyntösi käsittely on valmistunut')
	#	self.assertEqual(msg.to, ['test123@321.asdfgh'])

	#DEPRECATED
	#SKIP STRAIGHT TO DOWNLOAD
	#def test_correct_mail_is_sent_when_request_is_handled_perms(self):
	#	req = store(JSON_MOCK6)
	#	req.save()
	#	mailsTotal = 1
	#	
	#	for j in range(0,2):
	#		wantedRequest = Request.objects.get(id=req.id)
	#		if j == 0:
	#			wantedRequest.sensStatus = 0
	#		elif j == 1:
	#			wantedRequest.sensStatus = 3
	#		elif j == 2:
	#			wantedRequest.sensStatus = 4
	#		wantedRequest.save()
	#		for k in range(-1,4):
	#			if k != 1:
	#				requestCollections = Collection.objects.filter(request=req.id)
	#				for i in requestCollections:
	#					i.status=k
	#					i.save()
	#				
	#				update_request_status(req, "fi")
	#				self.assertEqual(len(mail.outbox), mailsTotal)
	#				mailsTotal+=1
	#				msg = mail.outbox[0]
	#				self.assertEqual(msg.subject, 'Pyyntösi käsittely on valmistunut')
	#				self.assertEqual(msg.to, ['test123@321.asdfgh'])













