# coding=utf-8
from pyha.models import Collection, Request, RequestLogEntry, StatusEnum, Col_StatusEnum
from pyha import warehouse
from django.urls import reverse
from pyha.roles import *
from pyha.test.base_test import BaseTestCase
from pyha.test.mocks import *
import mock


def fake_is_allowed_to_view(request, requestId):
    return True


def fake_is_allowed_to_handle(userId, requestId):
    return True


def fake_is_download_handler_in_collection(userId, collectionId):
    return True


def fake_get_collections_where_download_handler(userId):
    return ['HR.1', 'HR.39']


def set_request_to_waiting_state(request_id):
    req = Request.objects.get(id=request_id)
    req.status = StatusEnum.WAITING
    req.changedBy = 'test'
    req.save()

    collections = Collection.objects.filter(request=request_id)
    for c in collections:
        c.status = Col_StatusEnum.WAITING
        c.changedBy = 'test'
        c.save()


def set_request_to_approved_state(request_id):
    req = Request.objects.get(id=request_id)
    req.status = StatusEnum.APPROVED
    req.changedBy = 'test'
    req.save()

    collections = Collection.objects.filter(request=request_id)
    for c in collections:
        c.status = Col_StatusEnum.APPROVED
        c.changedBy = 'test'
        c.save()


def set_current_user_to_handler(session):
    session['user_id'] = 'MA.313'
    session['user_roles'] = [CAT_HANDLER_COLL]
    session['current_user_role'] = HANDLER_ANY
    session.save()


class RequestTesting(BaseTestCase):

    def setUp(self):
        super().setUp()
        session = self.client.session
        session['user_name'] = 'paisti'
        session['user_id'] = 'MA.309'
        session['user_email'] = 'ex.apmle@example.com'
        session['current_user_role'] = USER
        session['token'] = 'asd213'
        session.save()
        warehouse.store(JSON_MOCK)

    def test_request_has_its_own_page(self):
        response = self.client.get('/request/1')
        self.assertEqual(len(Request.objects.all()), 1)
        self.assertEqual(response.status_code, 200)

    def test_user_can_only_see_their_own_requests(self):
        warehouse.store(JSON_MOCK10)
        response = self.client.get(reverse('pyha:get_request_list_ajax'))
        data = response.json()['data']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], 1)

    @mock.patch('pyha.views.index.get_collections_where_download_handler', fake_get_collections_where_download_handler)
    def test_handler_can_filter_only_uncompleted_request(self):
        warehouse.store(JSON_MOCK10)
        set_request_to_approved_state(1)
        set_request_to_waiting_state(2)
        
        set_current_user_to_handler(self.client.session)

        response = self.client.get(reverse('pyha:get_request_list_ajax'), {'onlyUncompleted': 'true'})
        data = response.json()['data']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], 2)

    @mock.patch('pyha.views.index.get_collections_where_download_handler', fake_get_collections_where_download_handler)
    def test_handler_can_also_see_completed_requests(self):
        warehouse.store(JSON_MOCK10)
        set_request_to_approved_state(1)
        set_request_to_waiting_state(2)

        set_current_user_to_handler(self.client.session)

        response = self.client.get(reverse('pyha:get_request_list_ajax'), {'onlyUncompleted': 'false'})
        data = response.json()['data']
        self.assertEqual(len(data), 2)

    @mock.patch('pyha.views.index.get_collections_where_download_handler', fake_get_collections_where_download_handler)
    def test_handler_cannot_see_requests_they_do_not_handle(self):
        warehouse.store(JSON_MOCK4)
        warehouse.store(JSON_MOCK10)
        set_request_to_approved_state(1)
        set_request_to_waiting_state(2)
        set_request_to_waiting_state(3)

        set_current_user_to_handler(self.client.session)

        response = self.client.get(reverse('pyha:get_request_list_ajax'), {'onlyUncompleted': 'false'})
        data = response.json()['data']
        self.assertEqual(len(data), 2)
        self.assertCountEqual([data[0]['id'], data[1]['id']], [1, 3])

    def test_request_with_missing_attributes_is_not_saved(self):
        warehouse.store(JSON_MOCK3)
        response = self.client.get(reverse('pyha:root'))
        self.assertEqual(len(Request.objects.all()), 1)
        self.assertNotContains(response, 'http://tun.fi/HBF.C60AB314-43E9-41F8-BB7D-0775773B15555')

    def test_requests_filters_labels_and_values_comes_from_apitest(self):
        warehouse.store(JSON_MOCK7)
        response = self.client.get('/request/2')
        self.assertContains(response, 'Vain salatut')
        self.assertContains(response, 'true')
        self.assertContains(response, 'Lajin hallinnollinen rajaus')
        self.assertContains(response, 'Uhanalaiset lajit')
        self.assertContains(response, 'Lajiryhmä')
        self.assertContains(response, 'Kalat')
        self.assertContains(response, 'Lepakot')
        self.assertContains(response, 'Aika')
        self.assertContains(response, '2000/')

    def test_RequestLogEntry_view_own_request(self):
        self.client.get('/request/1')
        self.assertEqual(len(RequestLogEntry.requestLog.all()), 0)

    @mock.patch('pyha.views.requestview.is_allowed_to_view', fake_is_allowed_to_view)
    @mock.patch('pyha.views.requestview.is_allowed_to_handle', fake_is_allowed_to_handle)
    def test_RequestLogEntry_view_someone_elses_request(self):
        warehouse.store(JSON_MOCK6)
        wanted = Request.objects.get(id=2)
        wanted.status = 1
        wanted.changedBy = 'test'
        wanted.save()
        set_current_user_to_handler(self.client.session)

        response = self.client.get('/request/2')
        logEntry = RequestLogEntry.requestLog.get(request=wanted)
        self.assertEqual(logEntry.user, 'MA.313')
        self.assertEqual(logEntry.role, CAT_HANDLER_COLL)
        self.assertEqual(logEntry.collection, None)
        self.assertEqual(logEntry.action, 'VIEW')
        self.assertEqual(len(RequestLogEntry.requestLog.all()), 1)

    def test_RequestLogEntry_accept(self):
        warehouse.store(JSON_MOCK6)
        self.client.post(reverse('pyha:approve'), {'requestid': 2, 'checkb': ['sens', 'colcustomsec1']})
        logEntry = RequestLogEntry.requestLog.get(request=Request.objects.get(id=2), collection=None)
        self.assertEqual(logEntry.user, 'MA.309')
        self.assertEqual(logEntry.role, USER)
        self.assertEqual(logEntry.action, 'ACC')
        self.assertEqual(len(RequestLogEntry.requestLog.all()), 1)

    @mock.patch('pyha.views.requestview.is_allowed_to_view', fake_is_allowed_to_view)
    @mock.patch('pyha.views.requestview.is_allowed_to_handle', fake_is_allowed_to_handle)
    @mock.patch('pyha.database.is_download_handler_in_collection', fake_is_download_handler_in_collection)
    def test_RequestLogEntry_answer_coll_positive(self):
        request1 = Request.objects.get(id=1)
        request1.status = 1
        request1.changedBy = 'test'
        request1.save()
        col = Collection.objects.all().get(address='HR.39', request=1)
        col.downloadRequestHandler = ['MA.313']
        col.changedBy = 'test'
        col.save()
        session = self.client.session
        session['user_id'] = 'MA.313'
        session['user_roles'] = CAT_HANDLER_COLL
        session['current_user_role'] = HANDLER_ANY
        session.save()

        self.client.post(reverse('pyha:answer'), {'requestid': 1, 'answer': 1, 'collectionid': 'HR.39'})
        logEntry = RequestLogEntry.requestLog.get(request=request1, collection=col)
        self.assertEqual(logEntry.user, 'MA.313')
        self.assertEqual(logEntry.role, CAT_HANDLER_COLL)
        self.assertEqual(logEntry.action, 'POS')
        self.assertEqual(len(RequestLogEntry.requestLog.all()), 1)

    @mock.patch('pyha.views.requestview.is_allowed_to_view', fake_is_allowed_to_view)
    @mock.patch('pyha.views.requestview.is_allowed_to_handle', fake_is_allowed_to_handle)
    @mock.patch('pyha.database.is_download_handler_in_collection', fake_is_download_handler_in_collection)
    def test_RequestLogEntry_answer_coll_negative(self):
        warehouse.store(JSON_MOCK6)
        request2 = Request.objects.get(id=2)
        request2.status = 1
        request2.changedBy = 'test'
        request2.save()
        col = Collection.objects.all().get(address='colcustomsec1', request=2)
        col.downloadRequestHandler = ['MA.313']
        col.changedBy = 'test'
        col.save()
        session = self.client.session
        session['user_id'] = 'MA.313'
        session['user_roles'] = CAT_HANDLER_COLL
        session['current_user_role'] = HANDLER_ANY
        session.save()

        self.client.post(reverse('pyha:answer'), {'requestid': 2, 'answer': 0,
                         'collectionid': 'colcustomsec1', 'reason': 'ei sovi'})
        logEntry = RequestLogEntry.requestLog.get(request=request2, collection=col)
        self.assertEqual(logEntry.user, 'MA.313')
        self.assertEqual(logEntry.role, CAT_HANDLER_COLL)
        self.assertEqual(logEntry.action, 'NEG')
        self.assertEqual(len(RequestLogEntry.requestLog.all()), 1)
