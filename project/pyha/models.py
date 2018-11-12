from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models


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
	downloadRequestHandler = models.CharField(max_length=500,null=True)
	decisionExplanation = models.CharField(max_length=1000,null=True)

	def __str__(self):
		return self.address
	

@python_2_unicode_compatible
class Request(models.Model):
	#id alkaa ykkösestä ja nousee
	id = models.AutoField(primary_key=True)
	lajiId = models.CharField(max_length=200) #id given by laji.api
	description = models.CharField(max_length=400)  #description given by the requester for his request
	
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
	
	#for sensstatus
	#status 0: Odottaa pyytäjän hyväksymistä
	#status 1: Odottaa viranomaisen käsittelyä
	#status 3: Hylätty
	#status 4: Hyväksytty
	#status 99: Ohitettu (skippofficial)
	
	sensstatus = models.IntegerField()
	sensDecisionExplanation = models.CharField(max_length=1000,null=True)
	sensComment = models.CharField(max_length=1000,null=True)
	date = models.DateTimeField()
	source = models.CharField(max_length=60)
	user = models.CharField(max_length=100)
	approximateMatches = models.IntegerField()
	downloadFormat = models.CharField(max_length=40)
	downloadIncludes = models.CharField(max_length=1000)
	downloadDate = models.CharField(max_length=400,null=True)
	filter_list = models.CharField(max_length=2000)
	personName = models.CharField(max_length=100,null=True)
	personStreetAddress = models.CharField(max_length=100,null=True)
	personPostOfficeName = models.CharField(max_length=100,null=True)
	personPostalCode = models.CharField(max_length=100,null=True)
	personCountry = models.CharField(max_length=100,null=True)
	personEmail = models.CharField(max_length=100,null=True)
	personPhoneNumber = models.CharField(max_length=100,null=True)
	personOrganizationName = models.CharField(max_length=100,null=True)
	personCorporationId = models.CharField(max_length=100,null=True)
	reason = models.CharField(max_length=16000,null=True)
	lang = models.CharField(max_length=10, default='fi') 
	frozen = models.BooleanField(default=False)

	def __str__(self):
		return self.id

@python_2_unicode_compatible
class RequestContact(models.Model):
	id = models.AutoField(primary_key=True)
	request = models.ForeignKey('Request', on_delete=models.CASCADE)
	personName = models.CharField(max_length=100,null=True)
	personStreetAddress = models.CharField(max_length=100,null=True)
	personPostOfficeName = models.CharField(max_length=100,null=True)
	personPostalCode = models.CharField(max_length=100,null=True)
	personCountry = models.CharField(max_length=100,null=True)
	personEmail = models.CharField(max_length=100,null=True)
	personPhoneNumber = models.CharField(max_length=100,null=True)
	personOrganizationName = models.CharField(max_length=100,null=True)
	personCorporationId = models.CharField(max_length=100,null=True)
	
	def __str__(self):
		return self.id

@python_2_unicode_compatible
class RequestLogEntry(models.Model):
	VIEW = 'VIEW'
	ACCEPT = 'ACC'
	DECISION_POSITIVE = 'POS'
	DECISION_RESET ='RESET'
	DECISION_NEGATIVE = 'NEG'
	ACTION = (
		(VIEW, 'views request'),
		(ACCEPT, 'accepts terms of use'),
		(DECISION_POSITIVE, 'accepts use of data'),
		(DECISION_RESET, 'resets the decision for a new round'),
		(DECISION_NEGATIVE, 'declines use of data'),
	)
	
	request = models.ForeignKey(Request, on_delete=models.CASCADE)
	collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, blank=True, null=True)
	date = models.DateTimeField(auto_now_add=True)
	user = models.CharField(max_length=100)
	role = models.CharField(max_length=100)
	action = models.CharField(max_length=5, choices=ACTION)
	requestLog = models.Manager()
	
	def __str__(self):
		return '%s (role: %s): %s (request: %d, collection: %s)' %(self.user, self.role, self.get_action_display(), self.request.id, self.collection )

@python_2_unicode_compatible		
class RequestSensitiveChatEntry(models.Model):
	request = models.ForeignKey(Request, on_delete=models.CASCADE)
	date = models.DateTimeField(auto_now_add=True)
	user = models.CharField(max_length=100)
	message = models.CharField(max_length=2000)
	requestChat = models.Manager()
	
	def __str__(self):
		return self.message
	
@python_2_unicode_compatible		
class RequestHandlerChatEntry(models.Model):
	request = models.ForeignKey(Request, on_delete=models.CASCADE)
	date = models.DateTimeField(auto_now_add=True)
	user = models.CharField(max_length=100)
	message = models.CharField(max_length=2000)
	target = models.CharField(max_length=200)
	requestHandlerChat = models.Manager()
	
	def __str__(self):
		return self.message

@python_2_unicode_compatible
class RequestInformationChatEntry(models.Model):
	request = models.ForeignKey(Request, on_delete=models.CASCADE)
	date = models.DateTimeField(auto_now_add=True)
	user = models.CharField(max_length=100)
	question = models.BooleanField()
	message = models.CharField(max_length=2000)
	target = models.CharField(max_length=200) #'sens' or apilaji defined collection id
	requestInformationChat = models.Manager()
	
	def __str__(self):
		return self.message

@python_2_unicode_compatible
class ContactPreset(models.Model):
	user = models.CharField(primary_key=True, max_length=100)
	requestPersonName = models.CharField(max_length=100,null=True)
	requestPersonStreetAddress = models.CharField(max_length=100,null=True)
	requestPersonPostOfficeName = models.CharField(max_length=100,null=True)
	requestPersonPostalCode = models.CharField(max_length=100,null=True)
	requestPersonCountry = models.CharField(max_length=100,null=True)
	requestPersonEmail = models.CharField(max_length=100,null=True)
	requestPersonPhoneNumber = models.CharField(max_length=100,null=True)
	requestPersonOrganizationName = models.CharField(max_length=100,null=True)
	requestPersonCorporationId = models.CharField(max_length=100,null=True)

	def __str__(self):
		return self.user



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