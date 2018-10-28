#coding=utf-8
from django.test import TestCase, Client
from django.conf import settings
from pyha.models import Collection, Request
from pyha import warehouse
from django.core import mail
from pyha.roles import USER
from pyha.test.mocks import *
import unittest

class RequestStatusTesting(TestCase):
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


