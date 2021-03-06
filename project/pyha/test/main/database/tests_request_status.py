# coding=utf-8
from django.test import TestCase, Client
from pyha.models import Collection, Request, StatusEnum
from pyha.warehouse import store
from pyha.database import update_request_status
from pyha.roles import USER
from pyha.test.mocks import *
import unittest
import mock


def dummy(*args, **kwargs):
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
        store(JSON_MOCK)

    @mock.patch('pyha.warehouse.requests.post', dummy)
    def test_requests_waiting(self):
        req = store(JSON_MOCK6)
        req.status = StatusEnum.WAITING
        req.changedBy = "test"
        req.save()
        requestCollections = Collection.objects.filter(request=req.id)
        c = requestCollections[0]
        c.status = StatusEnum.APPROVED
        c.changedBy = "test"
        c.save()
        c = requestCollections[1]
        c.status = StatusEnum.WAITING
        c.changedBy = "test"
        c.save()
        update_request_status(req, "fi")
        self.assertTrue(Request.objects.get(id=req.id).status == StatusEnum.WAITING)

    @mock.patch('pyha.warehouse.requests.post', dummy)
    def test_requests_skip_offi_approved(self):
        req = store(JSON_MOCK6)
        req.status = StatusEnum.WAITING
        req.changedBy = "test"
        req.save()
        for c in Collection.objects.filter(request=req.id):
            c.status = StatusEnum.APPROVED
            c.changedBy = "test"
            c.save()
        update_request_status(req, "fi")
        self.assertTrue(Request.objects.get(id=req.id).status == StatusEnum.WAITING_FOR_DOWNLOAD)

    @mock.patch('pyha.warehouse.requests.post', dummy)
    def test_requests_skip_offi_approved_with_discard(self):
        req = store(JSON_MOCK6)
        req.status = StatusEnum.WAITING
        req.changedBy = "test"
        req.save()
        requestCollections = Collection.objects.filter(request=req.id)
        c = requestCollections[0]
        c.status = StatusEnum.DISCARDED
        c.changedBy = "test"
        c.save()
        c = requestCollections[1]
        c.status = StatusEnum.APPROVED
        c.changedBy = "test"
        c.save()
        update_request_status(req, "fi")
        self.assertTrue(Request.objects.get(id=req.id).status == StatusEnum.WAITING_FOR_DOWNLOAD)

    @mock.patch('pyha.warehouse.requests.post', dummy)
    def test_requests_skip_offi_partially_approved(self):
        req = store(JSON_MOCK6)
        req.status = StatusEnum.WAITING
        req.changedBy = "test"
        req.save()
        requestCollections = Collection.objects.filter(request=req.id)
        c = requestCollections[0]
        c.status = StatusEnum.APPROVED
        c.changedBy = "test"
        c.save()
        c = requestCollections[1]
        c.status = StatusEnum.REJECTED
        c.changedBy = "test"
        c.save()
        update_request_status(req, "fi")
        self.assertTrue(Request.objects.get(id=req.id).status == StatusEnum.WAITING_FOR_DOWNLOAD)

    @mock.patch('pyha.warehouse.requests.post', dummy)
    def test_requests_skip_offi_rejected(self):
        req = store(JSON_MOCK6)
        req.status = StatusEnum.WAITING
        req.changedBy = "test"
        req.save()
        requestCollections = Collection.objects.filter(request=req.id)
        c = requestCollections[0]
        c.status = StatusEnum.REJECTED
        c.changedBy = "test"
        c.save()
        c = requestCollections[1]
        c.status = StatusEnum.REJECTED
        c.changedBy = "test"
        c.save()
        update_request_status(req, "fi")
        self.assertTrue(Request.objects.get(id=req.id).status == StatusEnum.REJECTED)

    @mock.patch('pyha.warehouse.requests.post', dummy)
    def test_requests_skip_offi_rejected_with_discard(self):
        req = store(JSON_MOCK6)
        req.status = StatusEnum.WAITING
        req.changedBy = "test"
        req.save()
        requestCollections = Collection.objects.filter(request=req.id)
        c = requestCollections[0]
        c.status = StatusEnum.DISCARDED
        c.changedBy = "test"
        c.save()
        c = requestCollections[1]
        c.status = StatusEnum.REJECTED
        c.changedBy = "test"
        c.save()
        update_request_status(req, "fi")
        self.assertTrue(Request.objects.get(id=req.id).status == StatusEnum.REJECTED)


# Haluttiin ett?? poistaa collectionin
    '''def test_removing_sens_secure_reasons_doesnt_remove_collection(self):
		req = warehouse.store(JSON_MOCK7)
		response = self.client.get('/pyha/request/2')
		self.assertContains(response, 'Talvilintulaskenta')
		col = Collection.objects.all().get(address="HR.39", request=2)
		self.client.post('/pyha/removeSens', {'collectionId': col.id, 'requestid':req.id })
		response = self.client.get('/request/2')

		self.assertContains(response, 'Talvilintulaskenta')'''


# Nyt pyynn??n sivulla n??kyy l??ht??kohtaisesti pelk??st????n yleisesti salattu data
'''	def test_requests_collections_are_shown_in_its_page(self):
		warehouse.store(JSON_MOCK6)
		response = self.client.get('/request/2')
		self.assertContains(response, "Pyynt????si sis??ltyv??t havainnot:")
		self.assertContains(response, "Talvilintulaskenta")
		self.assertContains(response, "Hatikka.fi")
		self.assertContains(response, "Lintujen ja nis??kk??iden ruokintapaikkaseuranta")'''
