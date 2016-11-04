from __future__ import unicode_literals

from django.db import models

class Collection(models.Model):
	#collection_id ei ole mallin oikea id: id on automaattisesti generoitu
	#korjataan kun kerkiää
	collection_id = models.CharField(max_length=500)
	count = models.IntegerField()
	status = models.IntegerField()
	request = models.ForeignKey('Request', on_delete=models.CASCADE)
	taxonSecured = models.IntegerField(default=0)
	customSecured = models.IntegerField(default=0)

	# termsOfUse = models.CharField(max_length=1000
	secureReasons = models.CharField(max_length=500)
	# decision = models.CharField(max_length=100)
	# decisionDate = models.DateTimeField()
	decisionExplanation = models.CharField(max_length=1000,null=True)
	# collectionContact
	# collectionLicense 

	def __str__(self):
		return self.collection_id

class Request(models.Model):
	id = models.CharField(max_length=200, primary_key=True)
	description = models.CharField(max_length=400)
	order = models.IntegerField()
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
