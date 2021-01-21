from __future__ import unicode_literals
import json
from argparse import Namespace
from simple_history.models import HistoricalRecords
from django.db import models

#Use "python manage.py makemigrations pyha" to update the changes to model classes used by the app.
#After that, also do "bash updateserver.sh" or "python manage.py migrate" in development, deployment and staging
#to update these changes to the corresponding databases.

#WARNING
#It is definitely recommended to turn the pyha service down for the duration of the git pull and updateserver/migrate command.
#Older version of the app may cause unexpected behavior to the database if left running with users in it.

class TruncatingCharField(models.CharField):
	def get_prep_value(self, value):
		value = super(TruncatingCharField,self).get_prep_value(value)
		if value:
			return value[:self.max_length]
		return value

class TruncatingTextField(models.TextField):
	def get_prep_value(self, value):
		value = super(TruncatingTextField,self).get_prep_value(value)
		if value:
			return value[:self.max_length]
		return value

class TruncatingReasonJsonCharField(models.CharField):
	def get_prep_value(self, value):
		max_lengths = [("argument_project", 500),
		("argument_research", 500),
		("argument_research_address", 500),
		("argument_goals", 2000),
		("argument_planning", 2000),
		("argument_municipality", 2000),
		("argument_natura_areas", 2000),
		("argument_reason", 4000),
		("argument_customer", 500),
		("argument_customer_contact", 500)]

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

class Collection(models.Model):
	address = models.CharField(max_length=500)

	# old count fields, may be removed in the future
	count = models.IntegerField()
	taxonSecured = models.IntegerField(default=0)
	customSecured = models.IntegerField(default=0)
	quarantineSecured = models.IntegerField(default=0)

	# new count field
	count_list = models.CharField(max_length=2000)

	#for collection.status
	#status 0: Odottaa pyytäjän hyväksymistä
	#status 1: Odottaa aineiston toimittajan käsittelyä
	#status 3: Hylätty
	#status 4: Hyväksytty

	status = models.IntegerField()
	request = models.ForeignKey('Request', on_delete=models.CASCADE)
	downloadRequestHandler = models.CharField(max_length=500,blank=True,null=True)
	decisionExplanation = TruncatingTextField(max_length=5000,blank=True,null=True)
	changedBy = models.CharField(max_length=100)
	history = HistoricalRecords()

	def __str__(self):
		return 'Collection: %s (in Request: %d)' %(self.address, self.request.id)

class HandlerInRequest(models.Model): #Used currently for the admin email gatekeeper, on who has been emailed per request
	user = models.CharField(max_length=500)
	request = models.ForeignKey('Request', on_delete=models.CASCADE)
	emailed = models.BooleanField(default=False)
	changedBy = models.CharField(max_length=100)
	history = HistoricalRecords()

	def __str__(self):
		return 'Handler: %s (in Request: %d) is emailed %s' %(self.user, self.request.id, self.emailed)

class RequestSentStatusEmail(models.Model): # Keep track of the last status email that has been sent to user
	id = models.AutoField(primary_key=True)
	request = models.ForeignKey('Request', on_delete=models.CASCADE)
	accepted_count = models.IntegerField()
	declined_count = models.IntegerField()
	pending_count = models.IntegerField()
	date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return 'Status email (for Request: %d) that was sent %s' %(self.request.id, self.date.strftime('%d.%m.%Y %H:%M:%S'))

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

	date = models.DateTimeField()
	source = models.CharField(max_length=60)
	user = models.CharField(max_length=100)
	approximateMatches = models.IntegerField()
	downloadFormat = models.CharField(max_length=40)
	downloadIncludes = models.CharField(max_length=1000)
	downloadDate = models.CharField(max_length=400,blank=True,null=True)
	downloaded = models.BooleanField(null=True)
	filter_list = models.CharField(max_length=5000)
	filter_description_list = models.CharField(max_length=10000)
	public_link = models.CharField(max_length=10000)
	private_link = models.CharField(max_length=10000)
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

class RequestLogEntry(models.Model):
	VIEW = 'VIEW'
	RECEIVE = 'REC'
	ACCEPT = 'ACC'
	DECISION_POSITIVE = 'POS'
	DECISION_POSITIVE_OVERDUE = 'POSOV'
	DECISION_POSITIVE_NO_OBSERVATIONS = 'POSNO'
	DECISION_RESET = 'RESET'
	DECISION_NEGATIVE = 'NEG'
	DECISION_NEGATIVE_OVERDUE = 'NEGOV'
	WITHDRAW = 'WITHD'
	ACTION = (
		(VIEW, 'views request'),
		(RECEIVE, 'receives request'),
		(ACCEPT, 'accepts terms of use'),
		(DECISION_POSITIVE, 'accepts use of data'),
		(DECISION_POSITIVE_OVERDUE, 'accepted use of data, because decision has been overdue'),
		(DECISION_POSITIVE_NO_OBSERVATIONS, 'accepted use of data, because no observations'),
		(DECISION_RESET, 'resets the decision regarding data'),
		(DECISION_NEGATIVE, 'declines use of data'),
		(DECISION_NEGATIVE_OVERDUE, 'declines use of data, because decision has been overdue'),
		(WITHDRAW, 'withdraws request')
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

class RequestHandlerChatEntry(models.Model):
	request = models.ForeignKey(Request, on_delete=models.CASCADE)
	date = models.DateTimeField(auto_now_add=True)
	user = models.CharField(max_length=100)
	message = TruncatingTextField(max_length=5000)
	target = models.CharField(max_length=200)
	requestHandlerChat = models.Manager()
	changedBy = models.CharField(max_length=100)
	history = HistoricalRecords()

	def __str__(self):
		return 'RequestHandlerChatEntry: %s (in Request: %d, as target: %s) [%s]: %s' %(self.user, self.request.id, self.target, self.date.strftime('%d.%m.%Y %H:%M:%S'), self.message)

class RequestInformationChatEntry(models.Model):
	request = models.ForeignKey(Request, on_delete=models.CASCADE)
	date = models.DateTimeField(auto_now_add=True)
	user = models.CharField(max_length=100)
	question = models.BooleanField()
	message = TruncatingTextField(max_length=5000)
	target = models.CharField(max_length=200) #apilaji defined collection id
	requestInformationChat = models.Manager()
	changedBy = models.CharField(max_length=100)
	history = HistoricalRecords()

	def __str__(self):
		return 'RequestInformationChatEntry: %s (in Request: %d, as/to target: %s, Question: %s) [%s]: %s' %(self.user, self.request.id, self.target, self.question, self.date.strftime('%d.%m.%Y %H:%M:%S'), self.message)

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


class AdminUserSettings(models.Model):
	ALL = 'ALL'
	MISSING = 'MISSING'
	NONE = 'NONE'
	EMAIL_NEW_REQUESTS_SETTING = (
		(ALL, 'all requests'),
		(MISSING, 'requests missing handlers'),
		(NONE, 'none requests'),
	)

	user = models.CharField(primary_key=True, max_length=100)
	emailNewRequests = models.CharField(max_length=10, choices=EMAIL_NEW_REQUESTS_SETTING, default=NONE)
	enableCustomEmailAddress = models.BooleanField(default=False)
	customEmailAddress = TruncatingCharField(max_length=100,blank=True,null=True)
	changedBy = models.CharField(max_length=100)
	history = HistoricalRecords()

	def __str__(self):
		return 'AdminSettings: %s ' %(self.user)

class AdminPyhaSettings(models.Model):
	settingsName = TruncatingCharField(max_length=100,blank=False,null=False)
	enableDailyHandlerEmail = models.BooleanField(default=False)
	enableDailyRequesterEmail = models.BooleanField(default=False)
	enableWeeklyMissingHandlersEmail = models.BooleanField(default=False)
	enableDeclineOverdueCollections = models.BooleanField(default=False)
	changedBy = models.CharField(max_length=100)
	history = HistoricalRecords()

	def __str__(self):
		return 'AdminSettings: %s ' %(self.settingsName)

def enum(*sequential, **named):
	enums = dict(zip(sequential, range(len(sequential))), **named)
	return type(str('Enum'), (), enums)

StatusEnum = enum(
				WITHDRAWN=-2,
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

Col_StatusEnum = enum(
				APPROVETERMS_WAIT=0,
				WAITING=1,
				REJECTED=3,
				APPROVED=4)
