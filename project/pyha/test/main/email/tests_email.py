# coding=utf-8
from django.conf import settings
from pyha.models import Collection, Request
from pyha.warehouse import store
from django.core import mail
from django.core.cache import cache
from pyha.test.mocks import JSON_MOCK4, JSON_MOCK6
from pyha.email import send_mail_after_receiving_request, send_mail_after_request_status_change_to_requester
from pyha.database import update_request_status
from pyha.test.base_test import BaseTestCase
import base64


class EmailTesting (BaseTestCase):

    def setUp(self):
        super().setUp()
        cache.set('emailMA.309', 'test123@321.asdfgh')

    def test_send_mail_after_receiving_request(self):
        req = store(JSON_MOCK4)
        req.description = "Testausta"
        req.changedBy = "test"
        req.save()
        send_mail_after_receiving_request(req.id, "fi")
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertEqual(msg.subject, 'Aineistopyyntö: Testausta')

    def test_send_mail_after_request_status_change_to_requester(self):
        req = store(JSON_MOCK4)
        req.changedBy = "test"
        req.save()
        send_mail_after_request_status_change_to_requester(req.id, "fi")
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertEqual(msg.subject, 'Aineistopyyntösi tila on muuttunut')

    def test_mail_is_actually_sent_when_request_is_received(self):
        json_str = JSON_MOCK4
        self.client.post('/api/request', data=json_str, content_type='application/json', HTTP_AUTHORIZATION='Basic ' +
                         base64.b64encode((settings.SECRET_HTTPS_USER+':'+settings.SECRET_HTTPS_PW).encode()).decode())
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertEqual(msg.to, ['pyhatestaaja@gmail.com'])

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
        self.assertEqual(msg.subject, 'Aineistopyyntösi tila on muuttunut')
        self.assertEqual(msg.to, ['pyhatestaaja@gmail.com'])
