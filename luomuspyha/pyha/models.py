from __future__ import unicode_literals

from django.db import models

class Collection(models.Model):
	address = models.CharField(max_length=500)
	count = models.IntegerField()
	status = models.IntegerField()
	request = models.ForeignKey('Request', on_delete=models.CASCADE)
	taxonSecured = models.IntegerField(default=0)
	customSecured = models.IntegerField(default=0)
	downloadRequestHandler = models.CharField(max_length=500,null=True)
	decisionExplanation = models.CharField(max_length=1000,null=True)

	def __str__(self):
		return self.address

class Request(models.Model):
	#id alkaa ykkösestä ja nousee
	id = models.AutoField(primary_key=True)
	lajiId = models.CharField(max_length=200) #old id
	description = models.CharField(max_length=400)
	status = models.IntegerField()
	sensstatus = models.IntegerField()
	sensDecisionExplanation = models.CharField(max_length=1000,null=True)
	date = models.DateTimeField()
	source = models.CharField(max_length=60)
	user = models.CharField(max_length=100)
	approximateMatches = models.IntegerField()
	downloadFormat = models.CharField(max_length=40)
	downloadIncludes = models.CharField(max_length=1000)
	filter_list = models.CharField(max_length=2000)
	requests = models.Manager()
	reason = models.CharField(max_length=1000,null=True)
	def __str__(self):
		return self.id

class RequestLogEntry(models.Model):
	VIEW = 'VIEW'
	ACCEPT = 'ACC'
	DECISION_POSITIVE = 'POS'
	DECISION_NEGATIVE = 'NEG'
	ACTION = (
		(VIEW, 'views request'),
		(ACCEPT, 'accepts terms of use'),
		(DECISION_POSITIVE, 'accepts use of data'),
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