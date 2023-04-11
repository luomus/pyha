# coding=utf-8
from pyha.models import Collection, Request, StatusEnum
from pyha.warehouse import store
from pyha.database import update_request_status
from pyha.roles import USER
from pyha.test.base_test import BaseTestCase
from pyha.test.mocks import *


class RequestTesting(BaseTestCase):
    def setUp(self):
        super().setUp()
        session = self.client.session
        session['user_name'] = 'paisti'
        session['user_id'] = 'MA.309'
        session['user_email'] = 'ex.apmle@example.com'
        session["current_user_role"] = USER
        session['token'] = 'asd213'
        session.save()
        store(JSON_MOCK)

    def test_requests_skip_offi_waiting(self):
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
