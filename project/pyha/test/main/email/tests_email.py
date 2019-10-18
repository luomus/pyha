#coding=utf-8
from django.test import TestCase, Client
from django.conf import settings
from pyha.models import Collection, Request
from pyha.warehouse import store
from django.core import mail
from django.core.cache import cache
from pyha.test.mocks import JSON_MOCK4, JSON_MOCK6
from pyha.email import send_mail_after_receiving_request, send_mail_for_approval, send_mail_after_request_status_change_to_requester
from pyha.database import update_request_status
import mock
import base64
import ast

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
		emails = []
		for c in collections:
			personId = ast.literal_eval(c.downloadRequestHandler)[0]
			emails.append('test{}@321.asdfgh'.format(personId))
			cache.set('email{}'.format(personId), emails[-1])
			send_mail_for_approval(req.id, c, "fi")
		self.assertGreater(len(mail.outbox), 0)
		msg = mail.outbox[0]
		self.assertEqual(msg.subject, 'Aineistopyyntö Lajitietokeskuksesta odottaa hyväksymispäätöstänne')
		recipients = []
		for sent_mail in mail.outbox:
			recipients += sent_mail.to
		for email in emails:
			self.assertTrue(email in recipients)


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
		cols = Collection.objects.filter(request=req.id)
		col1 = cols.first()
		col1.status = 4
		col1.changedBy = "test"
		col1.save()
		col2 = cols.last()
		col2.status = 1
		col2.changedBy = "test"
		col2.save()
		update_request_status(req, "fi")
		self.assertEqual(len(mail.outbox), 1)
		msg = mail.outbox[0]
		self.assertEqual(msg.subject, 'Aineistopyyntösi tila Lajitietokeskuksessa on muuttunut')
		self.assertEqual(msg.to, ['test123@321.asdfgh'])
