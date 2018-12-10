﻿from __future__ import unicode_literals
import json
from argparse import Namespace
from simple_history.models import HistoricalRecords
from django.utils.encoding import python_2_unicode_compatible
from django.db import models


class TruncatingCharField(models.CharField):
	def get_prep_value(self, value):
		value = super(TruncatingCharField,self).get_prep_value(value)
		if value:
			return value[:self.max_length]
		return value
	
class TruncatingReasonJsonCharField(models.CharField):
	def get_prep_value(self, value):
		max_lengths = [("argument_project", 500),
		("argument_research", 500),
		("argument_goals", 2000),
		("argument_planning", 2000),
		("argument_municipality", 2000),
		("argument_natura_areas", 2000),
		("argument_reason", 4000)]
		
		value = super(TruncatingReasonJsonCharField,self).get_prep_value(value)
		if value:
			reasonlist = json.loads(value, object_hook=lambda d: Namespace(**d))
			fields = reasonlist.fields
			for f in fields.__dict__:
				for	m in max_lengths:
					if(m[0] == f):
						t = getattr(fields, f)
						setattr(fields, f, t[:m[1]])
						break
			reasonlist.fields = vars(fields)
			value = json.dumps(vars(reasonlist))
			return value
		return value


@python_2_unicode_compatible
class Collection(models.Model):
	address = models.CharField(max_length=500)
	count = models.IntegerField()
	
	#for collection.status
	#status 0: Odottaa pyytäjän hyväksymistä
	#status 1: Odottaa aineiston toimittajan käsittelyä
	#status 3: Hylätty
	#status 4: Hyväksytty
	#status 6: Odottaa vastausta lisäkysymyksiin
	
	status = models.IntegerField()
	request = models.ForeignKey('Request', on_delete=models.CASCADE)
	taxonSecured = models.IntegerField(default=0)
	customSecured = models.IntegerField(default=0)
	downloadRequestHandler = models.CharField(max_length=500,blank=True,null=True)
	decisionExplanation = TruncatingCharField(max_length=1000,blank=True,null=True)
	changedBy = models.CharField(max_length=100)
	history = HistoricalRecords()

	def __str__(self):
		return 'Collection: %s (in Request: %d)' %(self.address, self.request.id)
	

@python_2_unicode_compatible
class Request(models.Model):
	#id alkaa ykkösestä ja nousee
	id = models.AutoField(primary_key=True)
	lajiId = models.CharField(max_length=200) #id given by laji.api
	description = TruncatingCharField(max_length=400,blank=True,null=True)  #description given by the requester for his request
	
	#for status
	#status 0: Odottaa pyytäjän hyväksymistä
	#status 1: Odottaa aineiston toimittajan käsittelyä
	#status 2: Osittain hyväksytty
	#status 3: Hylätty
	#status 4: Hyväksytty
	#status 5: Tuntematon
	#status 6: Odottaa vastausta lisäkysymyksiin
	#status 7: Odottaa latauksen valmistumista
	#status 8: Ladattavissa
	
	status = models.IntegerField()
	
	#for sensStatus
	#status 0: Odottaa pyytäjän hyväksymistä
	#status 1: Odottaa viranomaisen käsittelyä
	#status 3: Hylätty
	#status 4: Hyväksytty
	#status 99: Ohitettu (skippofficial)
	
	sensStatus = models.IntegerField()
	sensDecisionExplanation = TruncatingCharField(max_length=1000,blank=True,null=True)
	sensComment = TruncatingCharField(max_length=1000,blank=True,null=True)
	date = models.DateTimeField()
	source = models.CharField(max_length=60)
	user = models.CharField(max_length=100)
	approximateMatches = models.IntegerField()
	downloadFormat = models.CharField(max_length=40)
	downloadIncludes = models.CharField(max_length=1000)
	downloadDate = models.CharField(max_length=400,blank=True,null=True)
	filter_list = models.CharField(max_length=2000)
	personName = TruncatingCharField(max_length=100,blank=True,null=True)
	personStreetAddress = TruncatingCharField(max_length=100,blank=True,null=True)
	personPostOfficeName = TruncatingCharField(max_length=100,blank=True,null=True)
	personPostalCode = TruncatingCharField(max_length=100,blank=True,null=True)
	personCountry = TruncatingCharField(max_length=100,blank=True,null=True)
	personEmail = TruncatingCharField(max_length=100,blank=True,null=True)
	personPhoneNumber = TruncatingCharField(max_length=100,blank=True,null=True)
	personOrganizationName = TruncatingCharField(max_length=100,blank=True,null=True)
	personCorporationId = TruncatingCharField(max_length=100,blank=True,null=True)
	reason = TruncatingReasonJsonCharField(max_length=16000,blank=True,null=True)
	lang = models.CharField(max_length=10, default='fi') 
	frozen = models.BooleanField(default=False)
	changedBy = models.CharField(max_length=100)
	history = HistoricalRecords()

	def __str__(self):
		return 'Request: %d [%s] (lajiId: %s)' %(self.id, self.date.strftime('%d.%m.%Y %H:%M:%S'), self.lajiId)

@python_2_unicode_compatible
class RequestContact(models.Model):
	id = models.AutoField(primary_key=True)
	request = models.ForeignKey('Request', on_delete=models.CASCADE)
	personName = TruncatingCharField(max_length=100,blank=True,null=True)
	personStreetAddress = TruncatingCharField(max_length=100,blank=True,null=True)
	personPostOfficeName = TruncatingCharField(max_length=100,blank=True,null=True)
	personPostalCode = TruncatingCharField(max_length=100,blank=True,null=True)
	personCountry = TruncatingCharField(max_length=100,blank=True,null=True)
	personEmail = TruncatingCharField(max_length=100,blank=True,null=True)
	personPhoneNumber = TruncatingCharField(max_length=100,blank=True,null=True)
	personOrganizationName = TruncatingCharField(max_length=100,blank=True,null=True)
	personCorporationId = TruncatingCharField(max_length=100,blank=True,null=True)
	changedBy = models.CharField(max_length=100)
	history = HistoricalRecords()
	
	def __str__(self):
		return 'RequestContact: %s (in Request: %d)' %(self.personName, self.request.id)

@python_2_unicode_compatible
class RequestLogEntry(models.Model):
	VIEW = 'VIEW'
	ACCEPT = 'ACC'
	DECISION_POSITIVE = 'POS'
	DECISION_POSITIVE_OVERDUE = 'POSOV'
	DECISION_RESET = 'RESET'
	DECISION_NEGATIVE = 'NEG'
	ACTION = (
		(VIEW, 'views request'),
		(ACCEPT, 'accepts terms of use'),
		(DECISION_POSITIVE, 'accepts use of data'),
		(DECISION_POSITIVE_OVERDUE, 'accepted use of data, because decision has been overdue'),
		(DECISION_RESET, 'resets the decision regarding data'),
		(DECISION_NEGATIVE, 'declines use of data'),
	)
	
	request = models.ForeignKey(Request, on_delete=models.CASCADE)
	collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, blank=True, null=True)
	date = models.DateTimeField(auto_now_add=True)
	user = models.CharField(max_length=100)
	role = models.CharField(max_length=100)
	action = models.CharField(max_length=5, choices=ACTION)
	requestLog = models.Manager()
	changedBy = models.CharField(max_length=100)
	history = HistoricalRecords()
	
	def __str__(self):
		return 'RequestLogEntry: %s (role: %s) [%s]: %s (Request: %d, collection: %s)' %(self.user, self.role, self.date.strftime('%d.%m.%Y %H:%M:%S'), self.get_action_display(), self.request.id, self.collection )

@python_2_unicode_compatible		
class RequestSensitiveChatEntry(models.Model):
	request = models.ForeignKey(Request, on_delete=models.CASCADE)
	date = models.DateTimeField(auto_now_add=True)
	user = models.CharField(max_length=100)
	message = TruncatingCharField(max_length=2000)
	requestChat = models.Manager()
	changedBy = models.CharField(max_length=100)
	history = HistoricalRecords()
	
	def __str__(self):
		return 'RequestSensitiveChatEntry: %s (in Request: %d) [%s]: %s' %(self.user, self.request.id, self.date.strftime('%d.%m.%Y %H:%M:%S'), self.message)
	
@python_2_unicode_compatible		
class RequestHandlerChatEntry(models.Model):
	request = models.ForeignKey(Request, on_delete=models.CASCADE)
	date = models.DateTimeField(auto_now_add=True)
	user = models.CharField(max_length=100)
	message = TruncatingCharField(max_length=2000)
	target = models.CharField(max_length=200)
	requestHandlerChat = models.Manager()
	changedBy = models.CharField(max_length=100)
	history = HistoricalRecords()
	
	def __str__(self):
		return 'RequestHandlerChatEntry: %s (in Request: %d, as target: %s) [%s]: %s' %(self.user, self.request.id, self.target, self.date.strftime('%d.%m.%Y %H:%M:%S'), self.message)

@python_2_unicode_compatible
class RequestInformationChatEntry(models.Model):
	request = models.ForeignKey(Request, on_delete=models.CASCADE)
	date = models.DateTimeField(auto_now_add=True)
	user = models.CharField(max_length=100)
	question = models.BooleanField()
	message = TruncatingCharField(max_length=2000)
	target = models.CharField(max_length=200) #'sens' or apilaji defined collection id
	requestInformationChat = models.Manager()
	changedBy = models.CharField(max_length=100)
	history = HistoricalRecords()
	
	def __str__(self):
		return 'RequestInformationChatEntry: %s (in Request: %d, as/to target: %s, Question: %s) [%s]: %s' %(self.user, self.request.id, self.target, self.question, self.date.strftime('%d.%m.%Y %H:%M:%S'), self.message)

@python_2_unicode_compatible
class ContactPreset(models.Model):
	user = models.CharField(primary_key=True, max_length=100)
	requestPersonName = TruncatingCharField(max_length=100,blank=True,null=True)
	requestPersonStreetAddress = TruncatingCharField(max_length=100,blank=True,null=True)
	requestPersonPostOfficeName = TruncatingCharField(max_length=100,blank=True,null=True)
	requestPersonPostalCode = TruncatingCharField(max_length=100,blank=True,null=True)
	requestPersonCountry = TruncatingCharField(max_length=100,blank=True,null=True)
	requestPersonEmail = TruncatingCharField(max_length=100,blank=True,null=True)
	requestPersonPhoneNumber = TruncatingCharField(max_length=100,blank=True,null=True)
	requestPersonOrganizationName = TruncatingCharField(max_length=100,blank=True,null=True)
	requestPersonCorporationId = TruncatingCharField(max_length=100,blank=True,null=True)
	changedBy = models.CharField(max_length=100)
	history = HistoricalRecords()
	
	def __str__(self):
		return 'ContactPreset: %s' %(self.user)

def enum(*sequential, **named):
	enums = dict(zip(sequential, range(len(sequential))), **named)
	return type(str('Enum'), (), enums)

StatusEnum = enum(
				DISCARDED=-1,
				APPROVETERMS_WAIT=0,
				WAITING=1,
				PARTIALLY_APPROVED=2,
				REJECTED=3,
				APPROVED=4,
				UNKNOWN=5,
				WAITING_FOR_INFORMATION=6,
				WAITING_FOR_DOWNLOAD=7,
				DOWNLOADABLE=8)

Sens_StatusEnum = enum(
				APPROVETERMS_WAIT=0,
				WAITING=1,
				REJECTED=3,
				APPROVED=4,
				IGNORE_OFFICIAL=99)

Col_StatusEnum = enum(
				APPROVETERMS_WAIT=0,
				WAITING=1,
				REJECTED=3,
				APPROVED=4)